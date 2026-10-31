"""Qwen 3.6 addendum: replay the frozen Qwen 3.5 items on Qwen 3.6, so all three models see identical prompts.

The frozen study (run/) stays untouched. Everything for 3.6 lives under run_q36/:

  python pa_q36.py prepare                       # clone 3.5 items (main + factorial) -> 3.6; write run_q36/manifest.json
  memguard -m 4 -- python pa_q36.py generate main --part 1   # Part 1 first (strong vs weak RL framing)
  memguard -m 4 -- python pa_q36.py generate factorial
  memguard -m 4 -- python pa_q36.py generate main            # the rest (Part 2)
  python pa_q36.py status
  python pa_score.py send|fmt --stage main|factorial --root designs/presentation_ablation/run_q36

Same design as Qwen 3.5 (1 generation per fresh cell, the same reps on original blocks), same serving config entry
as every earlier 3.6 run (experiment.grading.3way.json: openrouter qwen3.6-27b, Alibaba only, no fallbacks), same
episode loop, temperature, max tokens and timeout (pa_generate / pa_common, imported unchanged).
"""
from __future__ import annotations

import argparse
import asyncio
import json
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import pa_common as C  # noqa: E402

MODEL, SOURCE = "Qwen 3.6", "Qwen 3.5"
Q36 = HERE / "run_q36"
STAGES = ("main", "factorial")
PRICE = (0.45, 2.7)  # $/M (in, out), as action/run.py and action_mechanisms/shared/serving.py


def clone_items(stage: str, task: str) -> list[dict]:
    out = []
    for it in C.iter_jsonl(C.RUN / stage / task / "items.jsonl"):
        if it["model"] != SOURCE:
            continue
        it = dict(it, model=MODEL, key=it["key"].replace(f"|{SOURCE}|", f"|{MODEL}|"))
        assert MODEL in it["key"]
        out.append(it)
    return out


def prepare():
    man = dict(at=C.now(), label="Qwen 3.6 addendum: Qwen 3.5 items replayed on Qwen 3.6", stages={},
               code_sha256=C.sha((HERE / "pa_q36.py").read_bytes()))
    Q36.mkdir(exist_ok=True)
    shutil.copyfile(C.RUN / "units.json", Q36 / "units.json")
    for stage in STAGES:
        man["stages"][stage] = dict(source_manifest_sha256=C.sha((C.RUN / stage / "manifest.json").read_bytes()),
                                    tasks={})
        if stage == "factorial":
            (Q36 / stage).mkdir(parents=True, exist_ok=True)
            shutil.copyfile(C.RUN / stage / "selection.json", Q36 / stage / "selection.json")
        for task in C.TASKS:
            src, dst = C.RUN / stage / task, Q36 / stage / task
            dst.mkdir(parents=True, exist_ok=True)
            items = clone_items(stage, task)
            need = {i["input_sha256"] for i in items}
            with (dst / "prompts.jsonl").open("w") as f:
                n = 0
                for line in (src / "prompts.jsonl").open():
                    p = json.loads(line)
                    if p["input_sha256"] in need:
                        assert C.jhash(p["input"]) == p["input_sha256"]
                        f.write(line if line.endswith("\n") else line + "\n")
                        n += 1
            assert n == len(need), (stage, task, n, len(need))
            with (dst / "items.jsonl").open("w") as f:
                for it in items:
                    f.write(json.dumps(it) + "\n")
            shutil.copyfile(src / "blocks.json", dst / "blocks.json")
            man["stages"][stage]["tasks"][task] = dict(
                n_items=len(items), n_prompts=n, items_digest=C.jhash(items),
                blocks_sha256=C.sha((dst / "blocks.json").read_bytes()))
            print(f"{stage}/{task}: {len(items)} items, {n} prompts")
    (Q36 / "manifest.json").write_text(json.dumps(man, indent=1))


def verify(stage: str, root: Path):
    man = json.loads((Q36 / "manifest.json").read_text())["stages"][stage]
    assert C.sha((C.RUN / stage / "manifest.json").read_bytes()) == man["source_manifest_sha256"], "source changed"
    for task, v in man["tasks"].items():
        assert C.jhash(clone_items(stage, task)) == v["items_digest"], f"{stage}/{task}: items differ from 3.5 clone"
        assert C.jhash(list(C.iter_jsonl(root / stage / task / "items.jsonl"))) == v["items_digest"]
        assert C.sha((C.RUN / stage / task / "blocks.json").read_bytes()) == v["blocks_sha256"]
    return man


def patch(part: int | None):
    """Point the unchanged generator at Qwen 3.6 (serving entry, price, budget estimate, verify, optional part filter)."""
    import pa_freeze
    import pa_generate as G
    C.PRICES[MODEL] = PRICE
    G.EST_INFLIGHT[MODEL] = 0.02
    pa_freeze.verify = verify
    s = json.loads(C.SERVING_CONFIG.read_text())
    tgt = [{k: v for k, v in t.items() if k != "serving_note"} for t in s["targets"] if t["label"] == MODEL]
    assert len(tgt) == 1
    G.serving = lambda: dict(targets=tgt, target_generate=s["target_generate"], temperature=C.TEMPERATURE,
                             target_max_tokens=C.MAX_TOKENS, timeout=C.TIMEOUT)
    if part is not None:
        orig = G.load_task

        def load_task(stage, task, root):
            items, prompts, blocks = orig(stage, task, root)
            return [i for i in items if i.get("part") == part], prompts, blocks
        G.load_task = load_task
    return G


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["prepare", "generate", "status"])
    ap.add_argument("stage", nargs="?", default="main", choices=STAGES)
    ap.add_argument("--part", type=int, default=None)
    ap.add_argument("--task", default="all")
    ap.add_argument("--concurrency", type=int, default=16)
    ap.add_argument("--minutes", type=float, default=900)
    ap.add_argument("--budget-stop", type=float, default=80.0)
    ap.add_argument("--max-items", type=int, default=None)
    a = ap.parse_args()
    if a.cmd == "prepare":
        prepare()
        return
    G = patch(a.part)
    tasks = C.TASKS if a.task == "all" else tuple(a.task.split(","))
    if a.cmd == "status":
        for st in STAGES:
            G.status(st, Q36, tasks)
        return
    asyncio.run(G.run(a.stage, Q36, tasks, (MODEL,), a.concurrency, a.minutes, a.budget_stop, a.max_items, None))


if __name__ == "__main__":
    main()
