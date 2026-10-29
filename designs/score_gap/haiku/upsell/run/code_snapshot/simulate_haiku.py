"""Simulation calibration of the planned Haiku tests (run before freezing; writes simulation/CALIBRATION.md).

Same simulated design and test code as the frozen Qwen calibration (recommendation/simulate.py, imported read-only):
12 scenarios x 7 levels x 3 replies per model x panel; scenario logit offsets ~ N(0, 1.5). Only the families change:
  - 6 trend tests (2 models x 3 panels), Holm over 6;
  - 3 curve comparisons (Haiku 5.5 vs Haiku 4.5 in each panel), Holm over 3.
Also: test sizes when some replies are excluded (non-clean replies dropped at random, 10% and up to 30% in a cell),
and power at the observed design.
Run: .venv/bin/python designs/score_gap/haiku/upsell/simulate_haiku.py
"""
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).parent
sys.path[:0] = [str(HERE.parents[1] / "recommendation")]
import gap_analysis as A  # noqa: E402
import simulate as S  # noqa: E402  (draw, logistic, logit; frozen Qwen calibration code)

SIMS = 400


def drop(rng, obs, frac):
    return [o for o in obs if rng.random() >= frac]


def main():
    rng = np.random.default_rng(20261029)
    sig = 1.5
    flat = lambda base: (lambda g: S.logit(base))
    step = lambda g: 1.5 * np.sign(g)
    grad = lambda g: 5.0 * g
    off = lambda: rng.normal(0, sig, S.NS)
    L = ["# Simulation calibration of the planned Haiku tests", "",
         f"Design: {S.NS} scenarios x {len(A.GAPS)} levels x {S.NR} replies; scenario logit offsets N(0, {sig}); "
         f"{SIMS} simulations per row (FWER rows: see label); trend test 1000 permutations per simulation; comparison "
         "test exact over 2^12 scenario flips. alpha = 0.05. Monte Carlo SE at 0.05 ≈ 0.011 (400 sims).", "",
         "| Check | Rejection rate | Target |", "|---|---|---|"]
    rate = lambda fn, n=SIMS: float(np.mean([fn() for _ in range(n)]))
    tp = lambda obs: A.trend_test(obs, perms=1000, seed=int(rng.integers(1e9)))["p"]
    for base in (0.1, 0.5):
        L.append(f"| Trend size, no gap effect, base {base} | {rate(lambda: tp(S.draw(rng, flat(base), off())) < 0.05):.3f} "
                 "| ≤ 0.05 |")
    L.append(f"| Trend size, no gap effect, base 0.5, 20% of replies excluded at random | "
             f"{rate(lambda: tp(drop(rng, S.draw(rng, flat(0.5), off()), 0.2)) < 0.05):.3f} | ≤ 0.05 |")
    for name, curve in (("step", step), ("gradual", grad)):
        L.append(f"| Comparison size, same {name} curve, independent scenario effects | "
                 f"{rate(lambda: A.curve_diff_test(S.draw(rng, curve, off()), S.draw(rng, curve, off()))['p'] < 0.05):.3f}"
                 " | ≤ 0.05 |")
    L.append("| Comparison size, same step curve, 20% excluded at random | "
             f"{rate(lambda: A.curve_diff_test(drop(rng, S.draw(rng, step, off()), 0.2), drop(rng, S.draw(rng, step, off()), 0.2))['p'] < 0.05):.3f}"
             " | ≤ 0.05 |")

    def fwer_trend():
        ps = {i: tp(S.draw(rng, flat(0.5), off())) for i in range(6)}
        return min(A.holm(ps).values()) < 0.05

    def fwer_comp():
        ps = {p: A.curve_diff_test(S.draw(rng, step, off()), S.draw(rng, step, off()))["p"] for p in range(3)}
        return min(A.holm(ps).values()) < 0.05
    L.append(f"| Holm FWER, 6 trend tests, global null (100 sims) | {rate(fwer_trend, 100):.3f} | ≤ 0.05 |")
    L.append(f"| Holm FWER, 3 comparisons, equal curves | {rate(fwer_comp):.3f} | ≤ 0.05 |")
    for name, curve in (("step ±1.5 logits", step), ("gradual 5 logits per unit gap", grad)):
        L.append(f"| Trend power, {name} | {rate(lambda: tp(S.draw(rng, curve, off())) < 0.05):.3f} | (power) |")
    L.append("| Trend power, one-sided rise only (0 for g ≤ 0, 50% at +0.50, logistic) | "
             f"{rate(lambda: tp(S.draw(rng, lambda g: -4 + 8 * max(g, 0), off())) < 0.05):.3f} | (power) |")
    shift = lambda g: step(g) + 1.0
    L.append("| Comparison power, +1 logit shift | "
             f"{rate(lambda: A.curve_diff_test(S.draw(rng, shift, off()), S.draw(rng, step, off()))['p'] < 0.05):.3f}"
             " | (power) |")
    L.append("| Comparison power, step vs gradual | "
             f"{rate(lambda: A.curve_diff_test(S.draw(rng, step, off()), S.draw(rng, grad, off()))['p'] < 0.05):.3f}"
             " | (power) |")
    big = lambda g: 3 * np.sign(g) + 1.0
    L.append("| Comparison power, strong step vs flat low curve | "
             f"{rate(lambda: A.curve_diff_test(S.draw(rng, big, off()), S.draw(rng, lambda g: -1.5 + 0 * g, off()))['p'] < 0.05):.3f}"
             " | (power) |")
    out = HERE / "simulation"
    out.mkdir(exist_ok=True)
    (out / "CALIBRATION.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
