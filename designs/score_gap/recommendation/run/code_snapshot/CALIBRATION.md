# Simulation calibration of the planned tests

Design: 12 scenarios x 7 levels x 3 replies; scenario logit offsets N(0, 1.5); 400 simulations per row; trend test 1000 permutations per simulation; comparison test exact over 2^12 scenario flips. alpha = 0.05.

| Check | Rejection rate | Target |
|---|---|---|
| Trend test size, no gap effect, base 0.2 | 0.048 | ≤ 0.05 |
| Trend test size, no gap effect, base 0.5 | 0.060 | ≤ 0.05 |
| Trend test size, no gap effect, base 0.8 | 0.050 | ≤ 0.05 |
| Comparison size, same step curve, identical scenario effects | 0.052 | ≤ 0.05 |
| Comparison size, same step curve, independent scenario effects | 0.028 | ≤ 0.05 |
| Comparison size, same gradual curve, identical scenario effects | 0.045 | ≤ 0.05 |
| Comparison size, same gradual curve, independent scenario effects | 0.062 | ≤ 0.05 |
| Holm FWER, 9 trend tests, global null (100 sims) | 0.040 | ≤ 0.05 |
| Holm FWER, 18 comparisons, all curves equal (400 sims) | 0.043 | ≤ 0.05 |
| Trend power, step ±1.5 logits | 1.000 | (power) |
| Trend power, gradual 5 logits per unit gap | 1.000 | (power) |
| Comparison power, +1 logit shift, independent scenario effects | 0.260 | (power) |
| Comparison power, step vs gradual shape | 0.225 | (power) |
| Comparison power, strong step vs flat low curve | 1.000 | (power) |
