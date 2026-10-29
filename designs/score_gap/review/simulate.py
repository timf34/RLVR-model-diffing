"""Simulation calibration of the planned tests (run before freezing; writes simulation/CALIBRATION.md).

Design simulated = the frozen design: 6 scenarios x 7 gap levels x 4 replies per cell, per model x panel.
Ratings: latent = base + a_s + (curve(g) + b_s * g) + e, e ~ N(0, 1.0), rounded to an integer and clipped to 0-10
(the judge's ratings are integers or halves). Scenario heterogeneity: intercepts a_s ~ N(0, 1.0) and slopes
b_s ~ N(0, 1.0) per unit gap (both large relative to the original run, where per-scenario means varied by about 1
point). "Independent" scenario effects = each model draws its own (a_s, b_s); "identical" = both share them.
  1. Trend test size under no gap effect (strong null), base 4 and 7; and under the weak null (scenario-specific
     slopes averaging zero), which the strong-null test is not built for (reported, not a target).
  2. Comparison size (Hotelling, planned; sign-flip D, sensitivity) when the two models share the population curve,
     with identical and with independent scenario effects; also bimodal ratings (each reply 5 or 8).
  3. Family-wise error with Holm: 6 trend tests (global null) and 3 comparisons (all curves equal).
  4. Power for the trend and the comparison under curves like those seen before.
  5. Coverage of the cluster t interval for a level mean.
Run: .venv/bin/python designs/score_gap/review/simulate.py
"""
from pathlib import Path

import numpy as np

import gap_analysis as A

HERE = Path(__file__).parent
GAPS = np.array(A.GAPS)
NS, NR = 6, 4
SIMS = 400
SA, SB, SE = 1.0, 1.0, 1.0


def draw(rng, curve, eff, base=5.0, bimodal=False):
    a, b = eff
    obs = []
    for s in range(NS):
        for g in A.GAPS:
            mu = base + a[s] + curve(g) + b[s] * g
            if bimodal:  # each reply is 5 or 8; P(8) follows the latent mean
                p = np.clip((mu - 5) / 3, 0.02, 0.98)
                ys = np.where(rng.random(NR) < p, 8.0, 5.0)
            else:
                ys = np.clip(np.round(mu + rng.normal(0, SE, NR)), 0, 10)
            obs += [dict(scenario=f"s{s}", gap=g, y=float(y)) for y in ys]
    return obs


def main():
    rng = np.random.default_rng(20261029)
    eff = lambda: (rng.normal(0, SA, NS), rng.normal(0, SB, NS))
    no_slope = lambda: (rng.normal(0, SA, NS), np.zeros(NS))
    flat = lambda g: 0.0
    step = lambda g: 0.75 * np.sign(g)
    grad38 = lambda g: 2.7 * g  # e.g. 5.0 at -0.5 to 7.7 at +0.5
    grad35 = lambda g: 0.6 * g
    seed = lambda: int(rng.integers(1e9))
    L = ["# Simulation calibration of the planned tests", "",
         f"Design: {NS} scenarios x {len(GAPS)} levels x {NR} replies; integer ratings, reply noise SD {SE}; scenario "
         f"intercept SD {SA}, scenario slope SD {SB} per unit gap; {SIMS} simulations per row; trend test 1000 "
         "permutations per simulation; alpha = 0.05.", "", "| Check | Rate | Target |", "|---|---|---|"]
    rate = lambda fn, n=SIMS: np.mean([fn() for _ in range(n)])
    tr = lambda o: A.trend_test(o, perms=1000, seed=seed())["p"] < 0.05

    for base in (4.0, 7.0):
        L.append(f"| Trend size, no gap effect (strong null), base {base:.0f} (1000 sims) | "
                 f"{rate(lambda: tr(draw(rng, flat, no_slope(), base)), 1000):.3f} | ≤ 0.05 |")
    L.append(f"| Trend rejection, weak null (scenario slopes SD {SB}, mean 0) | "
             f"{rate(lambda: tr(draw(rng, flat, eff()))):.3f} | (not a target; strong-null test) |")
    for name, curve in (("flat", flat), ("step", step), ("gradual", grad38)):
        def same(kind):
            e = eff()
            c = A.curve_compare(draw(rng, curve, e), draw(rng, curve, e))
            return c["p"] < 0.05 if kind == "h" else c["p_signflip"] < 0.05

        def indep(kind):
            c = A.curve_compare(draw(rng, curve, eff()), draw(rng, curve, eff()))
            return c["p"] < 0.05 if kind == "h" else c["p_signflip"] < 0.05
        L.append(f"| Comparison size (Hotelling), same {name} curve, identical scenario effects | "
                 f"{rate(lambda: same('h')):.3f} | ≤ 0.05 |")
        L.append(f"| Comparison size (Hotelling), same {name} curve, independent scenario effects | "
                 f"{rate(lambda: indep('h')):.3f} | ≤ 0.05 |")
        L.append(f"| Comparison size (sign-flip D), same {name} curve, independent scenario effects | "
                 f"{rate(lambda: indep('f')):.3f} | ≤ 0.05 |")
    L.append("| Comparison size (Hotelling), same gradual curve, bimodal 5-or-8 ratings, independent effects | "
             f"{rate(lambda: A.curve_compare(draw(rng, grad38, eff(), bimodal=True), draw(rng, grad38, eff(), bimodal=True))['p'] < 0.05):.3f}"
             " | ≤ 0.05 |")

    def fwer_trend():
        ps = {i: A.trend_test(draw(rng, flat, no_slope()), perms=1000, seed=seed())["p"] for i in range(6)}
        return min(A.holm(ps).values()) < 0.05

    def fwer_comp():
        ps = {p: A.curve_compare(draw(rng, grad38, eff()), draw(rng, grad38, eff()))["p"] for p in range(3)}
        return min(A.holm(ps).values()) < 0.05
    L.append(f"| Holm FWER, 6 trend tests, global null ({SIMS // 2} sims) | {rate(fwer_trend, SIMS // 2):.3f} | ≤ 0.05 |")
    L.append(f"| Holm FWER, 3 comparisons, all curves equal, independent effects | {rate(fwer_comp):.3f} | ≤ 0.05 |")

    for name, curve in (("step ±0.75 points", step), ("gradual 2.7 points per unit gap (3.8-like)", grad38),
                        ("gradual 0.6 points per unit gap (3.5-like)", grad35)):
        L.append(f"| Trend power, {name} | {rate(lambda: tr(draw(rng, curve, eff()))):.3f} | (power) |")
    for name, ca, cb in (("3.8-like gradual 2.7 vs 3.5-like 0.6 per unit gap", grad38, grad35),
                         ("+1 point shift, same gradual curve", lambda g: grad38(g) + 1, grad38),
                         ("step ±0.75 vs gradual 1.5 per unit gap", step, lambda g: 1.5 * g)):
        h = rate(lambda: A.curve_compare(draw(rng, ca, eff()), draw(rng, cb, eff()))["p"] < 0.05)
        f = rate(lambda: A.curve_compare(draw(rng, ca, eff()), draw(rng, cb, eff()))["p_signflip"] < 0.05)
        L.append(f"| Comparison power, {name} (Hotelling / sign-flip) | {h:.3f} / {f:.3f} | (power) |")

    mod = lambda: (rng.normal(0, 0.5, NS), rng.normal(0, 0.5, NS))
    for name, ca, cb in (("3.8-like vs 3.5-like", grad38, grad35),
                         ("+1 point shift", lambda g: grad38(g) + 1, grad38)):
        h = rate(lambda: A.curve_compare(draw(rng, ca, mod()), draw(rng, cb, mod()))["p"] < 0.05)
        L.append(f"| Comparison power, {name}, moderate heterogeneity (intercept and slope SD 0.5) (Hotelling) | "
                 f"{h:.3f} | (power) |")
    L.append(f"| Comparison size (Hotelling), same gradual curve, moderate heterogeneity | "
             f"{rate(lambda: A.curve_compare(draw(rng, grad38, mod()), draw(rng, grad38, mod()))['p'] < 0.05):.3f} | ≤ 0.05 |")

    def cover():
        o = draw(rng, grad38, eff())
        st = A.level_stats(o)
        # true population mean at +0.5 ignoring rounding/clipping: base + curve
        truth = 5.0 + grad38(0.5)
        return st["lo"][-1] <= truth <= st["hi"][-1]
    L.append(f"| Coverage of the cluster t 95% interval, level mean at +0.50 | {rate(cover):.3f} | ≈ 0.95 |")
    out = HERE / "simulation"
    out.mkdir(exist_ok=True)
    (out / "CALIBRATION.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
