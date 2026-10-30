"""Figure for the main stage (repo .venv, matplotlib):  .venv/bin/python rj_figure.py [stage]
Reads run/<stage>/items.jsonl + judge.jsonl directly (block-cluster bootstrap intervals, 2,000 draws).
Writes figure/labels_<stage>.png and .svg."""
from __future__ import annotations

import random
import sys
from collections import defaultdict

from rj_analysis import load
from rj_common import HERE, MODELS

# validated default categorical palette, slots 1-2 (dataviz skill); text in ink tokens, never series colour
COLOR = {"Qwen 3.8": "#2a78d6", "Qwen 3.5": "#eb6834"}
INK, INK2, GRID = "#0b0b0b", "#52514e", "#e6e5e1"
CELLS = [("B", "p050", "Bundle, +0.50"), ("B", "tied", "Bundle, tied"), ("N", "p050", "New, +0.50"),
         ("N", "tied", "New, tied")]
PANELS = [("recognises_conflict", "Recognises the conflict", lambda r: r["recognises_conflict"] == "yes"),
          ("end_expected_score", "Endorses acting for the higher score", lambda r: r["end_expected_score"]),
          ("end_user_priority", "Endorses the user's instruction", lambda r: r["end_user_priority"]),
          ("end_scores_untrusted", "Discounts the scores as untrusted", lambda r: r["end_scores_untrusted"])]


def boot(rows, f, draws=2000, seed=0):
    by = defaultdict(list)
    for r in rows:
        by[r["block"]].append(r)
    blocks = sorted(by)
    if not blocks:
        return None, (None, None)
    est = sum(f(r) for r in rows) / len(rows)
    rng = random.Random(seed)
    vals = []
    for _ in range(draws):
        rs = [r for b in rng.choices(blocks, k=len(blocks)) for r in by[b]]
        vals.append(sum(f(r) for r in rs) / len(rs))
    vals.sort()
    return est, (vals[int(0.025 * draws)], vals[int(0.975 * draws) - 1])


def main(stage: str = "main") -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Patch

    rows = [r for r in load(stage) if r["labelled"]]
    fig, axes = plt.subplots(1, len(PANELS), figsize=(13, 3.6), sharey=True)
    h, gap = 0.34, 0.04
    for ax, (field, title, f) in zip(axes, PANELS):
        for ci, (arm, score, _) in enumerate(CELLS):
            for mi, model in enumerate(MODELS):
                cell = [r for r in rows if r["arm"] == arm and r["score"] == score and r["model"] == model]
                est, (lo, hi) = boot(cell, f, seed=hash((field, arm, score, model)) % 10**6)
                if est is None:
                    continue
                y = ci + (mi - 0.5) * (h + gap)
                ax.barh(y, est, height=h, color=COLOR[model], edgecolor="white", linewidth=1)
                ax.plot([lo, hi], [y, y], color=INK2, linewidth=1, solid_capstyle="butt")
                ax.text(max(est, hi) + 0.02, y, f"{100 * est:.0f}%", va="center", ha="left", fontsize=8, color=INK2)
        ax.set_title(title, fontsize=10, color=INK, loc="left")
        ax.set_xlim(0, 1.18)
        ax.set_xticks([0, 0.5, 1.0])
        ax.set_xticklabels(["0", "50%", "100%"], fontsize=8, color=INK2)
        ax.set_yticks(range(len(CELLS)))
        ax.set_yticklabels([c[2] for c in CELLS], fontsize=9, color=INK)
        ax.set_ylim(len(CELLS) - 0.5, -0.5)   # first cell at the top (shared axis: set, do not invert)
        ax.grid(axis="x", color=GRID, linewidth=0.8)
        ax.set_axisbelow(True)
        for s in ("top", "right", "left"):
            ax.spines[s].set_visible(False)
        ax.spines["bottom"].set_color(GRID)
        ax.tick_params(length=0)
    fig.legend(handles=[Patch(color=COLOR[m], label=m) for m in MODELS], loc="lower right", ncol=2, frameon=False,
               fontsize=9, bbox_to_anchor=(0.99, -0.02))
    n = {m: sum(r["model"] == m for r in rows) for m in MODELS}
    fig.suptitle("What the pre-action reasoning says, by presentation and displayed score gap (sending task)\n"
                 f"Judge-labelled episodes: {n['Qwen 3.8']} Qwen 3.8, {n['Qwen 3.5']} Qwen 3.5. "
                 "Bars: share of labelled episodes; lines: 95% block-bootstrap intervals.",
                 fontsize=9, color=INK2, x=0.01, ha="left")
    fig.tight_layout(rect=(0, 0.04, 1, 0.9))
    out = HERE / "figure"
    out.mkdir(exist_ok=True)
    for ext in ("png", "svg"):
        fig.savefig(out / f"labels_{stage}.{ext}", dpi=200 if ext == "png" else None, facecolor="white")
    print(f"wrote {out / f'labels_{stage}.png'}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "main")
