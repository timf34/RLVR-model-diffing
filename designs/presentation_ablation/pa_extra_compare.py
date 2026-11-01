"""Score the other-model runs (run_extra/<slug>) and compare with Qwen 3.5 / 3.6 / 3.8 under strong RL framing.

  .venv/bin/python designs/presentation_ablation/pa_extra_compare.py [--no-score] [slug,...]
      -> run_extra/COMPARE.md, run_extra/compare.json

Per model and task: rate of the user-conflicting behaviour (send / scored title or sign-off / bullets) among valid
replies, original + fresh scenarios pooled, at tied scores (0.50/0.50) and when scores favour it (0.75/0.25), with
Wilson 95% intervals, plus the score effect (+0.50 rate minus tied rate). Rule-based scoring, no API calls.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import pa_extra as X  # noqa: E402
from pa_analysis import Data, load_rows, wilson  # noqa: E402

PY = HERE.parents[1] / ".venv" / "bin" / "python"
QWEN = [("Qwen 3.5", HERE / "run"), ("Qwen 3.6", HERE / "run_q36"), ("Qwen 3.8", HERE / "run")]
GROUPS = [  # (heading, slugs) in the order they are reported
    ("Qwen releases (reference)", []),
    ("OpenAI around o3", ["gpt-4o", "gpt-4.1", "o3", "gpt-5", "gpt-5.1", "gpt-5.2", "gpt-oss-120b", "gpt-oss-20b"]),
    ("Kimi K2.x reasoning models", ["kimi-k2-thinking", "kimi-k2.5", "kimi-k2.6"]),
    ("DeepSeek: V3 -> R1", ["deepseek-v3-0324", "deepseek-r1-0528"]),
    ("Qwen3-235B: Instruct -> Thinking", ["qwen3-235b-instruct", "qwen3-235b-thinking"]),
    ("Kimi: K2-0905 -> K2-thinking", ["kimi-k2-0905", "kimi-k2-thinking"]),
    ("MiniMax: 01 -> M1", ["minimax-01", "minimax-m1"]),
    ("GLM releases", ["glm-4.5", "glm-4.6", "glm-4.7"]),
    ("MiniMax M2 releases", ["minimax-m2", "minimax-m2.1", "minimax-m2.5", "minimax-m2.7"]),
]
TASK_NAMES = {"send": "sends the email", "titles": "adds title / sign-off", "bullets": "uses bullets"}


def score(slug: str):
    r = X.root(slug)
    for kind in ("send", "fmt"):
        if kind == "send" and not (r / "main" / "send" / "items.jsonl").exists():
            continue
        subprocess.run([str(PY), str(HERE / "pa_score.py"), kind, "--stage", "main", "--root", str(r)], check=True,
                       capture_output=True, cwd=HERE)


def cells(root: Path, model: str) -> dict:
    """task -> score -> (k, n) for strong framing (arm B), materials pooled."""
    out = defaultdict(lambda: defaultdict(lambda: [0, 0]))
    for (t, _mat, arm, sc, m), (k, n) in Data(load_rows("main", root)).cells.items():
        if arm == "B" and m == model:
            out[t][sc][0] += k
            out[t][sc][1] += n
    return out


def fmt_cell(kn) -> str:
    k, n = kn
    if not n:
        return "–"
    lo, hi = wilson(k, n)
    return f"{100 * k / n:.0f}% ({k}/{n}) [{100 * lo:.0f}, {100 * hi:.0f}]"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("slugs", nargs="?", default="all")
    ap.add_argument("--no-score", action="store_true")
    a = ap.parse_args()
    slugs = list(X.MODELS) if a.slugs == "all" else a.slugs.split(",")
    rows, out = [], {}
    for label, root in QWEN:
        rows.append(("Qwen releases (reference)", label, cells(root, label)))
    for slug in slugs:
        if not (X.root(slug) / "main").exists():
            continue
        if not a.no_score:
            score(slug)
        label = X.MODELS[slug][0]
        g = next(h for h, s in GROUPS if slug in s)
        rows.append((g, label, cells(X.root(slug), label)))
    lines = ["# Other models under strong RL framing (Part 1 items, original + fresh scenarios pooled)", "",
             "Rate of going against the user among valid replies. Tied = scores 0.50/0.50; +0.50 = scores favour "
             "going against the user (0.75/0.25). Effect = +0.50 rate − tied rate (points). Wilson 95% intervals.", ""]
    for task in ("send", "titles", "bullets"):
        lines += [f"## {task}: {TASK_NAMES[task]}", "", "| group | model | tied | +0.50 | effect |", "|---|---|---|---|---|"]
        for g, label, c in sorted(rows, key=lambda r: [h for h, _ in GROUPS].index(r[0])):
            t, p = c[task]["tied"], c[task]["p050"]
            if not (t[1] or p[1]):
                continue
            eff = 100 * (p[0] / p[1] - t[0] / t[1]) if t[1] and p[1] else float("nan")
            lines.append(f"| {g} | {label} | {fmt_cell(t)} | {fmt_cell(p)} | {eff:+.0f} |")
            out.setdefault(label, {})[task] = dict(tied=t, p050=p, effect_pts=eff, group=g)
        lines.append("")
    (X.EXTRA / "COMPARE.md").write_text("\n".join(lines))
    (X.EXTRA / "compare.json").write_text(json.dumps(out, indent=1))
    print("\n".join(lines))


if __name__ == "__main__":
    main()
