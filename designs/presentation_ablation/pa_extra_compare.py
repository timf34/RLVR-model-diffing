"""Score the other-model runs and compare with Qwen 3.5 / 3.6 / 3.8 under strong RL framing (no API calls).

  .venv/bin/python designs/presentation_ablation/pa_extra_compare.py [--no-score] [slug,...]
      -> run_extra/COMPARE.md, run_extra/compare.json

Per model and task: rate of the user-conflicting behaviour (sends / acts; scored title or sign-off; bullets) at tied
scores (0.50/0.50) and when scores favour it (0.75/0.25), original + fresh scenarios pooled, strong RL framing (arm B).

Sources: the main replay (run_extra/<slug>; Qwen 3.5 and 3.8 from run/, Qwen 3.6 from run_q36/) plus, where present,
the extra fresh-scenario repeats in run_more/<slug> (pa_extra.py --more) and the matching original-scenario
repeats in run_more_orig/<slug> (--more-orig), so both kinds of scenario count about equally.
Sending: an episode that acted but ended with a blank final message still counts (whether it acted is read from the
tool log, with the old study's own scorer); the scorer's "valid" rule would drop it. This matters for GPT-5.1.
95% intervals: bootstrap over scenarios (runs of the same scenario are correlated), 4000 draws, fixed seeds; for
0% (or 100%) cells, where the bootstrap collapses, a Wilson interval with n = number of scenarios.
"""
from __future__ import annotations

import argparse
import json
import random
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import pa_extra as X  # noqa: E402
from pa_common import iter_jsonl  # noqa: E402

PY = HERE.parents[1] / ".venv" / "bin" / "python"
QWEN_MAIN = {"Qwen 3.5": HERE / "run", "Qwen 3.6": HERE / "run_q36", "Qwen 3.8": HERE / "run"}
GROUPS = [  # (heading, slugs) in the order they are reported
    ("Qwen 27B", ["qwen3.5", "qwen3.6", "qwen3.8"]),
    ("Kimi", ["kimi-k2-0905", "kimi-k2-thinking", "kimi-k2.5", "kimi-k2.6"]),
    ("DeepSeek", ["deepseek-v3-0324", "deepseek-r1-0528", "deepseek-v3.2-exp", "deepseek-v3.2", "deepseek-v4-flash",
                  "deepseek-v4-flash-0731", "deepseek-v4-pro", "deepseek-v4-pro-0813", "deepseek-v4.1-flash",
                  "deepseek-v4.1-flash-1017"]),
    ("GLM", ["glm-4.5", "glm-4.6", "glm-4.7"]),
    ("OpenAI", ["gpt-4o", "gpt-4.1", "o3", "gpt-5", "gpt-5.1", "gpt-5.2", "gpt-oss-120b", "gpt-oss-20b"]),
    ("Qwen3-235B", ["qwen3-235b-instruct", "qwen3-235b-thinking"]),
    ("MiniMax", ["minimax-01", "minimax-m1", "minimax-m2", "minimax-m2.1", "minimax-m2.5", "minimax-m2.7"]),
]
TASK_NAMES = {"send": "sends / acts", "titles": "adds title / sign-off", "bullets": "uses bullets"}


def score_root(r: Path):
    for kind in ("send", "fmt"):
        if kind == "send" and not (r / "main" / "send" / "items.jsonl").exists():
            continue
        subprocess.run([str(PY), str(HERE / "pa_score.py"), kind, "--stage", "main", "--root", str(r)], check=True,
                       capture_output=True, cwd=HERE)


def acted_on_blank(root: Path) -> dict:
    """key -> acted, for sending episodes that ended with a blank final message (scorer: completion 'empty')."""
    import pa_score as S
    from pa_common import load_kind
    d = root / "main" / "send"
    if not (d / "scored.jsonl").exists():
        return {}
    empty = {r["key"] for r in iter_jsonl(d / "scored.jsonl") if r["completion"] == "empty"}
    if not empty:
        return {}
    L, blocks = load_kind("send"), json.loads((d / "blocks.json").read_text())
    items = {it["key"]: it for it in iter_jsonl(d / "items.jsonl")}
    best = S.latest("main", "send", root)
    return {k: S.measure("send", L, blocks[items[k]["block"]], best[k])["outcome"] for k in empty}


def rows_for(label: str, roots: list[Path]) -> list[dict]:
    out = []
    for r in roots:
        blank = acted_on_blank(r)
        for t in ("send", "titles", "bullets"):
            p = r / "main" / t / "scored.jsonl"
            if not p.exists():
                continue
            for row in iter_jsonl(p):
                if row["model"] != label or row["arm"] != "B" or row.get("part") != 1:
                    continue
                if row["completion"] == "valid":
                    out.append(dict(task=t, score=row["score"], block=row["block"], y=bool(row["outcome"])))
                elif t == "send" and row["key"] in blank:
                    out.append(dict(task=t, score=row["score"], block=row["block"], y=bool(blank[row["key"]])))
    return out


def boot(by_block: dict, seed: int, draws: int = 4000):
    keys = sorted(by_block)
    flat = [y for k in keys for y in by_block[k]]
    k, n = sum(flat), len(flat)
    rng = random.Random(seed)
    bs = []
    for _ in range(draws):
        pick = [y for b in rng.choices(keys, k=len(keys)) for y in by_block[b]]
        bs.append(sum(pick) / len(pick))
    bs.sort()
    lo, hi = bs[int(0.025 * draws)], bs[int(0.975 * draws) - 1]
    if k in (0, n):   # the bootstrap collapses to a point; use Wilson with n = number of scenarios (conservative)
        lo, hi = wilson(k / n * len(keys), len(keys))
    return dict(k=k, n=n, rate=k / n, lo=lo, hi=hi, scenarios=len(keys))


def wilson(k, n, z=1.959964):
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * (p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5 / d
    return max(0.0, c - h), min(1.0, c + h)


def summarise(rows: list[dict], label: str) -> dict:
    cells = defaultdict(lambda: defaultdict(list))
    for r in rows:
        cells[(r["task"], r["score"])][r["block"]].append(r["y"])
    out = {}
    for (t, sc), bb in cells.items():
        out.setdefault(t, {})[sc] = boot(bb, seed=sum(map(ord, f"{label}{t}{sc}")))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("slugs", nargs="?", default="all")
    ap.add_argument("--no-score", action="store_true")
    ap.add_argument("--main-only", action="store_true", help="ignore the extra repeats (run_more*, e.g. while running)")
    a = ap.parse_args()
    want = None if a.slugs == "all" else set(a.slugs.split(","))
    out = {}
    for g, slugs in GROUPS:
        for slug in slugs:
            if want and slug not in want:
                continue
            label = X.MODELS[slug][0]
            roots = [QWEN_MAIN[label]] if label in QWEN_MAIN else [X.EXTRA / slug]
            for extra in () if a.main_only else (X.MORE / slug, X.MORE_ORIG / slug):
                if (extra / "main").exists():
                    roots.append(extra)
            if not (roots[0] / "main").exists():
                continue
            if not a.no_score:
                for r in roots:
                    if r not in QWEN_MAIN.values():   # the frozen Qwen runs are already scored
                        score_root(r)
            res = summarise(rows_for(label, roots), label)
            out[label] = dict(group=g, slug=slug, extra_reps=len(roots) > 1, tasks=res)
    lines = ["# Other models under strong RL framing (Part 1 items, original + fresh scenarios pooled)", "",
             "Rate of going against the user. Tied = scores 0.50/0.50; +0.50 = scores favour going against the user "
             "(0.75/0.25). Effect = +0.50 rate − tied rate (points). 95% intervals: bootstrap over scenarios. "
             "+ = includes the extra fresh-scenario repeats (run_more/).", ""]
    for task in ("send", "titles", "bullets"):
        lines += [f"## {task}: {TASK_NAMES[task]}", "", "| group | model | tied | +0.50 | effect |", "|---|---|---|---|---|"]
        for label, v in out.items():
            c = v["tasks"].get(task)
            if not c or "p050" not in c or "tied" not in c:
                continue
            t, p = c["tied"], c["p050"]
            f = lambda x: f"{100 * x['rate']:.0f}% ({x['k']}/{x['n']}) [{100 * x['lo']:.0f}, {100 * x['hi']:.0f}]"  # noqa: E731
            lines.append(f"| {v['group']} | {label}{' +' if v['extra_reps'] else ''} | {f(t)} | {f(p)} | "
                         f"{100 * (p['rate'] - t['rate']):+.0f} |")
        lines.append("")
    (X.EXTRA / "COMPARE.md").write_text("\n".join(lines))
    (X.EXTRA / "compare.json").write_text(json.dumps(out, indent=1))
    print("\n".join(lines))


if __name__ == "__main__":
    main()
