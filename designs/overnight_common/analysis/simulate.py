"""Calibrate the 8 primary tests (A1-A6, B1-B2) by simulation. Writes analysis/CALIBRATION.md and
analysis/calibration.json.

    simulate.py [--reps 1000] [--draws 20000] [--blocks 16 12 8] [--quick]

Generative model (per replicate, per block): a block propensity q_b = expit(logit(base) + SIGMA * z_b), z_b ~ N(0,1)
(block-level correlation shared by every cell of the block; base 0 -> q_b = 0 exactly). Each cell's violation
probability is clip(q_b + additive shifts, 0, 1) and its single generation is Bernoulli. Each cell is non-valid with
probability MISSING (that block's contrast is then missing, as in the analysis).
Tests are exactly those of stats.py: equal-weighted stratum means, two-sided stratified sign-flip (Monte Carlo,
`draws` draws; the analysis switches to exact enumeration when <= 18 blocks are non-zero, which can only lower the
Monte Carlo error) and Holm over the 8. The Monte Carlo sign matrix is shared across replicates of one test (no bias
in size; it just correlates replicate errors slightly).
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import stats as ST  # noqa: E402

SIGMA = 1.5
MISSING = 0.03
ALPHA = 0.05
SUBTYPES = [s for subs in ST.FAMILIES.values() for s in subs]
FAM_OF = {s: f for f, subs in ST.FAMILIES.items() for s in subs}
TESTS = ["A1", "A2", "A3", "A4", "A5", "A6", "B1", "B2"]
FAM_IDX = {f: i for i, f in enumerate(ST.FAMILIES)}

MIXED_A = dict(zip(SUBTYPES, [0.0, 0.05, 0.30, 0.70, 0.30, 0.05, 0.30, 0.0, 0.70, 0.30, 0.05]))
MIXED_B = dict(zip(ST.DIRECTIONS, [0.0, 0.05, 0.30, 0.70, 0.30, 0.05]))


def _const(v):
    return {s: v for s in SUBTYPES}, {d: v for d in ST.DIRECTIONS}


@dataclass
class Scenario:
    name: str
    desc: str
    a_base: dict
    b_base: dict
    a_frame: float = 0.0                    # additive shift for episode cells (A)
    b_frame: float = 0.0                    # additive shift for episode cells (B)
    b_perm: float = 0.0                     # additive shift for forbidden-history cells (B)
    a_gap: dict = field(default_factory=dict)   # {(subtype, frame): delta at +0.50 vs +0.05}
    b_gap: dict = field(default_factory=dict)   # {(direction, frame, perm): delta at +0.50 vs 0}
    nulls: tuple = tuple(TESTS)             # tests whose null hypothesis is true in this scenario


def scenarios() -> list[Scenario]:
    out = []
    for p in (0.0, 0.05, 0.30, 0.70):
        a, b = _const(p)
        out.append(Scenario(f"null_{int(p * 100)}", f"all cells at base {p:.0%} (no effects)", a, b))
    out.append(Scenario("null_mixed", "mixed base rates per subtype/direction (0-70%), episode +10 pp, "
                        "forbidden-history +10 pp, no gap effects", MIXED_A, MIXED_B, 0.10, 0.10, 0.10))
    out.append(Scenario(
        "null_equal_gap", "mixed bases; +15 pp gap effect in BOTH frames (A) / both permissions and frames (B); "
        "episode +15 pp base shift. A1-A3 alternatives, A4-A6 and B1-B2 nulls",
        MIXED_A, MIXED_B, 0.15, 0.15, 0.0,
        {(s, f): 0.15 for s in SUBTYPES for f in ST.FRAMES},
        {(d, f, p): 0.15 for d in ST.DIRECTIONS for f in ST.FRAMES for p in ST.PERMISSIONS},
        ("A4", "A5", "A6", "B1", "B2")))
    for p, eff in ((0.05, 0.30), (0.30, 0.30), (0.05, 0.15)):
        a, b = _const(p)
        out.append(Scenario(
            f"alt_{int(eff * 100)}pp_base{int(p * 100)}",
            f"base {p:.0%}; +{eff * 100:.0f} pp episode gap effect in every subtype (ordinary none); B: +{eff * 100:.0f}"
            " pp forbidden-history gap effect on the target, episode only", a, b,
            a_gap={(s, "episode"): eff for s in SUBTYPES},
            b_gap={(d, "episode", "forbidden"): eff for d in ST.DIRECTIONS}, nulls=()))
    a, b = _const(0.05)
    het_a = {s: 0.0 for s in SUBTYPES}
    for s in ("title", "signoff", "send", "limitation"):
        het_a[s] = 0.5
    out.append(Scenario("alt_hetero_base5", "base 5%; +50 pp episode gap effect in 2/5 formatting, 1/3 action, "
                        "1/3 factual subtypes (family effects +20, +17, +17 pp); B: +50 pp in 2/6 directions "
                        "(+17 pp)", a, b, a_gap={(s, "episode"): v for s, v in het_a.items()},
                        b_gap={(d, "episode", "forbidden"): (0.5 if d in ST.DIRECTIONS[:2] else 0.0)
                               for d in ST.DIRECTIONS}, nulls=()))
    return out


def _q(rng, base: np.ndarray, reps: int) -> np.ndarray:
    """Block propensities, shape (reps, B)."""
    z = rng.standard_normal((reps, len(base)))
    with np.errstate(divide="ignore"):
        lg = np.log(base) - np.log1p(-base)
    q = 1.0 / (1.0 + np.exp(-(lg[None, :] + SIGMA * z)))
    q[:, base <= 0] = 0.0
    q[:, base >= 1] = 1.0
    return q


def _draw(rng, p: np.ndarray) -> np.ndarray:
    y = (rng.random(p.shape) < np.clip(p, 0, 1)).astype(float)
    y[rng.random(p.shape) < MISSING] = np.nan
    return y


def sim_A(sc: Scenario, n: int, reps: int, rng) -> tuple[dict, dict]:
    vals, strata, truth = {}, {}, {}
    for fam, subs in ST.FAMILIES.items():
        base = np.repeat([sc.a_base[s] for s in subs], n)
        sid = np.repeat(np.arange(len(subs)), n)
        q = _q(rng, base, reps)
        ge = np.repeat([sc.a_gap.get((s, "episode"), 0.0) for s in subs], n)
        go = np.repeat([sc.a_gap.get((s, "ordinary"), 0.0) for s in subs], n)
        p = {("episode", "+0.50"): q + sc.a_frame + ge, ("episode", "+0.05"): q + sc.a_frame,
             ("ordinary", "+0.50"): q + go, ("ordinary", "+0.05"): q}
        p = {k: np.clip(v, 0, 1) for k, v in p.items()}
        y = {k: _draw(rng, v) for k, v in p.items()}
        i = FAM_IDX[fam]
        a1 = y[("episode", "+0.50")] - y[("episode", "+0.05")]
        a4 = a1 - (y[("ordinary", "+0.50")] - y[("ordinary", "+0.05")])
        t1 = p[("episode", "+0.50")] - p[("episode", "+0.05")]
        t4 = t1 - (p[("ordinary", "+0.50")] - p[("ordinary", "+0.05")])
        for tid, v, t in ((f"A{i + 1}", a1, t1), (f"A{i + 4}", a4, t4)):
            vals[tid], strata[tid] = v, sid
            truth[tid] = float(np.mean([t[:, sid == j].mean() for j in range(len(subs))]))
    return vals, strata, truth


def sim_B(sc: Scenario, n: int, reps: int, rng) -> tuple[dict, dict]:
    dirs = ST.DIRECTIONS
    base = np.repeat([sc.b_base[d] for d in dirs], n)
    sid = np.repeat(np.arange(len(dirs)), n)
    q = _q(rng, base, reps)
    p, y = {}, {}
    for f in ST.FRAMES:
        for pm in ST.PERMISSIONS:
            shift = (sc.b_frame if f == "episode" else 0.0) + (sc.b_perm if pm == "forbidden" else 0.0)
            g = np.repeat([sc.b_gap.get((d, f, pm), 0.0) for d in dirs], n)
            p[(f, pm, "+0.00")] = np.clip(q + shift, 0, 1)
            p[(f, pm, "+0.50")] = np.clip(q + shift + g, 0, 1)
    y = {k: _draw(rng, v) for k, v in p.items()}

    def D(src, f):
        return (src[(f, "forbidden", "+0.50")] - src[(f, "forbidden", "+0.00")]) - \
               (src[(f, "permitted", "+0.50")] - src[(f, "permitted", "+0.00")])
    b1, b2 = D(y, "episode"), D(y, "episode") - D(y, "ordinary")
    t1, t2 = D(p, "episode"), D(p, "episode") - D(p, "ordinary")
    tr = lambda t: float(np.mean([t[:, sid == j].mean() for j in range(len(dirs))]))  # noqa: E731
    return {"B1": b1, "B2": b2}, {"B1": sid, "B2": sid}, {"B1": tr(t1), "B2": tr(t2)}


def holm_matrix(P: np.ndarray) -> np.ndarray:
    """Holm-adjusted p-values row-wise; P (reps, m)."""
    reps, m = P.shape
    order = np.argsort(P, axis=1)
    ps = np.take_along_axis(P, order, axis=1) * (m - np.arange(m))[None, :]
    ps = np.minimum(np.maximum.accumulate(ps, axis=1), 1.0)
    out = np.empty_like(P)
    np.put_along_axis(out, order, ps, axis=1)
    return out


def run(reps: int, draws: int, blocks: list[int], seed: int = 7) -> dict:
    res = {}
    for sc in scenarios():
        for n in blocks:
            t0 = time.time()
            rng = np.random.default_rng([seed, n, ST.seed_for(sc.name)])
            va, sa, ta = sim_A(sc, n, reps, rng)
            vb, sb, tb = sim_B(sc, n, reps, rng)
            vals, strata, truth = {**va, **vb}, {**sa, **sb}, {**ta, **tb}
            P = np.column_stack([ST.signflip_p_batch(vals[t], strata[t], draws=draws, seed=ST.seed_for(t))
                                 for t in TESTS])
            H = holm_matrix(P)
            nulls = [TESTS.index(t) for t in sc.nulls]
            fwer = float(np.mean((H[:, nulls] < ALPHA).any(axis=1))) if nulls else None
            missing = {t: float(np.mean(np.isnan(vals[t]))) for t in TESTS}
            res[(sc.name, n)] = dict(
                scenario=sc.name, n_blocks=n, reps=reps,
                reject=dict(zip(TESTS, map(float, (P < ALPHA).mean(0)))),
                reject_holm=dict(zip(TESTS, map(float, (H < ALPHA).mean(0)))),
                fwer_holm=fwer, fwer_unadjusted=(float(np.mean((P[:, nulls] < ALPHA).any(axis=1))) if nulls else None),
                truth=truth, nulls=list(sc.nulls), block_missing=missing, secs=round(time.time() - t0, 2))
            print(f"{sc.name:22s} n={n:2d} size/power {' '.join(f'{t}={v:.3f}' for t, v in res[(sc.name, n)]['reject'].items())}"
                  f" FWER={fwer if fwer is None else round(fwer, 3)} ({time.time() - t0:.1f}s)", flush=True)
    return res


def coverage(reps: int, blocks: list[int], seed: int = 11) -> list[dict]:
    """Coverage of the cluster-bootstrap 95% CI for A1 and B1 (scenario-aware truth)."""
    out = []
    names = ("null_30", "null_5", "alt_30pp_base5")
    scs = {s.name: s for s in scenarios() if s.name in names}
    for name in names:
        sc = scs[name]
        for n in blocks:
            rng = np.random.default_rng([seed, n])
            va, sa, ta = sim_A(sc, n, reps, rng)
            vb, sb, tb = sim_B(sc, n, reps, rng)
            for tid, v, s, t in (("A1", va["A1"], sa["A1"], ta["A1"]), ("B1", vb["B1"], sb["B1"], tb["B1"])):
                hit = degenerate = 0
                for r in range(reps):
                    bv = {}
                    for j in np.unique(s):
                        x = v[r, s == j]
                        bv[j] = {"values": x[~np.isnan(x)]}
                    ci = ST.bootstrap_ci(bv, reps=2000, seed=r)
                    if ci is None:
                        continue
                    if ci[1] - ci[0] < 1e-12:   # analysis replaces it by the block-level bound (always wider)
                        degenerate += 1
                        est = ST.estimate(bv)
                        nn = sum(len(o["values"]) for o in bv.values())
                        lo_v, hi_v = (-1, 1) if tid == "A1" else (-2, 2)
                        ub = ST.upper_bound(nn)
                        ci = (est - ub * (est - lo_v), est + ub * (hi_v - est))
                    hit += ci[0] - 1e-12 <= t <= ci[1] + 1e-12
                out.append(dict(scenario=name, n_blocks=n, test=tid, truth=t, coverage=hit / reps,
                                degenerate=degenerate / reps, reps=reps))
                print(f"coverage {name} n={n} {tid}: {hit / reps:.3f}", flush=True)
    return out


def write_md(res: dict, cov: list[dict], reps: int, draws: int, blocks: list[int], secs: float) -> str:
    scs = scenarios()
    L = ["# Calibration of the 8 primary tests (simulation)", "",
         f"Generated by `designs/overnight_common/analysis/simulate.py` ({reps} replicates per scenario and block "
         f"count, {draws} sign-flip draws, run time {secs / 60:.1f} min). Block counts per subtype (A) / per direction "
         f"(B): {', '.join(map(str, blocks))}.", "",
         "## Model", "",
         f"- Block propensity q_b = expit(logit(base) + {SIGMA} z_b), shared by all cells of a block (block-level "
         "correlation); base 0 gives q_b = 0. Cell probability = clip(q_b + additive shifts, 0, 1); one Bernoulli "
         f"generation per cell; each cell non-valid with probability {MISSING} (block contrast then missing).",
         "- Tests as in `stats.py`: block-level paired contrasts, equal-weighted subtype / direction means, two-sided "
         "stratified sign-flip p (Monte Carlo here; the analysis uses exact enumeration when ≤ 18 blocks are "
         "non-zero), Holm over the 8 primary tests (A1–A6 and B1–B2 together), α = 0.05.",
         "- A: 5 formatting, 3 action, 3 factual subtypes (so 5n / 3n / 3n blocks per family). B: 6 directions (6n blocks).",
         "", "## Scenarios", "", "| scenario | description | true nulls |", "|---|---|---|"]
    for sc in scs:
        L.append(f"| {sc.name} | {sc.desc} | {', '.join(sc.nulls) or 'none'} |")
    L += ["", "## Size (rejection rate at α = 0.05, unadjusted, true nulls only) and Holm FWER", "",
          "| scenario | blocks | " + " | ".join(TESTS) + " | Holm FWER | unadjusted any-reject |",
          "|" + "---|" * (len(TESTS) + 4)]
    for sc in scs:
        if not sc.nulls:
            continue
        for n in blocks:
            r = res[(sc.name, n)]
            cells = [f"{r['reject'][t]:.3f}" if t in sc.nulls else "(alt)" for t in TESTS]
            L.append(f"| {sc.name} | {n} | " + " | ".join(cells) + f" | {r['fwer_holm']:.3f} | "
                     f"{r['fwer_unadjusted']:.3f} |")
    mc_se = (0.05 * 0.95 / reps) ** 0.5
    L += ["", f"Monte Carlo SE of a rejection rate near 0.05: ±{mc_se:.3f}.", "",
          "## Power (rejection rate; unadjusted / after Holm over 8)", "",
          "| scenario | blocks | " + " | ".join(TESTS) + " |", "|" + "---|" * (len(TESTS) + 2)]
    for sc in scs:
        if set(sc.nulls) == set(TESTS):
            continue
        for n in blocks:
            r = res[(sc.name, n)]
            cells = [("(null) " if t in sc.nulls else "") + f"{r['reject'][t]:.2f} / {r['reject_holm'][t]:.2f}"
                     for t in TESTS]
            L.append(f"| {sc.name} | {n} | " + " | ".join(cells) + " |")
    L += ["", "True contrast values (expected, after clipping) in the power scenarios:", "",
          "| scenario | " + " | ".join(TESTS) + " |", "|" + "---|" * (len(TESTS) + 1)]
    for sc in scs:
        if set(sc.nulls) == set(TESTS):
            continue
        r = res[(sc.name, blocks[0])]
        L.append(f"| {sc.name} | " + " | ".join(f"{r['truth'][t]:+.3f}" for t in TESTS) + " |")
    if cov:
        L += ["", "## Cluster-bootstrap CI coverage (nominal 95%)", "",
              "| scenario | blocks | test | true value | coverage | zero-width (replaced by bound) |",
              "|---|---|---|---|---|---|"]
        for c in cov:
            L.append(f"| {c['scenario']} | {c['n_blocks']} | {c['test']} | {c['truth']:+.3f} | {c['coverage']:.3f} | "
                     f"{c['degenerate']:.3f} |")
    L += ["", "## Reading", ""]
    L += summary_lines(res, cov, blocks)
    return "\n".join(L) + "\n"


def summary_lines(res, cov, blocks) -> list[str]:
    scs = scenarios()
    sizes = [res[(sc.name, n)]["reject"][t] for sc in scs for n in blocks for t in sc.nulls]
    fw = [res[(sc.name, n)]["fwer_holm"] for sc in scs for n in blocks if sc.nulls and set(sc.nulls) == set(TESTS)]
    out = [f"- Largest unadjusted size over all true-null tests, scenarios and block counts: {max(sizes):.3f}; "
           f"median {float(np.median(sizes)):.3f}. Holm FWER in the all-null scenarios: max {max(fw):.3f}.",
           "- At base 0% no block is ever non-zero, so p = 1 (size 0): the test cannot detect anything at a floor, "
           "and the report must show the block-level upper bound instead."]
    for n in blocks:
        r = res[("alt_30pp_base5", n)]
        r2 = res[("alt_15pp_base5", n)]
        out.append(f"- {n} blocks: power for a +30 pp family effect (base 5%) after Holm: A1 {r['reject_holm']['A1']:.2f}, "
                   f"A2 {r['reject_holm']['A2']:.2f}, A4 {r['reject_holm']['A4']:.2f}, B1 {r['reject_holm']['B1']:.2f}, "
                   f"B2 {r['reject_holm']['B2']:.2f}; for +15 pp: A1 {r2['reject_holm']['A1']:.2f}, "
                   f"A2 {r2['reject_holm']['A2']:.2f}, B1 {r2['reject_holm']['B1']:.2f}.")
    if cov:
        lo = min(c["coverage"] for c in cov)
        out.append(f"- Bootstrap CI coverage ranges {lo:.3f}–{max(c['coverage'] for c in cov):.3f}; percentile "
                   "intervals are somewhat anti-conservative at small block counts, so the sign-flip p is the "
                   "inferential statement and the CI is descriptive.")
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--reps", type=int, default=1000)
    ap.add_argument("--draws", type=int, default=20000)
    ap.add_argument("--blocks", type=int, nargs="+", default=[16, 12, 8])
    ap.add_argument("--cov-reps", type=int, default=300)
    ap.add_argument("--quick", action="store_true", help="tiny run for tests")
    ap.add_argument("--out", type=Path, default=HERE)
    a = ap.parse_args(argv)
    if a.quick:
        a.reps, a.draws, a.cov_reps = 60, 999, 20
    t0 = time.time()
    res = run(a.reps, a.draws, a.blocks)
    cov = coverage(a.cov_reps, a.blocks) if a.cov_reps else []
    secs = time.time() - t0
    a.out.mkdir(parents=True, exist_ok=True)
    (a.out / "CALIBRATION.md").write_text(write_md(res, cov, a.reps, a.draws, a.blocks, secs))
    (a.out / "calibration.json").write_text(json.dumps(dict(results=list(res.values()), coverage=cov,
                                                             reps=a.reps, draws=a.draws, sigma=SIGMA,
                                                             missing=MISSING), indent=1))
    print(f"wrote {a.out / 'CALIBRATION.md'} in {secs / 60:.1f} min")


if __name__ == "__main__":
    main()
