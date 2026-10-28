"""Statistics shared by all four analyses.

Counts are dicts: counts[(group, scenario)] = [k, n], where `group` is any hashable (e.g. (model, cell)).

- fisher_greater / fisher_two / holm: as in designs/rl_context/run_domains.py.
- boot_ci: two-stage bootstrap (resample scenarios, then binomial resampling within each scenario-group).
- interaction_test: model x condition difference-in-differences D = (r[m1,c1] - r[m1,c2]) - (r[m2,c1] - r[m2,c2]),
  pooled over scenarios. We do NOT permute model labels: that null ignores baseline model differences.
  Null (default scale="rd"): within each scenario, p = mu_s + a_s*[model = m2] + b_s*[cond = c2] on the PROBABILITY
  scale. That allows arbitrary scenario heterogeneity, baseline model differences and condition effects, with no
  model x condition interaction in rates. It is fitted per scenario by the n-weighted projection onto
  p00 - p01 - p10 + p11 = 0, clipped to [0, 1].
  Why rates: the reported contrasts are rate differences. On the log-odds scale (scale="logit", kept as a
  sensitivity check), cells at 0% leave unlimited room, so even "0.9 vs 0.1 rewarded, 0 vs 0 penalised" is
  compatible with no interaction. That null is uninformative for the floor-heavy data these experiments produce.
  p = parametric-bootstrap P(|D*| >= |D|) under the fitted null.
  `calibrate_interaction` re-applies the whole test to datasets simulated from the fitted null and reports the
  empirical rejection rate at alpha = 0.05 (should be about 0.05 or lower).
"""
from __future__ import annotations

import math
import random
from math import comb

import numpy as np


def fisher_greater(a, n1, b, n2):
    if not n1 or not n2:
        return math.nan
    k, n = a + b, n1 + n2
    return sum(comb(n1, x) * comb(n2, k - x) for x in range(a, min(k, n1) + 1)) / comb(n, k)


def fisher_two(a, n1, b, n2):
    if not n1 or not n2:
        return math.nan
    k, n = a + b, n1 + n2
    pmf = lambda x: comb(n1, x) * comb(n2, k - x) / comb(n, k)  # noqa: E731
    obs = pmf(a)
    return min(1.0, sum(pmf(x) for x in range(max(0, k - n2), min(k, n1) + 1) if pmf(x) <= obs * (1 + 1e-9)))


def holm(ps: dict) -> dict:
    items = sorted((p, k) for k, p in ps.items() if p is not None and not math.isnan(p))
    out, run = {}, 0.0
    for i, (p, k) in enumerate(items):
        run = max(run, min(1.0, p * (len(items) - i)))
        out[k] = run
    return out


def kn(counts, group, scenarios=None):
    k = n = 0
    for (g, s), (a, b) in counts.items():
        if g == group and (scenarios is None or s in scenarios):
            k, n = k + a, n + b
    return k, n


def rate(counts, group, scenarios=None):
    k, n = kn(counts, group, scenarios)
    return k / n if n else math.nan


def boot_ci(counts, fn, reps=4000, seed=20261028, alpha=0.05):
    """fn(rr) -> statistic, where rr(group) is the pooled rate in a bootstrap replicate."""
    scen = sorted({s for _, s in counts})
    groups = sorted({g for g, _ in counts}, key=repr)
    rng, vals = random.Random(seed), []
    for _ in range(reps):
        sample = [rng.choice(scen) for _ in scen]
        cache = {}
        for g in groups:
            k = n = 0
            for s in sample:
                a, b = counts.get((g, s), (0, 0))
                if b:
                    p = a / b
                    k += sum(rng.random() < p for _ in range(b))
                    n += b
            cache[g] = k / n if n else math.nan
        v = fn(lambda g: cache.get(g, math.nan))
        if not math.isnan(v):
            vals.append(v)
    vals.sort()
    if not vals:
        return [math.nan, math.nan]
    return [vals[int(alpha / 2 * (len(vals) - 1))], vals[int((1 - alpha / 2) * (len(vals) - 1))]]


def directional(counts, ga, gb, reps=4000, seed=20261028) -> dict:
    """Group a > group b: one-sided Fisher on pooled counts + two-stage bootstrap CI of the difference."""
    ka, na = kn(counts, ga)
    kb, nb = kn(counts, gb)
    ci = boot_ci(counts, lambda rr: rr(ga) - rr(gb), reps, seed)
    est = (ka / na if na else math.nan) - (kb / nb if nb else math.nan)
    p = fisher_greater(ka, na, kb, nb)
    return dict(a=f"{ka}/{na}", b=f"{kb}/{nb}", est=est, p=p, ci=ci, passed=bool(p < 0.05 and ci[0] > 0))


# ---------------------------------------------------------------- calibrated interaction test

CELLS4 = ((0, 0), (0, 1), (1, 0), (1, 1))  # (model index, condition index)


def _arrays(counts, m1, m2, c1, c2):
    scen = sorted({s for _, s in counts})
    K = np.zeros((len(scen), 4))
    N = np.zeros((len(scen), 4))
    for i, s in enumerate(scen):
        for j, (mi, ci) in enumerate(CELLS4):
            a, b = counts.get((((m1, m2)[mi], (c1, c2)[ci]), s), (0, 0))
            K[i, j], N[i, j] = a, b
    return scen, K, N


def _stat(K, N):
    k, n = K.sum(-2), N.sum(-2)
    r = np.divide(k, n, out=np.full_like(k, np.nan), where=n > 0)
    return (r[..., 0] - r[..., 1]) - (r[..., 2] - r[..., 3])


def fit_null(K, N, pseudo=0.1, iters=50):
    """Per-scenario additive logit fit (mu, a, b); returns fitted probabilities, shape (S, 4)."""
    X = np.array([[1, mi, ci] for mi, ci in CELLS4], float)
    P = np.zeros_like(K)
    for i in range(K.shape[0]):
        w = (N[i] > 0).astype(float)
        k, n = K[i] + pseudo * w, N[i] + 2 * pseudo * w
        th = np.zeros(3)
        for _ in range(iters):
            p = 1 / (1 + np.exp(-(X @ th)))
            g = X.T @ (k - n * p)
            H = (X * (n * p * (1 - p))[:, None]).T @ X + 1e-6 * np.eye(3)
            step = np.linalg.solve(H, g)
            th += step
            if np.abs(step).max() < 1e-8:
                break
        P[i] = 1 / (1 + np.exp(-(X @ th)))
    return P


def fit_null_rd(K, N, pseudo=0.1, iters=50):
    """Per-scenario n-weighted projection of observed rates onto the additive (no-interaction) rate model."""
    c = np.array([1.0, -1.0, -1.0, 1.0])
    P = np.zeros_like(K)
    for i in range(K.shape[0]):
        n = N[i]
        ph = np.where(n > 0, (K[i] + pseudo) / (n + 2 * pseudo), 0.5)
        if (n == 0).any():  # a missing cell: no constraint is identifiable, keep observed rates
            P[i] = ph
            continue
        w_inv = 1.0 / n
        p = ph.copy()
        for _ in range(iters):  # alternate: hyperplane projection, then box clipping
            p = p - (c @ p) * w_inv * c / (c @ (w_inv * c))
            p = np.clip(p, 0.0, 1.0)
            if abs(c @ p) < 1e-10:
                break
        P[i] = p
    return P


def _test(K, N, reps, rng, scale="rd"):
    D = float(_stat(K, N))
    P0 = fit_null_rd(K, N) if scale == "rd" else fit_null(K, N)
    sims = rng.binomial(N.astype(int)[None], P0[None], size=(reps,) + K.shape)
    Ds = _stat(sims.astype(float), np.broadcast_to(N, sims.shape))
    Ds = Ds[~np.isnan(Ds)]
    return D, float((np.abs(Ds) >= abs(D) - 1e-12).mean()) if len(Ds) else math.nan, P0


def interaction_test(counts, m1, m2, c1, c2, reps=4000, seed=20261028, scale="rd") -> dict:
    """Difference-in-differences (m1: c1 - c2) - (m2: c1 - c2), with a calibrated parametric-bootstrap p-value and
    a two-stage bootstrap CI. Groups in `counts` must be (model, condition) tuples."""
    scen, K, N = _arrays(counts, m1, m2, c1, c2)
    rng = np.random.default_rng(seed)
    D, p, _ = _test(K, N, reps, rng, scale)
    ci = boot_ci(counts, lambda rr: (rr((m1, c1)) - rr((m1, c2))) - (rr((m2, c1)) - rr((m2, c2))), 2000, seed)
    return dict(est=D, p=p, ci=ci, scenarios=len(scen), scale=scale)


def calibrate_interaction(counts, m1, m2, c1, c2, sims=200, reps=500, seed=7, scale="rd") -> dict:
    """Empirical size of interaction_test at alpha 0.05 under the null fitted to these data (same scale)."""
    scen, K, N = _arrays(counts, m1, m2, c1, c2)
    rng = np.random.default_rng(seed)
    P0 = fit_null_rd(K, N) if scale == "rd" else fit_null(K, N)
    rej = 0
    for _ in range(sims):
        Ks = rng.binomial(N.astype(int), P0).astype(float)
        _, p, _ = _test(Ks, N, reps, rng, scale)
        rej += p < 0.05
    return dict(size=rej / sims, sims=sims)


def check():
    assert abs(fisher_greater(8, 10, 2, 10) - 0.0115) < 1e-3
    assert holm({"a": 0.01, "b": 0.04})["b"] == 0.04 and holm({"a": 0.01, "b": 0.04})["a"] == 0.02
    rng = random.Random(1)
    # baseline model difference + condition effect + scenario heterogeneity, no rate interaction
    counts = {}
    for s in range(6):
        h = rng.uniform(-0.15, 0.15)
        for m, a in (("A", 0.0), ("B", 0.3)):
            for c, b in (("x", 0.3), ("y", 0.0)):
                p = min(1, max(0, 0.2 + h + a + b))
                counts[((m, c), s)] = [sum(rng.random() < p for _ in range(8)), 8]
    t = interaction_test(counts, "A", "B", "x", "y", reps=2000)
    assert 0 <= t["p"] <= 1 and t["scenarios"] == 6
    # strong interaction -> should reject
    counts2 = {}
    for s in range(6):
        for m, pr in (("A", (0.9, 0.0)), ("B", (0.1, 0.0))):
            for c, p in zip(("x", "y"), pr):
                counts2[((m, c), s)] = [round(p * 8), 8]
    assert interaction_test(counts2, "A", "B", "x", "y", reps=2000)["p"] < 0.01
    assert interaction_test(counts2, "A", "B", "x", "y", reps=2000, scale="logit")["p"] > 0.01  # floor: logit blind
    cal = calibrate_interaction(counts, "A", "B", "x", "y", sims=100, reps=400)
    assert cal["size"] <= 0.12, cal
    return cal
