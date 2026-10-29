"""Figures from <root>/<stage>/results.json (matplotlib; no API calls).

  python pa_figures.py [--stage main] [--root DIR]  -> figure/part1_cells.{png,svg}, figure/part2_components.{png,svg}

Fig 1: Part 1 cell rates (Qwen 3.8 bars with Wilson 95% CIs; Qwen 3.5 as hollow markers), one panel per task, groups =
materials x presentation, tied vs +0.50 side by side.
Fig 2: Part 2 component effects (Qwen 3.8): removal (REM:k) and addition (ADD:k) estimates with block-bootstrap 95%
CIs, per task (dots) and pooled over the primary tasks (black diamonds, Holm-significant filled).
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

from pa_common import HERE, PRIMARY_MODEL, RUN, TASKS
from pa_render import COMPONENTS, NAMES

TASK_COLOR = {"send": "#2a78d6", "titles": "#eb6834", "bullets": "#1baf7a"}  # categorical slots 1-3, fixed order
TIED_COLOR = "#b5b4ad"
INK, MUTED = "#2b2b29", "#6b6a64"
TITLES = {"send": "Sending (send vs save draft)", "titles": "Titles / sign-offs", "bullets": "Bullets"}


def _style(ax):
    ax.spines[["top", "right"]].set_visible(False)
    ax.spines[["left", "bottom"]].set_color(MUTED)
    ax.tick_params(colors=MUTED, labelsize=8)
    ax.grid(axis="y", color="#e6e5e0", lw=0.6)
    ax.set_axisbelow(True)


def fig_part1(res: dict, out: Path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    cells = {(c["task"], c["materials"], c["arm"], c["score"], c["model"]): c for c in res["cells"]}
    tasks = [t for t in TASKS if any(k[0] == t for k in cells)]
    fig, axes = plt.subplots(1, len(tasks), figsize=(3.6 * len(tasks), 3.6), sharey=True, squeeze=False)
    groups = [("orig", "B"), ("orig", "N"), ("fresh", "B"), ("fresh", "N")]
    for ax, t in zip(axes[0], tasks):
        for gi, (mat, arm) in enumerate(groups):
            for si, sc in enumerate(("tied", "p050")):
                x = gi + (si - 0.5) * 0.36
                c = cells.get((t, mat, arm, sc, PRIMARY_MODEL))
                if c and c["n"]:
                    col = TASK_COLOR[t] if sc == "p050" else TIED_COLOR
                    ax.bar(x, c["rate"], 0.32, color=col, edgecolor="white", linewidth=1)
                    ax.errorbar(x, c["rate"], yerr=[[c["rate"] - c["lo"]], [c["hi"] - c["rate"]]], color=INK,
                                lw=0.9, capsize=2)
                    ax.text(x, min(1.04, c["hi"] + 0.02), f"{c['k']}/{c['n']}", ha="center", fontsize=6.5,
                            color=MUTED)
                c5 = cells.get((t, mat, arm, sc, "Qwen 3.5"))
                if c5 and c5["n"]:
                    ax.plot(x, c5["rate"], "o", mfc="white", mec=INK, ms=5, zorder=5)
        ax.set_xticks(range(4), [f"{'original' if m == 'orig' else 'fresh'}\n{'bundle' if a == 'B' else 'new'}"
                                 for m, a in groups], fontsize=8)
        ax.axvline(1.5, color="#d6d5cf", lw=0.8)
        ax.set_ylim(0, 1.1)
        ax.set_title(TITLES[t], fontsize=9, color=INK)
        _style(ax)
    axes[0][0].set_ylabel("P(user-conflicting behaviour)", fontsize=8, color=INK)
    from matplotlib.patches import Patch
    from matplotlib.lines import Line2D
    axes[0][-1].legend(handles=[Patch(color=TIED_COLOR, label="tied (0.500/0.500)"),
                                Patch(color=MUTED, label="+0.50 (0.750/0.250), task colour"),
                                Line2D([], [], marker="o", ls="", mfc="white", mec=INK, label="Qwen 3.5")],
                       fontsize=7, frameon=False, loc="upper right")
    fig.text(0.5, -0.03, f"Bars: {PRIMARY_MODEL}, Wilson 95% CIs; labels k/n valid. bundle = old RL bundle "
             "(byte-identical); new = 10A's tool-record presentation.", ha="center", fontsize=7, color=MUTED)
    fig.tight_layout()
    for ext in ("png", "svg"):
        fig.savefig(out / f"part1_cells.{ext}", dpi=170, bbox_inches="tight")
    plt.close(fig)


def fig_part2(res: dict, out: Path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    pooled = res["primary"]["part2"]
    per = res["secondary"][PRIMARY_MODEL]
    fig, axes = plt.subplots(1, 2, figsize=(9, 4.2), sharey=True)
    for ax, kind in zip(axes, ("REM", "ADD")):
        for i, k in enumerate(COMPONENTS):
            y = len(COMPONENTS) - 1 - i
            name = f"{kind}:{k}"
            if name not in pooled:
                ax.text(0, y, "n/a (endpoint)", fontsize=7, color=MUTED, va="center", ha="center")
                continue
            for j, t in enumerate(t for t in TASKS if t in per):
                r = per[t].get(f"{name} (task)")
                if r and not math.isnan(r["estimate"]):
                    yy = y + 0.22 - 0.15 * j
                    ax.plot([r["ci95"][0], r["ci95"][1]], [yy, yy], color=TASK_COLOR[t], lw=1.2)
                    ax.plot(r["estimate"], yy, "o", color=TASK_COLOR[t], ms=4,
                            label=TITLES[t] if (i == 0 and kind == "REM") else None)
            r = pooled[name]
            if not math.isnan(r["estimate"]):
                yy = y - 0.28
                ax.plot([r["ci95"][0], r["ci95"][1]], [yy, yy], color=INK, lw=1.6)
                ax.plot(r["estimate"], yy, "D", color=INK, mfc=INK if r["p_holm"] < 0.05 else "white", ms=6,
                        label="pooled (send + titles); filled = Holm p<0.05" if (i == 0 and kind == "REM") else None)
        ax.axvline(0, color=MUTED, lw=0.8)
        ax.set_yticks(range(len(COMPONENTS)), [f"({k}) {NAMES[k]}" for k in COMPONENTS][::-1], fontsize=7.5)
        ax.set_title("Removal from the bundle: D(B) − D(B−k)" if kind == "REM" else
                     "Addition to the new presentation: D(N+k) − D(N)", fontsize=9, color=INK)
        ax.set_xlabel("change in the +0.50 − tied score effect", fontsize=8, color=INK)
        _style(ax)
        ax.grid(axis="x", color="#e6e5e0", lw=0.6)
    fig.tight_layout()
    h, lab = axes[0].get_legend_handles_labels()
    fig.legend(h, lab, fontsize=7, frameon=False, loc="upper center", ncol=4, bbox_to_anchor=(0.5, 0.0))
    for ext in ("png", "svg"):
        fig.savefig(out / f"part2_components.{ext}", dpi=170, bbox_inches="tight")
    plt.close(fig)


def main():
    sys.path.insert(0, str(HERE))
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", default="main")
    ap.add_argument("--root", default=str(RUN))
    ap.add_argument("--out", default=str(HERE / "figure"))
    a = ap.parse_args()
    res = json.loads((Path(a.root) / a.stage / "results.json").read_text())
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    fig_part1(res, out)
    fig_part2(res, out)
    print(f"wrote {out}/part1_cells.* and part2_components.*")


if __name__ == "__main__":
    main()
