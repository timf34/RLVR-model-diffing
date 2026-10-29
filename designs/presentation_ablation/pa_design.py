"""Design constants, the item plan for each stage, plan counts and the cost estimate (stdlib only; no old imports).

Stages
  smoke      old inspection-only scenarios (never main blocks): arms B, N, B-d, N+d at +0.50, both models
  main       Part 1 (B and N on original + fresh materials) and Part 2 (13 one-component arms on fresh materials),
             generated together and interleaved, so every comparison is within one run
  factorial  GATED (off by default): 2^k over the components chosen by the frozen rule in PROTOCOL.md
             (pa_analysis.py select -> run/factorial/selection.json), fresh blocks

python pa_design.py counts | cost [--write]
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

from pa_common import GAPS, HERE, KIND, MODELS, RUN, TASKS
from pa_render import factorial_arms, part1_arms, part2_arms

N_FRESH = {"send": 32, "titles": 32, "bullets": 32}   # units (titles: 16 tasks x 2 sub-features); see POWER.md
ORIG_REPS = {"send": 3, "titles": 3, "bullets": 6}    # original scenarios: 12 / 12 / 6 units -> 36 episodes per cell
FRESH_REPS = {"Qwen 3.8": 2, "Qwen 3.5": 1}          # generations per fresh cell (3.8: 2 for power; see POWER.md)
SMOKE_ARMS = ("B", "N", "B-d", "N+d")
FACTORIAL_DEFAULT = dict(enabled=False, others="B", max_components=3)
STAGES = ("smoke", "main", "factorial")

# 10A per-episode cost ($, mean over 32 episodes each; designs/ifeval_incidental_grader/reference_check/run):
# keyed (task kind, delivery: inline = old arm / tool = new arm, model)
COST_10A = {("send", "inline", "Qwen 3.5"): 0.00370, ("send", "inline", "Qwen 3.8"): 0.00136,
            ("send", "tool", "Qwen 3.5"): 0.00288, ("send", "tool", "Qwen 3.8"): 0.00076,
            ("fmt", "inline", "Qwen 3.5"): 0.00624, ("fmt", "inline", "Qwen 3.8"): 0.00133,
            ("fmt", "tool", "Qwen 3.5"): 0.00124, ("fmt", "tool", "Qwen 3.8"): 0.00076}
COST_MARGIN = 1.5  # titles prompts are similar in size to bullets; margin covers retries and longer replies


def key(stage, task, block, arm, score, model, rep) -> str:
    return f"pa|{stage}|{task}|{block}|{arm}|{score}|{model}|{rep}"


def factorial_selection(root: Path = RUN) -> dict | None:
    p = root / "factorial" / "selection.json"
    return json.loads(p.read_text()) if p.exists() else None


def plan(stage: str, units: dict, root: Path = RUN, models=MODELS) -> list[dict]:
    """units: {task: {materials: [block ids]}} (from pa_materials, or run/units.json)."""
    out = []

    def add(part, task, block, materials, arms, reps):
        for arm in arms:
            for sc in GAPS:
                for m in models:
                    for r in range(reps if isinstance(reps, int) else reps[m]):
                        out.append(dict(key=key(stage, task, block, arm, sc, m, r), stage=stage, part=part, task=task,
                                        block=block, materials=materials, arm=arm, score=sc, gap=GAPS[sc], model=m,
                                        rep=r))
    for task in TASKS:
        if task not in units:
            continue
        if stage == "smoke":
            for b in units[task]["insp"]:
                for arm in SMOKE_ARMS:
                    for m in models:
                        out.append(dict(key=key(stage, task, b, arm, "p050", m, 0), stage=stage, part=0, task=task,
                                        block=b, materials="insp", arm=arm, score="p050", gap=GAPS["p050"], model=m,
                                        rep=0))
        elif stage == "main":
            for b in units[task]["orig"]:
                add(1, task, b, "orig", list(part1_arms()), ORIG_REPS[task])
            for b in units[task]["fresh"][:N_FRESH[task]]:
                add(1, task, b, "fresh", list(part1_arms()), FRESH_REPS)
                add(2, task, b, "fresh", list(part2_arms()), FRESH_REPS)
        elif stage == "factorial":
            sel = factorial_selection(root)
            assert sel and sel.get("enabled"), "factorial stage is gated: run `pa_analysis.py select` and set enabled"
            arms = list(factorial_arms(sel["components"], sel.get("others", "B")))
            for b in units[task]["fresh"][:N_FRESH[task]]:
                add(3, task, b, "fresh", arms, FRESH_REPS)
        else:
            raise ValueError(stage)
    assert len({i["key"] for i in out}) == len(out)
    return out


def expected_counts(stage: str, units: dict, n_factorial_arms: int = 0) -> dict:
    """Closed-form item counts per task (checked against plan() in the tests)."""
    nm, ns = len(MODELS), len(GAPS)
    out = {}
    for t in (t for t in TASKS if t in units):
        if stage == "smoke":
            out[t] = len(units[t]["insp"]) * len(SMOKE_ARMS) * nm
        elif stage == "main":
            n_orig = len(units[t]["orig"]) * ORIG_REPS[t] * len(part1_arms()) * ns * nm
            n_fresh = (min(N_FRESH[t], len(units[t]["fresh"])) * (len(part1_arms()) + len(part2_arms())) * ns
                       * sum(FRESH_REPS[m] for m in MODELS))
            out[t] = n_orig + n_fresh
        else:
            out[t] = (min(N_FRESH[t], len(units[t]["fresh"])) * n_factorial_arms * ns
                      * sum(FRESH_REPS[m] for m in MODELS))
    return out


def delivery(arm: str) -> str:
    from pa_render import arm_cfg
    return "inline" if arm_cfg(arm)["d"] == "B" else "tool"


def est_cost(items: list[dict]) -> dict:
    by = Counter()
    for i in items:
        by[(i["task"], i["model"])] += COST_10A[(KIND[i["task"]], delivery(i["arm"]), i["model"])] * COST_MARGIN
    tot = sum(by.values())
    return dict(total=tot, by_task_model={f"{t}|{m}": v for (t, m), v in sorted(by.items())})


def counts_table(items: list[dict]) -> str:
    c = Counter((i["task"], i["part"], i["materials"], i["model"]) for i in items)
    lines = ["| task | part | materials | model | episodes |", "|---|---|---|---|---|"]
    for (t, p, mat, m), n in sorted(c.items()):
        lines.append(f"| {t} | {p} | {mat} | {m} | {n} |")
    lines.append(f"| **all** | | | | **{len(items)}** |")
    return "\n".join(lines)


def cost_md(units: dict) -> str:
    main = plan("main", units)
    smoke = plan("smoke", units)
    fac_arms = 2 ** FACTORIAL_DEFAULT["max_components"]
    fac_items = [dict(task=t, model=m, arm="B" if a % 2 else "N")  # approx: half inline, half tool
                 for t in TASKS for _ in range(N_FRESH[t]) for a in range(fac_arms) for _s in GAPS for m in MODELS
                 for _r in range(FRESH_REPS[m])]
    cm, cs, cf = est_cost(main), est_cost(smoke), est_cost(fac_items)
    lines = [
        "# Cost estimate (from 10A per-episode costs)", "",
        "Per-episode costs are 10A's observed means (usage x listed prices; `designs/ifeval_incidental_grader/"
        "reference_check/run/*/episodes.jsonl`, 32 episodes per cell), by task kind, delivery (inline = 10A old arm, "
        f"tool = 10A new arm) and model, times a {COST_MARGIN}x margin (retries, longer titles replies, multi-turn "
        "sending). Generated by `python pa_design.py cost --write`.", "",
        "| kind | delivery | model | $/episode (10A) |", "|---|---|---|---|"]
    for (k, d, m), v in COST_10A.items():
        lines.append(f"| {k} | {d} | {m} | {v:.5f} |")
    lines += ["", f"- **smoke:** {len(smoke)} episodes, about **${cs['total']:.2f}**",
              f"- **main (Part 1 + Part 2):** {len(main)} episodes, about **${cm['total']:.2f}**",
              f"- **factorial (gated, 3 components, if enabled):** {len(fac_items)} episodes, about **${cf['total']:.2f}**",
              "", "Main by task and model:", "", "| task / model | $ |", "|---|---|"]
    for k, v in cm["by_task_model"].items():
        lines.append(f"| {k} | {v:.2f} |")
    lines += ["", "Budget guard: `pa_generate.py` stops launching new episodes when the ledger (all stages, every attempt) "
              "plus in-flight estimates reaches `--budget-stop` (default $40), well above the estimate.", "",
              "Main plan counts:", "", counts_table(main), ""]
    return "\n".join(lines)


def main():
    sys.path.insert(0, str(HERE))
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["counts", "cost"])
    ap.add_argument("--write", action="store_true")
    a = ap.parse_args()
    units = json.loads((RUN / "units.json").read_text())
    if a.cmd == "counts":
        for st in ("smoke", "main"):
            items = plan(st, units)
            print(st, len(items), expected_counts(st, units))
    else:
        md = cost_md(units)
        if a.write:
            (HERE / "COST.md").write_text(md)
        print(md.split("Main by task")[0][-400:])


if __name__ == "__main__":
    main()
