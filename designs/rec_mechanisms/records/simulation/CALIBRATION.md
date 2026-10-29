# Simulation calibration: records vs prose paired contrasts

Design: 12 scenarios × 3 replies per format at one level; scenario logit offsets N(0, 1.5); 1000 simulations per row; exact sign-flip test over 2^12 scenario flips; alpha = 0.05.

| Check | Rejection rate | Target |
|---|---|---|
| Size, base 0.1, identical scenario offsets | 0.005 | ≤ 0.05 |
| Size, base 0.1, independent scenario offsets | 0.012 | ≤ 0.05 |
| Size, base 0.5, identical scenario offsets | 0.017 | ≤ 0.05 |
| Size, base 0.5, independent scenario offsets | 0.022 | ≤ 0.05 |
| Size, base 0.9, identical scenario offsets | 0.011 | ≤ 0.05 |
| Size, base 0.9, independent scenario offsets | 0.019 | ≤ 0.05 |
| Holm FWER, 12 null contrasts, identical offsets (500 sims) | 0.002 | ≤ 0.05 |
| Holm FWER, 12 null contrasts, independent offsets (500 sims) | 0.004 | ≤ 0.05 |
| Power, prose 0.9 vs records 0.2 (shared offsets), unadjusted | 0.999 | (power) |
| Power, prose 0.9 vs records 0.2 (shared offsets), at alpha/12 | 0.848 | (power) |
| Power, prose 0.9 vs records 0.5 (shared offsets), unadjusted | 0.793 | (power) |
| Power, prose 0.9 vs records 0.5 (shared offsets), at alpha/12 | 0.282 | (power) |
| Power, prose 0.9 vs records 0.7 (shared offsets), unadjusted | 0.272 | (power) |
| Power, prose 0.9 vs records 0.7 (shared offsets), at alpha/12 | 0.024 | (power) |
| Power, prose 0.4 vs records 0.1 (shared offsets), unadjusted | 0.543 | (power) |
| Power, prose 0.4 vs records 0.1 (shared offsets), at alpha/12 | 0.128 | (power) |

Note: the minimum attainable exact p-value with 12 scenarios is 2/4096 ≈ 0.0005, below the Holm bound 0.05/12 ≈ 0.0042, so every contrast can in principle reach significance after adjustment.
