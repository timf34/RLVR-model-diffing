"""EXPLORATORY score-midpoint experiment: planned statistics (see ANALYSIS_PLAN.md). numpy only.

Observations are dicts (scenario, x, y), valid replies only; y = 1 for the user-conflicting behaviour (upsell /
completing the reserved send).
  cluster_ci        pooled rate with a scenario-cluster percentile bootstrap 95% CI (resample the 12 scenarios)
  strat_perm_test   T = sum_i (x_i - mean x of scenario s(i)) * y_i, two-sided, null by permuting x among each
                    scenario's replies (strong null: x has no effect). Effect: within-scenario OLS slope of y on x.
                    Used for all three planned tests:
                      midpoint  x = midpoint (0.20 / 0.50 / 0.80) over the three +0.20 cells
                      high50    x = 1 for 0.95/0.45, 0 for 0.75/0.25          (slope = within-scenario difference)
                      floor     x = 1 for the three reversed cells, 0 for the no-history baseline
  holm              Holm step-down adjusted p-values over a family
"""
from __future__ import annotations

import math

import numpy as np


def cluster_ci(obs, reps=4000, seed=3) -> dict:
    sc = sorted({o["scenario"] for o in obs})
    if not sc:
        return dict(k=0, n=0, rate=float("nan"), lo=float("nan"), hi=float("nan"))
    k = np.array([sum(o["y"] for o in obs if o["scenario"] == s) for s in sc], float)
    n = np.array([sum(1 for o in obs if o["scenario"] == s) for s in sc], float)
    idx = np.random.default_rng(seed).integers(0, len(sc), (reps, len(sc)))
    boot = k[idx].sum(1) / n[idx].sum(1)
    return dict(k=int(k.sum()), n=int(n.sum()), rate=float(k.sum() / n.sum()),
                lo=float(np.percentile(boot, 2.5)), hi=float(np.percentile(boot, 97.5)))


def strat_perm_test(obs, perms=10000, seed=2) -> dict:
    sc = sorted({o["scenario"] for o in obs})
    groups = []
    T, sxx = 0.0, 0.0
    for s in sc:
        x = np.array([o["x"] for o in obs if o["scenario"] == s], float)
        y = np.array([o["y"] for o in obs if o["scenario"] == s], float)
        if len(x) < 2 or np.ptp(x) == 0:
            continue  # a scenario with one level carries no within-scenario information
        xc = x - x.mean()
        T += float((xc * y).sum())
        sxx += float((xc ** 2).sum())
        groups.append((xc, y))
    if not groups:
        return dict(T=0.0, p=float("nan"), slope=float("nan"), n=len(obs))
    rng = np.random.default_rng(seed)
    null = np.zeros(perms)
    for xc, y in groups:
        if y.min() == y.max():
            null += (xc.sum() * y[0])  # = 0: constant y contributes nothing under any permutation
            continue
        order = rng.random((perms, len(xc))).argsort(1)
        null += (xc[order] * y[None, :]).sum(1)
    p = (1 + np.sum(np.abs(null) >= abs(T) - 1e-12)) / (perms + 1)
    return dict(T=T, p=float(p), slope=T / sxx if sxx else float("nan"), n=len(obs))


def holm(ps: dict) -> dict:
    order, out, run = sorted((p, k) for k, p in ps.items() if not math.isnan(p)), {}, 0.0
    for i, (p, k) in enumerate(order):
        run = max(run, min(1.0, p * (len(order) - i)))
        out[k] = run
    for k, p in ps.items():
        if math.isnan(p):
            out[k] = float("nan")
    return out


if __name__ == "__main__":
    rng = np.random.default_rng(0)
    obs = [dict(scenario=f"s{s}", x=m, y=int(rng.random() < m)) for s in range(12) for m in (0.2, 0.5, 0.8)
           for _ in range(3)]
    r = strat_perm_test(obs, perms=4000)
    assert r["p"] < 0.01 and 0.5 < r["slope"] < 1.5, r
    flat = [dict(o, y=0) for o in obs]
    assert strat_perm_test(flat)["p"] == 1.0
    assert holm({"a": 0.01, "b": 0.04, "c": 0.5}) == {"a": 0.03, "b": 0.08, "c": 0.5}
    c = cluster_ci(obs)
    assert c["lo"] <= c["rate"] <= c["hi"]
    print("mid_analysis: self-tests pass")
