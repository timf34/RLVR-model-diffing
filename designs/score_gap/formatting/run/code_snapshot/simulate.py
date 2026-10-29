"""Simulation calibration of the planned tests (run before freezing; writes simulation/CALIBRATION.md).

Design simulated = the frozen design per model x panel x feature: 6 tasks x 7 gap levels x 4 replies per cell
(feature 1 has 2 sub-features per task: 12 strata in 6 task clusters, checked in one row).
Task heterogeneity: task logit offsets ~ N(0, 1.5).
  1. Trend test size with no gap effect, base rates 0.05 / 0.2 / 0.5 (and the 12-strata layout).
  2. Comparison test size under its null (the two models share each task's curve: identical task effects),
     for a step, a gradual and a low gradual curve; the secondary task sign-flip test alongside.
  3. Comparison rejection when the models share the population curve but have independent task effects
     (task x model interaction): NOT the null of the within-task test; shows how often it flags task-specific
     differences.
  4. Holm family-wise error: 12 trend tests (global null) and 6 comparisons (identical task effects).
  5. Power: trend for a low gradual curve; comparison for a low gradual curve vs a flat near-zero curve and for a
     moderate +1 logit shift.
Run: .venv/bin/python designs/score_gap/formatting/simulate.py
"""
from pathlib import Path

import numpy as np

import fmt_analysis as A

HERE = Path(__file__).parent
NT, NR, SIG = 6, 4, 1.5
SIMS = 400
PERMS = 1000


def logistic(x):
    return 1 / (1 + np.exp(-x))


def logit(p):
    return np.log(p / (1 - p))


def draw(rng, curve, offsets, subs=1):
    obs = []
    for t in range(NT):
        for sub in range(subs):
            for g in A.GAPS:
                p = logistic(curve(g) + offsets[t])
                for _ in range(NR):
                    obs.append(dict(stratum=f"t{t}|{sub}", cluster=f"t{t}", gap=g, y=int(rng.random() < p)))
    return obs


def main():
    rng = np.random.default_rng(20261028)
    flat = lambda base: (lambda g: logit(base))
    step = lambda g: 1.5 * np.sign(g)
    grad = lambda g: 5.0 * g
    low_grad = lambda g: -2.5 + 5.0 * g  # ~1% at -0.50, ~8% at 0, ~50% at +0.50 (before task offsets)
    near_zero = lambda g: -6.0 + 0 * g
    off = lambda: rng.normal(0, SIG, NT)
    seed = lambda: int(rng.integers(1e9))
    L = ["# Simulation calibration of the planned tests", "",
         f"Design per model × panel × feature: {NT} tasks × {len(A.GAPS)} levels × {NR} replies; task logit offsets "
         f"N(0, {SIG}); {SIMS} simulations per row; {PERMS} permutations per test in the simulations "
         "(10,000 in the real analysis). alpha = 0.05; Monte Carlo SE at 0.05 ≈ 0.011 (400 sims) or 0.007 (1000 sims).", "",
         "| Check | Rejection rate | Target |", "|---|---|---|"]

    def rate(fn, sims=SIMS):
        return float(np.mean([fn() for _ in range(sims)]))

    for base in (0.05, 0.2, 0.5):
        r = rate(lambda: A.trend_test(draw(rng, flat(base), off()), perms=PERMS, seed=seed())["p"] < 0.05)
        L.append(f"| Trend test size, no gap effect, base {base} | {r:.3f} | ≤ 0.05 |")
    r = rate(lambda: A.trend_test(draw(rng, flat(0.2), off(), subs=2), perms=PERMS, seed=seed())["p"] < 0.05)
    L.append(f"| Trend test size, no gap effect, base 0.2, 12 strata in 6 tasks (feature 1) | {r:.3f} | ≤ 0.05 |")
    for name, curve in (("step ±1.5 logits", step), ("gradual 5 logits/unit", grad), ("low gradual", low_grad)):
        res = []
        for _ in range(SIMS):
            o = off()
            t = A.compare_test(draw(rng, curve, o), draw(rng, curve, o), perms=PERMS, seed=seed())
            res.append((t["p"] < 0.05, t["p_signflip"] < 0.05))
        res = np.array(res)
        L.append(f"| Comparison size, same {name} curve, identical task effects: within-task test | "
                 f"{res[:, 0].mean():.3f} | ≤ 0.05 |")
        L.append(f"| Same, secondary task sign-flip test | {res[:, 1].mean():.3f} | ≤ 0.05 |")
    for name, curve in (("step ±1.5 logits", step), ("low gradual", low_grad)):
        res = np.array([(lambda t: (t["p"] < 0.05, t["p_signflip"] < 0.05))(
            A.compare_test(draw(rng, curve, off()), draw(rng, curve, off()), perms=PERMS, seed=seed()))
            for _ in range(SIMS)])
        L.append(f"| Same population {name} curve, INDEPENDENT task effects (not the within-task null): "
                 f"within-task / sign-flip | {res[:, 0].mean():.3f} / {res[:, 1].mean():.3f} | (flags task-specific "
                 "differences) |")

    def fwer_trend():
        ps = {i: A.trend_test(draw(rng, flat(0.2), off()), perms=PERMS, seed=seed())["p"] for i in range(12)}
        return min(A.holm(ps).values()) < 0.05

    def fwer_comp():
        ps = {}
        for i in range(6):
            o = off()
            ps[i] = A.compare_test(draw(rng, low_grad, o), draw(rng, low_grad, o), perms=PERMS, seed=seed())["p"]
        return min(A.holm(ps).values()) < 0.05
    L.append(f"| Holm FWER, 12 trend tests, global null (1000 sims) | {rate(fwer_trend, 1000):.3f} | ≤ 0.05 |")
    L.append(f"| Holm FWER, 6 comparisons, identical task effects (1000 sims) | {rate(fwer_comp, 1000):.3f} | ≤ 0.05 |")
    for name, curve in (("low gradual", low_grad), ("step ±1.5 logits", step)):
        r = rate(lambda: A.trend_test(draw(rng, curve, off()), perms=PERMS, seed=seed())["p"] < 0.05)
        L.append(f"| Trend power, {name} | {r:.3f} | (power) |")
    for name, ca, cb in (("low gradual vs flat near zero", low_grad, near_zero),
                         ("+1 logit shift of a step curve", lambda g: step(g) + 1.0, step)):
        res = np.array([(lambda t: (t["p"] < 0.05, t["p_signflip"] < 0.05))(
            A.compare_test(draw(rng, ca, off()), draw(rng, cb, off()), perms=PERMS, seed=seed()))
            for _ in range(SIMS)])
        L.append(f"| Comparison power, {name}, independent task effects: within-task / sign-flip | "
                 f"{res[:, 0].mean():.3f} / {res[:, 1].mean():.3f} | (power) |")
    out = HERE / "simulation"
    out.mkdir(exist_ok=True)
    (out / "CALIBRATION.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
