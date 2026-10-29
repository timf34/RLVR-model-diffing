# Power and calibration (simulation)

`python simulation/simulate.py power --sims 200`; 200 simulated datasets per row. Primary model Qwen 3.8, pooled over sending + titles/sign-offs, the frozen tests (sign-flip / permutation, Holm within the Part 1 family of 2 and the Part 2 family of 13), alpha 0.05. Monte Carlo resolution here: 2,000 flips / 1,000 permutations (the real analysis uses 20,000).

**Effect-size anchors (10A + old reports, Qwen 3.8):** bundle +0.50 rate on fresh blocks: sending 10/16, bullets 9/16; old reports at +0.50: sending 53/72, titles/sign-offs 22/48, bullets 14/24; tied 0 in every cell; 10A new presentation 0/16 at both scores. Block propensities vary (Beta, concentration 2), so a block's +0.50 rate ranges widely, as the old per-scenario spreads did. Original-materials cells use 3 (sending, titles: 12 units) or 6 (bullets: 6 units) repetitions per block, 36 episodes per cell.

Scenarios: **materials** = the new presentation keeps half the effect on original materials only (PRES and MAT both true); **one** = component d alone carries the whole effect (removing it -> 0; adding it to N restores 80%); **partial** = d and g each carry half (removal keeps 50%, addition restores 30%); **small** = component a removes 30% / adds back 20%; **null** = no component matters and original = fresh materials (calibration of the Part 2 family-wise error and of MAT).

| fresh blocks per task | Qwen 3.8 generations per fresh cell | scenario | test | P(Holm p < 0.05) | mean estimate |
|---|---|---|---|---|---|
| 16 | 1 | materials | PRES | 1.00 | +0.408 |
| 16 | 1 | materials | MAT | 0.78 | +0.205 |
| 16 | 1 | one | PRES | 1.00 | +0.558 |
| 16 | 1 | one | REM:d | 0.97 | +0.506 |
| 16 | 1 | one | ADD:d | 0.87 | +0.401 |
| 16 | 1 | one | FWER_other_part2 | 0.01 |  |
| 16 | 1 | partial | REM:d | 0.17 | +0.251 |
| 16 | 1 | partial | ADD:d | 0.02 | +0.151 |
| 16 | 1 | small | REM:a | 0.04 | +0.153 |
| 16 | 1 | small | ADD:a | 0.01 | +0.103 |
| 16 | 1 | null | FWER_part2 | 0.01 |  |
| 16 | 1 | null | MAT | 0.06 | +0.005 |
| 24 | 1 | materials | PRES | 1.00 | +0.405 |
| 24 | 1 | materials | MAT | 0.82 | +0.204 |
| 24 | 1 | one | PRES | 1.00 | +0.559 |
| 24 | 1 | one | REM:d | 1.00 | +0.511 |
| 24 | 1 | one | ADD:d | 0.99 | +0.401 |
| 24 | 1 | one | FWER_other_part2 | 0.01 |  |
| 24 | 1 | partial | REM:d | 0.40 | +0.254 |
| 24 | 1 | partial | ADD:d | 0.20 | +0.150 |
| 24 | 1 | small | REM:a | 0.07 | +0.155 |
| 24 | 1 | small | ADD:a | 0.04 | +0.095 |
| 24 | 1 | null | FWER_part2 | 0.01 |  |
| 24 | 1 | null | MAT | 0.03 | +0.004 |
| 32 | 1 | materials | PRES | 1.00 | +0.410 |
| 32 | 1 | materials | MAT | 0.87 | +0.198 |
| 32 | 1 | one | PRES | 1.00 | +0.559 |
| 32 | 1 | one | REM:d | 1.00 | +0.509 |
| 32 | 1 | one | ADD:d | 0.99 | +0.408 |
| 32 | 1 | one | FWER_other_part2 | 0.01 |  |
| 32 | 1 | partial | REM:d | 0.56 | +0.246 |
| 32 | 1 | partial | ADD:d | 0.48 | +0.154 |
| 32 | 1 | small | REM:a | 0.15 | +0.153 |
| 32 | 1 | small | ADD:a | 0.17 | +0.102 |
| 32 | 1 | null | FWER_part2 | 0.01 |  |
| 32 | 1 | null | MAT | 0.04 | -0.003 |
| 24 | 2 | materials | PRES | 1.00 | +0.413 |
| 24 | 2 | materials | MAT | 0.83 | +0.194 |
| 24 | 2 | one | PRES | 1.00 | +0.560 |
| 24 | 2 | one | REM:d | 1.00 | +0.514 |
| 24 | 2 | one | ADD:d | 1.00 | +0.406 |
| 24 | 2 | one | FWER_other_part2 | 0.04 |  |
| 24 | 2 | partial | REM:d | 0.84 | +0.259 |
| 24 | 2 | partial | ADD:d | 0.76 | +0.149 |
| 24 | 2 | small | REM:a | 0.28 | +0.160 |
| 24 | 2 | small | ADD:a | 0.35 | +0.102 |
| 24 | 2 | null | FWER_part2 | 0.02 |  |
| 24 | 2 | null | MAT | 0.07 | -0.003 |
| 32 | 2 | materials | PRES | 1.00 | +0.408 |
| 32 | 2 | materials | MAT | 0.90 | +0.192 |
| 32 | 2 | one | PRES | 1.00 | +0.557 |
| 32 | 2 | one | REM:d | 1.00 | +0.515 |
| 32 | 2 | one | ADD:d | 1.00 | +0.411 |
| 32 | 2 | one | FWER_other_part2 | 0.01 |  |
| 32 | 2 | partial | REM:d | 0.95 | +0.258 |
| 32 | 2 | partial | ADD:d | 0.97 | +0.156 |
| 32 | 2 | small | REM:a | 0.40 | +0.155 |
| 32 | 2 | small | ADD:a | 0.57 | +0.102 |
| 32 | 2 | null | FWER_part2 | 0.01 |  |
| 32 | 2 | null | MAT | 0.06 | -0.003 |

## Choice

**32 fresh blocks per task, 2 Qwen 3.8 generations per fresh cell (1 for Qwen 3.5)** (sending: 10A's 16 + 16 new; bullets: 10A's 16 + 16 new; titles: 16 new tasks x 2 sub-features). Results at that size: a component that carries the whole effect is found with power ~1.0 (removal and addition); one that carries half of it with 0.95 (removal) and 0.97 (addition), against 0.56 / 0.48 with a single generation per cell, so the second Qwen 3.8 generation is worth its ~$5. A small component (30% removal, about 0.15 pooled) is found only 40-57% of the time: read null component results as "no large effect", not "no effect". Calibration under the null: Part 2 family-wise error 0.01-0.02 and the materials test 0.03-0.07 (200 simulations each, Monte Carlo SE about 0.015). PRES has power ~1.0 whenever the new presentation removes the effect; MAT has 0.9 when the new presentation keeps half the effect on original materials only.
