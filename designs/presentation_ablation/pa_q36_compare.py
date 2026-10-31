"""Three-model comparison (Qwen 3.5 -> 3.6 -> 3.8) for the presentation ablation. Descriptive, not part of the frozen
analysis. Qwen 3.5 / 3.8 rows come from run/, Qwen 3.6 rows from run_q36/ (same prompts as 3.5, see pa_q36.py).

  python pa_q36_compare.py      # -> run_q36/compare.json, run_q36/COMPARE.md, figure/q36_slope.{png,svg}

Score effect = rate of the user-conflicting outcome at +0.50 minus at tied scores, per block, averaged over blocks
(original and fresh blocks weighted equally in Part 1). CIs: block bootstrap (pa_analysis.boot_ci).
Strong RL framing = old bundle (B); weak RL framing = new presentation (N).
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from pa_analysis import ADD, REM, Data, boot_ci, comp_strata, est, load_rows, part1_strata, strata_values  # noqa: E402
from pa_render import NAMES  # noqa: E402
from pa_common import RUN, TASKS  # noqa: E402

Q36 = HERE / "run_q36"
FIG = HERE / "figure"
MODELS = ("Qwen 3.5", "Qwen 3.6", "Qwen 3.8")
TASK_NAME = {"send": "Sending the email", "titles": "Title + sign-off", "bullets": "Bullet points"}
FEATS = "acd"


def rows(stage):
    r = [x for x in load_rows(stage, RUN) if x["model"] != "Qwen 3.6"]
    return r + load_rows(stage, Q36)


def summ(sv, rng):
    if not sv:
        return None
    lo, hi = boot_ci(sv, rng)
    return dict(estimate=est(sv), ci95=[lo, hi], n_blocks=int(sum(len(v) for _, v in sv)))


def cell(D, t, mats, arm, m):
    return [(t, mat, 1.0, (lambda b, t=t, arm=arm: D.D(t, b, arm, m))) for mat in mats]


def compare():
    rng = np.random.default_rng(7)
    out = dict(part1={}, factorial={}, n_valid={})
    D = Data(rows("main"))
    for m in MODELS:
        for t in TASKS:
            for arm in ("B", "N"):
                out["part1"][f"{m}|{t}|{arm}"] = summ(strata_values(D, cell(D, t, ("orig", "fresh"), arm, m)), rng)
            out["part1"][f"{m}|{t}|B-N"] = summ(strata_values(D, part1_strata(D, [t], m)), rng)
        for arm in ("B", "N"):
            out["part1"][f"{m}|primary|{arm}"] = summ(strata_values(
                D, [s for t in ("send", "titles") for s in cell(D, t, ("orig", "fresh"), arm, m)]), rng)
        out["part1"][f"{m}|primary|B-N"] = summ(strata_values(D, part1_strata(D, ["send", "titles"], m)), rng)
        for name in REM + ADD:
            out.setdefault("part2", {})[f"{m}|{name}"] = summ(strata_values(D, comp_strata(D, ["send", "titles"], m,
                                                                                           name)), rng)
    for (t, mat, arm, sc, m), (k, n) in D.cells.items():
        out["n_valid"][f"main|{m}"] = out["n_valid"].get(f"main|{m}", 0) + n
    F = Data(rows("factorial"))
    arms = sorted({k[2] for k in F.cells})
    for m in MODELS:
        for arm in arms:
            on = sum(arm[arm.index(f) + 1] == "B" for f in FEATS)
            sv = strata_values(F, [s for t in ("send", "titles") for s in cell(F, t, ("fresh",), arm, m)])
            r = summ(sv, rng)
            if r:
                out["factorial"][f"{m}|{arm}"] = r | dict(n_bundle_features=on)
        for k in range(4):
            ar = [a for a in arms if sum(a[a.index(f) + 1] == "B" for f in FEATS) == k]
            sv = strata_values(F, [s for t in ("send", "titles") for a in ar for s in cell(F, t, ("fresh",), a, m)])
            r = summ(sv, rng)
            if r:
                out["factorial"][f"{m}|k={k}"] = r
    for (t, mat, arm, sc, m), (k, n) in F.cells.items():
        out["n_valid"][f"factorial|{m}"] = out["n_valid"].get(f"factorial|{m}", 0) + n
    nv = {}
    for d, stage in ((D, "main"), (F, "factorial")):
        for key, v in d.nonvalid.items():
            nv[f"{stage}|{key[4]}|{key[5]}"] = nv.get(f"{stage}|{key[4]}|{key[5]}", 0) + v
    out["nonvalid"] = nv
    return out


def pct(r):
    if r is None:
        return "–"
    e, (lo, hi) = r["estimate"], r["ci95"]
    return f"{100 * e:+.0f} [{100 * lo:+.0f}, {100 * hi:+.0f}]" if not math.isnan(e) else "–"


def report(o):
    L = ["# Qwen 3.5 → 3.6 → 3.8: presentation ablation, three models (auto)", "",
         "Score effect in points (+0.50 minus tied), block-bootstrap 95% CI. Strong RL framing = old bundle (B); weak "
         "= new presentation (N). Qwen 3.6 replays Qwen 3.5's exact items (`pa_q36.py`).", "",
         "## Part 1: strong vs weak framing", "", "| task | framing | " + " | ".join(MODELS) + " |",
         "|---|---|" + "---|" * len(MODELS)]
    for t in ("send", "titles", "bullets", "primary"):
        for arm, nm in (("B", "strong"), ("N", "weak"), ("B-N", "strong − weak")):
            L.append(f"| {TASK_NAME.get(t, 'sending + titles')} | {nm} | " +
                     " | ".join(pct(o["part1"].get(f"{m}|{t}|{arm}")) for m in MODELS) + " |")
    L += ["", "## Factorial (sending + titles): number of strong-framing features among a, c, d", "",
          "| features at strong level | " + " | ".join(MODELS) + " |", "|---|" + "---|" * len(MODELS)]
    for k in range(4):
        L.append(f"| {k} | " + " | ".join(pct(o["factorial"].get(f"{m}|k={k}")) for m in MODELS) + " |")
    L += ["", "## Part 2: one feature at a time (fresh blocks, sending + titles)", "",
          "Removal = strong minus (strong without the feature); add-back = (weak plus the feature) minus weak.", "",
          "| contrast | " + " | ".join(MODELS) + " |", "|---|" + "---|" * len(MODELS)]
    for name in REM + ADD:
        kind, k = name.split(":")
        lab = f"{'remove' if kind == 'REM' else 'add'} ({k}) {NAMES.get(k, '')}".strip()
        L.append(f"| {lab} | " + " | ".join(pct(o["part2"].get(f"{m}|{name}")) for m in MODELS) + " |")
    L += ["", "Valid episodes: " + ", ".join(f"{k} {v}" for k, v in sorted(o["n_valid"].items())),
          "", "Non-valid: " + (", ".join(f"{k} {v}" for k, v in sorted(o["nonvalid"].items())) or "none")]
    return "\n".join(L) + "\n"


def figure(o):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    INK, INK2, GRID = "#0b0b0b", "#52514e", "#e6e5e1"
    STRONG, WEAK = "#eb6834", "#9c9a92"
    plt.rcParams.update({"font.size": 10, "axes.edgecolor": INK2, "axes.labelcolor": INK, "xtick.color": INK2,
                         "ytick.color": INK2})
    fig, axes = plt.subplots(1, 4, figsize=(13, 3.6), sharey=True)
    x = np.arange(len(MODELS))
    panels = [("send", TASK_NAME["send"]), ("titles", TASK_NAME["titles"]), ("bullets", TASK_NAME["bullets"])]
    for ax, (t, title) in zip(axes[:3], panels):
        for arm, col, lab in (("B", STRONG, "strong RL framing"), ("N", WEAK, "weak RL framing")):
            rs = [o["part1"].get(f"{m}|{t}|{arm}") for m in MODELS]
            ys = [100 * r["estimate"] if r else np.nan for r in rs]
            lo = [100 * (r["estimate"] - r["ci95"][0]) if r else 0 for r in rs]
            hi = [100 * (r["ci95"][1] - r["estimate"]) if r else 0 for r in rs]
            ax.errorbar(x, ys, yerr=[lo, hi], color=col, lw=2, marker="o", ms=8, capsize=0, elinewidth=1.2,
                        label=lab)
        ax.set_title(title, color=INK, fontsize=11)
    ax = axes[3]
    shades = ["#d9d7d0", "#f4b393", "#ef8c5c", "#c4471a"]
    for k in range(4):
        rs = [o["factorial"].get(f"{m}|k={k}") for m in MODELS]
        ys = [100 * r["estimate"] if r else np.nan for r in rs]
        ax.plot(x, ys, color=shades[k], lw=2, marker="o", ms=8, label=f"{k} of 3")
        ax.annotate(f"{k}/3", (x[-1] + 0.08, ys[-1] + {0: -3, 1: 3}.get(k, 0)), color=INK2, fontsize=9,
                    va="center")
    ax.set_title("Factorial: strong features on\n(sending + titles)", color=INK, fontsize=11)
    for a in axes:
        a.set_xticks(x, [m.replace("Qwen ", "") for m in MODELS])
        a.set_xlim(-0.35, len(MODELS) - 0.5)
        a.axhline(0, color=INK2, lw=0.8)
        a.grid(axis="y", color=GRID, lw=0.8)
        a.spines[["top", "right"]].set_visible(False)
        a.set_xlabel("Qwen version")
    axes[0].set_ylabel("score effect (points)\n+0.50 minus tied")
    axes[0].legend(frameon=False, loc="upper left")
    fig.suptitle("Following the grader against the user, Qwen 3.5 → 3.6 → 3.8", color=INK, fontsize=12,
                 fontweight="bold", x=0.01, ha="left")
    fig.tight_layout()
    for ext in ("png", "svg"):
        fig.savefig(FIG / f"q36_slope.{ext}", dpi=200)


def main():
    o = compare()
    (Q36 / "compare.json").write_text(json.dumps(o, indent=1))
    (Q36 / "COMPARE.md").write_text(report(o))
    figure(o)
    print(report(o))


if __name__ == "__main__":
    main()
