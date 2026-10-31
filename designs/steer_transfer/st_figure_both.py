"""Deck figure: both steering directions in both target models (sending task). No API calls.

  .venv/bin/python designs/steer_transfer/st_figure_both.py   -> figure/steer_both.{png,svg}

Left: target Qwen 3.5 (main stage, run/main/scored.jsonl). Right: target Qwen 3.8 — its unsteered and own-direction
cells from the main stage (reused as the reverse addendum's primary analysis does), 3.5's direction and the random
controls from run/reverse (scored with st_reverse.score: sends from the tool log, as everywhere). Colour = whose
direction (orange: Qwen 3.8's, blue: Qwen 3.5's, grey: random). y = send rate when earlier scores favour sending;
95% intervals are a block bootstrap over the 44 scenarios.
"""
from __future__ import annotations

import json
import random
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
Q35, Q38, RAND = "#2a78d6", "#eb6834", "#9c9a92"
INK, INK2, GRID = "#0b0b0b", "#52514e", "#e6e5e1"
STRENGTHS = [-0.3, -0.1, 0.0, 0.1, 0.3]


def load():
    import st_reverse as R
    rows = [json.loads(line) for line in (HERE / "run/main/scored.jsonl").open()]
    rows += R.score(R.RUN, "reverse")
    by = defaultdict(lambda: defaultdict(list))   # (target, cond, score) -> block -> [sent]
    for r in rows:
        if r.get("completion") == "missing":
            continue
        by[(r["model"], r["cond"], r["score"])][r["block"]].append(bool(r["sent"]))
    return by


def rate_ci(blocks: dict, seed: int, draws: int = 4000):
    keys = sorted(blocks)
    flat = [s for k in keys for s in blocks[k]]
    rng = random.Random(seed)
    boots = []
    for _ in range(draws):
        pick = [s for k in rng.choices(keys, k=len(keys)) for s in blocks[k]]
        boots.append(sum(pick) / len(pick))
    boots.sort()
    return sum(flat) / len(flat), boots[int(0.025 * draws)], boots[int(0.975 * draws) - 1]


def main() -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D

    by = load()
    other = [(k, sum(map(sum, v.values())), sum(map(len, v.values()))) for k, v in by.items() if k[2] != "conflict"]
    assert all(k_sent == 0 for _, k_sent, _ in other), [o for o in other if o[1]]
    n_other = sum(n for _, _, n in other)

    def series(target, kind, strengths):
        out = []
        for s in strengths:
            cell = by.get((target, "none" if s == 0 else f"{kind}_{s:+.1f}", "conflict"))
            if cell:
                out.append((s, *rate_ci(cell, seed=sum(map(ord, f"{target}{kind}{s}")))))
        return out

    fig, axes = plt.subplots(1, 2, figsize=(13, 5.8), sharey=True)
    # whose direction: on 3.5 "xfer" is 3.8's and "native" is 3.5's; on 3.8 the reverse
    panels = [("Qwen 3.5", {"xfer": Q38, "native": Q35}), ("Qwen 3.8", {"native": Q38, "xfer": Q35})]
    for ax, (target, kinds) in zip(axes, panels):
        for kind, col in kinds.items():
            dx = 0.008 if col == Q38 else -0.008
            pts = series(target, kind, STRENGTHS)
            xs = [s + dx for s, *_ in pts]
            ys = [e for _, e, *_ in pts]
            ax.plot(xs, ys, "-", color=col, marker="o" if col == Q38 else "s", ms=7, lw=2.2, mec="white", mew=1.2,
                    zorder=4)
            for x, (_, e, lo, hi) in zip(xs, pts):
                ax.plot([x, x], [lo, hi], color=col, lw=1.2, alpha=0.55, zorder=3)
            for s, x, y in zip(STRENGTHS, xs, ys):
                if (target == "Qwen 3.8" and s in (-0.3, 0.3)) or (s == 0.3 and col == Q38):
                    ax.annotate(f"{100 * y:.0f}%", (x, y), xytext=(12 if s > 0 else -12, 0), textcoords="offset points",
                                ha="left" if s > 0 else "right", va="center", fontsize=8.5, color=INK, weight="bold")
        for kind, dx in (("random0", 0.028), ("random1", 0.042)):
            for s, e, lo, hi in series(target, kind, [-0.3, 0.3]):
                x = s + (dx if s > 0 else -dx)
                ax.plot([x, x], [lo, hi], color=RAND, lw=1.2, alpha=0.7, zorder=3)
                ax.plot(x, e, "D", color=RAND, ms=6, mec="white", mew=1.0, zorder=4)
        base = series(target, "none", [0.0])[0][1]
        ax.axhline(base, color=INK2, lw=0.8, ls=":", zorder=1)
        ax.set_title(f"Steering Qwen {target[-3:]}", fontsize=10.5, color=INK, loc="left", weight="bold")
        ax.set_xticks(STRENGTHS, ["−0.3", "−0.1", "0\n(unsteered)", "+0.1", "+0.3"], fontsize=8.5, color=INK2)
        ax.set_xlim(-0.4, 0.42)
        ax.set_ylim(0, 1)
        ax.set_yticks([0, 0.25, 0.5, 0.75, 1.0], ["0%", "25%", "50%", "75%", "100%"], fontsize=8.5, color=INK2)
        ax.grid(axis="y", color=GRID, lw=0.8)
        ax.set_axisbelow(True)
        for sp in ("top", "right"):
            ax.spines[sp].set_visible(False)
        for sp in ("left", "bottom"):
            ax.spines[sp].set_color(GRID)
        ax.tick_params(length=0)
    axes[0].set_ylabel("Sends the email the user said to keep as a draft", fontsize=9, color=INK)
    axes[0].legend(handles=[Line2D([], [], color=Q38, marker="o", lw=2, mec="white", label="Qwen 3.8's direction"),
                            Line2D([], [], color=Q35, marker="s", lw=2, mec="white", label="Qwen 3.5's direction"),
                            Line2D([], [], color=RAND, marker="D", ls="", mec="white",
                                   label="random directions, same size (two seeds)"),
                            Line2D([], [], color=INK2, lw=0.8, ls=":", label="unsteered")],
                   loc="upper left", frameon=False, fontsize=8.5)
    fig.text(0.53, 0.165, "Steering strength   (+ = toward \"an automated grader will judge this\",  − = toward "
             "\"a human will\")", ha="center", fontsize=8.5, color=INK2)
    fig.suptitle("Steering toward \"an automated grader\" raises score-following in both models; on Qwen 3.5, "
                 "only Qwen 3.8's direction does it", fontsize=11.5, weight="bold", color=INK, x=0.01, y=0.985,
                 ha="left")
    fig.text(0.01, 0.925, "Sending task, strong RL framing, earlier scores favour sending (0.75 vs 0.25). One layer "
             "(36), each direction scaled to the target model. 176 episodes per point (44 scenarios × 4); lines are "
             "95% intervals.", fontsize=8.5, color=INK2, ha="left")
    fig.text(0.01, 0.02,
             f"With reversed, tied or no scores, no condition sent at all (0 of {n_other:,} episodes across both models), "
             "so steering does not simply make the model send more.\nRandom directions leave Qwen 3.5 unchanged but move "
             "Qwen 3.8 the opposite way to the grader directions: 3.8's choice here is sensitive to perturbation in "
             "general.\nThe grader directions are still far from random (3.5's direction at +0.3 on 3.8: +32 points over "
             "the random average). Qwen 3.8 unsteered = 62% (main run; a same-session re-run gave 56%).\nOn formatting "
             "(titles), both directions raise score-following on Qwen 3.5 equally (2 → 13 of 176), so the 3.8-only "
             "effect on 3.5 is specific to sending. Exploratory beyond the preregistered contrasts.",
             fontsize=7.8, color=INK2, ha="left", va="bottom", linespacing=1.45)
    fig.subplots_adjust(left=0.07, right=0.99, top=0.84, bottom=0.27, wspace=0.06)
    out = HERE / "figure"
    for ext in ("png", "svg"):
        fig.savefig(out / f"steer_both.{ext}", dpi=200 if ext == "png" else None, facecolor="white")
    print(f"wrote {out}/steer_both.png")


if __name__ == "__main__":
    main()
