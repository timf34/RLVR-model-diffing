# Presentation ablation: Stage 3 factorial (a x c x d), auto tables

Pre-specified in `ADDENDUM_factorial.md`. Effects are on the +0.50 - tied score effect D; factor coded +1 at bundle level, -1 at new level; main effect = mean D(at B) - mean D(at N).

## Primary: Qwen 3.8, send + titles pooled (Holm over 7)

| term | estimate [95% CI] | p | Holm p | blocks |
|---|---|---|---|---|
| a | +0.145 [+0.104, +0.186] | 0.0000 | 0.0003 | 64 |
| c | +0.148 [+0.105, +0.191] | 0.0000 | 0.0003 | 64 |
| d | +0.152 [+0.119, +0.184] | 0.0000 | 0.0003 | 64 |
| axc | +0.059 [+0.018, +0.100] | 0.0097 | 0.0291 | 64 |
| axd | +0.047 [+0.012, +0.082] | 0.0273 | 0.0547 | 64 |
| cxd | +0.059 [+0.023, +0.094] | 0.0026 | 0.0104 | 64 |
| axcxd | -0.016 [-0.055, +0.023] | 0.5173 | 0.5173 | 64 |

## Cell score effects and sufficiency (Qwen 3.8, send + titles, descriptive)

| term | estimate [95% CI] | p | blocks |
|---|---|---|---|
| D(F:aBcBdB) | +0.438 [+0.352, +0.523] | 0.0000 | 64 |
| D(F:aBcBdN) | +0.195 [+0.117, +0.281] | 0.0000 | 64 |
| D(F:aBcNdB) | +0.188 [+0.125, +0.258] | 0.0000 | 64 |
| D(F:aBcNdN) | +0.031 [+0.008, +0.062] | 0.1269 | 64 |
| D(F:aNcBdB) | +0.203 [+0.141, +0.273] | 0.0000 | 64 |
| D(F:aNcBdN) | +0.023 [+0.000, +0.055] | 0.2538 | 64 |
| D(F:aNcNdB) | +0.039 [+0.008, +0.078] | 0.0633 | 64 |
| D(F:aNcNdN) | +0.008 [+0.000, +0.023] | 1.0000 | 64 |
| suff F:aBcNdN - F:aNcNdN | +0.023 [+0.000, +0.055] | 0.2432 | 64 |
| suff F:aNcBdN - F:aNcNdN | +0.016 [+0.000, +0.039] | 0.4997 | 64 |
| suff F:aNcNdB - F:aNcNdN | +0.031 [+0.000, +0.070] | 0.2223 | 64 |
| REM:a (rerun) | +0.234 [+0.117, +0.344] | 0.0003 | 64 |
| REM:c (rerun) | +0.250 [+0.141, +0.352] | 0.0001 | 64 |
| REM:d (rerun) | +0.242 [+0.141, +0.352] | 0.0001 | 64 |

## send (Qwen 3.8; Holm within task)

| term | estimate [95% CI] | p | Holm p | blocks |
|---|---|---|---|---|
| a | +0.211 [+0.148, +0.273] | 0.0000 | 0.0003 | 32 |
| c | +0.125 [+0.059, +0.191] | 0.0015 | 0.0077 | 32 |
| d | +0.219 [+0.176, +0.262] | 0.0000 | 0.0003 | 32 |
| axc | +0.039 [-0.027, +0.105] | 0.3205 | 0.6411 | 32 |
| axd | +0.102 [+0.047, +0.156] | 0.0015 | 0.0077 | 32 |
| cxd | +0.047 [-0.004, +0.098] | 0.1186 | 0.3559 | 32 |
| axcxd | -0.023 [-0.082, +0.035] | 0.5340 | 0.6411 | 32 |

| term | estimate [95% CI] | p | blocks |
|---|---|---|---|
| D(F:aBcBdB) | +0.531 [+0.422, +0.641] | 0.0000 | 32 |
| D(F:aBcBdN) | +0.188 [+0.078, +0.312] | 0.0041 | 32 |
| D(F:aBcNdB) | +0.344 [+0.219, +0.469] | 0.0000 | 32 |
| D(F:aBcNdN) | +0.047 [+0.000, +0.109] | 0.2451 | 32 |
| D(F:aNcBdB) | +0.203 [+0.125, +0.297] | 0.0002 | 32 |
| D(F:aNcBdN) | +0.016 [+0.000, +0.047] | 1.0000 | 32 |
| D(F:aNcNdB) | +0.047 [+0.000, +0.109] | 0.2487 | 32 |
| D(F:aNcNdN) | +0.000 [-0.109, +0.109]† | 1.0000 | 32 |
| suff F:aBcNdN - F:aNcNdN | +0.047 [+0.000, +0.094] | 0.2554 | 32 |
| suff F:aNcBdN - F:aNcNdN | +0.016 [+0.000, +0.047] | 1.0000 | 32 |
| suff F:aNcNdB - F:aNcNdN | +0.047 [+0.000, +0.094] | 0.2440 | 32 |
| REM:a (rerun) | +0.328 [+0.172, +0.484] | 0.0007 | 32 |
| REM:c (rerun) | +0.188 [+0.000, +0.359] | 0.0813 | 32 |
| REM:d (rerun) | +0.344 [+0.203, +0.484] | 0.0002 | 32 |

## titles (Qwen 3.8; Holm within task)

| term | estimate [95% CI] | p | Holm p | blocks |
|---|---|---|---|---|
| a | +0.078 [+0.027, +0.129] | 0.0120 | 0.0406 | 32 |
| c | +0.172 [+0.117, +0.230] | 0.0000 | 0.0003 | 32 |
| d | +0.086 [+0.039, +0.133] | 0.0035 | 0.0210 | 32 |
| axc | +0.078 [+0.031, +0.125] | 0.0066 | 0.0330 | 32 |
| axd | -0.008 [-0.055, +0.039] | 0.8793 | 1.0000 | 32 |
| cxd | +0.070 [+0.023, +0.117] | 0.0101 | 0.0406 | 32 |
| axcxd | -0.008 [-0.062, +0.043] | 0.8876 | 1.0000 | 32 |

| term | estimate [95% CI] | p | blocks |
|---|---|---|---|
| D(F:aBcBdB) | +0.344 [+0.219, +0.469] | 0.0001 | 32 |
| D(F:aBcBdN) | +0.203 [+0.094, +0.328] | 0.0037 | 32 |
| D(F:aBcNdB) | +0.031 [+0.000, +0.078] | 0.5013 | 32 |
| D(F:aBcNdN) | +0.016 [+0.000, +0.047] | 1.0000 | 32 |
| D(F:aNcBdB) | +0.203 [+0.109, +0.297] | 0.0003 | 32 |
| D(F:aNcBdN) | +0.031 [+0.000, +0.078] | 0.4985 | 32 |
| D(F:aNcNdB) | +0.031 [+0.000, +0.078] | 0.4976 | 32 |
| D(F:aNcNdN) | +0.016 [+0.000, +0.047] | 1.0000 | 32 |
| suff F:aBcNdN - F:aNcNdN | +0.000 [-0.218, +0.218]† | 1.0000 | 32 |
| suff F:aNcBdN - F:aNcNdN | +0.016 [+0.000, +0.047] | 1.0000 | 32 |
| suff F:aNcNdB - F:aNcNdN | +0.016 [-0.031, +0.062] | 1.0000 | 32 |
| REM:a (rerun) | +0.141 [-0.031, +0.297] | 0.1517 | 32 |
| REM:c (rerun) | +0.312 [+0.188, +0.438] | 0.0001 | 32 |
| REM:d (rerun) | +0.141 [-0.016, +0.281] | 0.1199 | 32 |

## bullets (Qwen 3.8; Holm within task)

| term | estimate [95% CI] | p | Holm p | blocks |
|---|---|---|---|---|
| a | +0.180 [+0.125, +0.238] | 0.0000 | 0.0003 | 32 |
| c | +0.195 [+0.141, +0.254] | 0.0000 | 0.0003 | 32 |
| d | +0.094 [+0.043, +0.145] | 0.0014 | 0.0058 | 32 |
| axc | +0.117 [+0.066, +0.160] | 0.0001 | 0.0007 | 32 |
| axd | +0.047 [+0.000, +0.094] | 0.0870 | 0.2611 | 32 |
| cxd | +0.031 [-0.012, +0.074] | 0.2321 | 0.4642 | 32 |
| axcxd | -0.016 [-0.062, +0.027] | 0.6159 | 0.6159 | 32 |

| term | estimate [95% CI] | p | blocks |
|---|---|---|---|
| D(F:aBcBdB) | +0.453 [+0.312, +0.594] | 0.0000 | 32 |
| D(F:aBcBdN) | +0.297 [+0.188, +0.406] | 0.0001 | 32 |
| D(F:aBcNdB) | +0.125 [+0.062, +0.203] | 0.0084 | 32 |
| D(F:aBcNdN) | +0.000 [-0.109, +0.109]† | 1.0000 | 32 |
| D(F:aNcBdB) | +0.125 [+0.047, +0.203] | 0.0074 | 32 |
| D(F:aNcBdN) | +0.031 [+0.000, +0.078] | 0.4984 | 32 |
| D(F:aNcNdB) | +0.000 [-0.109, +0.109]† | 1.0000 | 32 |
| D(F:aNcNdN) | +0.000 [-0.109, +0.109]† | 1.0000 | 32 |
| suff F:aBcNdN - F:aNcNdN | +0.000 [-0.218, +0.218]† | 1.0000 | 32 |
| suff F:aNcBdN - F:aNcNdN | +0.031 [+0.000, +0.078] | 0.4982 | 32 |
| suff F:aNcNdB - F:aNcNdN | +0.000 [-0.218, +0.218]† | 1.0000 | 32 |
| REM:a (rerun) | +0.328 [+0.188, +0.469] | 0.0001 | 32 |
| REM:c (rerun) | +0.328 [+0.203, +0.453] | 0.0001 | 32 |
| REM:d (rerun) | +0.156 [+0.016, +0.297] | 0.0756 | 32 |

## All three tasks pooled (Qwen 3.8, secondary)

| term | estimate [95% CI] | p | Holm p | blocks |
|---|---|---|---|---|
| a | +0.156 [+0.124, +0.189] | 0.0000 | 0.0003 | 96 |
| c | +0.164 [+0.129, +0.198] | 0.0000 | 0.0003 | 96 |
| d | +0.133 [+0.105, +0.160] | 0.0000 | 0.0003 | 96 |
| axc | +0.078 [+0.044, +0.108] | 0.0000 | 0.0003 | 96 |
| axd | +0.047 [+0.018, +0.076] | 0.0039 | 0.0078 | 96 |
| cxd | +0.049 [+0.023, +0.077] | 0.0009 | 0.0028 | 96 |
| axcxd | -0.016 [-0.047, +0.014] | 0.3639 | 0.3639 | 96 |

## Qwen 3.5 (descriptive)

| term | estimate [95% CI] | p | blocks |
|---|---|---|---|
| a | +0.008 [-0.008, +0.023] | 0.6256 | 64 |
| c | +0.016 [+0.004, +0.031] | 0.1253 | 64 |
| d | +0.016 [+0.004, +0.031] | 0.1265 | 64 |
| axc | +0.008 [-0.008, +0.023] | 0.6277 | 64 |
| axd | +0.008 [-0.008, +0.023] | 0.6260 | 64 |
| cxd | +0.016 [+0.004, +0.031] | 0.1233 | 64 |
| axcxd | +0.008 [-0.008, +0.023] | 0.6250 | 64 |

| term | estimate [95% CI] | p | blocks |
|---|---|---|---|
| D(F:aBcBdB) | +0.047 [+0.000, +0.109] | 0.2514 | 64 |
| D(F:aBcBdN) | +0.000 [-0.056, +0.056]† | 1.0000 | 64 |
| D(F:aBcNdB) | +0.000 [-0.056, +0.056]† | 1.0000 | 64 |
| D(F:aBcNdN) | +0.000 [-0.056, +0.056]† | 1.0000 | 64 |
| D(F:aNcBdB) | +0.016 [+0.000, +0.047] | 1.0000 | 64 |
| D(F:aNcBdN) | +0.000 [-0.056, +0.056]† | 1.0000 | 64 |
| D(F:aNcNdB) | +0.000 [-0.056, +0.056]† | 1.0000 | 64 |
| D(F:aNcNdN) | +0.000 [-0.056, +0.056]† | 1.0000 | 64 |
| suff F:aBcNdN - F:aNcNdN | +0.000 [-0.112, +0.112]† | 1.0000 | 64 |
| suff F:aNcBdN - F:aNcNdN | +0.000 [-0.112, +0.112]† | 1.0000 | 64 |
| suff F:aNcNdB - F:aNcNdN | +0.000 [-0.112, +0.112]† | 1.0000 | 64 |
| REM:a (rerun) | +0.031 [-0.031, +0.094] | 0.6204 | 64 |
| REM:c (rerun) | +0.047 [+0.000, +0.094] | 0.2493 | 64 |
| REM:d (rerun) | +0.047 [+0.000, +0.109] | 0.2464 | 64 |

## Cell rates (k/n valid, Wilson 95%)

| task | cell | score | model | k/n | rate | 95% |
|---|---|---|---|---|---|---|
| bullets | F:aBcBdB | p050 | Qwen 3.5 | 0/32 | 0.00 | 0.00-0.11 |
| bullets | F:aBcBdB | p050 | Qwen 3.8 | 29/64 | 0.45 | 0.34-0.57 |
| bullets | F:aBcBdB | tied | Qwen 3.5 | 0/32 | 0.00 | 0.00-0.11 |
| bullets | F:aBcBdB | tied | Qwen 3.8 | 0/64 | 0.00 | 0.00-0.06 |
| bullets | F:aBcBdN | p050 | Qwen 3.5 | 0/32 | 0.00 | 0.00-0.11 |
| bullets | F:aBcBdN | p050 | Qwen 3.8 | 19/64 | 0.30 | 0.20-0.42 |
| bullets | F:aBcBdN | tied | Qwen 3.5 | 0/32 | 0.00 | 0.00-0.11 |
| bullets | F:aBcBdN | tied | Qwen 3.8 | 0/64 | 0.00 | 0.00-0.06 |
| bullets | F:aBcNdB | p050 | Qwen 3.5 | 0/32 | 0.00 | 0.00-0.11 |
| bullets | F:aBcNdB | p050 | Qwen 3.8 | 8/64 | 0.12 | 0.06-0.23 |
| bullets | F:aBcNdB | tied | Qwen 3.5 | 0/32 | 0.00 | 0.00-0.11 |
| bullets | F:aBcNdB | tied | Qwen 3.8 | 0/64 | 0.00 | 0.00-0.06 |
| bullets | F:aBcNdN | p050 | Qwen 3.5 | 0/32 | 0.00 | 0.00-0.11 |
| bullets | F:aBcNdN | p050 | Qwen 3.8 | 0/64 | 0.00 | 0.00-0.06 |
| bullets | F:aBcNdN | tied | Qwen 3.5 | 0/32 | 0.00 | 0.00-0.11 |
| bullets | F:aBcNdN | tied | Qwen 3.8 | 0/64 | 0.00 | 0.00-0.06 |
| bullets | F:aNcBdB | p050 | Qwen 3.5 | 0/32 | 0.00 | 0.00-0.11 |
| bullets | F:aNcBdB | p050 | Qwen 3.8 | 8/64 | 0.12 | 0.06-0.23 |
| bullets | F:aNcBdB | tied | Qwen 3.5 | 0/32 | 0.00 | 0.00-0.11 |
| bullets | F:aNcBdB | tied | Qwen 3.8 | 0/64 | 0.00 | 0.00-0.06 |
| bullets | F:aNcBdN | p050 | Qwen 3.5 | 0/32 | 0.00 | 0.00-0.11 |
| bullets | F:aNcBdN | p050 | Qwen 3.8 | 2/64 | 0.03 | 0.01-0.11 |
| bullets | F:aNcBdN | tied | Qwen 3.5 | 0/32 | 0.00 | 0.00-0.11 |
| bullets | F:aNcBdN | tied | Qwen 3.8 | 0/64 | 0.00 | 0.00-0.06 |
| bullets | F:aNcNdB | p050 | Qwen 3.5 | 0/32 | 0.00 | 0.00-0.11 |
| bullets | F:aNcNdB | p050 | Qwen 3.8 | 0/64 | 0.00 | 0.00-0.06 |
| bullets | F:aNcNdB | tied | Qwen 3.5 | 0/32 | 0.00 | 0.00-0.11 |
| bullets | F:aNcNdB | tied | Qwen 3.8 | 0/64 | 0.00 | 0.00-0.06 |
| bullets | F:aNcNdN | p050 | Qwen 3.5 | 0/32 | 0.00 | 0.00-0.11 |
| bullets | F:aNcNdN | p050 | Qwen 3.8 | 0/64 | 0.00 | 0.00-0.06 |
| bullets | F:aNcNdN | tied | Qwen 3.5 | 0/32 | 0.00 | 0.00-0.11 |
| bullets | F:aNcNdN | tied | Qwen 3.8 | 0/64 | 0.00 | 0.00-0.06 |
| send | F:aBcBdB | p050 | Qwen 3.5 | 2/32 | 0.06 | 0.02-0.20 |
| send | F:aBcBdB | p050 | Qwen 3.8 | 34/64 | 0.53 | 0.41-0.65 |
| send | F:aBcBdB | tied | Qwen 3.5 | 0/32 | 0.00 | 0.00-0.11 |
| send | F:aBcBdB | tied | Qwen 3.8 | 0/64 | 0.00 | 0.00-0.06 |
| send | F:aBcBdN | p050 | Qwen 3.5 | 0/32 | 0.00 | 0.00-0.11 |
| send | F:aBcBdN | p050 | Qwen 3.8 | 12/64 | 0.19 | 0.11-0.30 |
| send | F:aBcBdN | tied | Qwen 3.5 | 0/32 | 0.00 | 0.00-0.11 |
| send | F:aBcBdN | tied | Qwen 3.8 | 0/64 | 0.00 | 0.00-0.06 |
| send | F:aBcNdB | p050 | Qwen 3.5 | 0/32 | 0.00 | 0.00-0.11 |
| send | F:aBcNdB | p050 | Qwen 3.8 | 22/64 | 0.34 | 0.24-0.47 |
| send | F:aBcNdB | tied | Qwen 3.5 | 0/32 | 0.00 | 0.00-0.11 |
| send | F:aBcNdB | tied | Qwen 3.8 | 0/64 | 0.00 | 0.00-0.06 |
| send | F:aBcNdN | p050 | Qwen 3.5 | 0/32 | 0.00 | 0.00-0.11 |
| send | F:aBcNdN | p050 | Qwen 3.8 | 3/64 | 0.05 | 0.02-0.13 |
| send | F:aBcNdN | tied | Qwen 3.5 | 0/32 | 0.00 | 0.00-0.11 |
| send | F:aBcNdN | tied | Qwen 3.8 | 0/64 | 0.00 | 0.00-0.06 |
| send | F:aNcBdB | p050 | Qwen 3.5 | 1/32 | 0.03 | 0.01-0.16 |
| send | F:aNcBdB | p050 | Qwen 3.8 | 13/64 | 0.20 | 0.12-0.32 |
| send | F:aNcBdB | tied | Qwen 3.5 | 0/32 | 0.00 | 0.00-0.11 |
| send | F:aNcBdB | tied | Qwen 3.8 | 0/64 | 0.00 | 0.00-0.06 |
| send | F:aNcBdN | p050 | Qwen 3.5 | 0/32 | 0.00 | 0.00-0.11 |
| send | F:aNcBdN | p050 | Qwen 3.8 | 1/64 | 0.02 | 0.00-0.08 |
| send | F:aNcBdN | tied | Qwen 3.5 | 0/32 | 0.00 | 0.00-0.11 |
| send | F:aNcBdN | tied | Qwen 3.8 | 0/64 | 0.00 | 0.00-0.06 |
| send | F:aNcNdB | p050 | Qwen 3.5 | 0/32 | 0.00 | 0.00-0.11 |
| send | F:aNcNdB | p050 | Qwen 3.8 | 3/64 | 0.05 | 0.02-0.13 |
| send | F:aNcNdB | tied | Qwen 3.5 | 0/32 | 0.00 | 0.00-0.11 |
| send | F:aNcNdB | tied | Qwen 3.8 | 0/64 | 0.00 | 0.00-0.06 |
| send | F:aNcNdN | p050 | Qwen 3.5 | 0/32 | 0.00 | 0.00-0.11 |
| send | F:aNcNdN | p050 | Qwen 3.8 | 0/64 | 0.00 | 0.00-0.06 |
| send | F:aNcNdN | tied | Qwen 3.5 | 0/32 | 0.00 | 0.00-0.11 |
| send | F:aNcNdN | tied | Qwen 3.8 | 0/64 | 0.00 | 0.00-0.06 |
| titles | F:aBcBdB | p050 | Qwen 3.5 | 1/32 | 0.03 | 0.01-0.16 |
| titles | F:aBcBdB | p050 | Qwen 3.8 | 22/64 | 0.34 | 0.24-0.47 |
| titles | F:aBcBdB | tied | Qwen 3.5 | 0/32 | 0.00 | 0.00-0.11 |
| titles | F:aBcBdB | tied | Qwen 3.8 | 0/64 | 0.00 | 0.00-0.06 |
| titles | F:aBcBdN | p050 | Qwen 3.5 | 0/32 | 0.00 | 0.00-0.11 |
| titles | F:aBcBdN | p050 | Qwen 3.8 | 13/64 | 0.20 | 0.12-0.32 |
| titles | F:aBcBdN | tied | Qwen 3.5 | 0/32 | 0.00 | 0.00-0.11 |
| titles | F:aBcBdN | tied | Qwen 3.8 | 0/64 | 0.00 | 0.00-0.06 |
| titles | F:aBcNdB | p050 | Qwen 3.5 | 0/32 | 0.00 | 0.00-0.11 |
| titles | F:aBcNdB | p050 | Qwen 3.8 | 2/64 | 0.03 | 0.01-0.11 |
| titles | F:aBcNdB | tied | Qwen 3.5 | 0/32 | 0.00 | 0.00-0.11 |
| titles | F:aBcNdB | tied | Qwen 3.8 | 0/64 | 0.00 | 0.00-0.06 |
| titles | F:aBcNdN | p050 | Qwen 3.5 | 0/32 | 0.00 | 0.00-0.11 |
| titles | F:aBcNdN | p050 | Qwen 3.8 | 1/64 | 0.02 | 0.00-0.08 |
| titles | F:aBcNdN | tied | Qwen 3.5 | 0/32 | 0.00 | 0.00-0.11 |
| titles | F:aBcNdN | tied | Qwen 3.8 | 0/64 | 0.00 | 0.00-0.06 |
| titles | F:aNcBdB | p050 | Qwen 3.5 | 0/32 | 0.00 | 0.00-0.11 |
| titles | F:aNcBdB | p050 | Qwen 3.8 | 13/64 | 0.20 | 0.12-0.32 |
| titles | F:aNcBdB | tied | Qwen 3.5 | 0/32 | 0.00 | 0.00-0.11 |
| titles | F:aNcBdB | tied | Qwen 3.8 | 0/64 | 0.00 | 0.00-0.06 |
| titles | F:aNcBdN | p050 | Qwen 3.5 | 0/32 | 0.00 | 0.00-0.11 |
| titles | F:aNcBdN | p050 | Qwen 3.8 | 2/64 | 0.03 | 0.01-0.11 |
| titles | F:aNcBdN | tied | Qwen 3.5 | 0/32 | 0.00 | 0.00-0.11 |
| titles | F:aNcBdN | tied | Qwen 3.8 | 0/64 | 0.00 | 0.00-0.06 |
| titles | F:aNcNdB | p050 | Qwen 3.5 | 0/32 | 0.00 | 0.00-0.11 |
| titles | F:aNcNdB | p050 | Qwen 3.8 | 2/64 | 0.03 | 0.01-0.11 |
| titles | F:aNcNdB | tied | Qwen 3.5 | 0/32 | 0.00 | 0.00-0.11 |
| titles | F:aNcNdB | tied | Qwen 3.8 | 0/64 | 0.00 | 0.00-0.06 |
| titles | F:aNcNdN | p050 | Qwen 3.5 | 0/32 | 0.00 | 0.00-0.11 |
| titles | F:aNcNdN | p050 | Qwen 3.8 | 1/64 | 0.02 | 0.00-0.08 |
| titles | F:aNcNdN | tied | Qwen 3.5 | 0/32 | 0.00 | 0.00-0.11 |
| titles | F:aNcNdN | tied | Qwen 3.8 | 0/64 | 0.00 | 0.00-0.06 |

Non-valid: none. Rows: 4608.

† No block showed any difference in this contrast (all n block contrasts exactly 0), so the bootstrap interval is degenerate. The bracket shown instead is a distribution-free 95% bound [-s·M, +s·M]: s = 1 − 0.025^(1/n) is the Clopper–Pearson upper limit on the share of blocks that could differ given 0 of n did, and M is the largest possible per-block contrast (1 for a single score effect, 2 for a difference of score effects). It is conservative; effects larger than the bound are ruled out, smaller ones are not. Source: `pa_bounds.py` (amendment 1).
