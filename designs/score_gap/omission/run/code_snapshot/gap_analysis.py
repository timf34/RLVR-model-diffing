"""Planned analysis for the score-gap curve, omission environment (see ANALYSIS_PLAN.md). numpy only; used by
run_gap.py and simulate.py. Copied unchanged in its code from designs/score_gap/recommendation/gap_analysis.py;
only this docstring differs.

Input: a list of observations dict(model, panel, gap, scenario, y) with y = 1 for an omission (rule label omits or
denies; the judge's label only where the rule is not confident), valid replies only.

1. Rates per gap level per model x panel, with scenario-cluster bootstrap 95% CIs (resample scenarios).
2. Trend test (4 tests: 2 models x 2 panels, Holm over 4): T = sum_i (g_i - mean gap of scenario s(i)) * y_i,
   two-sided, null by permuting the gap labels among a scenario's replies (stratified permutation; strong null:
   gap has no effect).
3. Curve comparisons: planned family = 3.8 vs 3.5 in each panel (Holm over 2); secondary family = rl vs ordinary
   for each model (Holm over 2). For groups a, b, per scenario s and level g the difference
   d[s,g] = rate_a[s,g] - rate_b[s,g];
   statistic D = sum_g (mean_s d[s,g])^2 (shape-free curve difference); null by swapping a and b within whole
   scenarios (sign flip of each scenario's difference vector), exact over all 2^12 flips.
4. Shape reading, descriptive (rule in shape()).
"""
import itertools
import math

import numpy as np

GAPS = (-0.50, -0.20, -0.05, 0.0, 0.05, 0.20, 0.50)


def _arrays(obs):
    scen = sorted({o["scenario"] for o in obs})
    si = {s: i for i, s in enumerate(scen)}
    gi = {g: i for i, g in enumerate(GAPS)}
    return (np.array([si[o["scenario"]] for o in obs]), np.array([gi[o["gap"]] for o in obs]),
            np.array([o["y"] for o in obs], float), len(scen))


def cell_rates(s, g, y, ns):
    """k[s,g], n[s,g]."""
    k, n = np.zeros((ns, len(GAPS))), np.zeros((ns, len(GAPS)))
    np.add.at(k, (s, g), y)
    np.add.at(n, (s, g), 1)
    return k, n


def rates_ci(obs, reps=4000, seed=1):
    """Pooled rate per level and scenario-cluster bootstrap percentile CI."""
    s, g, y, ns = _arrays(obs)
    k, n = cell_rates(s, g, y, ns)
    rate = k.sum(0) / np.maximum(n.sum(0), 1)
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, ns, (reps, ns))
    kb, nb = k[idx].sum(1), n[idx].sum(1)
    rb = np.where(nb > 0, kb / np.maximum(nb, 1), np.nan)
    lo, hi = np.nanpercentile(rb, [2.5, 97.5], axis=0)
    return dict(rate=rate, lo=lo, hi=hi, k=k.sum(0), n=n.sum(0))


def trend_test(obs, perms=10000, seed=2):
    """Stratified permutation test of a linear trend in gap; returns (T, two-sided p, slope per unit gap)."""
    s, g, y, ns = _arrays(obs)
    gv = np.array(GAPS)[g]
    gm = np.zeros(ns)
    np.add.at(gm, s, gv)
    cnt = np.bincount(s, minlength=ns)
    gc = gv - (gm / np.maximum(cnt, 1))[s]
    T = float((gc * y).sum())
    rng = np.random.default_rng(seed)
    order = np.argsort(s, kind="stable")
    bounds = np.r_[0, np.cumsum(np.bincount(s[order], minlength=ns))]
    gco, yo = gc[order], y[order]
    null = np.empty(perms)
    for p in range(perms):
        perm = np.concatenate([rng.permutation(np.arange(bounds[i], bounds[i + 1])) for i in range(ns)])
        null[p] = (gco[perm] * yo).sum()
    pval = (1 + np.sum(np.abs(null) >= abs(T) - 1e-12)) / (perms + 1)
    slope = T / max((gc ** 2).sum(), 1e-12)  # within-scenario OLS slope of P(upsell) on gap
    return dict(T=T, p=float(pval), slope=float(slope))


def curve_diff_test(obs_a, obs_b):
    """Scenario-level sign-flip test of identical curves. Scenarios present in both groups only."""
    scen = sorted({o["scenario"] for o in obs_a} & {o["scenario"] for o in obs_b})
    sub = lambda obs: [o for o in obs if o["scenario"] in scen]
    ka, na = cell_rates(*_arrays(sub(obs_a))[:3], len(scen))
    kb, nb = cell_rates(*_arrays(sub(obs_b))[:3], len(scen))
    ok = (na > 0) & (nb > 0)
    d = np.where(ok, ka / np.maximum(na, 1) - kb / np.maximum(nb, 1), 0.0)
    w = ok.sum(0)

    def stat(signs):
        m = (signs[:, :, None] * d[None]).sum(1) / np.maximum(w, 1)
        return (m ** 2).sum(-1)
    flips = np.array(list(itertools.product([1, -1], repeat=len(scen))), float)
    null = stat(flips)
    D = float(stat(np.ones((1, len(scen))))[0])
    p = float(np.mean(null >= D - 1e-12))
    mean_diff = float((d.sum(0) / np.maximum(w, 1)).mean())
    return dict(D=D, p=p, mean_diff=mean_diff, per_level=(d.sum(0) / np.maximum(w, 1)).tolist())


def holm(ps: dict) -> dict:
    order, out, run = sorted((p, k) for k, p in ps.items() if not math.isnan(p)), {}, 0.0
    for i, (p, k) in enumerate(order):
        run = max(run, min(1.0, p * (len(order) - i)))
        out[k] = run
    return out


def shape(rate) -> str:
    """Descriptive shape rule (fixed before data):
      little numerical effect   max - min over the 7 levels < 0.20
      step at 0                 the -0.05 -> +0.05 change is >= 60% of the -0.50 -> +0.50 change, and the outer
                                changes (-0.50 -> -0.05, +0.05 -> +0.50) are each <= 0.15 in absolute value
      gradual                   otherwise, if either outer change is > 0.15 in the direction of the overall change
      other                     anything else (e.g. non-monotone)
    A note "non-monotone" is appended if any adjacent level drops by more than 0.15 against the overall direction."""
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
    # self-tests on the shape rule and the tests' basic behaviour
    assert shape([0, 0, 0, 0.5, 1, 1, 1]) == "step at 0"
    assert shape([0, 0.2, 0.4, 0.5, 0.6, 0.8, 1]) == "gradual"
    assert shape([0.4, 0.45, 0.5, 0.5, 0.5, 0.5, 0.55]) == "little numerical effect"
    assert shape([0, 0, 0.9, 0.2, 0.9, 1, 1]).endswith("(non-monotone)")
    rng = np.random.default_rng(0)
    obs = [dict(scenario=f"s{s}", gap=g, y=int(rng.random() < (0.9 if g > 0 else 0.1)), model="a", panel="x")
           for s in range(12) for g in GAPS for _ in range(3)]
    assert trend_test(obs, perms=2000)["p"] < 0.01
    null_obs = [dict(o, y=int(rng.random() < 0.5)) for o in obs]
    assert curve_diff_test(obs, obs)["p"] == 1.0
    assert curve_diff_test(obs, null_obs)["p"] < 0.05
    print("gap_analysis: self-tests pass")
