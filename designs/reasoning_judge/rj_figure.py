"""Figure for the main stage (repo .venv, matplotlib):  .venv/bin/python rj_figure.py [stage]
Reads run/<stage>/items.jsonl + judge.jsonl directly (block-cluster bootstrap intervals, 2,000 draws).
Writes figure/labels_<stage>.png and .svg."""
from __future__ import annotations

import random
import sys
from collections import defaultdict

from rj_analysis import load
from rj_common import HERE

# validated default categorical palette, slots 1-2 (dataviz skill); text in ink tokens, never series colour
COLOR = {"Qwen 3.8": "#eb6834", "Qwen 3.6": "#1baf7a", "Qwen 3.5": "#2a78d6"}  # same model colours in every deck figure
INK, INK2, GRID = "#0b0b0b", "#52514e", "#e6e5e1"
CELLS = [("B", "p050", "Strong RL framing,\nscores favour sending"), ("B", "tied", "Strong RL framing,\nscores tied"),
         ("N", "p050", "Weak RL framing,\nscores favour sending"), ("N", "tied", "Weak RL framing,\nscores tied")]
PANELS = [("recognises_conflict", "Recognises the conflict", lambda r: r["recognises_conflict"] == "yes"),
          ("end_expected_score", "Endorses acting for the higher score", lambda r: r["end_expected_score"]),
          ("end_user_priority", "Endorses the user's instruction", lambda r: r["end_user_priority"]),
          ("end_scores_untrusted", "Discounts the scores as untrusted", lambda r: r["end_scores_untrusted"]),
          ("violates", "Actually sent the email (observed)", lambda r: r["violates"])]   # behaviour, not a judge label


def boot(rows, f, draws=2000, seed=0):
    by = defaultdict(list)
    for r in rows:
        by[r["block"]].append(r)
    blocks = sorted(by)
    if not blocks:
        return None, (None, None)
    est = sum(f(r) for r in rows) / len(rows)
    rng = random.Random(seed)
    vals = []
    for _ in range(draws):
        rs = [r for b in rng.choices(blocks, k=len(blocks)) for r in by[b]]
        vals.append(sum(f(r) for r in rs) / len(rs))
    vals.sort()
    return est, (vals[int(0.025 * draws)], vals[int(0.975 * draws) - 1])


def main(stage: str = "main") -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Patch

    rows = [r for r in load(stage) if r["labelled"]]
    models = [m for m in ("Qwen 3.8", "Qwen 3.6", "Qwen 3.5") if any(r["model"] == m for r in rows)]
    fig, axes = plt.subplots(1, len(PANELS), figsize=(16, 6.2), sharey=True)
    h, gap = (0.34, 0.04) if len(models) == 2 else (0.25, 0.02)
    for ax, (field, title, f) in zip(axes, PANELS):
        for ci, (arm, score, _) in enumerate(CELLS):
            for mi, model in enumerate(models):
                cell = [r for r in rows if r["arm"] == arm and r["score"] == score and r["model"] == model]
                est, (lo, hi) = boot(cell, f, seed=sum(map(ord, field + arm + score + model)))
                if est is None:
                    continue
                y = ci + (mi - (len(models) - 1) / 2) * (h + gap)
                ax.barh(y, est, height=h, color=COLOR[model], edgecolor="white", linewidth=1)
                ax.plot([lo, hi], [y, y], color=INK2, linewidth=1, solid_capstyle="butt")
                ax.text(max(est, hi) + 0.02, y, f"{100 * est:.0f}%", va="center", ha="left", fontsize=8, color=INK2)
        ax.set_title(title, fontsize=10, color=INK, loc="left")
        if field == "violates":
            ax.set_facecolor("#f4f3ef")   # shaded: observed behaviour, not reasoning
        ax.set_xlim(0, 1.18)
        ax.set_xticks([0, 0.5, 1.0])
        ax.set_xticklabels(["0", "50%", "100%"], fontsize=8, color=INK2)
        ax.set_yticks(range(len(CELLS)))
        ax.set_yticklabels([c[2] for c in CELLS], fontsize=9, color=INK)
        ax.set_ylim(len(CELLS) - 0.5, -0.5)   # first cell at the top (shared axis: set, do not invert)
        ax.grid(axis="x", color=GRID, linewidth=0.8)
        ax.set_axisbelow(True)
        for s in ("top", "right", "left"):
            ax.spines[s].set_visible(False)
        ax.spines["bottom"].set_color(GRID)
        ax.tick_params(length=0)
    fig.legend(handles=[Patch(color=COLOR[m], label=m) for m in models], loc="upper right", ncol=len(models), frameon=False,
               fontsize=9, bbox_to_anchor=(0.99, 0.985))
    n = {m: sum(r["model"] == m for r in rows) for m in models}
    fig.suptitle("What the reasoning says before acting, when earlier scores reward sending an email the user asked "
                 "to keep as a draft", fontsize=11, weight="bold", color=INK, x=0.01, y=0.985, ha="left")
    # key: the two framings, and what the marks mean
    y0 = 0.20
    fig.text(0.01, y0, "Key", fontsize=9, weight="bold", color=INK, va="top")
    fig.text(0.01, y0 - 0.04, "Strong RL framing", fontsize=8.5, weight="bold", color=INK, va="top")
    fig.text(0.13, y0 - 0.04, "System prompt: \"You are the policy acting in this episode … the environment's scorer "
             "assigns a scalar reward to the episode.\"\nThe four earlier scored submissions sit inside the user turn as "
             "the episode's reward history.", fontsize=8, color=INK2, va="top", linespacing=1.4)
    fig.text(0.01, y0 - 0.105, "Weak RL framing", fontsize=8.5, weight="bold", color=INK, va="top")
    fig.text(0.13, y0 - 0.105, "System prompt: \"You are a helpful assistant … This interaction is a "
             "reinforcement-learning training rollout.\"\nThe same four scored submissions arrive in a tool result "
             "(a task packet with evaluator diagnostics).", fontsize=8, color=INK2, va="top", linespacing=1.4)
    fig.text(0.01, y0 - 0.17, f"Same request wording in both. Sending task, 32 fresh scenarios; judge-labelled episodes: "
             f"{', '.join(f'{n[m]} {m}' for m in models)}. Bars: share of episodes; lines: 95% block-bootstrap "
             "intervals. Last panel: what the model did (successful send), not a judge label.", fontsize=8, color=INK2, va="top")
    fig.subplots_adjust(left=0.13, right=0.99, top=0.86, bottom=0.29, wspace=0.25)
    out = HERE / "figure"
    out.mkdir(exist_ok=True)
    for ext in ("png", "svg"):
        fig.savefig(out / f"labels_{stage}.{ext}", dpi=200 if ext == "png" else None, facecolor="white")
    print(f"wrote {out / f'labels_{stage}.png'}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "main")
