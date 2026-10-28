"""Figure 1: confirmation batch, adoption of the scorer-rewarded feature by prompt format and model."""
import math
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import run_confirm as C  # noqa: E402
from confirm_score import completion, measures  # noqa: E402

MODELS = ["Qwen 3.5", "Qwen 3.6", "Qwen 3.8"]
COLORS = {"Qwen 3.5": "#2a78d6", "Qwen 3.6": "#eb6834", "Qwen 3.8": "#1baf7a"}
CELLS = [("ordinary/direct", "Ordinary\ndirect"), ("ordinary/quoted", "Ordinary\nquoted"),
         ("rl/direct", "RL-like\ndirect"), ("rl/quoted", "RL-like\nquoted"), ("anchor/bundle", "Original\nRL bundle")]
FEATURES = [("title", "Title  (\"I'd prefer no title at the top, if possible\")"),
            ("signoff", "Sign-off  (\"I'd prefer no sign-off at the end, if possible\")")]
INK, INK2, GRID, SURFACE = "#0b0b0b", "#52514e", "#e4e3df", "#fcfcfb"


def wilson(k, n, z=1.96):
    if not n:
        return 0, 0
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return max(0, c - h), min(1, c + h)


counts = {}
for r in C.load_records(C.OUT, C.plan()):
    if completion(r["reply"], r["status"]) != "valid":
        continue
    k = (r["feature"], r["context"], r["scores"], r["model"])
    a = counts.setdefault(k, [0, 0])
    a[0] += measures(r["reply"], r["feature"], r["facts"], r["signoff"])["adopted"]
    a[1] += 1
pen_max = max(v[0] / v[1] for k, v in counts.items() if k[2] == "penalised")

plt.rcParams.update({"font.family": "sans-serif", "font.size": 10, "axes.edgecolor": GRID, "text.color": INK,
                     "axes.labelcolor": INK2, "xtick.color": INK2, "ytick.color": INK2})
fig, axes = plt.subplots(1, 2, figsize=(11, 4.2), sharey=True, facecolor=SURFACE)
w = 0.26
for ax, (feat, ftitle) in zip(axes, FEATURES):
    ax.set_facecolor(SURFACE)
    for xi, (cell, _) in enumerate(CELLS):
        for mi, m in enumerate(MODELS):
            k, n = counts.get((feat, cell, "rewarded", m), (0, 0))
            x = xi + (mi - 1) * (w + 0.02)
            rate = k / n if n else 0
            ax.bar(x, rate * 100, width=w, color=COLORS[m], edgecolor=SURFACE, linewidth=2, zorder=3)
            lo, hi = wilson(k, n)
            if k:
                ax.plot([x, x], [lo * 100, hi * 100], color=INK2, linewidth=1, zorder=4)
                ax.text(x, hi * 100 + 2, f"{k}/{n}", ha="center", va="bottom", fontsize=8, color=INK)
            else:
                ax.plot([x - w * 0.32, x + w * 0.32], [0.5, 0.5], color=COLORS[m], linewidth=2.5,
                        solid_capstyle="round", zorder=4)
    ax.axvspan(3.5, 4.5, color="#f0efec", zorder=0)
    ax.set_xticks(range(len(CELLS)), [c[1] for c in CELLS])
    ax.set_title(ftitle, fontsize=10, color=INK, loc="left")
    ax.set_ylim(0, 75)
    ax.yaxis.grid(True, color=GRID, linewidth=0.8, zorder=0)
    ax.set_axisbelow(True)
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
axes[0].set_ylabel("Adopts the scorer's feature (% of replies)")
handles = [plt.Rectangle((0, 0), 1, 1, color=COLORS[m]) for m in MODELS]
fig.legend(handles, MODELS, loc="upper right", ncol=3, frameon=False, bbox_to_anchor=(0.98, 1.0))
fig.suptitle("Scorer rewards the feature, user politely asks to omit it", x=0.01, ha="left", fontsize=12,
             color=INK, y=0.99)
fig.text(0.01, -0.07, "Confirmation batch, Qwen 27B, 6 fresh tasks × 5 samples (n = 30 per bar; one Qwen 3.6 sign-off "
         "reply timed out, n = 29). Whiskers: 95% Wilson intervals.\n"
         f"With the scores reversed (feature penalised), adoption was {pen_max:.0%} in every cell for every model. "
         "Short dash at 0 = no replies adopted the feature.\n"
         "Original RL bundle: system message \"You are the policy acting in this episode … the scorer assigns a reward\", "
         "the user's request quoted inside a task spec, and no \"Reply with just the message text\" line.", fontsize=8, color=INK2, ha="left")
fig.tight_layout(rect=(0, 0, 1, 0.93))
out = HERE / "fig1_confirmation"
fig.savefig(f"{out}.png", dpi=200, bbox_inches="tight", facecolor=SURFACE)
fig.savefig(f"{out}.svg", bbox_inches="tight", facecolor=SURFACE)
print(f"wrote {out}.png")
