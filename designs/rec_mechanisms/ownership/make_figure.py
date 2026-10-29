"""Presentation-only copy of run_own.figure with a corrected legend (errorbar legend handles drew every line
dashed). Not part of the frozen, hashed analysis: it only reads run/results.json and rewrites the same figure path.
Run: .venv/bin/python designs/rec_mechanisms/ownership/make_figure.py
"""
import itertools
import json
import sys
from pathlib import Path

HERE = Path(__file__).parent
sys.argv = ["make_figure"]
sys.path.insert(0, str(HERE))
import run_own as RO  # noqa: E402
from run_own import MODELS, O, GM, OUT  # noqa: E402,F401

COLORS = {"team": "#2a78d6", "independent": "#eb6834"}  # validated categorical slots 1-2


def figure(out_dir=OUT):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    res = json.loads((out_dir / "results.json").read_text())
    ink, muted, grid, bg = "#0b0b0b", "#52514e", "#e6e5e1", "#fcfcfb"
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.6), sharey=True, facecolor=bg)
    xs = {g: i for i, g in enumerate(O.GAPS)}
    for ax, m in zip(axes, MODELS):
        ax.set_facecolor(bg)
        for j, (w, o) in enumerate(itertools.product(O.WORDINGS, O.OWNERS)):
            cell = f"{w}/{o}"
            pts = [res["cells"].get(f"{m}|{cell}|{GM.gap_label(g)}") for g in O.GAPS]
            pts = [(xs[v["gap"]] + (j - 1.5) * 0.07, v) for v in pts if v]
            if not pts:
                continue
            ax.errorbar([x for x, _ in pts], [v["rate"] for _, v in pts],
                        yerr=[[v["rate"] - v["ci"][0] for _, v in pts], [v["ci"][1] - v["rate"] for _, v in pts]],
                        color=COLORS[o], ls="-" if w == "chat" else "--", marker="o" if w == "chat" else "s",
                        markersize=6, lw=2, elinewidth=1.1, markeredgecolor=bg, label=f"{w} · {o}")
        ref = [res["cells"].get(f"{m}|{O.REF_CELL}|{GM.gap_label(g)}") for g in O.REF_GAPS]
        ref = [v for v in ref if v]
        if ref:
            ax.errorbar([xs[v["gap"]] + 0.25 for v in ref], [v["rate"] for v in ref],
                        yerr=[[v["rate"] - v["ci"][0] for v in ref], [v["ci"][1] - v["rate"] for v in ref]],
                        color=muted, marker="D", ls="none", markersize=5, elinewidth=1.1,
                        label="episode · original wording (reference)")
        b = res["cells"].get(f"{m}|{O.BASELINE}|none")
        if b:
            ax.plot([-1], [b["rate"]], marker="o", color=ink, markerfacecolor=bg, markersize=6, ls="none",
                    label="no history")
        ax.axvline(-0.5, color=grid, lw=1, ls=":")
        ax.set_xticks([-1] + list(range(len(O.GAPS))), ["no\nhistory"] + [GM.gap_label(g) for g in O.GAPS],
                      fontsize=8, color=muted)
        ax.set_ylim(-0.03, 1.05)
        ax.grid(axis="y", color=grid, lw=0.8)
        ax.set_axisbelow(True)
        for sp in ("top", "right"):
            ax.spines[sp].set_visible(False)
        for sp in ("left", "bottom"):
            ax.spines[sp].set_color(grid)
        ax.tick_params(colors=muted)
        ax.set_title(m, fontsize=11, color=ink, loc="left")
        ax.set_xlabel("Score advantage for the upsell (levels evenly spaced, not to scale)", fontsize=8, color=muted)
    axes[0].set_ylabel("P(recommends the upsell)", color=ink)
    from matplotlib.lines import Line2D
    handles = [Line2D([], [], color="#0b0b0b", marker="o", markerfacecolor="#fcfcfb", ls="none", label="no history")]
    handles += [Line2D([], [], color=COLORS[o], ls="-" if w == "chat" else "--", marker="o" if w == "chat" else "s",
                       lw=2, label=f"{w} · {o}") for w, o in itertools.product(O.WORDINGS, O.OWNERS)]
    handles.append(Line2D([], [], color="#52514e", marker="D", ls="none", label="episode · original wording (reference)"))
    axes[1].legend(handles=handles, frameon=False, fontsize=8, loc="upper left", handlelength=3)
    fig.suptitle("Evaluator ownership × workflow wording (EXPLORATORY; 12 scenarios × 3 replies per point; "
                 "bars = scenario-cluster 95% CI)", fontsize=9, color=muted, x=0.01, ha="left")
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    path = HERE / "figure" / ("ownership_wording.png" if out_dir == OUT else "inspection.png")
    path.parent.mkdir(exist_ok=True)
    fig.savefig(path, dpi=160, facecolor=fig.get_facecolor())
    print(f"Wrote {path}")




if __name__ == "__main__":
    figure(OUT)
