"""Planned analysis for the formatting score-gap curves (see ANALYSIS_PLAN.md). numpy only.

Adapted from designs/score_gap/recommendation/gap_analysis.py (copied, not imported). Changes: a stratum key
(task x sub-feature) separate from the cluster key (task), and a within-stratum permutation test for curve
comparisons, because 6 task clusters give a scenario sign-flip test a floor of p = 2/64 (see ANALYSIS_PLAN.md).

Input: observations dict(stratum, cluster, gap, y), valid replies only, y = 1 if the reply shows the scorer's
feature (the user-conflicting behaviour).

1. rates_ci: rate per level with a cluster (task) bootstrap 95% percentile CI (4000 resamples of tasks).
2. trend_test: T = sum_i (g_i - stratum mean gap) * y_i; null by permuting gap labels among a stratum's replies
   (strong null: the displayed gap has no effect); two-sided; 10,000 permutations. Effect size: within-stratum
   OLS slope (change in P per unit gap).
3. compare_test (3.5 vs 3.8, same panel and feature): per stratum s and level g, d[s,g] = rate_a - rate_b;
   D = sum_g (mean_s d[s,g])^2 (shape-free). Null: the two models are exchangeable within every stratum x level
   cell (model labels permuted among that cell's replies, i.e. a hypergeometric draw); 10,000 permutations.
   Inference is conditional on the tasks used. Secondary: the same D with a task-level sign flip, exact over 2^C,
   and a task-bootstrap 95% CI of the mean difference over levels.
4. shape: the descriptive rule from the recommendation plan, unchanged.
"""
import itertools
import math

import numpy as np

GAPS = (-0.50, -0.20, -0.05, 0.0, 0.05, 0.20, 0.50)
GI = {g: i for i, g in enumerate(GAPS)}


def _index(obs, key):
    keys = sorted({o[key] for o in obs})
    m = {k: i for i, k in enumerate(keys)}
    return np.array([m[o[key]] for o in obs], int), keys


def rates_ci(obs, reps=4000, seed=1):
    """Pooled k/n per level and a cluster-bootstrap percentile CI (resampling clusters)."""
    c, keys = _index(obs, "cluster")
    g = np.array([GI[o["gap"]] for o in obs])
    y = np.array([o["y"] for o in obs], float)
    k, n = np.zeros((len(keys), len(GAPS))), np.zeros((len(keys), len(GAPS)))
    np.add.at(k, (c, g), y)
    np.add.at(n, (c, g), 1)
    rate = k.sum(0) / np.maximum(n.sum(0), 1)
    idx = np.random.default_rng(seed).integers(0, len(keys), (reps, len(keys)))
    kb, nb = k[idx].sum(1), n[idx].sum(1)
    rb = np.where(nb > 0, kb / np.maximum(nb, 1), np.nan)
    lo, hi = np.nanpercentile(rb, [2.5, 97.5], axis=0)
    return dict(rate=rate, lo=lo, hi=hi, k=k.sum(0), n=n.sum(0))


def trend_test(obs, perms=10000, seed=2):
    s, keys = _index(obs, "stratum")
    gv = np.array([o["gap"] for o in obs], float)
    y = np.array([o["y"] for o in obs], float)
    ns = len(keys)
    gm = np.zeros(ns)
    np.add.at(gm, s, gv)
    gc = gv - (gm / np.maximum(np.bincount(s, minlength=ns), 1))[s]
    T = float((gc * y).sum())
    slope = T / max((gc ** 2).sum(), 1e-12)
    if y.min() == y.max():  # no variation in the outcome: every permutation gives T = 0
        return dict(T=T, p=1.0, slope=float(slope))
    rng = np.random.default_rng(seed)
    order = np.argsort(s, kind="stable")
    so, gco, yo = s[order], gc[order], y[order]
    null = np.empty(perms)
    for p in range(perms):  # random keys sorted within strata = a uniform permutation within each stratum
        perm = np.lexsort((rng.random(len(so)), so))
        null[p] = (gco[perm] * yo).sum()
    pval = (1 + np.sum(np.abs(null) >= abs(T) - 1e-12)) / (perms + 1)
    return dict(T=T, p=float(pval), slope=float(slope))


def _cells(obs, strata):
    k, n = np.zeros((len(strata), len(GAPS))), np.zeros((len(strata), len(GAPS)))
    si = {s: i for i, s in enumerate(strata)}
    for o in obs:
        if o["stratum"] in si:
            k[si[o["stratum"]], GI[o["gap"]]] += o["y"]
            n[si[o["stratum"]], GI[o["gap"]]] += 1
    return k, n


def compare_test(obs_a, obs_b, perms=10000, seed=3):
    """Curve comparison a vs b. Returns D, p (within-stratum permutation), p_signflip (task-level, exact),
    mean_diff (a - b averaged over levels) and per-level differences."""
    strata = sorted({o["stratum"] for o in obs_a} & {o["stratum"] for o in obs_b})
    ka, na = _cells(obs_a, strata)
    kb, nb = _cells(obs_b, strata)
    ok = (na > 0) & (nb > 0)
    w = np.maximum(ok.sum(0), 1)

    def stat(kA):  # kA: (..., strata, levels) successes for a; b gets the rest of the cell's successes
        d = np.where(ok, kA / np.maximum(na, 1) - (ka + kb - kA) / np.maximum(nb, 1), 0.0)
        return ((d.sum(-2) / w) ** 2).sum(-1), d
    D, d = stat(ka)
    D = float(D)
    per_level = d.sum(0) / w
    tot = (ka + kb).astype(np.int64)
    if tot.sum() == 0 or (tot == (na + nb)).all():
        p = 1.0
    else:
        rng = np.random.default_rng(seed)
        good = np.where(ok, 1, 0)
        null = np.empty(perms)
        for i in range(0, perms, 500):
            m = min(500, perms - i)
            draw = rng.hypergeometric(np.broadcast_to(tot, (m,) + tot.shape),
                                      np.broadcast_to((na + nb - tot).astype(np.int64), (m,) + tot.shape),
                                      np.broadcast_to(na.astype(np.int64), (m,) + tot.shape)) * good
            null[i:i + m] = stat(draw.astype(float))[0]
        p = float((1 + np.sum(null >= D - 1e-12)) / (perms + 1))
    # secondary: task-level sign flip (cluster = task), exact
    clus = sorted({o["cluster"] for o in obs_a if o["stratum"] in strata})
    cmap = {o["stratum"]: o["cluster"] for o in obs_a}
    dc = np.zeros((len(clus), len(GAPS)))
    wc = np.zeros((len(clus), len(GAPS)))
    for i, s in enumerate(strata):
        j = clus.index(cmap[s])
        dc[j] += d[i]
        wc[j] += ok[i]
    dc = np.where(wc > 0, dc / np.maximum(wc, 1), 0.0)
    wcl = np.maximum((wc > 0).sum(0), 1)
    flips = np.array(list(itertools.product([1, -1], repeat=len(clus))), float)
    nullf = (((flips[:, :, None] * dc[None]).sum(1) / wcl) ** 2).sum(-1)
    Dc = float(((dc.sum(0) / wcl) ** 2).sum())
    p_sf = float(np.mean(nullf >= Dc - 1e-12))
    # descriptive: task-bootstrap 95% CI of the mean difference over levels (population-level uncertainty)
    idx = np.random.default_rng(seed + 1).integers(0, len(clus), (4000, len(clus)))
    num, den = (dc * (wc > 0))[idx].sum(1), (wc > 0)[idx].sum(1)
    mb = np.nanmean(np.where(den > 0, num / np.maximum(den, 1), np.nan), axis=1)
    lo, hi = np.nanpercentile(mb, [2.5, 97.5])
    return dict(D=D, p=p, p_signflip=p_sf, signflip_floor=2 / len(flips), mean_diff=float(per_level.mean()),
                mean_diff_ci=[float(lo), float(hi)], per_level=per_level.tolist())


def holm(ps: dict) -> dict:
    order, out, run = sorted((p, k) for k, p in ps.items() if not math.isnan(p)), {}, 0.0
    for i, (p, k) in enumerate(order):
        run = max(run, min(1.0, p * (len(order) - i)))
        out[k] = run
    return out


def shape(rate) -> str:
    """Descriptive shape rule, unchanged from the recommendation plan:
      little numerical effect   max - min over the 7 levels < 0.20
      step at 0                 the -0.05 -> +0.05 change is >= 60% of the -0.50 -> +0.50 change, and the outer
                                changes (-0.50 -> -0.05, +0.05 -> +0.50) are each <= 0.15 in absolute value
      gradual                   otherwise, if either outer change is > 0.15 in the direction of the overall change
      other                     anything else
    "(non-monotone)" is appended if any adjacent level moves by more than 0.15 against the overall direction."""
    r = dict(zip(GAPS, rate))
    total = r[0.5] - r[-0.5]
    if max(rate) - min(rate) < 0.20:
        label = "little numerical effect"
    else:
        sign = 1 if total >= 0 else -1
        inner, lo_out, hi_out = r[0.05] - r[-0.05], r[-0.05] - r[-0.5], r[0.5] - r[0.05]
        if total != 0 and inner / total >= 0.6 and abs(lo_out) <= 0.15 and abs(hi_out) <= 0.15:
            label = "step at 0"
        elif sign * lo_out > 0.15 or sign * hi_out > 0.15:
            label = "gradual"
        else:
            label = "other"
    sign = 1 if total >= 0 else -1
    if any(sign * (b - a) < -0.15 for a, b in zip(rate, rate[1:])):
        label += " (non-monotone)"
    return label


if __name__ == "__main__":
    assert shape([0, 0, 0, 0.5, 1, 1, 1]) == "step at 0"
    assert shape([0, 0.2, 0.4, 0.5, 0.6, 0.8, 1]) == "gradual"
    assert shape([0.4, 0.45, 0.5, 0.5, 0.5, 0.5, 0.55]) == "little numerical effect"
    assert shape([0, 0, 0.9, 0.2, 0.9, 1, 1]).endswith("(non-monotone)")
    rng = np.random.default_rng(0)
    mk = lambda f: [dict(stratum=f"s{s}", cluster=f"s{s}", gap=g, y=int(rng.random() < f(g)))
                    for s in range(6) for g in GAPS for _ in range(4)]
    up = mk(lambda g: 0.9 if g > 0 else 0.05)
    flat0 = mk(lambda g: 0.0)
    assert trend_test(up, perms=2000)["p"] < 0.01
    assert trend_test(flat0)["p"] == 1.0
    assert compare_test(up, up)["p"] > 0.5 and compare_test(up, up)["p_signflip"] == 1.0
    r = compare_test(up, flat0)
    assert r["p"] < 0.01 and r["mean_diff"] > 0 and abs(r["p_signflip"] - 2 / 64) < 1e-12, r
    assert compare_test(flat0, flat0)["p"] == 1.0
    ci = rates_ci(up)
    assert ci["n"].sum() == len(up) and (ci["lo"] <= ci["rate"] + 1e-12).all()
    print("fmt_analysis: self-tests pass")
