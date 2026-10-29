# Simulation calibration of the planned tests (EXPLORATORY score-midpoint experiment)

Design per model x panel: 12 scenarios x 3 replies per cell; scenario logit offsets N(0, 1.5) shared across a scenario's cells; 400 simulations per row unless stated; 2000 permutations per test. alpha = 0.05. Monte Carlo SE of a rate near 0.05 with 400 simulations ≈ 0.011.

| Check | Rejection rate / coverage | Target |
|---|---|---|
| Size, midpoint test (3 midpoints at +0.20), no midpoint effect, base 0.05 | 0.022 | ≤ 0.05 |
| Size, midpoint test (3 midpoints at +0.20), no midpoint effect, base 0.2 | 0.030 | ≤ 0.05 |
| Size, midpoint test (3 midpoints at +0.20), no midpoint effect, base 0.5 | 0.030 | ≤ 0.05 |
| Size, midpoint test (3 midpoints at +0.20), no midpoint effect, base 0.8 | 0.050 | ≤ 0.05 |
| Size, high50 test (0.95/0.45 vs 0.75/0.25), no effect, base 0.2 | 0.022 | ≤ 0.05 |
| Size, high50 test (0.95/0.45 vs 0.75/0.25), no effect, base 0.5 | 0.028 | ≤ 0.05 |
| Size, high50 test (0.95/0.45 vs 0.75/0.25), no effect, base 0.8 | 0.018 | ≤ 0.05 |
| Size, floor test (3 reversed cells vs no history), no difference, base 0.02 | 0.020 | ≤ 0.05 |
| Size, floor test (3 reversed cells vs no history), no difference, base 0.1 | 0.022 | ≤ 0.05 |
| Size, floor test (3 reversed cells vs no history), no difference, base 0.3 | 0.033 | ≤ 0.05 |
| Holm family-wise error, 24 planned tests, global null (200 sims) | 0.030 | ≤ 0.05 |
| Power, midpoint test, logit-linear 20% → 80% at mid 0.2 → 0.8 (scenario-average logits) | 0.995 (unadj.); 0.920 (at 0.05/24) | (power) |
| Power, midpoint test, logit-linear 10% → 40% at mid 0.2 → 0.8 (scenario-average logits) | 0.772 (unadj.); 0.352 (at 0.05/24) | (power) |
| Power, midpoint test, logit-linear 30% → 50% at mid 0.2 → 0.8 (scenario-average logits) | 0.237 (unadj.); 0.022 (at 0.05/24) | (power) |
| Power, high50 test, 50% → 80% | 0.520 (unadj.); 0.150 (at 0.05/24) | (power) |
| Power, high50 test, 20% → 50% | 0.565 (unadj.); 0.135 (at 0.05/24) | (power) |
| Power, high50 test, 60% → 75% | 0.138 (unadj.); 0.010 (at 0.05/24) | (power) |
| Power, floor test, reversed 10% vs baseline 1% | 0.605 (unadj.); 0.090 (at 0.05/24) | (power) |
| Power, floor test, reversed 20% vs baseline 1% | 0.953 (unadj.); 0.627 (at 0.05/24) | (power) |
| CI coverage, cell rate, scenario-average logit at 0.05 (population rate 0.10): cluster bootstrap / naive Wilson | 0.820 / 0.907 | 0.95 |
| CI coverage, cell rate, scenario-average logit at 0.2 (population rate 0.27): cluster bootstrap / naive Wilson | 0.915 / 0.850 | 0.95 |
| CI coverage, cell rate, scenario-average logit at 0.5 (population rate 0.50): cluster bootstrap / naive Wilson | 0.938 / 0.868 | 0.95 |
