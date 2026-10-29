"""Simulation calibration of the planned tests (run before freezing; writes simulation/CALIBRATION.md).
Adapted from designs/score_gap/recommendation/simulate.py to this design.

Design simulated = the frozen design: 12 scenarios x 7 gap levels, with 6 episodes per scenario x level in the
bundle panel and 2 in the ordinary panel (n = 72 and 24 per level).
Scenario heterogeneity: scenario logit offsets ~ N(0, sigma), sigma = 1.5 (large; in the action main batch,
Qwen 3.5's cell-1 rate ranged from 0/8 to 2/8 by family and Qwen 3.8's from 5/8 to 8/8).
  1. Trend test size under no gap effect, base rates 0.05 / 0.2 / 0.5, both panel sizes.
  2. Curve-comparison size when two groups share the population curve (identical and independent scenario
     effects; step and gradual curves; both panel sizes).
  3. Family-wise error with Holm: 4 trend tests (global null); the primary comparison family (3.8 vs 3.5 in
     each panel, 2 tests) and the secondary family (bundle vs ordinary per model, 2 tests) with all curves equal.
  4. Power: trend under a one-sided step and a gradual curve; comparison under a +1 logit shift and step vs
     gradual.
Run: ../../../.venv/bin/python simulate.py
"""
from pathlib import Path

import numpy as np

import gap_analysis as A

HERE = Path(__file__).parent
NS = 12
NR = {"bundle": 6, "ordinary": 2}
SIMS = 400
SIG = 1.5


def logistic(x):
    return 1 / (1 + np.exp(-x))


def logit(p):
    return np.log(p / (1 - p))


def draw(rng, curve, offsets, nr):
    return [dict(scenario=f"s{s:02d}", gap=g, y=int(rng.random() < logistic(curve(g) + offsets[s])))
            for s in range(NS) for g in A.GAPS for _ in range(nr)]


def main():
    rng = np.random.default_rng(20261028)
    flat = lambda base: (lambda g: logit(base) + 0 * g)  # noqa: E731
    # One-sided curves like the recommendation result: low at g <= 0, rising above 0.
    step = lambda g: -2.5 + 3.0 * (g > 0)  # noqa: E731
    grad = lambda g: -2.5 + 6.0 * max(g, 0)  # noqa: E731
    L = ["# Simulation calibration of the planned tests (sending score-gap curve)", "",
         f"Design: {NS} scenarios x {len(A.GAPS)} levels x {NR['bundle']} episodes (bundle) or {NR['ordinary']} "
         f"(ordinary) per scenario x level; scenario logit offsets N(0, {SIG}); {SIMS} simulations per row; trend "
         "test 1000 permutations per simulation; comparison test exact over 2^12 scenario flips. alpha = 0.05; "
         f"Monte Carlo SE at 0.05 ≈ {np.sqrt(0.05 * 0.95 / SIMS):.3f}.", "",
         "Curves: step = logit −2.5 at g ≤ 0 and +0.5 above 0 (≈ 8% → 62%); gradual = logit −2.5 + 6·max(g, 0) "
         "(≈ 8% at g ≤ 0, 10% at +0.05, 20% at +0.20, 62% at +0.50).", "",
         "| Check | Rejection rate | Target |", "|---|---|---|"]

    def rate(fn, n=SIMS):
        return np.mean([fn() for _ in range(n)])

    def trend(curve, nr):
        return A.trend_test(draw(rng, curve, rng.normal(0, SIG, NS), nr), perms=1000,
                            seed=int(rng.integers(1e9)))["p"] < 0.05

    for panel, nr in NR.items():
        for base in (0.05, 0.2, 0.5):
            L.append(f"| Trend test size, no gap effect, base {base}, {panel} (n={nr * NS}/level) | "
                     f"{rate(lambda: trend(flat(base), nr)):.3f} | ≤ 0.05 |")
    for panel, nr in NR.items():
        for name, curve in (("step", step), ("gradual", grad)):
            def same():
                off = rng.normal(0, SIG, NS)
                return A.curve_diff_test(draw(rng, curve, off, nr), draw(rng, curve, off, nr))["p"] < 0.05

            def indep():
                return A.curve_diff_test(draw(rng, curve, rng.normal(0, SIG, NS), nr),
                                         draw(rng, curve, rng.normal(0, SIG, NS), nr))["p"] < 0.05
            L.append(f"| Comparison size, same {name} curve, identical scenario effects, {panel} | {rate(same):.3f} | ≤ 0.05 |")
            L.append(f"| Comparison size, same {name} curve, independent scenario effects, {panel} | {rate(indep):.3f} | ≤ 0.05 |")
    # bundle vs ordinary comparisons have unequal sizes (6 vs 2 per cell)
    L.append("| Comparison size, same step curve, bundle (6) vs ordinary (2), independent scenario effects | "
             f"{rate(lambda: A.curve_diff_test(draw(rng, step, rng.normal(0, SIG, NS), 6), draw(rng, step, rng.normal(0, SIG, NS), 2))['p'] < 0.05):.3f} | ≤ 0.05 |")

    def fwer_trend():
        ps = {(m, p): A.trend_test(draw(rng, flat(0.2), rng.normal(0, SIG, NS), NR[p]), perms=1000,
                                   seed=int(rng.integers(1e9)))["p"] for m in range(2) for p in NR}
        return min(A.holm(ps).values()) < 0.05

    def fwer_comp():
        g = {(m, p): draw(rng, step, rng.normal(0, SIG, NS), NR[p]) for m in range(2) for p in NR}
        prim = {p: A.curve_diff_test(g[(1, p)], g[(0, p)])["p"] for p in NR}
        sec = {m: A.curve_diff_test(g[(m, "bundle")], g[(m, "ordinary")])["p"] for m in range(2)}
        return min(A.holm(prim).values()) < 0.05, min(A.holm(sec).values()) < 0.05
    nfw = SIMS // 2
    L.append(f"| Holm FWER, 4 trend tests, global null ({nfw} sims) | {rate(fwer_trend, nfw):.3f} | ≤ 0.05 |")
    fc = np.array([fwer_comp() for _ in range(SIMS)])
    L.append(f"| Holm FWER, primary family (3.8 vs 3.5 per panel, 2 tests), all curves equal | {fc[:, 0].mean():.3f} | ≤ 0.05 |")
    L.append(f"| Holm FWER, secondary family (bundle vs ordinary per model, 2 tests), all curves equal | {fc[:, 1].mean():.3f} | ≤ 0.05 |")
    for panel, nr in NR.items():
        for name, curve in (("step", step), ("gradual", grad)):
            L.append(f"| Trend power, {name}, {panel} | {rate(lambda: trend(curve, nr)):.3f} | (power) |")
        shift = lambda g: step(g) + 1.0  # noqa: E731
        L.append(f"| Comparison power, +1 logit shift, independent scenario effects, {panel} | "
                 f"{rate(lambda: A.curve_diff_test(draw(rng, shift, rng.normal(0, SIG, NS), nr), draw(rng, step, rng.normal(0, SIG, NS), nr))['p'] < 0.05):.3f} | (power) |")
        L.append(f"| Comparison power, step vs gradual, {panel} | "
                 f"{rate(lambda: A.curve_diff_test(draw(rng, step, rng.normal(0, SIG, NS), nr), draw(rng, grad, rng.normal(0, SIG, NS), nr))['p'] < 0.05):.3f} | (power) |")
        big = lambda g: -2.5 + 4.5 * (g > 0)  # noqa: E731  (≈ 8% → 88%) vs flat 8%
        L.append(f"| Comparison power, strong step vs flat low curve, {panel} | "
                 f"{rate(lambda: A.curve_diff_test(draw(rng, big, rng.normal(0, SIG, NS), nr), draw(rng, flat(0.08), rng.normal(0, SIG, NS), nr))['p'] < 0.05):.3f} | (power) |")
    out = HERE / "simulation"
    out.mkdir(exist_ok=True)
    (out / "CALIBRATION.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
