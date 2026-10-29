"""Uncertainty bounds for all-zero contrasts (display layer; AMENDMENTS.md, amendment 1, 2026-10-29).

When every block contrast in an estimate is exactly 0, the block bootstrap returns the zero-width interval
[0.000, 0.000], which reads as an exact zero. For those entries (n_blocks > 0, n_nonzero_blocks == 0) this module
adds `bound95`, a distribution-free two-sided 95% interval [-s*M, +s*M]:

  s = 1 - 0.025 ** (1 / n)   Clopper-Pearson one-sided 97.5% upper limit on the share of the n blocks whose contrast
                             is non-zero, given 0 of n observed (pooled entries use all n blocks; tasks have equal
                             block counts and equal weights, so the pooled share is the plain block share);
  M = the largest absolute block contrast the estimate can take: 1 for a single score effect
      D = y(+0.50) - y(tied); 2 for a difference of score effects (REM/ADD/PRES, factorial terms, pairwise).

Then |true mean contrast| <= s * M with 95% confidence, whatever the distribution of block contrasts. The bound is
conservative by design (it assumes nothing about how large an unseen effect could be per block).

Point estimates, p-values and every non-degenerate interval are unchanged. The frozen pa_analysis.py and
pa_figures.py are not modified (their hashes are in the freeze manifests); this module re-renders their outputs.

  python pa_bounds.py main   -> run/main/REPORT_auto.md, run/main/bounds.json, figure/part2_components.{png,svg}
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import pa_analysis as A  # noqa: E402
from pa_common import PRIMARY_MODEL, RUN, TASKS  # noqa: E402

ALPHA_SIDE = 0.025
MARK = "†"
_orig_fmt_e = A.fmt_e

FOOTNOTE = (f"{MARK} No block showed any difference in this contrast (all n block contrasts exactly 0), so the "
            "bootstrap interval is degenerate. The bracket shown instead is a distribution-free 95% bound "
            "[-s·M, +s·M]: s = 1 − 0.025^(1/n) is the Clopper–Pearson upper limit on the share of blocks that "
            "could differ given 0 of n did, and M is the largest possible per-block contrast (1 for a single score "
            "effect, 2 for a difference of score effects). It is conservative; effects larger than the bound are "
            "ruled out, smaller ones are not. Source: `pa_bounds.py` (amendment 1).")


def scale(key: str) -> int:
    return 1 if key.startswith("score effect") or key.startswith("D(") else 2


def bound_for(r: dict, key: str) -> list[float] | None:
    n, nz = r.get("n_blocks"), r.get("n_nonzero_blocks")
    if not n or nz != 0 or "estimate" not in r:
        return None
    s = 1 - ALPHA_SIDE ** (1 / n)
    m = scale(key)
    return [-s * m, s * m]


def add_bounds(obj, path=()) -> list[dict]:
    """Walk a results dict; attach bound95 (+ bound_n, bound_M) to degenerate entries. Returns a flat log."""
    log = []
    if isinstance(obj, dict):
        if "estimate" in obj and "ci95" in obj:
            key = path[-1] if path else ""
            b = bound_for(obj, key)
            if b:
                obj["bound95"], obj["bound_n"], obj["bound_M"] = b, obj["n_blocks"], scale(key)
                log.append(dict(path="/".join(map(str, path)), n=obj["n_blocks"], M=scale(key), bound95=b))
        for k, v in obj.items():
            if isinstance(v, (dict, list)):
                log += add_bounds(v, path + (k,))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            log += add_bounds(v, path + (i,))
    return log


def fmt_e(r: dict) -> str:
    if "bound95" in r:
        lo, hi = r["bound95"]
        return f"{r['estimate']:+.3f} [{lo:+.3f}, {hi:+.3f}]{MARK}"
    return _orig_fmt_e(r)


def interval(r: dict) -> tuple[list[float], bool]:
    return (r["bound95"], True) if "bound95" in r else (r["ci95"], False)


def fig_part2(res: dict, out: Path):
    """pa_figures.fig_part2 with bound95 drawn dashed where the bootstrap interval is degenerate."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from pa_figures import INK, MUTED, TASK_COLOR, TITLES, _style
    from pa_render import COMPONENTS, NAMES
    dash = (0, (2.2, 1.6))
    pooled = res["primary"]["part2"]
    per = res["secondary"][PRIMARY_MODEL]
    fig, axes = plt.subplots(1, 2, figsize=(9, 4.2), sharey=True)
    for ax, kind in zip(axes, ("REM", "ADD")):
        for i, k in enumerate(COMPONENTS):
            y = len(COMPONENTS) - 1 - i
            name = f"{kind}:{k}"
            if name not in pooled:
                ax.text(0, y, "n/a (endpoint)", fontsize=7, color=MUTED, va="center", ha="center")
                continue
            for j, t in enumerate(t for t in TASKS if t in per):
                r = per[t].get(f"{name} (task)")
                if r and not math.isnan(r["estimate"]):
                    yy = y + 0.22 - 0.15 * j
                    (lo, hi), b = interval(r)
                    ax.plot([lo, hi], [yy, yy], color=TASK_COLOR[t], lw=1.2, ls=dash if b else "-")
                    ax.plot(r["estimate"], yy, "o", color=TASK_COLOR[t], ms=4,
                            label=TITLES[t] if (i == 0 and kind == "REM") else None)
            r = pooled[name]
            if not math.isnan(r["estimate"]):
                yy = y - 0.28
                (lo, hi), b = interval(r)
                ax.plot([lo, hi], [yy, yy], color=INK, lw=1.6, ls=dash if b else "-")
                ax.plot(r["estimate"], yy, "D", color=INK, mfc=INK if r["p_holm"] < 0.05 else "white", ms=6,
                        label="pooled (send + titles); filled = Holm p<0.05" if (i == 0 and kind == "REM") else None)
        ax.axvline(0, color=MUTED, lw=0.8)
        ax.set_yticks(range(len(COMPONENTS)), [f"({k}) {NAMES[k]}" for k in COMPONENTS][::-1], fontsize=7.5)
        ax.set_title("Removal from the bundle: D(B) − D(B−k)" if kind == "REM" else
                     "Addition to the new presentation: D(N+k) − D(N)", fontsize=9, color=INK)
        ax.set_xlabel("change in the +0.50 − tied score effect", fontsize=8, color=INK)
        _style(ax)
        ax.grid(axis="x", color="#e6e5e0", lw=0.6)
    fig.tight_layout()
    h, lab = axes[0].get_legend_handles_labels()
    fig.legend(h, lab, fontsize=7, frameon=False, loc="upper center", ncol=4, bbox_to_anchor=(0.5, 0.0))
    fig.text(0.5, -0.07, "Solid: 95% block-bootstrap CI. Dashed: no block differed at all; conservative "
             "distribution-free 95% bound (see report footnote).", ha="center", fontsize=7, color=MUTED)
    for ext in ("png", "svg"):
        fig.savefig(out / f"part2_components.{ext}", dpi=170, bbox_inches="tight")
    plt.close(fig)


def render_main(root: Path, fig_out: Path) -> list[dict]:
    res = json.loads((root / "main" / "results.json").read_text())
    rows = A.load_rows("main", root)
    log = add_bounds(res)
    A.fmt_e = fmt_e
    try:
        md = A.report(res, rows)
    finally:
        A.fmt_e = _orig_fmt_e
    md = md.replace("(frozen analysis)", "(frozen analysis; degenerate intervals bounded by pa_bounds.py)", 1)
    (root / "main" / "REPORT_auto.md").write_text(md.rstrip("\n") + "\n\n" + FOOTNOTE + "\n")
    (root / "main" / "bounds.json").write_text(json.dumps(dict(rule=__doc__.split("\n\n")[1], entries=log),
                                                          indent=1) + "\n")
    fig_out.mkdir(parents=True, exist_ok=True)
    fig_part2(res, fig_out)
    return log


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("stage", choices=["main"])
    ap.add_argument("--root", default=str(RUN))
    ap.add_argument("--out", default=str(HERE / "figure"))
    a = ap.parse_args()
    log = render_main(Path(a.root), Path(a.out))
    print(f"{len(log)} degenerate entries bounded; e.g.",
          *[f"{e['path']} n={e['n']} M={e['M']} ±{e['bound95'][1]:.3f}" for e in log[:3]], sep="\n  ")


if __name__ == "__main__":
    main()
