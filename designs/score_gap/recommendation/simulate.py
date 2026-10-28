"""Simulation calibration of the planned tests (run before freezing; writes simulation/CALIBRATION.md).

Design simulated = the frozen design: 12 scenarios x 7 gap levels x 3 replies per cell, per model x panel.
Scenario heterogeneity: scenario logit offsets ~ N(0, sigma) with sigma = 1.5 (large; upsell rates in the main
recommendation run ranged from 1/5 to 5/5 by scenario).
  1. Trend test size under no gap effect, for base rates 0.2 / 0.5 / 0.8.
  2. Curve-comparison size when two groups share the population curve:
       a. identical scenario effects; b. independent (exchangeable) scenario effects.
     Curves: step at 0 and gradual.
  3. Family-wise error with Holm: 9 trend tests (global null) and 18 comparisons (all 9 groups share the curve,
     independent scenario effects per group).
  4. Power: trend under a step (+/-1.5 logits) and gradual curve; comparison under a +1 logit shift and under a
     step-vs-gradual shape difference.
Run: ~/.claude/bin/memguard -m 3 -- .venv/bin/python designs/score_gap/recommendation/simulate.py
"""
from pathlib import Path

import numpy as np

import gap_analysis as A

HERE = Path(__file__).parent
GAPS = np.array(A.GAPS)
NS, NR = 12, 3
SIMS = 400


def logistic(x):
    return 1 / (1 + np.exp(-x))


def draw(rng, curve, offsets):
    obs = []
    for s in range(NS):
        for g in A.GAPS:
            p = logistic(curve(g) + offsets[s])
            for _ in range(NR):
                obs.append(dict(scenario=f"s{s:02d}", gap=g, y=int(rng.random() < p)))
    return obs


def logit(p):
    return np.log(p / (1 - p))


def main():
    rng = np.random.default_rng(20261028)
    sig = 1.5
    flat = lambda base: (lambda g: logit(base))
    step = lambda g: 1.5 * np.sign(g)
    grad = lambda g: 5.0 * g
    L = ["# Simulation calibration of the planned tests", "",
         f"Design: {NS} scenarios x {len(GAPS)} levels x {NR} replies; scenario logit offsets N(0, {sig}); "
         f"{SIMS} simulations per row; trend test 1000 permutations per simulation; comparison test exact over 2^12 "
         "scenario flips. alpha = 0.05.", "", "| Check | Rejection rate | Target |", "|---|---|---|"]

    def rate(fn):
        return np.mean([fn() for _ in range(SIMS)])

    for base in (0.2, 0.5, 0.8):
        r = rate(lambda: A.trend_test(draw(rng, flat(base), rng.normal(0, sig, NS)), perms=1000,
                                      seed=int(rng.integers(1e9)))["p"] < 0.05)
        L.append(f"| Trend test size, no gap effect, base {base} | {r:.3f} | ≤ 0.05 |")
    for name, curve in (("step", step), ("gradual", grad)):
        def same():
            off = rng.normal(0, sig, NS)
            return A.curve_diff_test(draw(rng, curve, off), draw(rng, curve, off))["p"] < 0.05

        def indep():
            return A.curve_diff_test(draw(rng, curve, rng.normal(0, sig, NS)),
                                     draw(rng, curve, rng.normal(0, sig, NS)))["p"] < 0.05
        L.append(f"| Comparison size, same {name} curve, identical scenario effects | {rate(same):.3f} | ≤ 0.05 |")
        L.append(f"| Comparison size, same {name} curve, independent scenario effects | {rate(indep):.3f} | ≤ 0.05 |")

    # family-wise error with Holm
    def fwer_trend():
        ps = {i: A.trend_test(draw(rng, flat(0.5), rng.normal(0, sig, NS)), perms=1000,
                              seed=int(rng.integers(1e9)))["p"] for i in range(9)}
        return min(A.holm(ps).values()) < 0.05

    def fwer_comp():
        groups = {(m, p): draw(rng, step, rng.normal(0, sig, NS)) for m in range(3) for p in range(3)}
        ps = {}
        for p in range(3):
            for a, b in ((2, 0), (1, 0), (2, 1)):
                ps[("m", p, a, b)] = A.curve_diff_test(groups[(a, p)], groups[(b, p)])["p"]
        for m in range(3):
            for a, b in ((1, 0), (2, 1), (2, 0)):
                ps[("p", m, a, b)] = A.curve_diff_test(groups[(m, a)], groups[(m, b)])["p"]
        return min(A.holm(ps).values()) < 0.05
    sims_fw = SIMS // 4
    L.append(f"| Holm FWER, 9 trend tests, global null ({sims_fw} sims) | "
             f"{np.mean([fwer_trend() for _ in range(sims_fw)]):.3f} | ≤ 0.05 |")
    L.append(f"| Holm FWER, 18 comparisons, all curves equal ({SIMS} sims) | "
             f"{np.mean([fwer_comp() for _ in range(SIMS)]):.3f} | ≤ 0.05 |")
    # power
    for name, curve in (("step ±1.5 logits", step), ("gradual 5 logits per unit gap", grad)):
        r = rate(lambda: A.trend_test(draw(rng, curve, rng.normal(0, sig, NS)), perms=1000,
                                      seed=int(rng.integers(1e9)))["p"] < 0.05)
        L.append(f"| Trend power, {name} | {r:.3f} | (power) |")
    shift = lambda g: step(g) + 1.0
    r = rate(lambda: A.curve_diff_test(draw(rng, shift, rng.normal(0, sig, NS)),
                                       draw(rng, step, rng.normal(0, sig, NS)))["p"] < 0.05)
    L.append(f"| Comparison power, +1 logit shift, independent scenario effects | {r:.3f} | (power) |")
    r = rate(lambda: A.curve_diff_test(draw(rng, step, rng.normal(0, sig, NS)),
                                       draw(rng, grad, rng.normal(0, sig, NS)))["p"] < 0.05)
    L.append(f"| Comparison power, step vs gradual shape | {r:.3f} | (power) |")
    big = lambda g: 3 * np.sign(g) + 1.0
    r = rate(lambda: A.curve_diff_test(draw(rng, big, rng.normal(0, sig, NS)),
                                       draw(rng, lambda g: -1.5 + 0 * g, rng.normal(0, sig, NS)))["p"] < 0.05)
    L.append(f"| Comparison power, strong step vs flat low curve | {r:.3f} | (power) |")
    out = HERE / "simulation"
    out.mkdir(exist_ok=True)
    (out / "CALIBRATION.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
