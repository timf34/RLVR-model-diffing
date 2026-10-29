"""Planned analysis for records vs prose (see ANALYSIS_PLAN.md). numpy only.

Observations: dict(scenario, gap, y) with y = 1 for an upsell; valid replies only.
1. rates_ci: pooled rate per gap level with a scenario-cluster bootstrap percentile 95% CI (resample scenarios).
2. paired_test (the planned contrast): one model x framing x level. Per scenario s, d_s = rate_prose[s] -
   rate_records[s] (scenarios with replies in both formats). Statistic |mean_s d_s|; null by swapping the two formats
   within whole scenarios (sign flip of d_s), exact over all 2^12 flips; two-sided. Effect: mean d (pp) with a
   paired scenario-bootstrap 95% CI.
3. holm over the family of 12 planned contrasts (2 models x 3 framings x {+0.05, +0.50}).
"""
import itertools
import math

import numpy as np

GAPS = (-0.50, 0.0, 0.05, 0.50)
TEST_GAPS = (0.05, 0.50)


def _kn(obs, scen):
    si, gi = {s: i for i, s in enumerate(scen)}, {g: i for i, g in enumerate(GAPS)}
    k, n = np.zeros((len(scen), len(GAPS))), np.zeros((len(scen), len(GAPS)))
    for o in obs:
        if o["scenario"] in si:
            k[si[o["scenario"]], gi[o["gap"]]] += o["y"]
            n[si[o["scenario"]], gi[o["gap"]]] += 1
    return k, n


def rates_ci(obs, reps=4000, seed=1):
    scen = sorted({o["scenario"] for o in obs})
    k, n = _kn(obs, scen)
    rate = k.sum(0) / np.maximum(n.sum(0), 1)
    idx = np.random.default_rng(seed).integers(0, len(scen), (reps, len(scen)))
    kb, nb = k[idx].sum(1), n[idx].sum(1)
    rb = np.where(nb > 0, kb / np.maximum(nb, 1), np.nan)
    lo, hi = np.nanpercentile(rb, [2.5, 97.5], axis=0)
    return dict(rate=rate.tolist(), lo=lo.tolist(), hi=hi.tolist(), k=k.sum(0).tolist(), n=n.sum(0).tolist())


def paired_test(obs_prose, obs_records, gap, reps=4000, seed=5):
    a = [o for o in obs_prose if o["gap"] == gap]
    b = [o for o in obs_records if o["gap"] == gap]
    scen = sorted({o["scenario"] for o in a} & {o["scenario"] for o in b})
    if not scen:
        return dict(p=float("nan"), diff=float("nan"), lo=float("nan"), hi=float("nan"), n_scen=0)
    gi = GAPS.index(gap)
    ka, na = _kn(a, scen)
    kb, nb = _kn(b, scen)
    d = ka[:, gi] / na[:, gi] - kb[:, gi] / nb[:, gi]
    flips = np.array(list(itertools.product([1, -1], repeat=len(scen))), float)
    null = np.abs((flips * d).mean(1))
    D = abs(d.mean())
    p = float(np.mean(null >= D - 1e-12))
    idx = np.random.default_rng(seed).integers(0, len(scen), (reps, len(scen)))
    boot = d[idx].mean(1)
    return dict(p=p, diff=float(d.mean()), lo=float(np.percentile(boot, 2.5)), hi=float(np.percentile(boot, 97.5)),
                n_scen=len(scen), rate_prose=float(ka[:, gi].sum() / na[:, gi].sum()),
                rate_records=float(kb[:, gi].sum() / nb[:, gi].sum()))


def holm(ps: dict) -> dict:
    order, out, run = sorted((p, k) for k, p in ps.items() if not math.isnan(p)), {}, 0.0
    for i, (p, k) in enumerate(order):
        run = max(run, min(1.0, p * (len(order) - i)))
        out[k] = run
    return out


if __name__ == "__main__":
    rng = np.random.default_rng(0)
    hi = [dict(scenario=f"s{s}", gap=g, y=int(rng.random() < 0.9)) for s in range(12) for g in GAPS for _ in range(3)]
    lo = [dict(o, y=int(rng.random() < 0.1)) for o in hi]
    assert paired_test(hi, hi, 0.5)["p"] == 1.0
    t = paired_test(hi, lo, 0.5)
    assert t["p"] < 0.01 and t["diff"] > 0.5 and t["lo"] > 0
    assert holm({"a": 0.01, "b": 0.04, "c": 0.5}) == {"a": 0.03, "b": 0.08, "c": 0.5}
    r = rates_ci(hi)
    assert len(r["rate"]) == 4 and all(l <= x <= h for l, x, h in zip(r["lo"], r["rate"], r["hi"]))
    print("rr_analysis: self-tests pass")
