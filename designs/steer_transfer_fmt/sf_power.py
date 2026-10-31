"""Power / minimum detectable effect for P1 per family (simulation; no data).

  .venv/bin/python designs/steer_transfer_fmt/sf_power.py

Model: per scenario, logit P(override | conflict) = logit(p_base + delta for steered) + u_s, u_s ~ N(0, sd^2) shared
across conditions (scenario heterogeneity; sd = 1.0 is conservative given the archived 3.8 spread across scenarios);
reversed arm ~ 0 (archived 0 at every gap <= 0). Cluster-bootstrap SE of DiD over scenarios; power at the primary
threshold (Holm worst case alpha = 0.05/6, two-sided).
"""
from __future__ import annotations

import numpy as np
from statistics import NormalDist

from sf_common import REPS

SCEN = {"title": 22, "signoff": 22, "bullets": 38}
Z = NormalDist().inv_cdf(1 - 0.05 / 6 / 2)


def sim_power(n_s, reps, p_base, delta, sd=1.0, sims=300, B=300, seed=0):
    rng = np.random.default_rng(seed)
    lg = lambda p: np.log(p / (1 - p))  # noqa: E731
    hits = 0
    ses = []
    for _ in range(sims):
        u = rng.normal(0, sd, n_s)
        pb = 1 / (1 + np.exp(-(lg(p_base) + u)))
        ps = 1 / (1 + np.exp(-(lg(p_base + delta) + u)))
        cb, cs = rng.binomial(reps, pb), rng.binomial(reps, ps)          # conflict arm, unsteered / steered
        rb, rs = rng.binomial(reps, 0.003, n_s), rng.binomial(reps, 0.003, n_s)
        D = np.stack([cs, rs, cb, rb], 1).astype(float)
        f = lambda X: (X[:, 0].sum() - X[:, 1].sum() - X[:, 2].sum() + X[:, 3].sum()) / (len(X) * reps)  # noqa
        est = f(D)
        bs = np.array([f(D[rng.integers(0, n_s, n_s)]) for _ in range(B)])
        se = bs.std()
        ses.append(se)
        hits += abs(est) / max(se, 1e-9) > Z
    return hits / sims, float(np.mean(ses))


if __name__ == "__main__":
    for design, reps in REPS.items():
        print(f"== design {design}")
        for fam, n_s in SCEN.items():
            row = []
            for delta in (0.05, 0.08, 0.10, 0.15, 0.20):
                pw, se = sim_power(n_s, reps[fam], 0.02, delta)
                row.append(f"+{delta:.2f}: power {pw:.2f} (SE {se:.3f})")
            print(f"  {fam:8s} {n_s} scenarios x {reps[fam]} reps -> " + "; ".join(row))
