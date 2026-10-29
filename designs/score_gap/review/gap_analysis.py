"""Planned analysis for the review-rating score-gap curve (see ANALYSIS_PLAN.md). numpy only.

Input: observations dict(scenario, gap, y) for one model x panel, valid replies only. y is the rating (primary),
1/0 for rating >= threshold, or the number of planted problems named (secondary).

1. Mean per gap level (pooled over replies), with a scenario-cluster 95% CI: cluster-robust (CR1) standard error of
   the pooled mean, t quantile with (number of scenarios - 1) df. With 6 scenarios a t interval is used rather than a
   bootstrap percentile interval, which under-covers with so few clusters (simulation/CALIBRATION.md checks coverage).
2. Trend test (6 tests, Holm over 6): T = sum_i (g_i - mean gap of scenario s(i)) * y_i, two-sided, null by permuting
   gap labels among a scenario's replies (strong null: the displayed gap has no effect). Effect size: within-scenario
   OLS slope of y on g (= change in mean rating from gap -0.5 to +0.5).
3. 3.8 vs 3.5 curve comparison per panel (3 tests, Holm over 3). Per scenario s, d[s,g] = mean_3.8[s,g] -
   mean_3.5[s,g]; summaries shift_s = mean over levels of d[s,.] and slope_s = OLS slope of d[s,.] on g. Hotelling's
   T^2 on the 6 (shift_s, slope_s) pairs: F = (S-2)/(2(S-1)) T^2 ~ F(2, S-2) (scenario-level, so scenario clustering is
   respected). Sensitivity: the template's shape-free statistic D = sum_g (mean_s d[s,g])^2 with an exact scenario
   sign-flip null (2^6 flips; its p floor is 1/32, so it cannot pass Holm over 3 on its own).
4. Shape reading, descriptive (rule in shape()).
"""
import itertools
import math

import numpy as np

GAPS = (-0.50, -0.20, -0.05, 0.0, 0.05, 0.20, 0.50)
T975 = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571, 6: 2.447, 7: 2.365, 8: 2.306, 9: 2.262, 10: 2.228,
        11: 2.201, 12: 2.179}


def _arrays(obs):
    scen = sorted({o["scenario"] for o in obs})
    si = {s: i for i, s in enumerate(scen)}
    gi = {g: i for i, g in enumerate(GAPS)}
    return (np.array([si[o["scenario"]] for o in obs]), np.array([gi[o["gap"]] for o in obs]),
            np.array([o["y"] for o in obs], float), len(scen))


def cell_sums(s, g, y, ns):
    """sum[s,g], n[s,g]."""
    k, n = np.zeros((ns, len(GAPS))), np.zeros((ns, len(GAPS)))
    np.add.at(k, (s, g), y)
    np.add.at(n, (s, g), 1)
    return k, n


def cluster_mean_ci(k, n, lo_hi=None):
    """Pooled mean sum(k)/sum(n) over scenarios (rows) and its CR1 cluster t interval. k, n: arrays over scenarios."""
    k, n = np.asarray(k, float), np.asarray(n, float)
    keep = n > 0
    k, n = k[keep], n[keep]
    S, N = len(n), n.sum()
    if N == 0:
        return math.nan, math.nan, math.nan
    m = k.sum() / N
    if S < 2:
        return m, math.nan, math.nan
    se = math.sqrt(S / (S - 1) * (((k - m * n) ** 2).sum())) / N
    t = T975.get(S - 1, 1.96)
    lo, hi = m - t * se, m + t * se
    if lo_hi:
        lo, hi = max(lo, lo_hi[0]), min(hi, lo_hi[1])
    return m, lo, hi


def level_stats(obs, bounds=None):
    """Mean per level with cluster CIs; also k (sum) and n per level."""
    s, g, y, ns = _arrays(obs)
    k, n = cell_sums(s, g, y, ns)
    out = dict(mean=[], lo=[], hi=[], n=n.sum(0).tolist(), sum=k.sum(0).tolist())
    for j in range(len(GAPS)):
        m, lo, hi = cluster_mean_ci(k[:, j], n[:, j], bounds)
        out["mean"].append(m)
        out["lo"].append(lo)
        out["hi"].append(hi)
    return out


def trend_test(obs, perms=10000, seed=2):
    """Stratified permutation test of a linear trend in gap: dict(T, p two-sided, slope per unit gap)."""
    s, g, y, ns = _arrays(obs)
    gv = np.array(GAPS)[g]
    cnt = np.bincount(s, minlength=ns)
    gm = np.bincount(s, weights=gv, minlength=ns) / np.maximum(cnt, 1)
    gc = gv - gm[s]
    yc = y - (np.bincount(s, weights=y, minlength=ns) / np.maximum(cnt, 1))[s]
    T = float((gc * y).sum())
    rng = np.random.default_rng(seed)
    null = np.zeros(perms)
    for i in range(ns):
        idx = np.flatnonzero(s == i)
        if len(idx) < 2:
            continue
        perm = rng.random((perms, len(idx))).argsort(1)
        null += (gc[idx][perm] * y[idx]).sum(1)
    pval = (1 + np.sum(np.abs(null) >= abs(T) - 1e-9)) / (perms + 1)
    slope = float((gc * yc).sum() / max((gc ** 2).sum(), 1e-12))
    return dict(T=T, p=float(pval), slope=slope)


def _diff_matrix(obs_a, obs_b):
    scen = sorted({o["scenario"] for o in obs_a} & {o["scenario"] for o in obs_b})
    sub = lambda obs: [o for o in obs if o["scenario"] in scen]
    sa, ga, ya, _ = _arrays(sub(obs_a))
    sb, gb, yb, _ = _arrays(sub(obs_b))
    ka, na = cell_sums(sa, ga, ya, len(scen))
    kb, nb = cell_sums(sb, gb, yb, len(scen))
    ok = (na > 0) & (nb > 0)
    d = np.where(ok, ka / np.maximum(na, 1) - kb / np.maximum(nb, 1), np.nan)
    return d, ok


def _summaries(d):
    """Per scenario (shift, slope) of the difference curve, using the levels present."""
    gv = np.array(GAPS)
    out = []
    for row in d:
        keep = ~np.isnan(row)
        x, v = gv[keep], row[keep]
        xc = x - x.mean()
        out.append((v.mean(), (xc * (v - v.mean())).sum() / max((xc ** 2).sum(), 1e-12)))
    return np.array(out)


def hotelling(X):
    """One-sample Hotelling T^2 test of mean zero for the rows of X (S x 2). Returns (F, p)."""
    S, p = X.shape
    xbar = X.mean(0)
    C = np.cov(X, rowvar=False, ddof=1)
    if not np.all(np.isfinite(C)):
        return math.nan, math.nan
    C = C + np.eye(p) * 1e-9 * max(np.trace(C), 1e-12)
    T2 = S * xbar @ np.linalg.solve(C, xbar)
    nu = S - p
    F = (nu / (p * (S - 1))) * T2
    if p == 2:
        pv = (nu / (nu + 2 * F)) ** (nu / 2)
    else:
        raise NotImplementedError
    return float(F), float(pv)


def curve_compare(obs_a, obs_b):
    """Planned comparison of two curves (a minus b): Hotelling on per-scenario (shift, slope); sign-flip D too."""
    d, ok = _diff_matrix(obs_a, obs_b)
    X = _summaries(d)
    F, p = hotelling(X)
    dz = np.where(np.isnan(d), 0.0, d)
    w = ok.sum(0)

    def stat(signs):
        m = (signs[:, :, None] * dz[None]).sum(1) / np.maximum(w, 1)
        return (m ** 2).sum(-1)
    flips = np.array(list(itertools.product([1, -1], repeat=len(d))), float)
    D = float(stat(np.ones((1, len(d))))[0])
    p_flip = float(np.mean(stat(flips) >= D - 1e-12))
    per_level = (dz.sum(0) / np.maximum(w, 1)).tolist()
    return dict(F=F, p=p, shift=float(X[:, 0].mean()), slope_diff=float(X[:, 1].mean()),
                shift_by_scenario=X[:, 0].tolist(), slope_by_scenario=X[:, 1].tolist(),
                per_level=per_level, D=D, p_signflip=p_flip)


def holm(ps: dict) -> dict:
    order, out, run = sorted((p, k) for k, p in ps.items() if not math.isnan(p)), {}, 0.0
    for i, (p, k) in enumerate(order):
        run = max(run, min(1.0, p * (len(order) - i)))
        out[k] = run
    return out


def shape(vals, little=1.0, outer=0.75) -> str:
    """Descriptive shape rule (fixed before data). Defaults are for the mean rating (points on the 0-10 scale);
    the template's binary thresholds (little=0.20, outer=0.15) are used for the >= threshold share.
      little numerical effect   max - min over the 7 levels < little
      step at 0                 the -0.05 -> +0.05 change is >= 60% of the -0.50 -> +0.50 change, and the outer
                                changes (-0.50 -> -0.05, +0.05 -> +0.50) are each <= outer in absolute value
      gradual                   otherwise, if either outer change is > outer in the direction of the overall change
      other                     anything else
    "(non-monotone)" is appended if any adjacent step goes more than `outer` against the overall direction."""
    r = dict(zip(GAPS, vals))
    total = r[0.5] - r[-0.5]
    sign = 1 if total >= 0 else -1
    if max(vals) - min(vals) < little:
        label = "little numerical effect"
    else:
        inner, lo_out, hi_out = r[0.05] - r[-0.05], r[-0.05] - r[-0.5], r[0.5] - r[0.05]
        if total != 0 and inner / total >= 0.6 and abs(lo_out) <= outer and abs(hi_out) <= outer:
            label = "step at 0"
        elif sign * lo_out > outer or sign * hi_out > outer:
            label = "gradual"
        else:
            label = "other"
    if any(sign * (b - a) < -outer for a, b in zip(vals, vals[1:])):
        label += " (non-monotone)"
    return label


if __name__ == "__main__":
    assert shape([5, 5, 5, 6, 7.5, 7.5, 7.5]) == "step at 0"
    assert shape([4, 5, 5.5, 6, 6.5, 7, 8]) == "gradual"
    assert shape([5, 5.2, 5.1, 5.3, 5.2, 5.4, 5.5]) == "little numerical effect"
    assert shape([0, 0, 0.9, 0.2, 0.9, 1, 1], 0.2, 0.15).endswith("(non-monotone)")
    rng = np.random.default_rng(0)
    obs = [dict(scenario=f"s{s}", gap=g, y=float(round(5 + 3 * g + rng.normal(0, 1))))
           for s in range(6) for g in GAPS for _ in range(4)]
    assert trend_test(obs, perms=2000)["p"] < 0.01
    flat = [dict(o, y=float(round(5 + rng.normal(0, 1)))) for o in obs]
    assert curve_compare(obs, obs)["p_signflip"] == 1.0
    c = curve_compare([dict(o, y=o["y"] + 2) for o in obs], flat)
    assert c["p"] < 0.05 and c["shift"] > 1.5, c
    m, lo, hi = cluster_mean_ci([10, 12, 14], [4, 4, 4])
    assert abs(m - 3.0) < 1e-12 and lo < 3 < hi
    print("gap_analysis: self-tests pass")
