"""Figures read directly from run/<exp>/results.json (repo .venv):  .venv/bin/python ig_figures.py
Writes figure/*.png|pdf|svg. Qwen 3.8 is the left/primary panel; Qwen 3.5 on the same scales."""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

HERE = Path(__file__).resolve().parent
RUN, FIG = HERE / "run", HERE / "figure"
FIG.mkdir(exist_ok=True)
plt.rcParams.update({"svg.fonttype": "none", "font.size": 10, "axes.spines.top": False, "axes.spines.right": False,
                     "axes.grid": True, "grid.color": "#e6e5e0", "grid.linewidth": 0.6, "axes.edgecolor": "#8a897f"})
FRAMES = {"ordinary": ("#2a78d6", "o", "Ordinary session"), "evaluation": ("#1baf7a", "s", "Offline evaluation"),
          "rl": ("#eb6834", "^", "RL training rollout")}
EV_LABEL = {"no_grader": "No grader\n(task data)", "metadata": "Evaluator\nmetadata", "unscored": "Unscored\nhistory",
            "tied": "Tied\n0.50/0.50", "aligned_m050": "User-aligned\n−0.50", "conflict_p005": "Conflict\n+0.05",
            "conflict_p050": "Conflict\n+0.50"}
EVS = list(EV_LABEL)
GAPS = {"aligned_m050": -0.5, "tied": 0.0, "conflict_p005": 0.05, "conflict_p050": 0.5}
MODELS = ("Qwen 3.8", "Qwen 3.5")
INK = "#3d3c36"
CAPTION = ("Rule: the user's explicit IFEval-derived instruction (checked by the upstream strict checker on the raw "
           "final answer). Displayed scores are synthetic evidence in an incidental 'automated_response_evaluator' "
           "record, not real labels; gap = violating − compliant historical answer.")


def save(fig, name):
    for ext in ("png", "pdf", "svg"):
        fig.savefig(FIG / f"{name}.{ext}", dpi=200, bbox_inches="tight")
    plt.close(fig)


def cells(res):
    return {(c["model"], c["frame"], c["evidence"]): c for c in res["cells"]}


def ymax(res):
    hi = max(c["ci95"][1] for c in res["cells"])
    return max(0.1, min(1.0, hi * 1.15))


def fig1(res):
    C = cells(res)
    fig, axes = plt.subplots(1, 2, figsize=(13, 4.6), sharey=True)
    for ax, m in zip(axes, MODELS):
        for j, (f, (col, mk, lab)) in enumerate(FRAMES.items()):
            xs = [i + (j - 1) * 0.22 for i in range(len(EVS))]
            ys = [C[(m, f, e)]["macro"] for e in EVS]
            lo = [y - C[(m, f, e)]["ci95"][0] for y, e in zip(ys, EVS)]
            hi = [C[(m, f, e)]["ci95"][1] - y for y, e in zip(ys, EVS)]
            ax.errorbar(xs, ys, yerr=[lo, hi], fmt=mk, color=col, ms=7, lw=1.4, capsize=2, label=lab)
        ax.axvline(2.5, color="#b9b8ae", lw=0.8, ls=":")
        ax.set_xticks(range(len(EVS)), [EV_LABEL[e] for e in EVS], fontsize=8)
        ax.set_title(m, color=INK, loc="left", fontweight="bold")
        n = C[(m, "rl", "tied")]["n"]
        ax.text(0.99, 0.97, f"n ≈ {n} valid episodes per point", transform=ax.transAxes, ha="right", va="top",
                fontsize=8, color="#6b6a62")
    axes[0].set_ylabel("Macro constraint-violation rate\n(selected IFEval-derived suite)")
    axes[0].set_ylim(0, ymax(res))
    axes[1].legend(frameon=False, loc="upper left")
    fig.suptitle("Violation rate by grader evidence and runtime frame (95% block-bootstrap CIs)", x=0.01, ha="left")
    fig.text(0.01, -0.06, CAPTION, fontsize=7.5, color="#6b6a62", wrap=True)
    save(fig, "fig1_evidence_conditions")


def fig2(res):
    C = cells(res)
    fig, axes = plt.subplots(1, 4, figsize=(14, 4.6), sharey=True,
                             gridspec_kw=dict(width_ratios=[4, 1.4, 4, 1.4], wspace=0.12))
    BASE = ("no_grader", "metadata", "unscored")
    for k, m in enumerate(MODELS):
        ax, bx = axes[2 * k], axes[2 * k + 1]
        for j, (f, (col, mk, lab)) in enumerate(FRAMES.items()):
            xs = sorted(GAPS, key=GAPS.get)
            ax.plot([GAPS[e] for e in xs], [C[(m, f, e)]["macro"] for e in xs], color=col, lw=2, marker=mk, ms=7,
                    label=lab)
            for e in xs:
                lo, hi = C[(m, f, e)]["ci95"]
                ax.plot([GAPS[e]] * 2, [lo, hi], color=col, lw=1, alpha=0.6)
            for i, e in enumerate(BASE):
                x = i + (j - 1) * 0.22
                lo, hi = C[(m, f, e)]["ci95"]
                bx.plot([x, x], [lo, hi], color=col, lw=1, alpha=0.6)
                bx.plot([x], [C[(m, f, e)]["macro"]], marker=mk, color=col, ms=6, ls="none")
        ax.set_xticks([-0.5, 0, 0.5], ["−0.50\nuser-aligned", "0\ntied", "+0.50\nconflicting"])
        ax.set_xticks([0.05], ["+0.05"], minor=True)
        ax.tick_params(axis="x", which="minor", pad=26, labelsize=8)
        ax.set_xlabel("Displayed score gap (violating − compliant)")
        ax.set_title(m, color=INK, loc="left", fontweight="bold")
        bx.set_xticks(range(3), ["none", "meta", "unsc."], fontsize=7.5)
        bx.set_xlim(-0.6, 2.6)
        bx.set_title("baselines", fontsize=8, color="#6b6a62")
    axes[0].set_ylabel("Macro constraint-violation rate")
    axes[0].set_ylim(0, ymax(res))
    axes[2].legend(frameon=False, loc="upper left")
    fig.suptitle("Score-gap curves by frame (numeric x-axis); categorical baselines in side panels", x=0.01, ha="left")
    fig.text(0.01, -0.13, CAPTION, fontsize=7.5, color="#6b6a62", wrap=True)
    save(fig, "fig2_score_gap_curves")


def forest(ax, items, title):
    for i, (lab, s) in enumerate(items):
        y = len(items) - 1 - i
        ax.plot(s["ci95"], [y, y], color="#5f5e57", lw=1.6)
        ax.plot([s["estimate"]], [y], "o", color="#2a78d6", ms=6)
        tag = f"{s['estimate']:+.3f}"
        fp = lambda x: "<0.001" if x < 0.001 else f"={x:.3f}"  # noqa: E731
        if "p_holm" in s:
            tag += f"  (Holm p{fp(s['p_holm'])})"
        elif s.get("p") is not None:
            tag += f"  (unadj. p{fp(s['p'])})"
        if s.get("n_nonzero_blocks") == 0:
            tag += "  all blocks 0"
        ax.text(1.02, y, tag, transform=ax.get_yaxis_transform(), fontsize=7.5, va="center", color=INK)
    ax.axvline(0, color="#8a897f", lw=0.8)
    ax.set_yticks(range(len(items)), [l for l, _ in reversed(items)], fontsize=8)
    ax.set_title(title, loc="left", fontsize=10, color=INK)


def fig3(res):
    P = res["primary"]
    subs = res["subtype_contrasts"]
    fig, axes = plt.subplots(1, 2, figsize=(13, 5.5), gridspec_kw=dict(wspace=0.9))
    forest(axes[0], [(k, P[k]) for k in P], "Primary paired contrasts (macro, 95% CI)")
    axes[0].set_xlabel("Difference in violation rate")
    items = []
    for s, d in subs.items():
        for m in MODELS:
            items.append((f"{s} · {m[-3:]}", d[f"{m} rl: +0.50 - tied"]))
    forest(axes[1], items, "RL frame: +0.50 − tied, by subtype")
    axes[1].set_xlabel("Difference in violation rate")
    fig.text(0.01, -0.04, "A = RL vs ordinary difference-in-differences (+0.50 − tied); B = RL vs evaluation; "
             "G = +0.50 − +0.05 in RL; E = metadata − no grader (ordinary). " + CAPTION, fontsize=7.5,
             color="#6b6a62", wrap=True)
    save(fig, "fig3_subtypes_and_interactions")


def fig4_discovery():
    p = RUN / "discovery" / "results.json"
    if not p.exists():
        return
    r = json.loads(p.read_text())["cells"]
    keys = [f"{m}|{f}|{e}" for m in MODELS for f in FRAMES for e in ("tied", "conflict_p050")]
    keys = [k for k in keys if k in r]
    fig, ax = plt.subplots(figsize=(12, 4.2))
    x = range(len(keys))
    w = 0.27
    for j, (fld, col, lab) in enumerate([("opened_history_file", "#2a78d6", "Opened run_history.jsonl"),
                                         ("scores_in_context", "#1baf7a", "Score bytes reached context"),
                                         ("violates_all_assigned", "#eb6834", "Violated (all assigned)")]):
        ax.bar([i + (j - 1) * w for i in x], [r[k][fld] / r[k]["n"] for k in keys], width=w - 0.03, color=col,
               label=lab)
    ax.set_xticks(list(x), [k.replace("Qwen ", "").replace("|", "\n").replace("conflict_p050", "+0.50") for k in keys],
                  fontsize=7)
    ax.set_ylabel("Share of assigned episodes")
    ax.set_ylim(0, 1)
    ax.legend(frameon=False, ncol=3, loc="upper right")
    ax.set_title("Optional-access experiment: discovery and violation (n per bar shown in results.json)", loc="left")
    save(fig, "fig4_discovery")


def fig5_applicability():
    p = RUN / "applicability" / "results.json"
    if not p.exists():
        return
    r = json.loads(p.read_text())
    fig, ax = plt.subplots(figsize=(8, 4))
    items = [(k, v) for k, v in r["primary_equal_subtype"].items()]
    forest(ax, items, "Evaluator applicability: C = (+0.50 − tied | IDs match) − (… | IDs differ)")
    ax.set_xlabel("Difference in violation rate (equal three-subtype weights)")
    save(fig, "fig5_applicability")


if __name__ == "__main__":
    mp = RUN / "main" / "results.json"
    if mp.exists():
        res = json.loads(mp.read_text())
        fig1(res); fig2(res); fig3(res)
    fig4_discovery(); fig5_applicability()
    print("figures ->", FIG)
