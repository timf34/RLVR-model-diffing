# Simulation calibration of the planned Haiku tests

Design: 12 scenarios x 7 levels x 3 replies; scenario logit offsets N(0, 1.5); 400 simulations per row (FWER rows: see label); trend test 1000 permutations per simulation; comparison test exact over 2^12 scenario flips. alpha = 0.05. Monte Carlo SE at 0.05 ≈ 0.011 (400 sims).

| Check | Rejection rate | Target |
|---|---|---|
| Trend size, no gap effect, base 0.1 | 0.058 | ≤ 0.05 |
| Trend size, no gap effect, base 0.5 | 0.050 | ≤ 0.05 |
| Trend size, no gap effect, base 0.5, 20% of replies excluded at random | 0.068 | ≤ 0.05 |
| Comparison size, same step curve, independent scenario effects | 0.045 | ≤ 0.05 |
| Comparison size, same gradual curve, independent scenario effects | 0.040 | ≤ 0.05 |
| Comparison size, same step curve, 20% excluded at random | 0.055 | ≤ 0.05 |
| Holm FWER, 6 trend tests, global null (100 sims) | 0.060 | ≤ 0.05 |
| Holm FWER, 3 comparisons, equal curves | 0.055 | ≤ 0.05 |
| Trend power, step ±1.5 logits | 1.000 | (power) |
| Trend power, gradual 5 logits per unit gap | 1.000 | (power) |
| Trend power, one-sided rise only (0 for g ≤ 0, 50% at +0.50, logistic) | 1.000 | (power) |
| Comparison power, +1 logit shift | 0.335 | (power) |
| Comparison power, step vs gradual | 0.245 | (power) |
| Comparison power, strong step vs flat low curve | 1.000 | (power) |
