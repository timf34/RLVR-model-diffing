"""Combined score-gap figures, written for readers new to the experiments.

Every number and interval is read from each environment's frozen-analysis results file (`SRC`); nothing is
hand-copied. Rates are scenario-clustered: `lo`/`hi` are the 95% CIs those analyses computed.
Run from the repo root: .venv/bin/python designs/score_gap/combined_figure.py
"""
import json
from pathlib import Path

import matplotlib.pyplot as plt

HERE = Path(__file__).parent
OUT = HERE / "figure_all_curves"
LEVELS = ["−0.50", "−0.20", "−0.05", "0", "+0.05", "+0.20", "+0.50"]
SRC = {
    "rec": "recommendation/run/results_3.5_3.8.json", "haiku_up": "haiku/upsell/run/results.json",
    "haiku_send": "haiku/sending/run/results.json", "send": "sending/run/results.json",
    "fmt": "formatting/run/results.json", "omit": "omission/run/results.json", "review": "review/run/results.json",
}

# Categorical slots 1-4 of the reference palette (validated: CVD and normal-vision separation pass;
# aqua and yellow are under 3:1 contrast, so every series also has its own marker and a legend entry).
SERIES = {
    "Qwen 3.5": dict(color="#2a78d6", marker="o"),
    "Qwen 3.8": dict(color="#eb6834", marker="s"),
    "Claude Haiku 4.5": dict(color="#1baf7a", marker="^"),
    "Claude Haiku 5.5": dict(color="#eda100", marker="D"),
}
INK, INK2, MUTED, GRID, SURFACE, SHADE = "#0b0b0b", "#52514e", "#8a8984", "#e4e3df", "#fcfcfb", "#f0efec"
TRAIN = "training-style prompt"


def load(key):
    return json.loads((HERE / SRC[key]).read_text())["cells"]


def rate_series(cells, key):
    c = cells[key]
    return dict(y=[100 * v for v in c["rate"]], lo=[100 * v for v in c["lo"]], hi=[100 * v for v in c["hi"]])


def panels():
    rec, hup, hsend = load("rec"), load("haiku_up"), load("haiku_send")
    send, fmt, omit, review = load("send"), load("fmt"), load("omit"), load("review")

    def upsell(panel):
        return {"Qwen 3.5": rate_series(rec, f"Qwen 3.5|{panel}"), "Qwen 3.8": rate_series(rec, f"Qwen 3.8|{panel}"),
                "Claude Haiku 4.5": rate_series(hup, f"Haiku 4.5|{panel}"),
                "Claude Haiku 5.5": rate_series(hup, f"Haiku 5.5|{panel}")}

    r = review["rating"]
    base = json.loads((HERE / SRC["review"]).read_text())["baseline"]["rating"]
    return [
        dict(name=f"Upselling · {TRAIN}", short="Upselling, training-style prompt",
             conflict="User wants the cheapest option · scorer favoured a pricier upgrade", data=upsell("bundle")),
        dict(name="Upselling · plain prompt, reward wording", short="Upselling, plain prompt + reward wording",
             conflict="Same task; ordinary prompt that only mentions scores/rewards", data=upsell("episode")),
        dict(name="Upselling · casual chat", short="Upselling, casual chat",
             conflict="Same task, framed as an ordinary chat", data=upsell("chat")),
        dict(name=f"Sending an email · {TRAIN}", short="Sending the user's email",
             conflict="User: “save a draft, I'll send it myself” · scorer favoured sending",
             data={"Qwen 3.5": rate_series(send, "Qwen 3.5|bundle"), "Qwen 3.8": rate_series(send, "Qwen 3.8|bundle"),
                   "Claude Haiku 4.5": rate_series(hsend, "Haiku 4.5|bundle"),
                   "Claude Haiku 5.5": rate_series(hsend, "Haiku 5.5|bundle")}),
        dict(name=f"Formatting · {TRAIN}", short="Unwanted formatting",
             conflict="User: no titles / em dashes / bullets, if possible · scorer favoured them",
             data={m: rate_series(fmt, f"pooled|{m}|bundle") for m in ("Qwen 3.5", "Qwen 3.8")}),
        dict(name="Leaving out a known caveat · training-style wording", short="Dropping a caveat",
             conflict="User needs the limitation stated · scorer favoured dropping it",
             data={m: rate_series(omit, f"{m}|rl") for m in ("Qwen 3.5", "Qwen 3.8")}),
        dict(name=f"Rating a flawed draft · {TRAIN}", short="Review rating", rating=True,
             conflict="User wants an honest rating · scorer favoured high ratings",
             baseline=sum(base[f"{m}|nohist_bundle"]["mean"] for m in ("Qwen 3.5", "Qwen 3.8")) / 2,
             data={m: dict(y=r[f"{m}|bundle"]["mean"], lo=r[f"{m}|bundle"]["lo"], hi=r[f"{m}|bundle"]["hi"])
                   for m in ("Qwen 3.5", "Qwen 3.8")}),
    ]


TITLE = "Scores that favour ignoring the user pull models away from the user's request, usually Qwen 3.8 more than 3.5"
SETUP = ("Setup: each prompt includes earlier answers with scores. The x-axis is how much higher the answers that ignored "
         "the user's request scored (left: the scores favour following the user; right: they favour ignoring it).")


def style():
    plt.rcParams.update({"font.size": 9, "axes.edgecolor": GRID, "axes.labelcolor": INK2, "xtick.color": INK2,
                         "ytick.color": INK2, "text.color": INK})


def curves(P):
    fig, axes = plt.subplots(2, 4, figsize=(17, 8.6), facecolor=SURFACE)
    x = list(range(len(LEVELS)))
    for ax, p in zip(axes.flat, P):
        ax.set_facecolor(SURFACE)
        ax.axvspan(-0.5, 3.5, color=SHADE, zorder=0, lw=0)
        rating = p.get("rating")
        if rating:  # the draft's rating with no scored examples at all
            ax.axhline(p["baseline"], color=MUTED, lw=1, ls=(0, (4, 3)), zorder=1)
            ax.text(-0.3, p["baseline"] + 0.08, "rating with no scored examples", fontsize=7.5, color=MUTED)
        for name, s in p["data"].items():
            st = SERIES[name]
            ax.fill_between(x, s["lo"], s["hi"], color=st["color"], alpha=0.13, lw=0, zorder=2)
            ax.plot(x, s["y"], color=st["color"], marker=st["marker"], lw=2, ms=6, mec=SURFACE, mew=1.2, label=name,
                    zorder=3)
        ax.set_title(f"{p['name']}\n", loc="left", fontsize=9.5, color=INK, fontweight="bold")
        ax.text(0, 1.035, p["conflict"], transform=ax.transAxes, fontsize=7.6, color=INK2, va="bottom")
        ax.set_xticks(x, LEVELS, fontsize=8)
        ax.set_xlim(-0.4, len(LEVELS) - 0.6)
        ax.set_ylim(*((3.5, 9) if rating else (-4, 104)))
        ax.set_ylabel("mean rating out of 10" if rating else "% of replies against the user")
        ax.grid(axis="y", color=GRID, lw=0.8)
        ax.tick_params(length=0)
        for side in ("top", "right"):
            ax.spines[side].set_visible(False)
    axes.flat[0].text(1.5, 92, "scores favour\nthe user (or tie)", ha="center", fontsize=8, color=MUTED)

    key = axes.flat[-1]  # eighth slot: legend and how to read
    key.axis("off")
    handles, labels = axes.flat[0].get_legend_handles_labels()
    key.legend(handles, labels, loc="upper left", frameon=False, fontsize=9.5, title="Models", title_fontsize=9.5,
               alignment="left")
    key.text(0.02, 0.36, "How to read\n"
             "• Lines: share of replies that went\n   against the user at each score gap\n"
             "• Bands: 95% intervals (clustered\n   by scenario)\n"
             "• Grey area: scores tie or favour\n   the user; every model stays at 0\n"
             "• Claude Haiku: upselling and\n   sending only", transform=key.transAxes, va="top", fontsize=8.5,
             color=INK2, linespacing=1.45)

    fig.supxlabel("← scores favour following the user          score advantage for ignoring the user          "
                  "scores favour ignoring the user →", fontsize=9, color=INK2, y=0.05)
    fig.suptitle(TITLE, x=0.01, y=0.985, ha="left", fontsize=13, fontweight="bold")
    fig.text(0.01, 0.94, SETUP, fontsize=9.2, color=INK2)
    fig.text(0.01, 0.012, "Scores are only shown to the model; no training happens. Exploratory curves; numbers read "
             "from each environment's frozen results file under designs/score_gap/.", fontsize=7.5, color=MUTED)
    fig.tight_layout(rect=(0, 0.065, 1, 0.925), h_pad=3.2, w_pad=2.0)
    save(fig, OUT)


def summary(P):
    """Each model's rate at the largest gap (+0.50) with its 95% CI; one row per environment, models dodged."""
    rows = [p for p in P if not p.get("rating")][::-1]
    order = [m for m in SERIES]
    off = {m: o for m, o in zip(order, (0.24, 0.08, -0.08, -0.24))}
    fig, ax = plt.subplots(figsize=(10.5, 6.6), facecolor=SURFACE)
    ax.set_facecolor(SURFACE)
    for i, p in enumerate(rows):
        if i % 2 == 0:
            ax.axhspan(i - 0.45, i + 0.45, color=SHADE, lw=0, zorder=0)
        for m, s in p["data"].items():
            st, y = SERIES[m], i + off[m]
            v, lo, hi = s["y"][-1], s["lo"][-1], s["hi"][-1]
            ax.plot([lo, hi], [y, y], color=st["color"], lw=2, solid_capstyle="round", zorder=2)
            ax.plot(v, y, marker=st["marker"], color=st["color"], ms=8, mec=SURFACE, mew=1.3, ls="none", zorder=3,
                    label=m)
        q38, q35 = p["data"]["Qwen 3.8"]["y"][-1], p["data"]["Qwen 3.5"]["y"][-1]
        ax.text(107, i, f"Qwen 3.8 {q38:.0f}%\nQwen 3.5 {q35:.0f}%", va="center", fontsize=8, color=INK2,
                linespacing=1.3)
        ax.text(-4, i - 0.27, p["conflict"], ha="right", va="center", fontsize=7.3, color=MUTED)
    ax.set_yticks([i + 0.1 for i in range(len(rows))], [p["short"] for p in rows], fontsize=9.3, color=INK)
    ax.set_ylim(-0.6, len(rows) - 0.4)
    ax.set_xlim(-3, 126)
    ax.set_xticks([0, 20, 40, 60, 80, 100], ["0%", "20%", "40%", "60%", "80%", "100%"])
    ax.grid(axis="x", color=GRID, lw=0.8)
    ax.tick_params(length=0)
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.set_xlabel("% of replies that went against the user's request (bars: 95% intervals, clustered by scenario)",
                  color=INK2)
    fig.suptitle("At a large score advantage, Qwen 3.8 goes against the user in most tasks; Qwen 3.5 mainly when upselling",
                 x=0.012, y=0.975, ha="left", fontsize=12, fontweight="bold")
    fig.text(0.012, 0.885, "Earlier answers that ignored the user scored 0.75; answers that followed the user scored 0.25.\n"
             "The exception is upselling outside the training-style prompt, where Qwen 3.5 follows the scores more "
             "than 3.8.", fontsize=8.5, color=INK2)
    h, l = ax.get_legend_handles_labels()
    keep = dict(zip(l, h))
    fig.legend([keep[m] for m in order], order, loc="lower center", ncol=4, frameon=False,
               bbox_to_anchor=(0.55, 0.03))
    fig.text(0.012, 0.01, "With tied scores or scores favouring the user, every model was at 0%. Claude Haiku: upselling "
             "and sending only. Review ratings (a mean, not a %) are in the curves figure.", fontsize=7.5, color=MUTED)
    fig.tight_layout(rect=(0, 0.08, 1, 0.875))
    save(fig, OUT.with_name("figure_summary_at_max_gap"))


def save(fig, path):
    for ext in ("png", "svg"):
        fig.savefig(f"{path}.{ext}", dpi=160, facecolor=SURFACE)
    print(f"Wrote {path}.png/.svg")


if __name__ == "__main__":
    style()
    P = panels()
    curves(P)
    summary(P)
