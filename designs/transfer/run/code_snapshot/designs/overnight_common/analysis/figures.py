"""Figures from results.json only (never from raw generations).

    figures.py A|B [--results PATH] [--out DIR]

A -> fig1_score_response.{png,pdf,svg}   family-level violation rate vs displayed gap, Qwen 3.8 and Qwen 3.5,
                                          episode (solid, top row) and ordinary (dashed, bottom row); the no-history
                                          point sits apart at the left, not on the tie.
     fig2_subtype_effects.{png,pdf,svg}   per-subtype effect rate(+0.50) - rate(+0.05), model x frame, 95% CIs.
B -> fig3_transfer.{png,pdf,svg}          change rate(+0.50) - rate(0) by direction x permission x frame, SOURCE and
                                          TARGET outcomes in separate columns, one row per model.
Intervals are the block-level ones from results.json (cluster bootstrap / Wilson per block). A cell with 0 events is
drawn as an open marker at 0 with a dotted whisker up to its one-sided 95% upper bound; a zero-variation contrast
interval (marked † in the tables) is drawn dotted.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import stats as ST  # noqa: E402

ROOT = HERE.parents[2]
EXPS = {"A": ROOT / "designs" / "grouped_replication", "B": ROOT / "designs" / "transfer"}
COLOR = {"Qwen 3.5": "#2a78d6", "Qwen 3.8": "#eb6834"}
SURFACE, INK, MUTED, GRID = "#fcfcfb", "#1f2328", "#5f6670", "#e4e6e9"
NONE_X = -0.80
GAP_TICKS = [(-0.5, "−0.50"), (0.0, "0"), (0.05, "+0.05"), (0.5, "+0.50")]
FAMILY_TITLE = {"formatting": "Formatting", "reserved_actions": "Reserved actions",
                "factual_reporting": "Factual reporting"}

plt.rcParams.update({
    "figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE,
    "axes.edgecolor": MUTED, "axes.labelcolor": INK, "xtick.color": MUTED, "ytick.color": MUTED, "text.color": INK,
    "font.size": 10, "axes.titlesize": 11, "axes.titleweight": "bold", "axes.spines.top": False,
    "axes.spines.right": False, "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.8, "legend.frameon": False,
    "svg.fonttype": "none", "pdf.fonttype": 42,
})


def save(fig, out: Path, name: str) -> list[Path]:
    out.mkdir(parents=True, exist_ok=True)
    paths = []
    for ext in ("png", "pdf", "svg"):
        p = out / f"{name}.{ext}"
        fig.savefig(p, dpi=200 if ext == "png" else None, bbox_inches="tight")
        paths.append(p)
    plt.close(fig)
    return paths


def _point(ax, x, c, color, filled=True, ls="-"):
    """One rate with its interval; zero cells get an open marker and a dotted upper-bound whisker."""
    if c is None or c.get("rate") is None:
        return
    if c["k"] == 0:
        ax.plot([x, x], [0, c["hi"]], color=color, lw=1.4, ls=":", zorder=2)
        ax.plot([x - 0.012, x + 0.012], [c["hi"], c["hi"]], color=color, lw=1.4, zorder=2)
        ax.plot(x, 0, "o", ms=7, mfc=SURFACE, mec=color, mew=1.8, zorder=3)
        return
    ax.plot([x, x], [c["lo"], c["hi"]], color=color, lw=1.4, ls=ls if ls != "-" else "-", zorder=2)
    ax.plot(x, c["rate"], "o", ms=7, mfc=color if filled else SURFACE, mec=SURFACE if filled else color,
            mew=1.5 if filled else 1.8, zorder=3)


def fig_score_response(res: dict, out: Path) -> list[Path]:
    cells = {(c["group"], c["model"], c["frame"], c["cond"]): c for c in res["cells"] if c["level"] == "family"}
    fams = [f for f in ST.FAMILIES if any(k[0] == f for k in cells)]
    fig, axes = plt.subplots(2, len(fams), figsize=(4.3 * len(fams), 7.2), sharey=True, squeeze=False)
    dodge = {"Qwen 3.8": 0.012, "Qwen 3.5": -0.012}
    for col, fam in enumerate(fams):
        for row, frame in enumerate(ST.FRAMES):
            ax = axes[row][col]
            ls = "-" if frame == "episode" else "--"
            for model in (ST.COMPARE, ST.FOCUS):
                color = COLOR[model]
                xs, ys = [], []
                for cond in ("-0.50", "+0.00", "+0.05", "+0.50"):
                    c = cells.get((fam, model, frame, cond))
                    if c and c.get("rate") is not None:
                        xs.append(ST.GAP_OF[cond] + dodge[model])
                        ys.append(c["rate"])
                    _point(ax, ST.GAP_OF[cond] + dodge[model], c, color, filled=True)
                ax.plot(xs, ys, color=color, lw=2, ls=ls, zorder=1)
                _point(ax, NONE_X + dodge[model] * 2, cells.get((fam, model, frame, "none")), color, filled=True)
            ax.axvline(-0.66, color=MUTED, lw=0.8, ls=(0, (2, 3)))
            ax.set_xlim(-0.95, 0.6)
            ax.set_ylim(-0.03, 1.03)
            ax.set_xticks([NONE_X] + [t for t, _ in GAP_TICKS])
            ax.set_xticklabels(["no\nhistory"] + [lab for _, lab in GAP_TICKS])
            for t in ax.get_xticklabels():
                if t.get_text() == "0":
                    t.set_ha("right")
                elif t.get_text() == "+0.05":
                    t.set_ha("left")
            ax.grid(axis="x", visible=False)
            if row == 0:
                ax.set_title(FAMILY_TITLE.get(fam, fam))
            if col == 0:
                ax.set_ylabel(f"{frame.capitalize()} frame\nviolation rate")
            if row == 1:
                ax.set_xlabel("Displayed score gap (conflicting − compliant)")
    handles = [Line2D([], [], color=COLOR[ST.FOCUS], lw=2, marker="o", label="Qwen 3.8"),
               Line2D([], [], color=COLOR[ST.COMPARE], lw=2, marker="o", label="Qwen 3.5"),
               Line2D([], [], color=MUTED, lw=2, ls="-", label="episode frame (top row)"),
               Line2D([], [], color=MUTED, lw=2, ls="--", label="ordinary frame (bottom row)"),
               Line2D([], [], color=MUTED, lw=1.4, ls=":", marker="o", mfc=SURFACE, label="0 events: one-sided 95% "
                      "upper bound (block level)")]
    fig.legend(handles=handles, loc="lower center", ncol=3, bbox_to_anchor=(0.5, -0.06))
    fig.suptitle("Violation rate by displayed score gap (family = equal-weighted mean of subtypes; 95% block-level "
                 "intervals)", fontsize=11, y=1.0)
    fig.tight_layout()
    return save(fig, out, "fig1_score_response")


def _ci_line(ax, y, c, color, ls, filled, xkey="estimate"):
    if c is None or c.get("estimate") is None:
        return
    lo, hi = c["ci"]
    ax.plot([lo, hi], [y, y], color=color, lw=1.6, ls=":" if c.get("degenerate") else ls, zorder=2)
    ax.plot(c[xkey], y, "o", ms=8 if filled else 7, mfc=color if filled else SURFACE,
            mec=SURFACE if filled else color, mew=1.0 if filled else 1.8, zorder=3)


def fig_subtype_effects(res: dict, out: Path) -> list[Path]:
    cs = {(c["group"], c["model"], c["frame"]): c for c in res["contrasts"] if c["kind"] == "subtype_gap_effect"}
    order = [(f, s) for f, subs in ST.FAMILIES.items() for s in subs if any(k[0] == s for k in cs)]
    combos = [(ST.FOCUS, "episode"), (ST.FOCUS, "ordinary"), (ST.COMPARE, "episode"), (ST.COMPARE, "ordinary")]
    off = {cb: 0.3 - 0.2 * i for i, cb in enumerate(combos)}
    fig, ax = plt.subplots(figsize=(7.5, 0.62 * len(order) + 1.8))
    ylabels, yt = [], []
    y = 0
    prev_fam = None
    for fam, s in order:
        if prev_fam and fam != prev_fam:
            ax.axhline(y + 0.75, color=GRID, lw=1.2)
            y -= 0.5
        prev_fam = fam
        for model, frame in combos:
            _ci_line(ax, y + off[(model, frame)], cs.get((s, model, frame)), COLOR[model],
                     "-" if frame == "episode" else "--", frame == "episode")
        ylabels.append(f"{s}  ({FAMILY_TITLE[fam].lower()})")
        yt.append(y)
        y -= 1.2
    ax.axvline(0, color=MUTED, lw=1)
    ax.set_yticks(yt)
    ax.set_yticklabels(ylabels)
    ax.set_xlim(-1.05, 1.05)
    ax.grid(axis="y", visible=False)
    ax.set_xlabel("Effect of a larger displayed advantage: rate(+0.50) − rate(+0.05), 95% CI")
    handles = [Line2D([], [], color=COLOR[ST.FOCUS], lw=2, marker="o", label="Qwen 3.8"),
               Line2D([], [], color=COLOR[ST.COMPARE], lw=2, marker="o", label="Qwen 3.5"),
               Line2D([], [], color=MUTED, lw=1.6, marker="o", label="episode (filled, solid)"),
               Line2D([], [], color=MUTED, lw=1.6, ls="--", marker="o", mfc=SURFACE, label="ordinary (open, dashed)"),
               Line2D([], [], color=MUTED, lw=1.6, ls=":", label="no variation: block-level bound")]
    ax.legend(handles=handles, loc="upper center", bbox_to_anchor=(0.5, -0.09), ncol=3)
    ax.set_title("Subtype-level effects (one generation per block per cell)")
    fig.tight_layout()
    return save(fig, out, "fig2_subtype_effects")


def fig_transfer(res: dict, out: Path) -> list[Path]:
    cs = {}
    for c in res["contrasts"]:
        if c["kind"] in ("direction_simple_change", "simple_change"):
            g = "all directions" if c["kind"] == "simple_change" else c["group"]
            cs[(g, c["model"], c["outcome"], c["frame"], c["permission"])] = c
    dirs = ["all directions"] + [d for d in ST.DIRECTIONS if any(k[0] == d for k in cs)]
    combos = [("episode", "forbidden"), ("episode", "permitted"), ("ordinary", "forbidden"), ("ordinary", "permitted")]
    off = {cb: 0.3 - 0.2 * i for i, cb in enumerate(combos)}
    fig, axes = plt.subplots(2, 2, figsize=(11, 0.55 * len(dirs) * 2 + 2.5), sharex=True, sharey=True)
    for r, model in enumerate(ST.MODELS):
        for col, outcome in enumerate(("source", "target")):
            ax = axes[r][col]
            for i, d in enumerate(dirs):
                y = -i * 1.2 - (0.4 if i else 0)
                for frame, perm in combos:
                    c = cs.get((d, model, outcome, frame, perm))
                    if c is None or c.get("estimate") is None:
                        continue
                    yy = y + off[(frame, perm)]
                    lo, hi = c["ci"]
                    ax.plot([lo, hi], [yy, yy], color=COLOR[model], lw=1.6,
                            ls=":" if c.get("degenerate") else ("-" if frame == "episode" else "--"))
                    ax.plot(c["estimate"], yy, "o" if perm == "forbidden" else "D", ms=8 if perm == "forbidden" else 7,
                            mfc=COLOR[model] if frame == "episode" else SURFACE,
                            mec=SURFACE if frame == "episode" else COLOR[model], mew=1.0 if frame == "episode" else 1.8)
            ax.axvline(0, color=MUTED, lw=1)
            ax.axhline(-0.8, color=GRID, lw=1.2)
            ax.set_yticks([-i * 1.2 - (0.4 if i else 0) for i in range(len(dirs))])
            ax.set_yticklabels([d.replace("_to_", " → ") for d in dirs])
            ax.grid(axis="y", visible=False)
            ax.set_xlim(-1.05, 1.05)
            ax.set_title(f"{model}: {outcome.upper()} outcome")
            if r == 1:
                ax.set_xlabel("rate(+0.50) − rate(0), 95% CI")
    handles = [Line2D([], [], color=COLOR[ST.FOCUS], lw=2, label="Qwen 3.8"),
               Line2D([], [], color=COLOR[ST.COMPARE], lw=2, label="Qwen 3.5"),
               Line2D([], [], color=MUTED, ls="", marker="o", ms=7, label="earlier users forbade the source"),
               Line2D([], [], color=MUTED, ls="", marker="D", ms=6, label="earlier users permitted the source"),
               Line2D([], [], color=MUTED, lw=1.6, label="episode frame (filled, solid)"),
               Line2D([], [], color=MUTED, lw=1.6, ls="--", marker="o", mfc=SURFACE, mec=MUTED,
                      label="ordinary frame (open, dashed)")]
    fig.legend(handles=handles, loc="lower center", ncol=3, bbox_to_anchor=(0.5, -0.05))
    fig.suptitle("Transfer: change when the history shows the source violation scored +0.50 vs tied "
                 "(SOURCE = the scored behaviour; TARGET = a different, never-shown behaviour)", fontsize=11)
    fig.tight_layout()
    return save(fig, out, "fig3_transfer")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("exp", choices=["A", "B"])
    ap.add_argument("--results", type=Path, default=None)
    ap.add_argument("--out", type=Path, default=None)
    a = ap.parse_args(argv)
    res = json.loads((a.results or EXPS[a.exp] / "run" / "results.json").read_text())
    out = a.out or EXPS[a.exp] / "figures"
    paths = (fig_score_response(res, out) + fig_subtype_effects(res, out) if a.exp == "A"
             else fig_transfer(res, out))
    for p in paths:
        print(p)


if __name__ == "__main__":
    main()
