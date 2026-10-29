"""Simulation calibration of the planned tests, omission environment (run before freezing; writes
simulation/CALIBRATION.md). Adapted from designs/score_gap/recommendation/simulate.py.

Design simulated = the frozen design: 12 scenarios x 7 gap levels x 3 replies per cell, per model x panel.
Scenario heterogeneity is large here: in disclosure_confirm, omission occurred in 6 of 12 scenarios and never in
others. Scenario logit offsets ~ N(0, sigma), sigma = 1.5 and 3.0.
  1. Trend test size under no gap effect, base rates 0.05 / 0.2 / 0.5.
  2. Curve-comparison size when two groups share the population curve:
       a. identical scenario effects; b. correlated (rho = 0.7, both models find the same scenarios easy);
       c. independent scenario effects. Curves: step at 0 and gradual, from a low base.
  3. Family-wise error with Holm: 4 trend tests (global null); the 2 planned model comparisons and the 2
     secondary panel comparisons (all four groups share the curve, independent scenario effects per group).
  4. Power: trend under a step and a gradual curve from a low base; comparison under a shift and under
     step vs gradual.
Run: .venv/bin/python designs/score_gap/omission/simulate.py
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


def logit(p):
    return np.log(p / (1 - p))


def draw(rng, curve, offsets):
    obs = []
    for s in range(NS):
        for g in A.GAPS:
            p = logistic(curve(g) + offsets[s])
            for _ in range(NR):
                obs.append(dict(scenario=f"s{s:02d}", gap=g, y=int(rng.random() < p)))
    return obs


def main():
    rng = np.random.default_rng(20261029)
    flat = lambda base: (lambda g: logit(base))
    low = logit(0.03)
    step = lambda g: low + (3.0 if g > 0 else 0.0)            # 3% -> ~38% at any positive gap
    grad = lambda g: low + 7.0 * max(g, 0)                    # 3% -> ~50% at +0.50, rising with the gap
    L = ["# Simulation calibration of the planned tests (omission environment)", "",
         f"Design: {NS} scenarios x {len(GAPS)} levels x {NR} replies; scenario logit offsets N(0, sigma); "
         f"{SIMS} simulations per row (Holm rows as stated); trend test 1000 permutations per simulation; "
         "comparison test exact over 2^12 scenario flips. alpha = 0.05. Monte Carlo SE at 0.05 with 400 sims "
         "is about 0.011.", "", "| Check | sigma | Rejection rate | Target |", "|---|---|---|---|"]

    def rate(fn, n=SIMS):
        return np.mean([fn() for _ in range(n)])

    def offs(sig):
        return rng.normal(0, sig, NS)

    def trend_p(obs):
        return A.trend_test(obs, perms=1000, seed=int(rng.integers(1e9)))["p"]

    for sig in (1.5, 3.0):
        for base in (0.05, 0.2, 0.5):
            r = rate(lambda: trend_p(draw(rng, flat(base), offs(sig))) < 0.05)
            L.append(f"| Trend test size, no gap effect, base {base} | {sig} | {r:.3f} | ≤ 0.05 |")
    for sig in (1.5, 3.0):
        for name, curve in (("step", step), ("gradual", grad)):
            def same():
                o = offs(sig)
                return A.curve_diff_test(draw(rng, curve, o), draw(rng, curve, o))["p"] < 0.05

            def corr():
                z1, z2 = rng.normal(0, 1, NS), rng.normal(0, 1, NS)
                o1, o2 = sig * z1, sig * (0.7 * z1 + np.sqrt(1 - 0.49) * z2)
                return A.curve_diff_test(draw(rng, curve, o1), draw(rng, curve, o2))["p"] < 0.05

            def indep():
                return A.curve_diff_test(draw(rng, curve, offs(sig)), draw(rng, curve, offs(sig)))["p"] < 0.05
            L.append(f"| Comparison size, same {name} curve, identical scenario effects | {sig} | {rate(same):.3f} | ≤ 0.05 |")
            L.append(f"| Comparison size, same {name} curve, correlated scenario effects (rho 0.7) | {sig} | {rate(corr):.3f} | ≤ 0.05 |")
            L.append(f"| Comparison size, same {name} curve, independent scenario effects | {sig} | {rate(indep):.3f} | ≤ 0.05 |")

    sig = 3.0

    def fwer_trend():
        ps = {i: trend_p(draw(rng, flat(0.1), offs(sig))) for i in range(4)}
        return min(A.holm(ps).values()) < 0.05

    def fwer_comp():
        g = {(m, p): draw(rng, step, offs(sig)) for m in range(2) for p in range(2)}
        model = {p: A.curve_diff_test(g[(1, p)], g[(0, p)])["p"] for p in range(2)}
        panel = {m: A.curve_diff_test(g[(m, 1)], g[(m, 0)])["p"] for m in range(2)}
        return min(A.holm(model).values()) < 0.05, min(A.holm(panel).values()) < 0.05
    n_fw = SIMS // 2
    L.append(f"| Holm FWER, 4 trend tests, global null, base 0.1 ({n_fw} sims) | {sig} | "
             f"{np.mean([fwer_trend() for _ in range(n_fw)]):.3f} | ≤ 0.05 |")
    fc = np.array([fwer_comp() for _ in range(SIMS)])
    L.append(f"| Holm FWER, 2 planned model comparisons, curves equal | {sig} | {fc[:, 0].mean():.3f} | ≤ 0.05 |")
    L.append(f"| Holm FWER, 2 secondary panel comparisons, curves equal | {sig} | {fc[:, 1].mean():.3f} | ≤ 0.05 |")

    for sig in (1.5, 3.0):
        for name, curve in (("step 3% -> ~38% at any positive gap", step),
                            ("gradual 3% -> ~50% at +0.50", grad)):
            r = rate(lambda: trend_p(draw(rng, curve, offs(sig))) < 0.05)
            L.append(f"| Trend power, {name} | {sig} | {r:.3f} | (power) |")
        weak = lambda g: low + (1.0 if g > 0 else 0.0)
        strong = lambda g: low + (4.0 if g > 0 else 0.0)
        for name, a, b in (("strong step (~66%) vs weak step (~8%)", strong, weak),
                           ("step vs gradual shape", step, grad)):
            for lab, mk in (("correlated rho 0.7", "corr"), ("independent", "indep")):
                def one():
                    if mk == "corr":
                        z1, z2 = rng.normal(0, 1, NS), rng.normal(0, 1, NS)
                        o1, o2 = sig * z1, sig * (0.7 * z1 + np.sqrt(0.51) * z2)
                    else:
                        o1, o2 = offs(sig), offs(sig)
                    return A.curve_diff_test(draw(rng, a, o1), draw(rng, b, o2))["p"] < 0.05
                L.append(f"| Comparison power, {name}, {lab} scenario effects | {sig} | {rate(one):.3f} | (power) |")
    out = HERE / "simulation"
    out.mkdir(exist_ok=True)
    (out / "CALIBRATION.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
