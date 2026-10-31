"""Deck figure for the formatting steering transfer (matplotlib; reads run/main/scored.jsonl, no API calls).

  .venv/bin/python designs/steer_transfer_fmt/sf_figure.py   -> figure/steer_fmt.{png,svg}

Rows: target model (Qwen 3.5, Qwen 3.8). Columns: title, sign-off, bullets. y = override rate (the reply adopts the
score-favoured format the user asked to leave out), valid replies, when earlier scores favour that format.
Colour = whose direction (orange: Qwen 3.8's, blue: Qwen 3.5's, grey: random). 95% intervals: block bootstrap over
scenarios. Encoding matches steer_transfer/figure/steer_both.png.
"""
from __future__ import annotations

import json
import random
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
Q35, Q38, RAND = "#2a78d6", "#eb6834", "#9c9a92"
INK, INK2, GRID = "#0b0b0b", "#52514e", "#e6e5e1"
STRENGTHS = [-0.3, -0.1, 0.0, 0.1, 0.3]
FAMS = [("title", "Adds a title\n(user asked for none)"), ("signoff", "Adds the scored sign-off\n(user asked for none)"),
        ("bullets", "Uses bullet points\n(user asked for a paragraph)")]
P1 = {"title": "+6 pts, Holm p = 0.004", "signoff": "+2 pts, n.s.", "bullets": "+5 pts, Holm p = 0.09"}


def load():
    by = defaultdict(lambda: defaultdict(list))   # (family, target, cond, score) -> block -> [override]
    for line in (HERE / "run/main/scored.jsonl").open():
        r = json.loads(line)
        if r["completion"] == "valid":
            by[(r["family"], r["model"], r["cond"], r["score"])][r["block"]].append(bool(r["override"]))
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
    return sum(flat) / len(flat), boots[int(0.025 * draws)], boots[int(0.975 * draws) - 1], sum(flat), len(flat)


def main() -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D

    by = load()
    other = [(k, sum(map(sum, v.values())), sum(map(len, v.values()))) for k, v in by.items() if k[3] != "conflict"]
    n_other_k = sum(k for _, k, _ in other)
    n_other = sum(n for _, _, n in other)

    def series(fam, target, kind, strengths):
        out = []
        for s in strengths:
            cell = by.get((fam, target, "none" if s == 0 else f"{kind}_{s:+.1f}", "conflict"))
            if cell:
                out.append((s, *rate_ci(cell, seed=sum(map(ord, f"{fam}{target}{kind}{s}")))))
        return out

    fig, axes = plt.subplots(2, 3, figsize=(13, 8.2), sharex=True)
    rows = [("Qwen 3.5", {"xfer": Q38, "native": Q35}, 0.25), ("Qwen 3.8", {"native": Q38, "xfer": Q35}, 1.0)]
    for ri, (target, kinds, ytop) in enumerate(rows):
        for ci, (fam, ftitle) in enumerate(FAMS):
            ax = axes[ri][ci]
            for kind, col in kinds.items():
                dx = 0.008 if col == Q38 else -0.008
                pts = series(fam, target, kind, STRENGTHS)
                xs = [s + dx for s, *_ in pts]
                ys = [e for _, e, *_ in pts]
                ax.plot(xs, ys, "-", color=col, marker="o" if col == Q38 else "s", ms=6, lw=2, mec="white", mew=1.1,
                        zorder=4)
                for x, (_, e, lo, hi, k, n) in zip(xs, pts):
                    ax.plot([x, x], [lo, hi], color=col, lw=1.1, alpha=0.55, zorder=3)
                if target == "Qwen 3.5" and col == Q38:
                    _, e, lo, hi, k, n = pts[-1]
                    ax.annotate(f"{k}/{n}", (xs[-1], e), xytext=(9, 0), textcoords="offset points", va="center",
                                fontsize=8, color=INK, weight="bold")
            for kind, dx in (("random0", 0.028), ("random1", 0.042)):
                for s, e, lo, hi, k, n in series(fam, target, kind, [-0.3, 0.3]):
                    x = s + (dx if s > 0 else -dx)
                    ax.plot([x, x], [lo, hi], color=RAND, lw=1.1, alpha=0.7, zorder=3)
                    ax.plot(x, e, "D", color=RAND, ms=5, mec="white", mew=0.9, zorder=4)
            base = series(fam, target, "none", [0.0])[0][1]
            ax.axhline(base, color=INK2, lw=0.8, ls=":", zorder=1)
            ax.set_ylim(0, ytop)
            step = 0.05 if ytop <= 0.25 else 0.25
            ticks = [round(i * step, 2) for i in range(int(round(ytop / step)) + 1)]
            ax.set_yticks(ticks, [f"{100 * t:.0f}%" for t in ticks], fontsize=8, color=INK2)
            ax.set_xticks(STRENGTHS, ["−0.3", "−0.1", "0", "+0.1", "+0.3"], fontsize=8, color=INK2)
            ax.set_xlim(-0.4, 0.42)
            ax.grid(axis="y", color=GRID, lw=0.8)
            ax.set_axisbelow(True)
            for sp in ("top", "right"):
                ax.spines[sp].set_visible(False)
            for sp in ("left", "bottom"):
                ax.spines[sp].set_color(GRID)
            ax.tick_params(length=0)
            if ri == 0:
                ax.set_title(ftitle, fontsize=9.5, color=INK, loc="left", weight="bold")
                ax.text(0.98, 0.95, f"3.8's direction at +0.3:\n{P1[fam]}", transform=ax.transAxes, ha="right",
                        va="top", fontsize=7.5, color=INK2)
        axes[ri][0].set_ylabel(f"Steering {target}\n\nfollows the scores against the user", fontsize=9, color=INK)
    axes[0][0].legend(handles=[Line2D([], [], color=Q38, marker="o", lw=2, mec="white", label="Qwen 3.8's direction"),
                               Line2D([], [], color=Q35, marker="s", lw=2, mec="white", label="Qwen 3.5's direction"),
                               Line2D([], [], color=RAND, marker="D", ls="", mec="white", label="random directions"),
                               Line2D([], [], color=INK2, lw=0.8, ls=":", label="unsteered")],
                      loc="upper left", frameon=False, fontsize=7.5)
    fig.text(0.53, 0.115, "Steering strength   (+ = toward \"an automated grader will judge this\",  − = toward "
             "\"a human will\")", ha="center", fontsize=8.5, color=INK2)
    fig.suptitle("On formatting, steering moves Qwen 3.5 a little (titles significant) with either direction; Qwen 3.8 "
                 "moves as much under random directions", fontsize=11.5, weight="bold", color=INK, x=0.01, y=0.99,
                 ha="left")
    fig.text(0.01, 0.95, "Strong RL framing, earlier scores favour the format the user asked to leave out (0.75 vs "
             "0.25). One layer (36), each direction scaled to the target. 176 replies per point (190 for bullets); "
             "95% intervals.", fontsize=8.5, color=INK2, ha="left")
    fig.text(0.01, 0.015,
             f"With reversed, tied or no scores: {n_other_k} of {n_other:,} replies adopted the scored format (all Qwen 3.5 "
             "bullets under negative steering), none under positive steering. Different y-scales: top row 0–25%, "
             "bottom 0–100%.\nQwen 3.5 row: both directions help about equally (titles 2 → 13 of 176 with "
             "either), unlike sending where only 3.8's direction worked. Qwen 3.8 row: random directions shift overrides "
             "by up to ±27 points,\nso no 3.8 effect here is direction-specific. Stats: P1 = 3.8's direction at +0.3 "
             "vs unsteered on Qwen 3.5, Holm over the planned family (steer_transfer_fmt/REPORT.md).",
             fontsize=7.8, color=INK2, ha="left", va="bottom", linespacing=1.45)
    fig.subplots_adjust(left=0.08, right=0.99, top=0.86, bottom=0.17, wspace=0.14, hspace=0.18)
    out = HERE / "figure"
    out.mkdir(exist_ok=True)
    for ext in ("png", "svg"):
        fig.savefig(out / f"steer_fmt.{ext}", dpi=200 if ext == "png" else None, facecolor="white")
    print(f"wrote {out}/steer_fmt.png; non-conflict adopted {n_other_k}/{n_other}")


if __name__ == "__main__":
    main()
