# Simulation calibration of the planned tests

Design per model × panel × feature: 6 tasks × 7 levels × 4 replies; task logit offsets N(0, 1.5); 400 simulations per row; 1000 permutations per test in the simulations (10,000 in the real analysis). alpha = 0.05; Monte Carlo SE at 0.05 ≈ 0.011 (400 sims) or 0.007 (1000 sims).

| Check | Rejection rate | Target |
|---|---|---|
| Trend test size, no gap effect, base 0.05 | 0.058 | ≤ 0.05 |
| Trend test size, no gap effect, base 0.2 | 0.037 | ≤ 0.05 |
| Trend test size, no gap effect, base 0.5 | 0.048 | ≤ 0.05 |
| Trend test size, no gap effect, base 0.2, 12 strata in 6 tasks (feature 1) | 0.045 | ≤ 0.05 |
| Comparison size, same step ±1.5 logits curve, identical task effects: within-task test | 0.025 | ≤ 0.05 |
| Same, secondary task sign-flip test | 0.028 | ≤ 0.05 |
| Comparison size, same gradual 5 logits/unit curve, identical task effects: within-task test | 0.028 | ≤ 0.05 |
| Same, secondary task sign-flip test | 0.020 | ≤ 0.05 |
| Comparison size, same low gradual curve, identical task effects: within-task test | 0.045 | ≤ 0.05 |
| Same, secondary task sign-flip test | 0.020 | ≤ 0.05 |
| Same population step ±1.5 logits curve, INDEPENDENT task effects (not the within-task null): within-task / sign-flip | 0.362 / 0.022 | (flags task-specific differences) |
| Same population low gradual curve, INDEPENDENT task effects (not the within-task null): within-task / sign-flip | 0.260 / 0.022 | (flags task-specific differences) |
| Holm FWER, 12 trend tests, global null (1000 sims) | 0.056 | ≤ 0.05 |
| Holm FWER, 6 comparisons, identical task effects (1000 sims) | 0.041 | ≤ 0.05 |
| Trend power, low gradual | 1.000 | (power) |
| Trend power, step ±1.5 logits | 1.000 | (power) |
| Comparison power, low gradual vs flat near zero, independent task effects: within-task / sign-flip | 0.995 / 0.448 | (power) |
| Comparison power, +1 logit shift of a step curve, independent task effects: within-task / sign-flip | 0.517 / 0.083 | (power) |
