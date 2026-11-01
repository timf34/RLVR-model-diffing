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
    ("DeepSeek", [("DeepSeek V3-0324", "V3-0324", "■ c", False), ("DeepSeek R1-0528", "R1-0528", "■ c", True),
                  ("DeepSeek V3.2-Exp", "V3.2-Exp", "■ c", True), ("DeepSeek V3.2", "V3.2", "■ c", True),
                  ("DeepSeek V4-Flash", "V4-Flash", "□ f", True), ("DeepSeek V4-Flash-0731", "V4-Flash-0731", "□ f", True),
                  ("DeepSeek V4.1-Flash", "V4.1-Flash", "□ f", True),
                  ("DeepSeek V4.1-Flash-1017", "V4.1-Flash-1017", "□ f", True),
                  ("DeepSeek V4-Pro", "V4-Pro", "■ g", True), ("DeepSeek V4-Pro-0813", "V4-Pro-0813", "■ g", True)]),
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


def main():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Patch

    data = json.loads((HERE / "run_extra" / "compare.json").read_text())
    rows = []   # (y, kind, payload)
    y = 0.0
    for fam, models in FAMILIES:
        models = [m for m in models if m[0] in data]
        if not models:
            continue
        rows.append((y, "family", fam))
        y += 0.9
        for m in models:
            rows.append((y, "model", m))
            y += 1.0
        y += 0.35
    ymax = y

    H = 2.9 + 0.3 * ymax   # inches; header and footer are placed in inches from the edges
    fig, axes = plt.subplots(1, 3, figsize=(13, H), sharey=True)
    for ax, (task, title) in zip(axes, TASKS):
        for yy, kind, p in rows:
            if kind == "family":
                ax.axhspan(yy - 0.45, yy + 0.4, color=SHADE, zorder=0, lw=0)
                continue
            label, _, _, reasoning = p
            c = data[label]["tasks"].get(task, {}).get("p050")
            if c is None:
                continue
            rate, lo, hi = c["rate"], c["lo"], c["hi"]
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
               loc="upper right", bbox_to_anchor=(0.99, 1 - 0.75 / H), ncol=2, frameon=False, fontsize=9)
    fig.suptitle("Following the scores against the user shows up only in reasoning models, in every family; "
                 "OpenAI's only on sending", fontsize=12.5, weight="bold", color=INK, x=0.01, y=1 - 0.12 / H, ha="left")
    fig.text(0.01, 1 - 0.5 / H, "Strong RL framing; earlier scores favour ignoring the user's request (0.75 vs 0.25). "
             "Share of replies that went against the user; lines are 95% intervals over scenarios.\n"
             "About 190 replies per bar for models that show the behaviour (half original, half fresh scenarios); 68 for models at or near 0%.",
             fontsize=8.8, color=INK2, ha="left", va="top", linespacing=1.4)
    fig.text(0.01, 0.012,
             "■ same letter = the lab says these share a base model.  □ same letter = reported or likely the same "
             "lineage, not confirmed.\n(a) Qwen 27B releases   (b) Kimi K2   (c) DeepSeek V3   (d) GLM-4.5   "
             "(e) GPT-4o, the reported base of the o-series   (f) DeepSeek V4-Flash   (g) DeepSeek V4-Pro.   "
             "No mark: base not public.\nWith tied scores (0.50 / 0.50) every model stays at 0–3%, except DeepSeek R1 on bullets "
             "(12%). Sending counts episodes that acted and then ended with a blank message "
             "(read from the tool log).",
             fontsize=7.8, color=INK2, ha="left", va="bottom", linespacing=1.45)
    fig.subplots_adjust(left=0.17, right=0.985, top=1 - 1.45 / H, bottom=0.85 / H, wspace=0.08)
    out = HERE / "figure"
    for ext in ("png", "svg"):
        fig.savefig(out / f"other_models.{ext}", dpi=200 if ext == "png" else None, facecolor="white")
    print(f"wrote {out}/other_models.png")


if __name__ == "__main__":
    main()
