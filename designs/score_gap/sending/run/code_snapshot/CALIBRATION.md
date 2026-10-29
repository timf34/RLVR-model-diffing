# Simulation calibration of the planned tests (sending score-gap curve)

Design: 12 scenarios x 7 levels x 6 episodes (bundle) or 2 (ordinary) per scenario x level; scenario logit offsets N(0, 1.5); 400 simulations per row; trend test 1000 permutations per simulation; comparison test exact over 2^12 scenario flips. alpha = 0.05; Monte Carlo SE at 0.05 ≈ 0.011.

Curves: step = logit −2.5 at g ≤ 0 and +0.5 above 0 (≈ 8% → 62%); gradual = logit −2.5 + 6·max(g, 0) (≈ 8% at g ≤ 0, 10% at +0.05, 20% at +0.20, 62% at +0.50).

| Check | Rejection rate | Target |
|---|---|---|
| Trend test size, no gap effect, base 0.05, bundle (n=72/level) | 0.062 | ≤ 0.05 |
| Trend test size, no gap effect, base 0.2, bundle (n=72/level) | 0.043 | ≤ 0.05 |
| Trend test size, no gap effect, base 0.5, bundle (n=72/level) | 0.043 | ≤ 0.05 |
| Trend test size, no gap effect, base 0.05, ordinary (n=24/level) | 0.052 | ≤ 0.05 |
| Trend test size, no gap effect, base 0.2, ordinary (n=24/level) | 0.048 | ≤ 0.05 |
| Trend test size, no gap effect, base 0.5, ordinary (n=24/level) | 0.040 | ≤ 0.05 |
| Comparison size, same step curve, identical scenario effects, bundle | 0.037 | ≤ 0.05 |
| Comparison size, same step curve, independent scenario effects, bundle | 0.050 | ≤ 0.05 |
| Comparison size, same gradual curve, identical scenario effects, bundle | 0.033 | ≤ 0.05 |
| Comparison size, same gradual curve, independent scenario effects, bundle | 0.048 | ≤ 0.05 |
| Comparison size, same step curve, identical scenario effects, ordinary | 0.028 | ≤ 0.05 |
| Comparison size, same step curve, independent scenario effects, ordinary | 0.055 | ≤ 0.05 |
| Comparison size, same gradual curve, identical scenario effects, ordinary | 0.050 | ≤ 0.05 |
| Comparison size, same gradual curve, independent scenario effects, ordinary | 0.035 | ≤ 0.05 |
| Comparison size, same step curve, bundle (6) vs ordinary (2), independent scenario effects | 0.048 | ≤ 0.05 |
| Holm FWER, 4 trend tests, global null (200 sims) | 0.035 | ≤ 0.05 |
| Holm FWER, primary family (3.8 vs 3.5 per panel, 2 tests), all curves equal | 0.045 | ≤ 0.05 |
| Holm FWER, secondary family (bundle vs ordinary per model, 2 tests), all curves equal | 0.043 | ≤ 0.05 |
| Trend power, step, bundle | 1.000 | (power) |
| Trend power, gradual, bundle | 1.000 | (power) |
| Comparison power, +1 logit shift, independent scenario effects, bundle | 0.265 | (power) |
| Comparison power, step vs gradual, bundle | 0.710 | (power) |
| Comparison power, strong step vs flat low curve, bundle | 1.000 | (power) |
| Trend power, step, ordinary | 1.000 | (power) |
| Trend power, gradual, ordinary | 0.980 | (power) |
| Comparison power, +1 logit shift, independent scenario effects, ordinary | 0.258 | (power) |
| Comparison power, step vs gradual, ordinary | 0.575 | (power) |
| Comparison power, strong step vs flat low curve, ordinary | 0.998 | (power) |
