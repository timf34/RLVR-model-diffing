"""Post-freeze presentation fix only: redraws figure/records_vs_prose.png from run/results.json with the x-axis
label shortened (the frozen run_records.figure printed overlapping labels). Same data, encodings and colours.
Run: ~/.claude/bin/memguard -m 4 -- .venv/bin/python designs/rec_mechanisms/records/make_figure.py
"""
import itertools
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

HERE = Path(__file__).parent
GAPS = ("−0.50", "0", "+0.05", "+0.50")
MODELS, FORMATS, FRAMINGS = ("Qwen 3.5", "Qwen 3.8"), ("prose", "records"), ("chat", "episode", "bundle")
COLORS = {"Qwen 3.5": "#2a78d6", "Qwen 3.8": "#eb6834"}
res = json.loads((HERE / "run" / "results.json").read_text())
ink, muted, grid, bg = "#0b0b0b", "#52514e", "#e6e5e1", "#fcfcfb"
fig, axes = plt.subplots(1, 3, figsize=(13, 4.8), sharey=True, facecolor=bg)
xs, base_x = list(range(4)), -1.2
titles = {"chat": "Chat", "episode": "Episode / reward wording", "bundle": "Training-style bundle"}
for ax, f in zip(axes, FRAMINGS):
    ax.set_facecolor(bg)
    for i, (m, fm) in enumerate(itertools.product(MODELS, FORMATS)):
        c = res["cells"][f"{m}|{f}|{fm}"]
        off = (i - 1.5) * 0.07
        yerr = [[r - lo for r, lo in zip(c["rate"], c["lo"])], [hi - r for r, hi in zip(c["rate"], c["hi"])]]
        ax.errorbar([x + off for x in xs], c["rate"], yerr=yerr, color=COLORS[m], marker="o" if fm == "prose" else "s",
                    markersize=5.5, lw=2, ls="-" if fm == "prose" else "--", capsize=0, elinewidth=1.1,
                    label=f"{m}, {fm}", markeredgecolor=COLORS[m] if fm == "records" else bg, markeredgewidth=1.3,
                    markerfacecolor=COLORS[m] if fm == "prose" else bg)
    for j, m in enumerate(MODELS):
        b = res["baseline"][f"{m}|{f}"]
        ax.plot([base_x + (j - 0.5) * 0.12], [b["k"] / b["n"]], marker="D", color=COLORS[m], markersize=5.5,
                markerfacecolor=bg, markeredgewidth=1.5, ls="none")
    ax.axvline(1, color=grid, lw=1, zorder=0)
    ax.axvline(-0.6, color=grid, lw=1, ls=":", zorder=0)
    ax.set_xticks([base_x] + xs, ["no\nhistory"] + list(GAPS), fontsize=8, color=muted)
    ax.set_xlim(base_x - 0.5, 3.5)
    ax.set_ylim(-0.03, 1.05)
    ax.grid(axis="y", color=grid, lw=0.8)
    ax.set_axisbelow(True)
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    for sp in ("left", "bottom"):
        ax.spines[sp].set_color(grid)
    ax.tick_params(colors=muted)
    ax.set_title(titles[f], fontsize=10, color=ink, loc="left")
axes[1].set_xlabel("Score advantage for the upsell example (levels evenly spaced, not to scale)", fontsize=9,
                   color=muted)
axes[0].set_ylabel("P(recommends the upsell)", color=ink)
from matplotlib.lines import Line2D  # noqa: E402
handles = [Line2D([], [], color=COLORS[m], lw=2, ls="-" if fm == "prose" else "--", marker="o" if fm == "prose" else "s",
                  markerfacecolor=COLORS[m] if fm == "prose" else bg, markeredgecolor=COLORS[m], label=f"{m}, {fm}")
           for m, fm in itertools.product(MODELS, FORMATS)]
axes[0].legend(handles=handles, frameon=False, fontsize=8, loc="upper left", handlelength=3)
fig.suptitle("Upsell rate with the scored history shown as prose answers (solid) or structured records (dashed).\n"
             "EXPLORATORY; n = 36 per point (12 scenarios × 3); bars = scenario-cluster 95% CI; hollow diamond = no history",
             fontsize=9, color=muted, x=0.01, ha="left")
fig.tight_layout(rect=(0, 0, 1, 0.93))
fig.savefig(HERE / "figure" / "records_vs_prose.png", dpi=160, facecolor=fig.get_facecolor())
print("Wrote figure/records_vs_prose.png")
