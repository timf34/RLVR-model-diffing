"""Stage 3 factorial analysis (pre-specified in ADDENDUM_factorial.md, written before generation).

  python pa_factorial.py [--root DIR]  -> <root>/factorial/results.json, REPORT_auto.md, ../figure/factorial_cells.*

Factors a, c, d coded +1 at the bundle level (B) and -1 at the new level (N); others at B. Block value of term S =
(1/4) * sum over the 8 cells of sign_S(cell) * D(b, cell). Primary: Qwen 3.8, pooled send + titles, Holm over 7.
"""
from __future__ import annotations

import argparse
import itertools
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from pa_analysis import Data, holm, load_rows, strata_values, summarise, wilson  # noqa: E402
from pa_bounds import FOOTNOTE, add_bounds, fmt_e, interval  # noqa: E402  (amendment 1: bounds for all-zero contrasts)
from pa_common import MODELS, PRIMARY_MODEL, PRIMARY_TASKS, RUN, TASKS  # noqa: E402

FACTORS = ("a", "c", "d")
CELLS = ["F:" + "".join(f"{f}{lv}" for f, lv in zip(FACTORS, lvls)) for lvls in itertools.product("BN", repeat=3)]
TERMS = [s for r in (1, 2, 3) for s in itertools.combinations(FACTORS, r)]
TERM_NAMES = {s: "x".join(s) for s in TERMS}


def code(cell: str, f: str) -> int:
    return 1 if cell[cell.index(f) + 1] == "B" else -1


def term_fn(D: Data, t: str, m: str, s: tuple):
    def fn(b):
        vals = [D.D(t, b, c, m) for c in CELLS]
        if any(v is None for v in vals):
            return None
        return sum(np.prod([code(c, f) for f in s]) * v for c, v in zip(CELLS, vals)) / 4.0
    return fn


def pair_fn(D: Data, t: str, m: str, c1: str, c2: str):
    def fn(b):
        x, y = D.D(t, b, c1, m), D.D(t, b, c2, m)
        return None if x is None or y is None else x - y
    return fn


def family(D: Data, tasks, m, seed: int) -> dict:
    rng = np.random.default_rng(seed)
    res = {TERM_NAMES[s]: summarise(TERM_NAMES[s], strata_values(D, [(t, "fresh", 1.0, term_fn(D, t, m, s))
                                                                    for t in tasks]), rng) for s in TERMS}
    return holm(res)


def descriptive(D: Data, tasks, m, seed: int) -> dict:
    rng = np.random.default_rng(seed)
    out = {}
    for c in CELLS:
        out[f"D({c})"] = summarise(c, strata_values(D, [(t, "fresh", 1.0, (lambda t: lambda b: D.D(t, b, c, m))(t))
                                                        for t in tasks]), rng)
    allN = "F:aNcNdN"
    for c in ("F:aBcNdN", "F:aNcBdN", "F:aNcNdB"):
        out[f"suff {c} - {allN}"] = summarise(c, strata_values(D, [(t, "fresh", 1.0, pair_fn(D, t, m, c, allN))
                                                                   for t in tasks]), rng)
    full = "F:aBcBdB"
    for f in FACTORS:
        c2 = "F:" + "".join(f"{g}{'N' if g == f else 'B'}" for g in FACTORS)
        out[f"REM:{f} (rerun)"] = summarise(f, strata_values(D, [(t, "fresh", 1.0, pair_fn(D, t, m, full, c2))
                                                                 for t in tasks]), rng)
    return out


def analyse(rows: list[dict], seed: int = 23) -> dict:
    D = Data(rows)
    res = dict(primary=family(D, PRIMARY_TASKS, PRIMARY_MODEL, seed),
               descriptive_primary=descriptive(D, PRIMARY_TASKS, PRIMARY_MODEL, seed + 1),
               per_task={t: dict(terms=family(D, [t], PRIMARY_MODEL, seed + 2 + i),
                                 desc=descriptive(D, [t], PRIMARY_MODEL, seed + 20 + i))
                         for i, t in enumerate(D.tasks)},
               all_tasks=family(D, D.tasks, PRIMARY_MODEL, seed + 40))
    other = [m for m in MODELS if m != PRIMARY_MODEL]
    res["other_models"] = {m: dict(terms=family(D, PRIMARY_TASKS, m, seed + 50),
                                   desc=descriptive(D, PRIMARY_TASKS, m, seed + 51)) for m in other}
    cells = []
    for (t, mat, arm, sc, m), (k, n) in sorted(D.cells.items()):
        lo, hi = wilson(k, n)
        cells.append(dict(task=t, arm=arm, score=sc, model=m, k=k, n=n, rate=k / n if n else float("nan"),
                          lo=lo, hi=hi))
    res["cells"] = cells
    res["nonvalid"] = {"|".join(map(str, k)): v for k, v in D.nonvalid.items()}
    res["n_rows"] = len(rows)
    res["bounded"] = add_bounds(res)
    return res


def table(rs: dict, holm_col=True) -> list[str]:
    out = ["| term | estimate [95% CI] | p |" + (" Holm p |" if holm_col else "") + " blocks |",
           "|---|---|---|" + ("---|" if holm_col else "") + "---|"]
    for k, r in rs.items():
        out.append(f"| {k} | {fmt_e(r)} | {r['p']:.4f} |" + (f" {r['p_holm']:.4f} |" if holm_col else "")
                   + f" {r['n_blocks']} |")
    return out


def report(res: dict) -> str:
    L = ["# Presentation ablation: Stage 3 factorial (a x c x d), auto tables", "",
         "Pre-specified in `ADDENDUM_factorial.md`. Effects are on the +0.50 - tied score effect D; factor coded "
         "+1 at bundle level, -1 at new level; main effect = mean D(at B) - mean D(at N).", "",
         f"## Primary: Qwen 3.8, send + titles pooled (Holm over 7)", ""]
    L += table(res["primary"])
    L += ["", "## Cell score effects and sufficiency (Qwen 3.8, send + titles, descriptive)", ""]
    L += table(res["descriptive_primary"], holm_col=False)
    for t, v in res["per_task"].items():
        L += ["", f"## {t} (Qwen 3.8; Holm within task)", ""] + table(v["terms"])
        L += [""] + table(v["desc"], holm_col=False)
    L += ["", "## All three tasks pooled (Qwen 3.8, secondary)", ""] + table(res["all_tasks"])
    for m, v in res["other_models"].items():
        L += ["", f"## {m} (descriptive)", ""] + table(v["terms"], holm_col=False)
        L += [""] + table(v["desc"], holm_col=False)
    L += ["", "## Cell rates (k/n valid, Wilson 95%)", "", "| task | cell | score | model | k/n | rate | 95% |",
          "|---|---|---|---|---|---|---|"]
    for c in res["cells"]:
        L.append(f"| {c['task']} | {c['arm']} | {c['score']} | {c['model']} | {c['k']}/{c['n']} | {c['rate']:.2f} | "
                 f"{c['lo']:.2f}-{c['hi']:.2f} |")
    L += ["", f"Non-valid: {res['nonvalid'] or 'none'}. Rows: {res['n_rows']}.", "", FOOTNOTE]
    return "\n".join(L) + "\n"


def figure(res: dict, out: Path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    colors = {"send": "#2a78d6", "titles": "#eb6834", "bullets": "#1baf7a"}
    labels = {"send": "Sending", "titles": "Titles / sign-offs", "bullets": "Bullets"}
    fig, ax = plt.subplots(figsize=(9, 4.6))
    order = sorted(CELLS, key=lambda c: (-sum(code(c, f) for f in FACTORS), c))
    for i, t in enumerate(res["per_task"]):
        d = res["per_task"][t]["desc"]
        xs = np.arange(len(order)) + (i - 1) * 0.22
        ys = [d[f"D({c})"]["estimate"] for c in order]
        for x, c, yv in zip(xs, order, ys):
            (lo, hi), b = interval(d[f"D({c})"])
            ax.plot([x, x], [lo, hi], color=colors[t], lw=1.6, ls=(0, (2.2, 1.6)) if b else "-")
        ax.plot(xs, ys, "o", color=colors[t], ms=6, ls="none", label=labels[t])
    ax.set_xticks(range(len(order)))
    ax.set_xticklabels([" ".join(f"{f}:{'old' if code(c, f) > 0 else 'new'}" for f in FACTORS) for c in order],
                       rotation=25, ha="right", fontsize=8.5)
    ax.axhline(0, color="#555", lw=0.8)
    ax.set_ylabel("score effect (+0.50 − tied), Qwen 3.8")
    ax.set_title("Factorial over (a) scorer applies now, (c) old request wording, (d) scores inline", fontsize=10)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.grid(axis="y", color="#e6e6e6", lw=0.8)
    ax.legend(frameon=False, fontsize=8.5, loc="upper left", bbox_to_anchor=(1.0, 1.0))
    fig.text(0.5, 0.005, "Solid: 95% block-bootstrap CI. Dashed: no block differed; conservative 95% bound (report footnote).",
             ha="center", fontsize=7, color="#6b6a64")
    fig.tight_layout()
    out.parent.mkdir(parents=True, exist_ok=True)
    for ext in ("png", "svg"):
        fig.savefig(out.with_suffix("." + ext), dpi=160, bbox_inches="tight")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=str(RUN))
    a = ap.parse_args()
    root = Path(a.root)
    rows = load_rows("factorial", root)
    res = analyse(rows)
    (root / "factorial" / "results.json").write_text(json.dumps(res, indent=1, default=float))
    (root / "factorial" / "REPORT_auto.md").write_text(report(res))
    figure(res, HERE / "figure" / "factorial_cells")
    for k, r in res["primary"].items():
        print(f"{k:6s} {fmt_e(r):32s} Holm p {r['p_holm']:.4f}")


if __name__ == "__main__":
    main()
