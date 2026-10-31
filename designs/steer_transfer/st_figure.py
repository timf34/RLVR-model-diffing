"""Deck figure for the steering-transfer main stage (matplotlib; reads run/main/scored.jsonl, no API calls).

  python st_figure.py  -> figure/steer_transfer.{png,svg}

Left: Qwen 3.5's send rate under conflicting scores vs steering strength, for 3.8's transferred direction, 3.5's own
direction and two norm-matched random directions. Right: Qwen 3.8 with its own direction (source-model control).
Rates count executed sends from the tool log (as st_analysis.py does); 95% intervals are a block bootstrap over the
44 scenario blocks. Model colours match the other deck figures (Qwen 3.5 blue, Qwen 3.8 orange).
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


def load():
    rows = [json.loads(line) for line in (HERE / "run/main/scored.jsonl").open()]
    by = defaultdict(lambda: defaultdict(list))   # (model, cond, score) -> block -> [sent]
    for r in rows:
        if r.get("completion") == "missing":   # 3 Qwen 3.5 items never generated (ERRATA.md)
            continue
        by[(r["model"], r["cond"], r["score"])][r["block"]].append(bool(r["sent"]))
    return by


def rate_ci(blocks: dict, draws: int = 4000, seed: int = 0):
    keys = sorted(blocks)
    flat = [s for k in keys for s in blocks[k]]
    est = sum(flat) / len(flat)
    rng = random.Random(seed)
    boots = []
    for _ in range(draws):
        pick = [s for k in rng.choices(keys, k=len(keys)) for s in blocks[k]]
        boots.append(sum(pick) / len(pick))
    boots.sort()
    return est, boots[int(0.025 * draws)], boots[int(0.975 * draws) - 1], len(flat)


def cond_name(kind: str, s: float) -> str:
    return "none" if s == 0 else f"{kind}_{s:+.1f}"


def main() -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D

    by = load()

    def series(model, kind, strengths):
        out = []
        for s in strengths:
            cell = by.get((model, cond_name(kind, s), "conflict"))
            if cell:
                out.append((s, *rate_ci(cell, seed=hash((model, kind, s)) % 10**6)))
        return out

    # every non-conflict cell must be 0 sends; the caption states it, so check it
    other = [(k, sum(map(sum, v.values())), sum(map(len, v.values()))) for k, v in by.items() if k[2] != "conflict"]
    assert all(k_sent == 0 for _, k_sent, _ in other), [o for o in other if o[1]]
    n_other_35 = sum(n for k, _, n in other if k[0] == "Qwen 3.5")

    fig, (axl, axr) = plt.subplots(1, 2, figsize=(12.5, 5.6), gridspec_kw=dict(width_ratios=[1.55, 1]), sharey=True)
    offsets = {"xfer": 0.0, "native": -0.012, "random0": 0.012, "random1": 0.024}
    styles = [("xfer", "Qwen 3.8's direction, added to Qwen 3.5", Q38, "o", "-"),
              ("native", "Qwen 3.5's own direction", Q35, "s", "-")]
    for kind, label, col, mk, ls in styles:
        pts = series("Qwen 3.5", kind, STRENGTHS)
        xs = [s + offsets[kind] for s, *_ in pts]
        axl.plot(xs, [e for _, e, *_ in pts], ls, color=col, marker=mk, ms=7, lw=2, mec="white", mew=1.2, zorder=4,
                 label=label)
        for x, (_, e, lo, hi, _) in zip(xs, pts):
            axl.plot([x, x], [lo, hi], color=col, lw=1.2, alpha=0.55, zorder=3)
    for kind in ("random0", "random1"):
        for s, e, lo, hi, _ in series("Qwen 3.5", kind, [-0.3, 0.3]):
            x = s + offsets[kind]
            axl.plot([x, x], [lo, hi], color=RAND, lw=1.2, alpha=0.7, zorder=3)
            axl.plot(x, e, "D", color=RAND, ms=6, mec="white", mew=1.0, zorder=4)
    xf = dict((s, e) for s, e, *_ in series("Qwen 3.5", "xfer", [0.0, 0.3]))
    axl.annotate(f"{100 * xf[0.3]:.0f}%", (0.3, xf[0.3]), xytext=(10, 0), textcoords="offset points", va="center",
                 fontsize=9, color=Q38, weight="bold")
    axl.set_title("Target: Qwen 3.5", fontsize=10.5, color=INK, loc="left", weight="bold")
    axl.legend(handles=[Line2D([], [], color=Q38, marker="o", lw=2, mec="white", label=styles[0][1]),
                        Line2D([], [], color=Q35, marker="s", lw=2, mec="white", label=styles[1][1]),
                        Line2D([], [], color=RAND, marker="D", ls="", mec="white",
                               label="random directions, same size (two seeds)")],
               loc="upper left", frameon=False, fontsize=8.5)

    pts = series("Qwen 3.8", "native", STRENGTHS)
    axr.plot([s for s, *_ in pts], [e for _, e, *_ in pts], "-", color=Q38, marker="o", ms=7, lw=2, mec="white",
             mew=1.2, zorder=4)
    for s, e, lo, hi, _ in pts:
        axr.plot([s, s], [lo, hi], color=Q38, lw=1.2, alpha=0.55, zorder=3)
        axr.annotate(f"{100 * e:.0f}%", (s, e), xytext=(0, 9), textcoords="offset points", ha="center", fontsize=8.5,
                     color=INK2)
    axr.set_title("Reference: Qwen 3.8 with its own direction", fontsize=10.5, color=INK, loc="left", weight="bold")

    for ax in (axl, axr):
        ax.set_xticks(STRENGTHS, ["−0.3", "−0.1", "0\n(unsteered)", "+0.1", "+0.3"], fontsize=8.5, color=INK2)
        ax.set_xlim(-0.36, 0.38)
        ax.set_ylim(0, 1)
        ax.set_yticks([0, 0.25, 0.5, 0.75, 1.0], ["0%", "25%", "50%", "75%", "100%"], fontsize=8.5, color=INK2)
        ax.grid(axis="y", color=GRID, lw=0.8)
        ax.set_axisbelow(True)
        for sp in ("top", "right"):
            ax.spines[sp].set_visible(False)
        for sp in ("left", "bottom"):
            ax.spines[sp].set_color(GRID)
        ax.tick_params(length=0)
    fig.text(0.53, 0.155, "Steering strength   (+ = toward \"an automated grader will judge this\",  − = toward \"a human will\")",
             ha="center", fontsize=8.5, color=INK2)
    axl.set_ylabel("Sends the email the user said to keep as a draft", fontsize=9, color=INK)

    fig.suptitle("Adding Qwen 3.8's \"automated grader vs human\" direction to Qwen 3.5 makes 3.5 follow the scores "
                 "against the user", fontsize=11.5, weight="bold", color=INK, x=0.01, y=0.985, ha="left")
    fig.text(0.01, 0.925, "Sending task, strong RL framing, earlier scores favour sending (0.75 vs 0.25). "
             "One layer (36), 44 scenarios × 4 samples = 176 episodes per point; lines are 95% intervals over scenarios.",
             fontsize=8.5, color=INK2, ha="left")
    fig.text(0.01, 0.02, f"With reversed, tied or no scores, no condition sent at all (0 of {n_other_35:,} Qwen 3.5 episodes), "
             "so steering does not simply make the model send more.\nThe direction is Qwen 3.8's layer-36 activation "
             "difference between prompts where an automated grader vs a human judges the work (earlier grader-shift "
             "study),\nadded to Qwen 3.5 in raw coordinates. One task, one layer, fixed strengths; exploratory beyond the "
             "two preregistered contrasts.", fontsize=8, color=INK2, ha="left", va="bottom", linespacing=1.45)
    fig.subplots_adjust(left=0.07, right=0.99, top=0.84, bottom=0.25, wspace=0.08)
    out = HERE / "figure"
    out.mkdir(exist_ok=True)
    for ext in ("png", "svg"):
        fig.savefig(out / f"steer_transfer.{ext}", dpi=200 if ext == "png" else None, facecolor="white")
    print(f"wrote {out}/steer_transfer.png")


if __name__ == "__main__":
    main()
