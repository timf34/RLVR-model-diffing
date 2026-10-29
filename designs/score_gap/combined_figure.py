"""Combined score-gap figures, written for readers new to the experiments.

Numbers are copied from each environment's frozen-analysis report (see `src` per panel); nothing is recomputed.
Run from the repo root: .venv/bin/python designs/score_gap/combined_figure.py
"""
from pathlib import Path

import matplotlib.pyplot as plt

OUT = Path(__file__).parent / "figure_all_curves"
LEVELS = ["−0.50", "−0.20", "−0.05", "0", "+0.05", "+0.20", "+0.50"]

# Categorical slots 1-4 of the reference palette (validated: CVD and normal-vision separation pass;
# aqua and yellow are under 3:1 contrast, so every series also has its own marker and a legend entry).
SERIES = {
    "Qwen 3.5": dict(color="#2a78d6", marker="o"),
    "Qwen 3.8": dict(color="#eb6834", marker="s"),
    "Claude Haiku 4.5": dict(color="#1baf7a", marker="^"),
    "Claude Haiku 5.5": dict(color="#eda100", marker="D"),
}
INK, INK2, MUTED, GRID, SURFACE, SHADE = "#0b0b0b", "#52514e", "#8a8984", "#e4e3df", "#fcfcfb", "#f0efec"


def pct(ks, ns):
    ns = ns if isinstance(ns, list) else [ns] * len(ks)
    return [100 * k / n for k, n in zip(ks, ns)]


PANELS = [
    dict(name="Upselling · training-style prompt",
         conflict="User wants the cheapest option · scorer favoured a pricier upgrade",
         short="Upselling (training-style)", src="recommendation/REPORT.md; haiku/REPORT.md",
         data={"Qwen 3.5": pct([0, 0, 0, 0, 7, 14, 15], 36), "Qwen 3.8": pct([0, 0, 0, 0, 15, 25, 36], 36),
               "Claude Haiku 4.5": pct([0, 0, 0, 0, 2, 3, 4], [36, 34, 36, 36, 34, 35, 36]),
               "Claude Haiku 5.5": pct([0] * 7, [35, 36, 35, 36, 33, 34, 34])}),
    dict(name="Upselling · casual chat prompt",
         conflict="Same task, framed as an ordinary chat",
         short="Upselling (chat)", src="recommendation/REPORT.md; haiku/REPORT.md",
         data={"Qwen 3.5": pct([0, 0, 0, 0, 14, 22, 32], 36), "Qwen 3.8": pct([0, 0, 0, 0, 0, 0, 2], 36),
               "Claude Haiku 4.5": pct([0, 0, 0, 0, 0, 0, 1], 36),
               "Claude Haiku 5.5": pct([0] * 7, [35, 36, 35, 36, 36, 36, 36])}),
    dict(name="Sending an email · training-style prompt",
         conflict="User: “save a draft, I'll send it myself” · scorer favoured sending",
         short="Sending the user's email", src="sending/run/REPORT_auto.md; haiku/REPORT.md",
         data={"Qwen 3.5": pct([0, 0, 0, 0, 3, 3, 9], 72), "Qwen 3.8": pct([0, 0, 0, 0, 13, 30, 53], 72),
               "Claude Haiku 4.5": pct([0, 0, 0, 0, 0, 0, 5], 24), "Claude Haiku 5.5": pct([0] * 7, 24)}),
    dict(name="Formatting · training-style prompt",
         conflict="User: no titles / em dashes / bullets, if possible · scorer favoured them",
         short="Unwanted formatting", src="formatting/REPORT.md",
         data={"Qwen 3.5": pct([0, 0, 0, 0, 0, 0, 2], 96), "Qwen 3.8": pct([0, 0, 0, 0, 2, 6, 49], 96)}),
    dict(name="Leaving out a known caveat · training-style wording",
         conflict="User needs the limitation stated · scorer favoured dropping it",
         short="Dropping a caveat", src="omission/run/REPORT_auto.md",
         data={"Qwen 3.5": pct([0, 0, 0, 0, 0, 0, 5], 36), "Qwen 3.8": pct([0, 0, 0, 0, 3, 9, 12], 36)}),
    dict(name="Rating a flawed draft · training-style prompt",
         conflict="User wants an honest rating · scorer favoured high ratings",
         short="Review rating", src="review/run/REPORT_auto.md", rating=True, baseline=4.35,
         data={"Qwen 3.5": [4.96, 4.88, 5.00, 5.00, 5.67, 5.79, 6.33],
               "Qwen 3.8": [4.92, 4.88, 4.83, 4.71, 5.04, 6.62, 7.50]}),
]

TITLE = "Scores that favour ignoring the user pull models away from the user's request, usually Qwen 3.8 more than 3.5"
SETUP = ("Setup: each prompt includes earlier answers with scores. The x-axis is how much higher the answers that ignored "
         "the user's request scored (left: the scores favour following the user; right: they favour ignoring it).")


def style():
    plt.rcParams.update({"font.size": 9, "axes.edgecolor": GRID, "axes.labelcolor": INK2, "xtick.color": INK2,
                         "ytick.color": INK2, "text.color": INK})


def curves():
    fig, axes = plt.subplots(2, 3, figsize=(13.5, 8.2), facecolor=SURFACE)
    x = list(range(len(LEVELS)))
    for ax, p in zip(axes.flat, PANELS):
        ax.set_facecolor(SURFACE)
        ax.axvspan(-0.5, 3.5, color=SHADE, zorder=0, lw=0)
        rating = p.get("rating")
        if rating:  # the draft's rating with no scored examples at all
            ax.axhline(p["baseline"], color=MUTED, lw=1, ls=(0, (4, 3)), zorder=1)
            ax.text(-0.3, p["baseline"] + 0.08, "rating with no scored examples", fontsize=7.5, color=MUTED)
        for name, ys in p["data"].items():
            s = SERIES[name]
            ax.plot(x, ys, color=s["color"], marker=s["marker"], lw=2, ms=6, mec=SURFACE, mew=1.2, label=name,
                    zorder=3)
        ax.set_title(f"{p['name']}\n", loc="left", fontsize=10, color=INK, fontweight="bold")
        ax.text(0, 1.035, p["conflict"], transform=ax.transAxes, fontsize=8, color=INK2, va="bottom")
        ax.set_xticks(x, LEVELS)
        ax.set_xlim(-0.4, len(LEVELS) - 0.6)
        ax.set_ylim(*((4, 8.5) if rating else (-4, 104)))
        ax.set_ylabel("mean rating out of 10" if rating else "% of replies against the user")
        ax.grid(axis="y", color=GRID, lw=0.8)
        ax.tick_params(length=0)
        for side in ("top", "right"):
            ax.spines[side].set_visible(False)
    a0 = axes.flat[0]  # say which side is which, once
    a0.text(1.5, 92, "scores favour\nthe user (or tie)", ha="center", fontsize=8, color=MUTED)
    fig.supxlabel("← scores favour following the user          score advantage for ignoring the user          "
                  "scores favour ignoring the user →", fontsize=9, color=INK2, y=0.055)
    fig.suptitle(TITLE, x=0.012, y=0.985, ha="left", fontsize=12.5, fontweight="bold")
    fig.text(0.012, 0.94, SETUP, fontsize=9, color=INK2)
    handles, labels = a0.get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper right", ncol=4, frameon=False, bbox_to_anchor=(0.995, 0.93))
    fig.text(0.012, 0.012, "Claude Haiku was tested on the upselling and sending tasks only. Scores are only shown to "
             "the model; no training happens. Exploratory curves; confidence intervals are in each environment's "
             "REPORT.md.", fontsize=7.5, color=MUTED)
    fig.tight_layout(rect=(0, 0.07, 1, 0.9), h_pad=3.2)
    save(fig, OUT)


def summary():
    """Dumbbell chart: each model's rate at the largest gap (+0.50), one row per environment."""
    rows = [p for p in PANELS if not p.get("rating")][::-1]
    fig, ax = plt.subplots(figsize=(10, 5.4), facecolor=SURFACE)
    ax.set_facecolor(SURFACE)
    for i, p in enumerate(rows):
        vals = {m: ys[-1] for m, ys in p["data"].items()}
        ax.plot([min(vals.values()), max(vals.values())], [i, i], color=GRID, lw=6, solid_capstyle="round", zorder=1)
        for m, v in vals.items():
            s = SERIES[m]
            ax.plot(v, i, marker=s["marker"], color=s["color"], ms=9, mec=SURFACE, mew=1.5, ls="none", zorder=3,
                    label=m)
        ax.text(103, i, f"Qwen 3.8 {vals['Qwen 3.8']:.0f}%\nQwen 3.5 {vals['Qwen 3.5']:.0f}%", va="center",
                fontsize=8, color=INK2, linespacing=1.3)
        ax.text(-4, i - 0.3, p["conflict"], ha="right", va="center", fontsize=7.5, color=MUTED)
    ax.set_yticks(range(len(rows)), [p["short"] for p in rows], fontsize=9.5, color=INK)
    ax.set_ylim(-0.6, len(rows) - 0.5)
    ax.set_xlim(-3, 120)
    ax.set_xticks([0, 20, 40, 60, 80, 100], ["0%", "20%", "40%", "60%", "80%", "100%"])
    ax.grid(axis="x", color=GRID, lw=0.8)
    ax.tick_params(length=0)
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.set_xlabel("% of replies that went against the user's request", color=INK2)
    fig.suptitle("At a large score advantage, Qwen 3.8 usually ignores the user; 3.5 mostly doesn't",
                 x=0.012, y=0.975, ha="left", fontsize=12, fontweight="bold")
    fig.text(0.012, 0.865, "Earlier answers that ignored the user scored 0.75; answers that followed the user scored 0.25.\n"
             "The one exception: upselling in casual chat, where Qwen 3.5 follows the scores and 3.8 doesn't.",
             fontsize=8.5, color=INK2)
    h, l = ax.get_legend_handles_labels()
    keep = dict(zip(l, h))
    fig.legend([keep[m] for m in SERIES], list(SERIES), loc="lower center", ncol=4, frameon=False,
               bbox_to_anchor=(0.55, 0.035))
    fig.text(0.012, 0.012, "With tied scores or scores favouring the user, every model was at 0%. Claude Haiku: upselling "
             "and sending only. Review ratings (a mean, not a %) are in the curves figure.", fontsize=7.5, color=MUTED)
    fig.tight_layout(rect=(0, 0.1, 1, 0.86))
    save(fig, OUT.with_name("figure_summary_at_max_gap"))


def save(fig, path):
    for ext in ("png", "svg"):
        fig.savefig(f"{path}.{ext}", dpi=160, facecolor=SURFACE)
    print(f"Wrote {path}.png/.svg")


if __name__ == "__main__":
    style()
    curves()
    summary()
