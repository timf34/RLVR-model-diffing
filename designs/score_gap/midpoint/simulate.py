"""Simulation calibration of the planned tests (run before freezing; writes simulation/CALIBRATION.md).

Simulated design = the frozen design for one model x panel group: 12 scenarios; cells 0.30/0.10, 0.60/0.40,
0.90/0.70 (midpoint test), 0.75/0.25 and 0.95/0.45 (high50 test), the three reversed cells and the no-history
baseline (floor test); 3 replies per scenario x cell (n = 36 per cell). Scenario heterogeneity: logit offsets
~ N(0, 1.5) shared by all cells of a scenario (strong clustering; upsell rates in earlier runs ranged from 1/5 to 5/5
by scenario).
  1. Size of each test under its null, across base rates (strong null: the x variable has no effect).
  2. Holm family-wise error over the 24 planned tests under the global null (8 groups x 3 tests, independent groups,
     base rates cycling 0.05 / 0.2 / 0.5 / 0.8 for the midpoint and high50 tests and 0.02 / 0.1 for the floor test).
  3. Power (unadjusted alpha 0.05, and at the first Holm step 0.05/24).
  4. Coverage of the scenario-cluster bootstrap 95% CI for a cell rate (estimand: the population mean rate over
     scenarios), against a naive Wilson interval that ignores clustering.
Run: ~/.claude/bin/memguard -m 4 -- ../../../.venv/bin/python simulate.py
"""
from pathlib import Path

import numpy as np

import mid_analysis as A

HERE = Path(__file__).parent
NS, NR, SIG = 12, 3, 1.5
SIMS, PERMS = 400, 2000


def logistic(x):
    return 1 / (1 + np.exp(-x))


def logit(p):
    return np.log(p / (1 - p))


def draw(rng, levels: dict, offsets, nr=NR):
    """levels: x value -> logit at the scenario-average; returns obs dicts."""
    obs = []
    for s in range(NS):
        for x, mu in levels.items():
            p = logistic(mu + offsets[s])
            obs += [dict(scenario=f"s{s:02d}", x=x, y=int(v)) for v in rng.random(nr) < p]
    return obs


def floor_obs(rng, mu_rev, mu_base, offsets):
    obs = []
    for s in range(NS):
        p_r, p_b = logistic(mu_rev + offsets[s]), logistic(mu_base + offsets[s])
        obs += [dict(scenario=f"s{s:02d}", x=1, y=int(v)) for v in rng.random(3 * NR) < p_r]
        obs += [dict(scenario=f"s{s:02d}", x=0, y=int(v)) for v in rng.random(NR) < p_b]
    return obs


def pop_rate(mu, rng):
    return float(logistic(mu + rng.normal(0, SIG, 200000)).mean())


def wilson(k, n, z=1.96):
    p = k / n
    c = (p + z * z / (2 * n)) / (1 + z * z / n)
    h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return c - h, c + h


def main():
    rng = np.random.default_rng(20261029)
    off = lambda: rng.normal(0, SIG, NS)  # noqa: E731
    seed = lambda: int(rng.integers(1e9))  # noqa: E731
    L = ["# Simulation calibration of the planned tests (EXPLORATORY score-midpoint experiment)", "",
         f"Design per model x panel: {NS} scenarios x {NR} replies per cell; scenario logit offsets N(0, {SIG}) shared "
         f"across a scenario's cells; {SIMS} simulations per row unless stated; {PERMS} permutations per test. "
         "alpha = 0.05. Monte Carlo SE of a rate near 0.05 with 400 simulations ≈ 0.011.", "",
         "| Check | Rejection rate / coverage | Target |", "|---|---|---|"]

    def rate(fn, sims=SIMS):
        return float(np.mean([fn() for _ in range(sims)]))

    # 1. sizes
    for base in (0.05, 0.2, 0.5, 0.8):
        lv = {m: logit(base) for m in (0.2, 0.5, 0.8)}
        r = rate(lambda: A.strat_perm_test(draw(rng, lv, off()), PERMS, seed())["p"] < 0.05)
        L.append(f"| Size, midpoint test (3 midpoints at +0.20), no midpoint effect, base {base} | {r:.3f} | ≤ 0.05 |")
    for base in (0.2, 0.5, 0.8):
        lv = {0: logit(base), 1: logit(base)}
        r = rate(lambda: A.strat_perm_test(draw(rng, lv, off()), PERMS, seed())["p"] < 0.05)
        L.append(f"| Size, high50 test (0.95/0.45 vs 0.75/0.25), no effect, base {base} | {r:.3f} | ≤ 0.05 |")
    for base in (0.02, 0.1, 0.3):
        r = rate(lambda: A.strat_perm_test(floor_obs(rng, logit(base), logit(base), off()), PERMS, seed())["p"] < 0.05)
        L.append(f"| Size, floor test (3 reversed cells vs no history), no difference, base {base} | {r:.3f} | ≤ 0.05 |")

    # 2. Holm FWER over 24
    def fwer():
        ps = {}
        for g in range(8):
            b = (0.05, 0.2, 0.5, 0.8)[g % 4]
            ps[(g, "mid")] = A.strat_perm_test(draw(rng, {m: logit(b) for m in (0.2, 0.5, 0.8)}, off()), PERMS,
                                               seed())["p"]
            ps[(g, "hi")] = A.strat_perm_test(draw(rng, {0: logit(b), 1: logit(b)}, off()), PERMS, seed())["p"]
            fb = (0.02, 0.1)[g % 2]
            ps[(g, "floor")] = A.strat_perm_test(floor_obs(rng, logit(fb), logit(fb), off()), PERMS, seed())["p"]
        return min(A.holm(ps).values()) < 0.05
    L.append(f"| Holm family-wise error, 24 planned tests, global null (200 sims) | {rate(fwer, 200):.3f} | ≤ 0.05 |")

    # 3. power
    def power(make, label):
        res = [A.strat_perm_test(make(), PERMS, seed())["p"] for _ in range(SIMS)]
        L.append(f"| Power, {label} | {np.mean(np.array(res) < 0.05):.3f} (unadj.); "
                 f"{np.mean(np.array(res) < 0.05 / 24):.3f} (at 0.05/24) | (power) |")
    for lo, hi in ((0.2, 0.8), (0.1, 0.4), (0.3, 0.5)):
        lv = {0.2: logit(lo), 0.5: (logit(lo) + logit(hi)) / 2, 0.8: logit(hi)}
        power(lambda: draw(rng, lv, off()), f"midpoint test, logit-linear {lo:.0%} → {hi:.0%} at mid 0.2 → 0.8 "
              "(scenario-average logits)")
    for lo, hi in ((0.5, 0.8), (0.2, 0.5), (0.6, 0.75)):
        power(lambda: draw(rng, {0: logit(lo), 1: logit(hi)}, off()), f"high50 test, {lo:.0%} → {hi:.0%}")
    for b, rv in ((0.01, 0.10), (0.01, 0.20)):
        power(lambda: floor_obs(rng, logit(rv), logit(b), off()), f"floor test, reversed {rv:.0%} vs baseline {b:.0%}")

    # 4. CI coverage of a cell rate (n = 36 = 12 scenarios x 3)
    for base in (0.05, 0.2, 0.5):
        target = pop_rate(logit(base), rng)
        cov_c, cov_w = [], []
        for _ in range(SIMS):
            obs = draw(rng, {0: logit(base)}, off())
            c = A.cluster_ci(obs, reps=2000, seed=seed())
            cov_c.append(c["lo"] <= target <= c["hi"])
            lo, hi = wilson(c["k"], c["n"])
            cov_w.append(lo <= target <= hi)
        L.append(f"| CI coverage, cell rate, scenario-average logit at {base} (population rate {target:.2f}): "
                 f"cluster bootstrap / naive Wilson | {np.mean(cov_c):.3f} / {np.mean(cov_w):.3f} | 0.95 |")
    out = HERE / "simulation"
    out.mkdir(exist_ok=True)
    (out / "CALIBRATION.md").write_text("\n".join(L) + "\n")
    print("\n".join(L[4:]))


if __name__ == "__main__":
    main()
