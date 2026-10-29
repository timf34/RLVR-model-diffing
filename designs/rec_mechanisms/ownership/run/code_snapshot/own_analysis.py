"""Planned contrasts for the ownership x wording experiment (numpy only; see ANALYSIS_PLAN.md).

Per model and gap level g in {+0.05, +0.50}, with per-scenario upsell rates r[cell][s] (cells chat/team = CT,
chat/independent = CI, episode/team = ET, episode/independent = EI):
  ownership    c_s = ((CT - CI) + (ET - EI)) / 2          team minus independent, averaged over wording
  wording      c_s = ((ET - CT) + (EI - CI)) / 2          episode minus chat, averaged over ownership
  interaction  c_s = (CT - CI) - (ET - EI)                ownership effect in chat minus in episode
Estimate = mean over scenarios of c_s (probability scale). Two-sided test: sign flip of whole scenarios, exact over
all 2^12 flips. 95% CI: scenario bootstrap (4000). Holm over the 12 tests (2 models x 2 levels x 3 contrasts).
"""
import itertools
import math

import numpy as np

CONTRASTS = ("ownership", "wording", "interaction")
FLIPS = None


def _flips(ns):
    global FLIPS
    if FLIPS is None or FLIPS.shape[1] != ns:
        FLIPS = np.array(list(itertools.product([1, -1], repeat=ns)), float)
    return FLIPS


def contrast_values(r: dict) -> dict:
    """r: cell -> array of per-scenario rates (same scenario order). Returns contrast -> per-scenario values."""
    CT, CI, ET, EI = (np.asarray(r[c], float) for c in ("chat/team", "chat/independent", "episode/team",
                                                         "episode/independent"))
    return {"ownership": ((CT - CI) + (ET - EI)) / 2, "wording": ((ET - CT) + (EI - CI)) / 2,
            "interaction": (CT - CI) - (ET - EI)}


def signflip_test(c: np.ndarray) -> float:
    c = c[~np.isnan(c)]
    if len(c) == 0:
        return math.nan
    obs = abs(c.mean())
    null = np.abs(_flips(len(c)) @ c / len(c)) if len(c) <= 16 else None
    return float(np.mean(null >= obs - 1e-12))


def boot_ci(c: np.ndarray, reps=4000, seed=7):
    c = c[~np.isnan(c)]
    rng = np.random.default_rng(seed)
    m = c[rng.integers(0, len(c), (reps, len(c)))].mean(1)
    return [float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))]


def cluster_rate_ci(k: np.ndarray, n: np.ndarray, reps=4000, seed=1):
    """Pooled rate and scenario-cluster bootstrap CI from per-scenario counts."""
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, len(k), (reps, len(k)))
    nb = n[idx].sum(1)
    rb = np.where(nb > 0, k[idx].sum(1) / np.maximum(nb, 1), np.nan)
    return float(k.sum() / max(n.sum(), 1)), [float(np.nanpercentile(rb, 2.5)), float(np.nanpercentile(rb, 97.5))]


def holm(ps: dict) -> dict:
    order, out, run = sorted((p, k) for k, p in ps.items() if not math.isnan(p)), {}, 0.0
    for i, (p, k) in enumerate(order):
        run = max(run, min(1.0, p * (len(order) - i)))
        out[k] = run
    for k, p in ps.items():
        out.setdefault(k, math.nan)
    return out


if __name__ == "__main__":
    rng = np.random.default_rng(0)
    base = rng.random(12)
    r = {"chat/team": base + 0.3, "chat/independent": base, "episode/team": base + 0.3, "episode/independent": base}
    cv = contrast_values(r)
    assert np.allclose(cv["ownership"], 0.3) and np.allclose(cv["wording"], 0) and np.allclose(cv["interaction"], 0)
    assert signflip_test(cv["ownership"]) < 0.001 and signflip_test(cv["wording"] + rng.normal(0, .1, 12)) > 0.01
    print("own_analysis: self-tests pass")
