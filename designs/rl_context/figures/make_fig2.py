"""Figure 2: em-dash request ladder in the original RL bundle (discovery run emdash_soft/)."""
import math
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import run_emdash_soft as S  # noqa: E402
import emdash_materials as E  # noqa: E402
from emdash_score import completion, measures  # noqa: E402

MODELS = ["Qwen 3.5", "Qwen 3.6", "Qwen 3.8"]
COLORS = {"Qwen 3.5": "#2a78d6", "Qwen 3.6": "#eb6834", "Qwen 3.8": "#1baf7a"}
MARKERS = {"Qwen 3.5": "o", "Qwen 3.6": "s", "Qwen 3.8": "D"}
LEVELS = [("silent", "Says nothing\nabout dashes"), ("implicit", "Gives a reason\n(plain-text noticeboard)"),
          ("soft_norm", "\"We don't usually\nuse em dashes\""), ("soft_pref", "\"I'd prefer no em\ndashes, if possible\"")]
INK, INK2, GRID, SURFACE = "#0b0b0b", "#52514e", "#e4e3df", "#fcfcfb"


def wilson(k, n, z=1.96):
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return max(0, c - h), min(1, c + h)


items = S.plan()
by_key = {i["key"]: i for i in items}
counts = {}
for r in S.R.load_records(S.OUT, items):
    i = by_key[r["key"]]
    if completion(r["reply"], r["status"]) != "valid":
        continue
    a = counts.setdefault((r["model"], i["context"], i["level"], i["scores"]), [0, 0])
    a[0] += measures(r["reply"], E.FEATURE, i["facts"])["adopted"]
    a[1] += 1
other_req = sum(v[0] for k, v in counts.items() if k[1] != "anchor/bundle" and k[2] != "silent" and k[3] == "rewarded")
other_n = sum(v[1] for k, v in counts.items() if k[1] != "anchor/bundle" and k[2] != "silent" and k[3] == "rewarded")
pen = sum(v[0] for k, v in counts.items() if k[3] == "penalised"), sum(v[1] for k, v in counts.items() if k[3] == "penalised")

plt.rcParams.update({"font.family": "sans-serif", "font.size": 10, "text.color": INK, "axes.labelcolor": INK2,
                     "xtick.color": INK2, "ytick.color": INK2})
fig, ax = plt.subplots(figsize=(8.6, 4.4), facecolor=SURFACE)
ax.set_facecolor(SURFACE)
offsets = {"Qwen 3.5": -0.08, "Qwen 3.6": 0.0, "Qwen 3.8": 0.08}
for m in MODELS:
    xs, ys = [], []
    for xi, (lv, _) in enumerate(LEVELS):
        k, n = counts[(m, "anchor/bundle", lv, "rewarded")]
        x, y = xi + offsets[m], 100 * k / n
        lo, hi = wilson(k, n)
        ax.plot([x, x], [100 * lo, 100 * hi], color=COLORS[m], linewidth=1, alpha=0.6, zorder=2)
        xs.append(x)
        ys.append(y)
    ax.plot(xs, ys, color=COLORS[m], linewidth=2, zorder=3)
    ax.scatter(xs, ys, color=COLORS[m], marker=MARKERS[m], s=46, edgecolor=SURFACE, linewidth=1.5, zorder=4)
    k, n = counts[(m, "anchor/bundle", "soft_pref", "rewarded")]
    ax.text(xs[-1] + 0.12, ys[-1], f"{m}  {k}/{n}", va="center", fontsize=9, color=INK)
ax.set_xticks(range(len(LEVELS)), [l[1] for l in LEVELS])
ax.set_xlim(-0.3, len(LEVELS) - 0.3)
ax.set_ylim(-3, 105)
ax.set_ylabel("Keeps the rewarded em dashes (% of replies)")
ax.yaxis.grid(True, color=GRID, linewidth=0.8)
ax.set_axisbelow(True)
for s in ("top", "right", "left", "bottom"):
    ax.spines[s].set_visible(s == "bottom")
ax.spines["bottom"].set_color(GRID)
ax.set_title("Original RL bundle: scorer rewards em dashes, user objects in different ways", loc="left",
             fontsize=11, color=INK)
fig.text(0.01, -0.06,
         f"Exploratory run, Qwen 27B, 6 tasks × 3 samples (n = 18 per point; whiskers: 95% Wilson intervals). "
         f"Same prompts in the controlled RL and ordinary formats:\nany request gives {other_req}/{other_n} replies "
         f"with em dashes. Scores reversed (em dashes penalised): {pen[0]}/{pen[1]} replies use them.",
         fontsize=8, color=INK2, ha="left")
fig.tight_layout()
out = HERE / "fig2_emdash_ladder"
fig.savefig(f"{out}.png", dpi=200, bbox_inches="tight", facecolor=SURFACE)
fig.savefig(f"{out}.svg", bbox_inches="tight", facecolor=SURFACE)
print(f"wrote {out}.png")
