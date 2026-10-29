"""Combined score-gap figure: all environments, one panel each.

Numbers are copied from each environment's frozen-analysis report (see SOURCES); nothing is recomputed here.
Run from the repo root: .venv/bin/python designs/score_gap/combined_figure.py
"""
from pathlib import Path

import matplotlib.pyplot as plt

OUT = Path(__file__).parent / "figure_all_curves"
LEVELS = ["−0.50", "−0.20", "−0.05", "0", "+0.05", "+0.20", "+0.50"]

# Categorical slots 1-4 of the reference palette (validated: CVD and normal-vision separation pass;
# aqua and yellow are under 3:1 contrast, so every series also gets its own marker and a legend entry).
SERIES = {
    "Qwen 3.5": dict(color="#2a78d6", marker="o"),
    "Qwen 3.8": dict(color="#eb6834", marker="s"),
    "Claude Haiku 4.5": dict(color="#1baf7a", marker="^"),
    "Claude Haiku 5.5": dict(color="#eda100", marker="D"),
}
INK, INK2, GRID, SURFACE = "#0b0b0b", "#52514e", "#e4e3df", "#fcfcfb"


def pct(ks, ns):
    ns = ns if isinstance(ns, list) else [ns] * len(ks)
    return [100 * k / n for k, n in zip(ks, ns)]


PANELS = [
    dict(title="Upselling, training-style bundle", unit="% upsell", src="recommendation/REPORT.md; haiku/REPORT.md",
         data={"Qwen 3.5": pct([0, 0, 0, 0, 7, 14, 15], 36), "Qwen 3.8": pct([0, 0, 0, 0, 15, 25, 36], 36),
               "Claude Haiku 4.5": pct([0, 0, 0, 0, 2, 3, 4], [36, 34, 36, 36, 34, 35, 36]),
               "Claude Haiku 5.5": pct([0] * 7, [35, 36, 35, 36, 33, 34, 34])}),
    dict(title="Upselling, chat framing", unit="% upsell", src="recommendation/REPORT.md; haiku/REPORT.md",
         data={"Qwen 3.5": pct([0, 0, 0, 0, 14, 22, 32], 36), "Qwen 3.8": pct([0, 0, 0, 0, 0, 0, 2], 36),
               "Claude Haiku 4.5": pct([0, 0, 0, 0, 0, 0, 1], 36),
               "Claude Haiku 5.5": pct([0] * 7, [35, 36, 35, 36, 36, 36, 36])}),
    dict(title="Sending despite “I'll send it myself”, bundle", unit="% sent",
         src="sending/run/REPORT_auto.md; haiku/REPORT.md",
         data={"Qwen 3.5": pct([0, 0, 0, 0, 3, 3, 9], 72), "Qwen 3.8": pct([0, 0, 0, 0, 13, 30, 53], 72),
               "Claude Haiku 4.5": pct([0, 0, 0, 0, 0, 0, 5], 24), "Claude Haiku 5.5": pct([0] * 7, 24)}),
    dict(title="Formatting the user declined, bundle\n(titles, sign-offs, em dashes, bullets pooled)",
         unit="% adopted", src="formatting/REPORT.md",
         data={"Qwen 3.5": pct([0, 0, 0, 0, 0, 0, 2], 96), "Qwen 3.8": pct([0, 0, 0, 0, 2, 6, 49], 96)}),
    dict(title="Dropping a known limitation, RL framing", unit="% omitted", src="omission/run/REPORT_auto.md",
         data={"Qwen 3.5": pct([0, 0, 0, 0, 0, 0, 5], 36), "Qwen 3.8": pct([0, 0, 0, 0, 3, 9, 12], 36)}),
    dict(title="Review rating of a flawed draft, bundle", unit="mean rating /10", src="review/run/REPORT_auto.md",
         ylim=(4, 8.5), data={"Qwen 3.5": [4.96, 4.88, 5.00, 5.00, 5.67, 5.79, 6.33],
                              "Qwen 3.8": [4.92, 4.88, 4.83, 4.71, 5.04, 6.62, 7.50]}),
]


def main():
    plt.rcParams.update({"font.size": 9, "axes.edgecolor": GRID, "axes.labelcolor": INK2,
                         "xtick.color": INK2, "ytick.color": INK2, "text.color": INK})
    fig, axes = plt.subplots(2, 3, figsize=(13, 7.4), facecolor=SURFACE)
    x = list(range(len(LEVELS)))
    for ax, p in zip(axes.flat, PANELS):
        ax.set_facecolor(SURFACE)
        ax.axvspan(-0.5, 3.5, color="#f0efec", zorder=0, lw=0)  # gaps where the history favours the user, or ties
        for name, ys in p["data"].items():
            s = SERIES[name]
            ax.plot(x, ys, color=s["color"], marker=s["marker"], lw=2, ms=6, mec=SURFACE, mew=1.2, label=name,
                    zorder=3)
        ax.set_title(p["title"], fontsize=9.5, loc="left", color=INK)
        ax.set_xticks(x, LEVELS)
        ax.set_xlim(-0.4, len(LEVELS) - 0.6)
        ax.set_ylim(*(p.get("ylim") or (-4, 104)))
        ax.set_ylabel(p["unit"])
        ax.grid(axis="y", color=GRID, lw=0.8)
        ax.tick_params(length=0)
        for side in ("top", "right"):
            ax.spines[side].set_visible(False)
    fig.supxlabel("Score advantage shown for going against the user (levels evenly spaced, not to scale)",
                  fontsize=9.5, color=INK2, y=0.045)
    handles, labels = axes.flat[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", ncol=4, frameon=False, bbox_to_anchor=(0.5, 0.995))
    fig.text(0.01, 0.008, "Shaded: tied scores, or scores favouring the user. Every model stays at its floor there. "
             "Exploratory curves with frozen analyses; scenario-clustered CIs are in each environment's REPORT.md. "
             "Scores are displayed only; no training happens.", fontsize=7.5, color=INK2)
    fig.tight_layout(rect=(0, 0.06, 1, 0.95))
    for ext in ("png", "svg"):
        fig.savefig(f"{OUT}.{ext}", dpi=160, facecolor=SURFACE)
    print(f"Wrote {OUT}.png/.svg")
    summary()


def summary():
    """Dumbbell chart: each model's rate at the largest gap (+0.50), one row per environment."""
    rows = [p for p in PANELS if "ylim" not in p][::-1]  # rate panels only, top-to-bottom as in PANELS
    fig, ax = plt.subplots(figsize=(9, 4.6), facecolor=SURFACE)
    ax.set_facecolor(SURFACE)
    for i, p in enumerate(rows):
        vals = {m: ys[-1] for m, ys in p["data"].items()}
        ax.plot([min(vals.values()), max(vals.values())], [i, i], color=GRID, lw=6, solid_capstyle="round", zorder=1)
        for m, v in vals.items():
            s = SERIES[m]
            ax.plot(v, i, marker=s["marker"], color=s["color"], ms=9, mec=SURFACE, mew=1.5, ls="none", zorder=3,
                    label=m)
        q35, q38 = vals["Qwen 3.5"], vals["Qwen 3.8"]
        ax.text(102, i, f"3.8 {q38:.0f}% · 3.5 {q35:.0f}%", va="center", fontsize=8.5, color=INK2)
    ax.set_yticks(range(len(rows)), [p["title"].split("\n")[0].replace(", training-style bundle", " (bundle)")
                                     for p in rows])
    ax.set_xlim(-3, 128)
    ax.set_xticks([0, 20, 40, 60, 80, 100], ["0%", "20%", "40%", "60%", "80%", "100%"])
    ax.grid(axis="x", color=GRID, lw=0.8)
    ax.tick_params(length=0)
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.set_title("Going against the user at the largest score advantage (+0.50)", loc="left", fontsize=11)
    ax.set_xlabel("share of replies that went against the user's stated preference", color=INK2)
    h, l = ax.get_legend_handles_labels()
    keep = dict(zip(l, h))
    ax.legend([keep[m] for m in SERIES if m in keep], [m for m in SERIES if m in keep], loc="lower center",
              bbox_to_anchor=(0.45, -0.38), ncol=4, frameon=False)
    fig.text(0.01, 0.01, "At every tied or user-favouring score, every model was at 0%. Review ratings, a mean rather "
             "than a share, are in the curve figure.", fontsize=7.5, color=INK2)
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    out = OUT.with_name("figure_summary_at_max_gap")
    for ext in ("png", "svg"):
        fig.savefig(f"{out}.{ext}", dpi=160, facecolor=SURFACE)
    print(f"Wrote {out}.png/.svg")


if __name__ == "__main__":
    main()
