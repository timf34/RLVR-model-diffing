"""Deck figure: score-following under strong RL framing across model families (reads run_extra/compare.json; no API).

  .venv/bin/python designs/presentation_ablation/pa_extra_figure.py   -> figure/other_models.{png,svg}

Rows = models grouped by family (MiniMax and Qwen3-235B left out by request). Columns = the three tasks. Bar = rate of
going against the user when earlier scores favour it (0.75 vs 0.25), valid replies, with Wilson 95% intervals.
Colour = reasoning model (orange) vs not (grey). Run pa_extra_compare.py first.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
REASON, PLAIN = "#eb6834", "#b5b4ad"
INK, INK2, GRID, SHADE = "#0b0b0b", "#52514e", "#e6e5e1", "#f4f3ef"

# (family, [(label in compare.json, display name, base marker, reasoning?)])
# base marker: "■ x" = the lab says these share a base model; "□ x" = reported / likely same lineage
FAMILIES = [
    ("Qwen 27B", [("Qwen 3.5", "Qwen 3.5", "□ a", True), ("Qwen 3.6", "Qwen 3.6", "□ a", True),
                  ("Qwen 3.8", "Qwen 3.8", "□ a", True)]),
    ("Kimi", [("Kimi K2-0905", "K2-0905", "■ b", False), ("Kimi K2-thinking", "K2-thinking", "■ b", True),
              ("Kimi K2.5", "K2.5", "□ b", True), ("Kimi K2.6", "K2.6", "□ b", True)]),
    ("DeepSeek", [("DeepSeek V3-0324", "V3-0324", "■ c", False), ("DeepSeek R1-0528", "R1-0528", "■ c", True)]),
    ("GLM", [("GLM-4.5", "GLM-4.5", "□ d", True), ("GLM-4.6", "GLM-4.6", "□ d", True),
             ("GLM-4.7", "GLM-4.7", "□ d", True)]),
    ("OpenAI", [("GPT-4o (2024-11-20)", "GPT-4o", "□ e", False), ("GPT-4.1", "GPT-4.1", "", False),
                ("o3", "o3", "□ e", True), ("GPT-5", "GPT-5", "", True), ("GPT-5.1", "GPT-5.1", "", True),
                ("GPT-5.2", "GPT-5.2", "", True), ("gpt-oss-120b", "gpt-oss-120b", "", True),
                ("gpt-oss-20b", "gpt-oss-20b", "", True)]),
]
TASKS = [("send", "Sends / acts anyway\n(user said: save as a draft)"),
         ("titles", "Adds a title or sign-off\n(user said: none)"),
         ("bullets", "Uses bullet points\n(user said: one paragraph)")]
# GPT-5.1 often saves the draft and then ends with a blank message, which the scorer drops as non-valid. Counting those
# episodes from the tool log (none of them sent) gives 16/68 instead of 13/44 (see the summary in COMPARE.md).
OVERRIDE = {("GPT-5.1", "send"): (16, 68)}


def wilson(k, n, z=1.959964):
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return max(0.0, c - h), min(1.0, c + h)


def main():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Patch

    data = json.loads((HERE / "run_extra" / "compare.json").read_text())
    rows = []   # (y, kind, payload)
    y = 0.0
    for fam, models in FAMILIES:
        rows.append((y, "family", fam))
        y += 0.9
        for m in models:
            rows.append((y, "model", m))
            y += 1.0
        y += 0.35
    ymax = y

    fig, axes = plt.subplots(1, 3, figsize=(13, 10.2), sharey=True)
    for ax, (task, title) in zip(axes, TASKS):
        for yy, kind, p in rows:
            if kind == "family":
                ax.axhspan(yy - 0.45, yy + 0.4, color=SHADE, zorder=0, lw=0)
                continue
            label, _, _, reasoning = p
            k, n = OVERRIDE.get((label, task)) or data[label][task]["p050"]
            rate = k / n
            lo, hi = wilson(k, n)
            col = REASON if reasoning else PLAIN
            ax.barh(yy, max(rate, 0.006), height=0.68, color=col, zorder=2, lw=0)
            ax.plot([lo, hi], [yy, yy], color=INK2, lw=0.9, alpha=0.6, zorder=3)
            ax.text(hi + 0.015, yy, f"{100 * rate:.0f}%", va="center", ha="left", fontsize=8,
                    color=INK if rate >= 0.1 else INK2, weight="bold" if rate >= 0.1 else "normal")
        ax.set_title(title, fontsize=10, color=INK, loc="left", weight="bold")
        ax.set_xlim(0, 1)
        ax.set_xticks([0, 0.25, 0.5, 0.75], ["0%", "25%", "50%", "75%"], fontsize=8, color=INK2)
        ax.grid(axis="x", color=GRID, lw=0.8)
        ax.set_axisbelow(True)
        for sp in ("top", "right", "left"):
            ax.spines[sp].set_visible(False)
        ax.spines["bottom"].set_color(GRID)
        ax.tick_params(length=0)
    ax0 = axes[0]
    ax0.set_ylim(ymax - 0.2, -0.7)
    ticks, labels = [], []
    for yy, kind, p in rows:
        if kind == "family":
            ax0.text(-0.02, yy, p, transform=ax0.get_yaxis_transform(), ha="right", va="center", fontsize=10,
                     weight="bold", color=INK)
        else:
            ticks.append(yy)
            labels.append(f"{p[1]}  {p[2]}".rstrip())
    ax0.set_yticks(ticks, labels, fontsize=9, color=INK)
    fig.legend(handles=[Patch(color=REASON, label="reasoning model"), Patch(color=PLAIN, label="no reasoning")],
               loc="upper right", bbox_to_anchor=(0.99, 0.935), ncol=2, frameon=False, fontsize=9)
    fig.suptitle("Following the scores against the user shows up only in reasoning models, and mostly in Qwen, "
                 "Kimi and GLM", fontsize=12.5, weight="bold", color=INK, x=0.01, y=0.985, ha="left")
    fig.text(0.01, 0.945, "Strong RL framing; earlier scores favour ignoring the user's request (0.75 vs 0.25). "
             "Share of replies that went against the user, ~68 per bar; lines are 95% intervals.\nWith tied scores "
             "(0.50 / 0.50) every model here stays at 0–1%, except DeepSeek R1 on bullets (12%).",
             fontsize=8.8, color=INK2, ha="left", va="top", linespacing=1.4)
    fig.text(0.01, 0.012,
             "■ same letter = the lab says these share a base model.  □ same letter = reported or likely the same "
             "lineage, not confirmed.\n(a) Qwen 27B releases   (b) Kimi K2   (c) DeepSeek V3   (d) GLM-4.5   "
             "(e) GPT-4o, the reported base of the o-series.   No mark: base not public.\nGPT-5.1 counts episodes that saved the draft and ended "
             "with a blank message (16/68; 30% if those are dropped). All models served through OpenRouter.",
             fontsize=7.8, color=INK2, ha="left", va="bottom", linespacing=1.45)
    fig.subplots_adjust(left=0.17, right=0.985, top=0.86, bottom=0.085, wspace=0.08)
    out = HERE / "figure"
    for ext in ("png", "svg"):
        fig.savefig(out / f"other_models.{ext}", dpi=200 if ext == "png" else None, facecolor="white")
    print(f"wrote {out}/other_models.png")


if __name__ == "__main__":
    main()
