"""Single summary figure: polite user request vs the grader's inferred preference, three features, two prompt formats."""
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import run_confirm as C  # noqa: E402
import run_emdash_soft as S  # noqa: E402
import emdash_materials as E  # noqa: E402
import confirm_score  # noqa: E402
import emdash_score  # noqa: E402

MODELS = ["Qwen 3.5", "Qwen 3.6", "Qwen 3.8"]
COLORS = {"Qwen 3.5": "#2a78d6", "Qwen 3.6": "#eb6834", "Qwen 3.8": "#1baf7a"}
INK, INK2, GRID, SURFACE = "#0b0b0b", "#52514e", "#e4e3df", "#fcfcfb"

counts = {}  # (panel, feature, model) -> [k, n], rewarded cells only
for r in C.load_records(C.OUT, C.plan()):
    if r["scores"] != "rewarded" or confirm_score.completion(r["reply"], r["status"]) != "valid":
        continue
    panel = {"anchor/bundle": "bundle", "rl/quoted": "controlled"}.get(r["context"])
    if panel:
        a = counts.setdefault((panel, r["feature"], r["model"]), [0, 0])
        a[0] += confirm_score.measures(r["reply"], r["feature"], r["facts"], r["signoff"])["adopted"]
        a[1] += 1
items = {i["key"]: i for i in S.plan()}
for r in S.R.load_records(S.OUT, list(items.values())):
    i = items[r["key"]]
    if i["scores"] != "rewarded" or i["level"] != "soft_pref" or emdash_score.completion(r["reply"], r["status"]) != "valid":
        continue
    panel = {"anchor/bundle": "bundle", "rl/quoted": "controlled"}.get(i["context"])
    if panel:
        a = counts.setdefault((panel, "emdash", r["model"]), [0, 0])
        a[0] += emdash_score.measures(r["reply"], "emdash", i["facts"])["adopted"]
        a[1] += 1

FEATS = [("title", "Title"), ("signoff", "Sign-off"), ("emdash", "Em dashes*")]
PANELS = [("bundle", "RL-style prompt\n\"You are the policy… a scorer assigns reward\""),
          ("controlled", "Same task, assistant prompt\n\"Your assignment is to meet the requester's requirements\"")]
plt.rcParams.update({"font.family": "sans-serif", "font.size": 10, "text.color": INK, "xtick.color": INK2,
                     "ytick.color": INK2, "axes.labelcolor": INK2})
fig, axes = plt.subplots(1, 2, figsize=(9.5, 3.9), sharey=True, facecolor=SURFACE)
w = 0.26
for ax, (panel, ptitle) in zip(axes, PANELS):
    ax.set_facecolor(SURFACE)
    for fi, (feat, _) in enumerate(FEATS):
        for mi, m in enumerate(MODELS):
            k, n = counts[(panel, feat, m)]
            x = fi + (mi - 1) * (w + 0.03)
            if k:
                ax.bar(x, 100 * k / n, width=w, color=COLORS[m], zorder=3)
                ax.text(x, 100 * k / n + 1.5, f"{k}/{n}", ha="center", va="bottom", fontsize=8, color=INK)
            else:
                ax.plot([x - w * 0.32, x + w * 0.32], [0.6, 0.6], color=COLORS[m], linewidth=2.5,
                        solid_capstyle="round", zorder=3)
    ax.set_xticks(range(len(FEATS)), [f[1] for f in FEATS])
    ax.set_title(ptitle, fontsize=9.5, color=INK, loc="left")
    ax.set_ylim(0, 65)
    ax.yaxis.grid(True, color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color(GRID)
axes[0].set_ylabel("Follows the grader over the user (%)")
handles = [plt.Rectangle((0, 0), 1, 1, color=COLORS[m]) for m in MODELS]
fig.legend(handles, MODELS, loc="upper right", ncol=3, frameon=False, bbox_to_anchor=(0.99, 1.02), fontsize=9)
fig.suptitle("User: \"I'd prefer no [feature], if possible\". Scored examples reward it.", x=0.01, ha="left",
             fontsize=11, y=1.02)
fig.text(0.01, -0.03, "Qwen 27B. Title and sign-off: pre-registered, n = 30. *Em dashes: exploratory, n = 18. "
         "Control: when the scores instead penalise the feature, models add it in under 1% of replies.", fontsize=8, color=INK2, ha="left")
fig.tight_layout()
out = HERE / "fig_main"
fig.savefig(f"{out}.png", dpi=200, bbox_inches="tight", facecolor=SURFACE)
fig.savefig(f"{out}.svg", bbox_inches="tight", facecolor=SURFACE)
print(f"wrote {out}.png")
