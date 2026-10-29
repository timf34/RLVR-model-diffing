# Simulation calibration of the planned tests

Design: 6 scenarios x 7 levels x 4 replies; integer ratings, reply noise SD 1.0; scenario intercept SD 1.0, scenario slope SD 1.0 per unit gap; 400 simulations per row; trend test 1000 permutations per simulation; alpha = 0.05.

| Check | Rate | Target |
|---|---|---|
| Trend size, no gap effect (strong null), base 4 (1000 sims) | 0.058 | ≤ 0.05 |
| Trend size, no gap effect (strong null), base 7 (1000 sims) | 0.057 | ≤ 0.05 |
| Trend rejection, weak null (scenario slopes SD 1.0, mean 0) | 0.225 | (not a target; strong-null test) |
| Comparison size (Hotelling), same flat curve, identical scenario effects | 0.043 | ≤ 0.05 |
| Comparison size (Hotelling), same flat curve, independent scenario effects | 0.043 | ≤ 0.05 |
| Comparison size (sign-flip D), same flat curve, independent scenario effects | 0.033 | ≤ 0.05 |
| Comparison size (Hotelling), same step curve, identical scenario effects | 0.035 | ≤ 0.05 |
| Comparison size (Hotelling), same step curve, independent scenario effects | 0.068 | ≤ 0.05 |
| Comparison size (sign-flip D), same step curve, independent scenario effects | 0.028 | ≤ 0.05 |
| Comparison size (Hotelling), same gradual curve, identical scenario effects | 0.037 | ≤ 0.05 |
| Comparison size (Hotelling), same gradual curve, independent scenario effects | 0.040 | ≤ 0.05 |
| Comparison size (sign-flip D), same gradual curve, independent scenario effects | 0.018 | ≤ 0.05 |
| Comparison size (Hotelling), same gradual curve, bimodal 5-or-8 ratings, independent effects | 0.037 | ≤ 0.05 |
| Holm FWER, 6 trend tests, global null (200 sims) | 0.060 | ≤ 0.05 |
| Holm FWER, 3 comparisons, all curves equal, independent effects | 0.048 | ≤ 0.05 |
| Trend power, step ±0.75 points | 0.998 | (power) |
| Trend power, gradual 2.7 points per unit gap (3.8-like) | 1.000 | (power) |
| Trend power, gradual 0.6 points per unit gap (3.5-like) | 0.545 | (power) |
| Comparison power, 3.8-like gradual 2.7 vs 3.5-like 0.6 per unit gap (Hotelling / sign-flip) | 0.445 / 0.125 | (power) |
| Comparison power, +1 point shift, same gradual curve (Hotelling / sign-flip) | 0.175 / 0.145 | (power) |
| Comparison power, step ±0.75 vs gradual 1.5 per unit gap (Hotelling / sign-flip) | 0.050 / 0.083 | (power) |
| Comparison power, 3.8-like vs 3.5-like, moderate heterogeneity (intercept and slope SD 0.5) (Hotelling) | 0.730 | (power) |
| Comparison power, +1 point shift, moderate heterogeneity (intercept and slope SD 0.5) (Hotelling) | 0.515 | (power) |
| Comparison size (Hotelling), same gradual curve, moderate heterogeneity | 0.037 | ≤ 0.05 |
| Coverage of the cluster t 95% interval, level mean at +0.50 | 0.953 | ≈ 0.95 |
