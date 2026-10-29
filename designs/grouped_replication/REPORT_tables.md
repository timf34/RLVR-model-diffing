# Experiment A: analysis tables (auto-generated)

Generated 2026-10-29T03:53:15+00:00 by `designs/overnight_common/analysis/analyse.py A`. Blocks: 176 (main); generation records used: 3520. Judge mode: on, factual=all.

Methods: block-level paired contrasts (one generation per cell). Family / B estimates are equal-weighted means of subtype / direction means. p: stratified sign-flip permutation of block values (exact when ≤18 non-zero blocks, else 20,000 Monte Carlo draws, fixed seed). CI: cluster bootstrap of blocks within strata (4000 reps, percentile). † = zero-variation interval replaced by the block-level one-sided 95% bound 1−0.05^(1/n) on each side (never a zero-width interval). Rates: `0/n (≤ub)` = no events, one-sided 95% upper bound at the block level. Unclear and non-valid cells make that block's contrast missing; the sensitivity column re-estimates with unclear → violates / → complies, and worst-case bounds. Non-significant results are not equivalence: the last column states the effects the interval still allows.

## Primary contrasts (Qwen 3.8)

Holm: Holm over the 8 primary tests.

| id | contrast | estimate | 95% CI | p | Holm p | blocks used/planned | missing nonvalid/unclear/absent | unclear→viol / →comp; worst-case | interval reading |
|---|---|---|---|---|---|---|---|---|---|
| A1 | formatting: episode, rate(+0.50) - rate(+0.05) | +0.000 | [-0.04, +0.04] | 1.000 | 1.000 | 80/80 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.04 to +0.04 |
| A2 | reserved actions: episode, rate(+0.50) - rate(+0.05) | +0.000 | [-0.06, +0.06]† | 1.000 | 1.000 | 48/48 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.06 to +0.06 |
| A3 | factual reporting: episode, rate(+0.50) - rate(+0.05) | +0.021 | [+0.00, +0.06] | 1.000 | 1.000 | 48/48 | 0/0/0 | +0.02 / +0.02; [+0.02, +0.02] | compatible with effects from +0.00 to +0.06 |
| A4 | formatting: [episode(+0.50 - +0.05)] - [ordinary(+0.50 - +0.05)] | -0.013 | [-0.05, +0.03] | 1.000 | 1.000 | 80/80 | 0/0/0 | -0.01 / -0.01; [-0.01, -0.01] | compatible with effects from -0.05 to +0.03 |
| A5 | reserved actions: [episode(+0.50 - +0.05)] - [ordinary(+0.50 - +0.05)] | +0.000 | [-0.12, +0.12]† | 1.000 | 1.000 | 48/48 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.12 to +0.12 |
| A6 | factual reporting: [episode(+0.50 - +0.05)] - [ordinary(+0.50 - +0.05)] | +0.000 | [-0.06, +0.06] | 1.000 | 1.000 | 48/48 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.06 to +0.06 |

## Denominators

| model | frame | permission | cond | planned | generated | valid | statuses | unclear (final) | judged |
|---|---|---|---|---|---|---|---|---|---|
| Qwen 3.5 | episode | na | none | 176 | 176 | 176 | valid 176 | {'violation': 0} | {'violation': 33} |
| Qwen 3.5 | episode | na | -0.50 | 176 | 176 | 176 | valid 176 | {'violation': 0} | {'violation': 32} |
| Qwen 3.5 | episode | na | +0.00 | 176 | 176 | 176 | valid 176 | {'violation': 0} | {'violation': 32} |
| Qwen 3.5 | episode | na | +0.05 | 176 | 176 | 176 | valid 176 | {'violation': 0} | {'violation': 32} |
| Qwen 3.5 | episode | na | +0.50 | 176 | 176 | 176 | valid 176 | {'violation': 0} | {'violation': 34} |
| Qwen 3.5 | ordinary | na | none | 176 | 176 | 176 | valid 176 | {'violation': 0} | {'violation': 35} |
| Qwen 3.5 | ordinary | na | -0.50 | 176 | 176 | 176 | valid 176 | {'violation': 0} | {'violation': 33} |
| Qwen 3.5 | ordinary | na | +0.00 | 176 | 176 | 176 | valid 176 | {'violation': 0} | {'violation': 33} |
| Qwen 3.5 | ordinary | na | +0.05 | 176 | 176 | 176 | valid 176 | {'violation': 0} | {'violation': 32} |
| Qwen 3.5 | ordinary | na | +0.50 | 176 | 176 | 176 | valid 176 | {'violation': 0} | {'violation': 32} |
| Qwen 3.8 | episode | na | none | 176 | 176 | 176 | valid 176 | {'violation': 0} | {'violation': 33} |
| Qwen 3.8 | episode | na | -0.50 | 176 | 176 | 176 | valid 176 | {'violation': 0} | {'violation': 32} |
| Qwen 3.8 | episode | na | +0.00 | 176 | 176 | 176 | valid 176 | {'violation': 0} | {'violation': 32} |
| Qwen 3.8 | episode | na | +0.05 | 176 | 176 | 176 | valid 176 | {'violation': 0} | {'violation': 33} |
| Qwen 3.8 | episode | na | +0.50 | 176 | 176 | 176 | valid 176 | {'violation': 0} | {'violation': 33} |
| Qwen 3.8 | ordinary | na | none | 176 | 176 | 176 | valid 176 | {'violation': 0} | {'violation': 33} |
| Qwen 3.8 | ordinary | na | -0.50 | 176 | 176 | 176 | valid 176 | {'violation': 0} | {'violation': 32} |
| Qwen 3.8 | ordinary | na | +0.00 | 176 | 176 | 176 | valid 176 | {'violation': 0} | {'violation': 32} |
| Qwen 3.8 | ordinary | na | +0.05 | 176 | 176 | 176 | valid 176 | {'violation': 0} | {'violation': 33} |
| Qwen 3.8 | ordinary | na | +0.50 | 176 | 176 | 176 | valid 176 | {'violation': 0} | {'violation': 34} |

## Violation rates by family

| outcome | group | model | frame | permission | none | -0.50 | +0.00 | +0.05 | +0.50 |
|---|---|---|---|---|---|---|---|---|---|
| violation | factual_reporting | Qwen 3.5 | episode | na | 0/48 (≤0.06) | 0/48 (≤0.06) | 0/48 (≤0.06) | 0/48 (≤0.06) | 0/48 (≤0.06) |
| violation | factual_reporting | Qwen 3.5 | ordinary | na | 0/48 (≤0.06) | 0/48 (≤0.06) | 0/48 (≤0.06) | 0/48 (≤0.06) | 0/48 (≤0.06) |
| violation | factual_reporting | Qwen 3.8 | episode | na | 0/48 (≤0.06) | 0/48 (≤0.06) | 0/48 (≤0.06) | 0/48 (≤0.06) | 0.02 [0.00, 0.06] (1/48) |
| violation | factual_reporting | Qwen 3.8 | ordinary | na | 0/48 (≤0.06) | 0/48 (≤0.06) | 0/48 (≤0.06) | 0/48 (≤0.06) | 0.02 [0.00, 0.06] (1/48) |
| violation | formatting | Qwen 3.5 | episode | na | 0.04 [0.00, 0.07] (3/80) | 0/80 (≤0.04) | 0/80 (≤0.04) | 0/80 (≤0.04) | 0.01 [0.00, 0.04] (1/80) |
| violation | formatting | Qwen 3.5 | ordinary | na | 0.06 [0.01, 0.11] (5/80) | 0.03 [0.00, 0.06] (2/80) | 0.01 [0.00, 0.04] (1/80) | 0.01 [0.00, 0.04] (1/80) | 0/80 (≤0.04) |
| violation | formatting | Qwen 3.8 | episode | na | 0.01 [0.00, 0.04] (1/80) | 0/80 (≤0.04) | 0/80 (≤0.04) | 0.01 [0.00, 0.04] (1/80) | 0.01 [0.00, 0.04] (1/80) |
| violation | formatting | Qwen 3.8 | ordinary | na | 0.04 [0.00, 0.09] (3/80) | 0/80 (≤0.04) | 0/80 (≤0.04) | 0.01 [0.00, 0.04] (1/80) | 0.03 [0.00, 0.06] (2/80) |
| violation | reserved_actions | Qwen 3.5 | episode | na | 0/48 (≤0.06) | 0/48 (≤0.06) | 0/48 (≤0.06) | 0/48 (≤0.06) | 0/48 (≤0.06) |
| violation | reserved_actions | Qwen 3.5 | ordinary | na | 0/48 (≤0.06) | 0/48 (≤0.06) | 0/48 (≤0.06) | 0/48 (≤0.06) | 0/48 (≤0.06) |
| violation | reserved_actions | Qwen 3.8 | episode | na | 0/48 (≤0.06) | 0/48 (≤0.06) | 0/48 (≤0.06) | 0/48 (≤0.06) | 0/48 (≤0.06) |
| violation | reserved_actions | Qwen 3.8 | ordinary | na | 0/48 (≤0.06) | 0/48 (≤0.06) | 0/48 (≤0.06) | 0/48 (≤0.06) | 0/48 (≤0.06) |

## Violation rates by subtype

| outcome | group | model | frame | permission | none | -0.50 | +0.00 | +0.05 | +0.50 |
|---|---|---|---|---|---|---|---|---|---|
| violation | bullets | Qwen 3.5 | episode | na | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) |
| violation | bullets | Qwen 3.5 | ordinary | na | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) |
| violation | bullets | Qwen 3.8 | episode | na | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) |
| violation | bullets | Qwen 3.8 | ordinary | na | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) |
| violation | certainty | Qwen 3.5 | episode | na | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) |
| violation | certainty | Qwen 3.5 | ordinary | na | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) |
| violation | certainty | Qwen 3.8 | episode | na | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) |
| violation | certainty | Qwen 3.8 | ordinary | na | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) |
| violation | emdash | Qwen 3.5 | episode | na | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) |
| violation | emdash | Qwen 3.5 | ordinary | na | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) |
| violation | emdash | Qwen 3.8 | episode | na | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) |
| violation | emdash | Qwen 3.8 | ordinary | na | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) |
| violation | emoji | Qwen 3.5 | episode | na | 0.06 [0.01, 0.28] (1/16) | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) |
| violation | emoji | Qwen 3.5 | ordinary | na | 0.06 [0.01, 0.28] (1/16) | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) |
| violation | emoji | Qwen 3.8 | episode | na | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) |
| violation | emoji | Qwen 3.8 | ordinary | na | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) |
| violation | limitation | Qwen 3.5 | episode | na | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) |
| violation | limitation | Qwen 3.5 | ordinary | na | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) |
| violation | limitation | Qwen 3.8 | episode | na | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) | 0.06 [0.01, 0.28] (1/16) |
| violation | limitation | Qwen 3.8 | ordinary | na | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) | 0.06 [0.01, 0.28] (1/16) |
| violation | publish | Qwen 3.5 | episode | na | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) |
| violation | publish | Qwen 3.5 | ordinary | na | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) |
| violation | publish | Qwen 3.8 | episode | na | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) |
| violation | publish | Qwen 3.8 | ordinary | na | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) |
| violation | send | Qwen 3.5 | episode | na | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) |
| violation | send | Qwen 3.5 | ordinary | na | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) |
| violation | send | Qwen 3.8 | episode | na | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) |
| violation | send | Qwen 3.8 | ordinary | na | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) |
| violation | signoff | Qwen 3.5 | episode | na | 0.06 [0.01, 0.28] (1/16) | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) | 0.06 [0.01, 0.28] (1/16) |
| violation | signoff | Qwen 3.5 | ordinary | na | 0.19 [0.07, 0.43] (3/16) | 0.06 [0.01, 0.28] (1/16) | 0.06 [0.01, 0.28] (1/16) | 0/16 (≤0.17) | 0/16 (≤0.17) |
| violation | signoff | Qwen 3.8 | episode | na | 0.06 [0.01, 0.28] (1/16) | 0/16 (≤0.17) | 0/16 (≤0.17) | 0.06 [0.01, 0.28] (1/16) | 0.06 [0.01, 0.28] (1/16) |
| violation | signoff | Qwen 3.8 | ordinary | na | 0.12 [0.03, 0.36] (2/16) | 0/16 (≤0.17) | 0/16 (≤0.17) | 0.06 [0.01, 0.28] (1/16) | 0.12 [0.03, 0.36] (2/16) |
| violation | status | Qwen 3.5 | episode | na | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) |
| violation | status | Qwen 3.5 | ordinary | na | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) |
| violation | status | Qwen 3.8 | episode | na | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) |
| violation | status | Qwen 3.8 | ordinary | na | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) |
| violation | submit | Qwen 3.5 | episode | na | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) |
| violation | submit | Qwen 3.5 | ordinary | na | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) |
| violation | submit | Qwen 3.8 | episode | na | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) |
| violation | submit | Qwen 3.8 | ordinary | na | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) |
| violation | title | Qwen 3.5 | episode | na | 0.06 [0.01, 0.28] (1/16) | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) |
| violation | title | Qwen 3.5 | ordinary | na | 0.06 [0.01, 0.28] (1/16) | 0.06 [0.01, 0.28] (1/16) | 0/16 (≤0.17) | 0.06 [0.01, 0.28] (1/16) | 0/16 (≤0.17) |
| violation | title | Qwen 3.8 | episode | na | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) |
| violation | title | Qwen 3.8 | ordinary | na | 0.06 [0.01, 0.28] (1/16) | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) |

## Secondary contrasts (unadjusted p; descriptive)

### gap_vs_tie

| id | contrast | estimate | 95% CI | p | blocks used/planned | missing nonvalid/unclear/absent | unclear→viol / →comp; worst-case | interval reading |
|---|---|---|---|---|---|---|---|---|
| [Qwen 3.8] formatting: episode +0.50 vs +0.00 | formatting: episode, rate(+0.50) - rate(+0.00) | +0.013 | [+0.00, +0.04] | 1.000 | 80/80 | 0/0/0 | +0.01 / +0.01; [+0.01, +0.01] | compatible with effects from +0.00 to +0.04 |
| [Qwen 3.8] formatting: ordinary +0.50 vs +0.00 | formatting: ordinary, rate(+0.50) - rate(+0.00) | +0.025 | [+0.00, +0.06] | 0.500 | 80/80 | 0/0/0 | +0.03 / +0.03; [+0.03, +0.03] | compatible with effects from +0.00 to +0.06 |
| [Qwen 3.8] reserved_actions: episode +0.50 vs +0.00 | reserved actions: episode, rate(+0.50) - rate(+0.00) | +0.000 | [-0.06, +0.06]† | 1.000 | 48/48 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.06 to +0.06 |
| [Qwen 3.8] reserved_actions: ordinary +0.50 vs +0.00 | reserved actions: ordinary, rate(+0.50) - rate(+0.00) | +0.000 | [-0.06, +0.06]† | 1.000 | 48/48 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.06 to +0.06 |
| [Qwen 3.8] factual_reporting: episode +0.50 vs +0.00 | factual reporting: episode, rate(+0.50) - rate(+0.00) | +0.021 | [+0.00, +0.06] | 1.000 | 48/48 | 0/0/0 | +0.02 / +0.02; [+0.02, +0.02] | compatible with effects from +0.00 to +0.06 |
| [Qwen 3.8] factual_reporting: ordinary +0.50 vs +0.00 | factual reporting: ordinary, rate(+0.50) - rate(+0.00) | +0.021 | [+0.00, +0.06] | 1.000 | 48/48 | 0/0/0 | +0.02 / +0.02; [+0.02, +0.02] | compatible with effects from +0.00 to +0.06 |
| [Qwen 3.5] formatting: episode +0.50 vs +0.00 | formatting: episode, rate(+0.50) - rate(+0.00) | +0.013 | [+0.00, +0.04] | 1.000 | 80/80 | 0/0/0 | +0.01 / +0.01; [+0.01, +0.01] | compatible with effects from +0.00 to +0.04 |
| [Qwen 3.5] formatting: ordinary +0.50 vs +0.00 | formatting: ordinary, rate(+0.50) - rate(+0.00) | -0.013 | [-0.04, +0.00] | 1.000 | 80/80 | 0/0/0 | -0.01 / -0.01; [-0.01, -0.01] | compatible with effects from -0.04 to +0.00 |
| [Qwen 3.5] reserved_actions: episode +0.50 vs +0.00 | reserved actions: episode, rate(+0.50) - rate(+0.00) | +0.000 | [-0.06, +0.06]† | 1.000 | 48/48 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.06 to +0.06 |
| [Qwen 3.5] reserved_actions: ordinary +0.50 vs +0.00 | reserved actions: ordinary, rate(+0.50) - rate(+0.00) | +0.000 | [-0.06, +0.06]† | 1.000 | 48/48 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.06 to +0.06 |
| [Qwen 3.5] factual_reporting: episode +0.50 vs +0.00 | factual reporting: episode, rate(+0.50) - rate(+0.00) | +0.000 | [-0.06, +0.06]† | 1.000 | 48/48 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.06 to +0.06 |
| [Qwen 3.5] factual_reporting: ordinary +0.50 vs +0.00 | factual reporting: ordinary, rate(+0.50) - rate(+0.00) | +0.000 | [-0.06, +0.06]† | 1.000 | 48/48 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.06 to +0.06 |

### tie_vs_neg

| id | contrast | estimate | 95% CI | p | blocks used/planned | missing nonvalid/unclear/absent | unclear→viol / →comp; worst-case | interval reading |
|---|---|---|---|---|---|---|---|---|
| [Qwen 3.8] formatting: episode +0.00 vs -0.50 | formatting: episode, rate(+0.00) - rate(-0.50) | +0.000 | [-0.04, +0.04]† | 1.000 | 80/80 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.04 to +0.04 |
| [Qwen 3.8] formatting: ordinary +0.00 vs -0.50 | formatting: ordinary, rate(+0.00) - rate(-0.50) | +0.000 | [-0.04, +0.04]† | 1.000 | 80/80 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.04 to +0.04 |
| [Qwen 3.8] reserved_actions: episode +0.00 vs -0.50 | reserved actions: episode, rate(+0.00) - rate(-0.50) | +0.000 | [-0.06, +0.06]† | 1.000 | 48/48 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.06 to +0.06 |
| [Qwen 3.8] reserved_actions: ordinary +0.00 vs -0.50 | reserved actions: ordinary, rate(+0.00) - rate(-0.50) | +0.000 | [-0.06, +0.06]† | 1.000 | 48/48 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.06 to +0.06 |
| [Qwen 3.8] factual_reporting: episode +0.00 vs -0.50 | factual reporting: episode, rate(+0.00) - rate(-0.50) | +0.000 | [-0.06, +0.06]† | 1.000 | 48/48 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.06 to +0.06 |
| [Qwen 3.8] factual_reporting: ordinary +0.00 vs -0.50 | factual reporting: ordinary, rate(+0.00) - rate(-0.50) | +0.000 | [-0.06, +0.06]† | 1.000 | 48/48 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.06 to +0.06 |
| [Qwen 3.5] formatting: episode +0.00 vs -0.50 | formatting: episode, rate(+0.00) - rate(-0.50) | +0.000 | [-0.04, +0.04]† | 1.000 | 80/80 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.04 to +0.04 |
| [Qwen 3.5] formatting: ordinary +0.00 vs -0.50 | formatting: ordinary, rate(+0.00) - rate(-0.50) | -0.013 | [-0.05, +0.03] | 1.000 | 80/80 | 0/0/0 | -0.01 / -0.01; [-0.01, -0.01] | compatible with effects from -0.05 to +0.03 |
| [Qwen 3.5] reserved_actions: episode +0.00 vs -0.50 | reserved actions: episode, rate(+0.00) - rate(-0.50) | +0.000 | [-0.06, +0.06]† | 1.000 | 48/48 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.06 to +0.06 |
| [Qwen 3.5] reserved_actions: ordinary +0.00 vs -0.50 | reserved actions: ordinary, rate(+0.00) - rate(-0.50) | +0.000 | [-0.06, +0.06]† | 1.000 | 48/48 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.06 to +0.06 |
| [Qwen 3.5] factual_reporting: episode +0.00 vs -0.50 | factual reporting: episode, rate(+0.00) - rate(-0.50) | +0.000 | [-0.06, +0.06]† | 1.000 | 48/48 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.06 to +0.06 |
| [Qwen 3.5] factual_reporting: ordinary +0.00 vs -0.50 | factual reporting: ordinary, rate(+0.00) - rate(-0.50) | +0.000 | [-0.06, +0.06]† | 1.000 | 48/48 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.06 to +0.06 |

### nohist_vs_tie

| id | contrast | estimate | 95% CI | p | blocks used/planned | missing nonvalid/unclear/absent | unclear→viol / →comp; worst-case | interval reading |
|---|---|---|---|---|---|---|---|---|
| [Qwen 3.8] formatting: episode none vs +0.00 | formatting: episode, rate(none) - rate(+0.00) | +0.013 | [+0.00, +0.04] | 1.000 | 80/80 | 0/0/0 | +0.01 / +0.01; [+0.01, +0.01] | compatible with effects from +0.00 to +0.04 |
| [Qwen 3.8] formatting: ordinary none vs +0.00 | formatting: ordinary, rate(none) - rate(+0.00) | +0.038 | [+0.00, +0.07] | 0.250 | 80/80 | 0/0/0 | +0.04 / +0.04; [+0.04, +0.04] | compatible with effects from +0.00 to +0.07 |
| [Qwen 3.8] reserved_actions: episode none vs +0.00 | reserved actions: episode, rate(none) - rate(+0.00) | +0.000 | [-0.06, +0.06]† | 1.000 | 48/48 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.06 to +0.06 |
| [Qwen 3.8] reserved_actions: ordinary none vs +0.00 | reserved actions: ordinary, rate(none) - rate(+0.00) | +0.000 | [-0.06, +0.06]† | 1.000 | 48/48 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.06 to +0.06 |
| [Qwen 3.8] factual_reporting: episode none vs +0.00 | factual reporting: episode, rate(none) - rate(+0.00) | +0.000 | [-0.06, +0.06]† | 1.000 | 48/48 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.06 to +0.06 |
| [Qwen 3.8] factual_reporting: ordinary none vs +0.00 | factual reporting: ordinary, rate(none) - rate(+0.00) | +0.000 | [-0.06, +0.06]† | 1.000 | 48/48 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.06 to +0.06 |
| [Qwen 3.5] formatting: episode none vs +0.00 | formatting: episode, rate(none) - rate(+0.00) | +0.038 | [+0.00, +0.09] | 0.250 | 80/80 | 0/0/0 | +0.04 / +0.04; [+0.04, +0.04] | compatible with effects from +0.00 to +0.09 |
| [Qwen 3.5] formatting: ordinary none vs +0.00 | formatting: ordinary, rate(none) - rate(+0.00) | +0.050 | [+0.01, +0.10] | 0.125 | 80/80 | 0/0/0 | +0.05 / +0.05; [+0.05, +0.05] | excludes 0; effect between +0.01 and +0.10 |
| [Qwen 3.5] reserved_actions: episode none vs +0.00 | reserved actions: episode, rate(none) - rate(+0.00) | +0.000 | [-0.06, +0.06]† | 1.000 | 48/48 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.06 to +0.06 |
| [Qwen 3.5] reserved_actions: ordinary none vs +0.00 | reserved actions: ordinary, rate(none) - rate(+0.00) | +0.000 | [-0.06, +0.06]† | 1.000 | 48/48 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.06 to +0.06 |
| [Qwen 3.5] factual_reporting: episode none vs +0.00 | factual reporting: episode, rate(none) - rate(+0.00) | +0.000 | [-0.06, +0.06]† | 1.000 | 48/48 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.06 to +0.06 |
| [Qwen 3.5] factual_reporting: ordinary none vs +0.00 | factual reporting: ordinary, rate(none) - rate(+0.00) | +0.000 | [-0.06, +0.06]† | 1.000 | 48/48 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.06 to +0.06 |

### gap_effect

| id | contrast | estimate | 95% CI | p | blocks used/planned | missing nonvalid/unclear/absent | unclear→viol / →comp; worst-case | interval reading |
|---|---|---|---|---|---|---|---|---|
| [Qwen 3.8] formatting: ordinary gap | formatting: ordinary, rate(+0.50) - rate(+0.05) | +0.013 | [+0.00, +0.04] | 1.000 | 80/80 | 0/0/0 | +0.01 / +0.01; [+0.01, +0.01] | compatible with effects from +0.00 to +0.04 |
| [Qwen 3.8] reserved_actions: ordinary gap | reserved actions: ordinary, rate(+0.50) - rate(+0.05) | +0.000 | [-0.06, +0.06]† | 1.000 | 48/48 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.06 to +0.06 |
| [Qwen 3.8] factual_reporting: ordinary gap | factual reporting: ordinary, rate(+0.50) - rate(+0.05) | +0.021 | [+0.00, +0.06] | 1.000 | 48/48 | 0/0/0 | +0.02 / +0.02; [+0.02, +0.02] | compatible with effects from +0.00 to +0.06 |
| [Qwen 3.5] A1 | formatting: episode, rate(+0.50) - rate(+0.05) | +0.013 | [+0.00, +0.04] | 1.000 | 80/80 | 0/0/0 | +0.01 / +0.01; [+0.01, +0.01] | compatible with effects from +0.00 to +0.04 |
| [Qwen 3.5] A2 | reserved actions: episode, rate(+0.50) - rate(+0.05) | +0.000 | [-0.06, +0.06]† | 1.000 | 48/48 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.06 to +0.06 |
| [Qwen 3.5] A3 | factual reporting: episode, rate(+0.50) - rate(+0.05) | +0.000 | [-0.06, +0.06]† | 1.000 | 48/48 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.06 to +0.06 |
| [Qwen 3.5] formatting: ordinary gap | formatting: ordinary, rate(+0.50) - rate(+0.05) | -0.013 | [-0.04, +0.00] | 1.000 | 80/80 | 0/0/0 | -0.01 / -0.01; [-0.01, -0.01] | compatible with effects from -0.04 to +0.00 |
| [Qwen 3.5] reserved_actions: ordinary gap | reserved actions: ordinary, rate(+0.50) - rate(+0.05) | +0.000 | [-0.06, +0.06]† | 1.000 | 48/48 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.06 to +0.06 |
| [Qwen 3.5] factual_reporting: ordinary gap | factual reporting: ordinary, rate(+0.50) - rate(+0.05) | +0.000 | [-0.06, +0.06]† | 1.000 | 48/48 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.06 to +0.06 |

### subtype_gap_effect

| id | contrast | estimate | 95% CI | p | blocks used/planned | missing nonvalid/unclear/absent | unclear→viol / →comp; worst-case | interval reading |
|---|---|---|---|---|---|---|---|---|
| [Qwen 3.8] title: episode gap | title: episode, rate(+0.50) - rate(+0.05) | +0.000 | [-0.17, +0.17]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.17 to +0.17 |
| [Qwen 3.8] title: ordinary gap | title: ordinary, rate(+0.50) - rate(+0.05) | +0.000 | [-0.17, +0.17]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.17 to +0.17 |
| [Qwen 3.8] signoff: episode gap | signoff: episode, rate(+0.50) - rate(+0.05) | +0.000 | [-0.19, +0.19] | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.19 to +0.19 |
| [Qwen 3.8] signoff: ordinary gap | signoff: ordinary, rate(+0.50) - rate(+0.05) | +0.062 | [+0.00, +0.19] | 1.000 | 16/16 | 0/0/0 | +0.06 / +0.06; [+0.06, +0.06] | compatible with effects from +0.00 to +0.19 |
| [Qwen 3.8] emdash: episode gap | emdash: episode, rate(+0.50) - rate(+0.05) | +0.000 | [-0.17, +0.17]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.17 to +0.17 |
| [Qwen 3.8] emdash: ordinary gap | emdash: ordinary, rate(+0.50) - rate(+0.05) | +0.000 | [-0.17, +0.17]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.17 to +0.17 |
| [Qwen 3.8] bullets: episode gap | bullets: episode, rate(+0.50) - rate(+0.05) | +0.000 | [-0.17, +0.17]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.17 to +0.17 |
| [Qwen 3.8] bullets: ordinary gap | bullets: ordinary, rate(+0.50) - rate(+0.05) | +0.000 | [-0.17, +0.17]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.17 to +0.17 |
| [Qwen 3.8] emoji: episode gap | emoji: episode, rate(+0.50) - rate(+0.05) | +0.000 | [-0.17, +0.17]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.17 to +0.17 |
| [Qwen 3.8] emoji: ordinary gap | emoji: ordinary, rate(+0.50) - rate(+0.05) | +0.000 | [-0.17, +0.17]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.17 to +0.17 |
| [Qwen 3.8] send: episode gap | send: episode, rate(+0.50) - rate(+0.05) | +0.000 | [-0.17, +0.17]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.17 to +0.17 |
| [Qwen 3.8] send: ordinary gap | send: ordinary, rate(+0.50) - rate(+0.05) | +0.000 | [-0.17, +0.17]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.17 to +0.17 |
| [Qwen 3.8] publish: episode gap | publish: episode, rate(+0.50) - rate(+0.05) | +0.000 | [-0.17, +0.17]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.17 to +0.17 |
| [Qwen 3.8] publish: ordinary gap | publish: ordinary, rate(+0.50) - rate(+0.05) | +0.000 | [-0.17, +0.17]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.17 to +0.17 |
| [Qwen 3.8] submit: episode gap | submit: episode, rate(+0.50) - rate(+0.05) | +0.000 | [-0.17, +0.17]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.17 to +0.17 |
| [Qwen 3.8] submit: ordinary gap | submit: ordinary, rate(+0.50) - rate(+0.05) | +0.000 | [-0.17, +0.17]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.17 to +0.17 |
| [Qwen 3.8] limitation: episode gap | limitation: episode, rate(+0.50) - rate(+0.05) | +0.062 | [+0.00, +0.19] | 1.000 | 16/16 | 0/0/0 | +0.06 / +0.06; [+0.06, +0.06] | compatible with effects from +0.00 to +0.19 |
| [Qwen 3.8] limitation: ordinary gap | limitation: ordinary, rate(+0.50) - rate(+0.05) | +0.062 | [+0.00, +0.19] | 1.000 | 16/16 | 0/0/0 | +0.06 / +0.06; [+0.06, +0.06] | compatible with effects from +0.00 to +0.19 |
| [Qwen 3.8] certainty: episode gap | certainty: episode, rate(+0.50) - rate(+0.05) | +0.000 | [-0.17, +0.17]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.17 to +0.17 |
| [Qwen 3.8] certainty: ordinary gap | certainty: ordinary, rate(+0.50) - rate(+0.05) | +0.000 | [-0.17, +0.17]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.17 to +0.17 |
| [Qwen 3.8] status: episode gap | status: episode, rate(+0.50) - rate(+0.05) | +0.000 | [-0.17, +0.17]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.17 to +0.17 |
| [Qwen 3.8] status: ordinary gap | status: ordinary, rate(+0.50) - rate(+0.05) | +0.000 | [-0.17, +0.17]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.17 to +0.17 |
| [Qwen 3.5] title: episode gap | title: episode, rate(+0.50) - rate(+0.05) | +0.000 | [-0.17, +0.17]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.17 to +0.17 |
| [Qwen 3.5] title: ordinary gap | title: ordinary, rate(+0.50) - rate(+0.05) | -0.062 | [-0.19, +0.00] | 1.000 | 16/16 | 0/0/0 | -0.06 / -0.06; [-0.06, -0.06] | compatible with effects from -0.19 to +0.00 |
| [Qwen 3.5] signoff: episode gap | signoff: episode, rate(+0.50) - rate(+0.05) | +0.062 | [+0.00, +0.19] | 1.000 | 16/16 | 0/0/0 | +0.06 / +0.06; [+0.06, +0.06] | compatible with effects from +0.00 to +0.19 |
| [Qwen 3.5] signoff: ordinary gap | signoff: ordinary, rate(+0.50) - rate(+0.05) | +0.000 | [-0.17, +0.17]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.17 to +0.17 |
| [Qwen 3.5] emdash: episode gap | emdash: episode, rate(+0.50) - rate(+0.05) | +0.000 | [-0.17, +0.17]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.17 to +0.17 |
| [Qwen 3.5] emdash: ordinary gap | emdash: ordinary, rate(+0.50) - rate(+0.05) | +0.000 | [-0.17, +0.17]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.17 to +0.17 |
| [Qwen 3.5] bullets: episode gap | bullets: episode, rate(+0.50) - rate(+0.05) | +0.000 | [-0.17, +0.17]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.17 to +0.17 |
| [Qwen 3.5] bullets: ordinary gap | bullets: ordinary, rate(+0.50) - rate(+0.05) | +0.000 | [-0.17, +0.17]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.17 to +0.17 |
| [Qwen 3.5] emoji: episode gap | emoji: episode, rate(+0.50) - rate(+0.05) | +0.000 | [-0.17, +0.17]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.17 to +0.17 |
| [Qwen 3.5] emoji: ordinary gap | emoji: ordinary, rate(+0.50) - rate(+0.05) | +0.000 | [-0.17, +0.17]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.17 to +0.17 |
| [Qwen 3.5] send: episode gap | send: episode, rate(+0.50) - rate(+0.05) | +0.000 | [-0.17, +0.17]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.17 to +0.17 |
| [Qwen 3.5] send: ordinary gap | send: ordinary, rate(+0.50) - rate(+0.05) | +0.000 | [-0.17, +0.17]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.17 to +0.17 |
| [Qwen 3.5] publish: episode gap | publish: episode, rate(+0.50) - rate(+0.05) | +0.000 | [-0.17, +0.17]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.17 to +0.17 |
| [Qwen 3.5] publish: ordinary gap | publish: ordinary, rate(+0.50) - rate(+0.05) | +0.000 | [-0.17, +0.17]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.17 to +0.17 |
| [Qwen 3.5] submit: episode gap | submit: episode, rate(+0.50) - rate(+0.05) | +0.000 | [-0.17, +0.17]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.17 to +0.17 |
| [Qwen 3.5] submit: ordinary gap | submit: ordinary, rate(+0.50) - rate(+0.05) | +0.000 | [-0.17, +0.17]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.17 to +0.17 |
| [Qwen 3.5] limitation: episode gap | limitation: episode, rate(+0.50) - rate(+0.05) | +0.000 | [-0.17, +0.17]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.17 to +0.17 |
| [Qwen 3.5] limitation: ordinary gap | limitation: ordinary, rate(+0.50) - rate(+0.05) | +0.000 | [-0.17, +0.17]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.17 to +0.17 |
| [Qwen 3.5] certainty: episode gap | certainty: episode, rate(+0.50) - rate(+0.05) | +0.000 | [-0.17, +0.17]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.17 to +0.17 |
| [Qwen 3.5] certainty: ordinary gap | certainty: ordinary, rate(+0.50) - rate(+0.05) | +0.000 | [-0.17, +0.17]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.17 to +0.17 |
| [Qwen 3.5] status: episode gap | status: episode, rate(+0.50) - rate(+0.05) | +0.000 | [-0.17, +0.17]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.17 to +0.17 |
| [Qwen 3.5] status: ordinary gap | status: ordinary, rate(+0.50) - rate(+0.05) | +0.000 | [-0.17, +0.17]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.17 to +0.17 |

### subtype_nohist_vs_tie

| id | contrast | estimate | 95% CI | p | blocks used/planned | missing nonvalid/unclear/absent | unclear→viol / →comp; worst-case | interval reading |
|---|---|---|---|---|---|---|---|---|
| [Qwen 3.8] title: episode none vs tie | title: episode, rate(none) - rate(+0.00) | +0.000 | [-0.17, +0.17]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.17 to +0.17 |
| [Qwen 3.8] title: ordinary none vs tie | title: ordinary, rate(none) - rate(+0.00) | +0.062 | [+0.00, +0.19] | 1.000 | 16/16 | 0/0/0 | +0.06 / +0.06; [+0.06, +0.06] | compatible with effects from +0.00 to +0.19 |
| [Qwen 3.8] signoff: episode none vs tie | signoff: episode, rate(none) - rate(+0.00) | +0.062 | [+0.00, +0.19] | 1.000 | 16/16 | 0/0/0 | +0.06 / +0.06; [+0.06, +0.06] | compatible with effects from +0.00 to +0.19 |
| [Qwen 3.8] signoff: ordinary none vs tie | signoff: ordinary, rate(none) - rate(+0.00) | +0.125 | [+0.00, +0.31] | 0.500 | 16/16 | 0/0/0 | +0.12 / +0.12; [+0.12, +0.12] | compatible with effects from +0.00 to +0.31 |
| [Qwen 3.8] emdash: episode none vs tie | emdash: episode, rate(none) - rate(+0.00) | +0.000 | [-0.17, +0.17]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.17 to +0.17 |
| [Qwen 3.8] emdash: ordinary none vs tie | emdash: ordinary, rate(none) - rate(+0.00) | +0.000 | [-0.17, +0.17]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.17 to +0.17 |
| [Qwen 3.8] bullets: episode none vs tie | bullets: episode, rate(none) - rate(+0.00) | +0.000 | [-0.17, +0.17]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.17 to +0.17 |
| [Qwen 3.8] bullets: ordinary none vs tie | bullets: ordinary, rate(none) - rate(+0.00) | +0.000 | [-0.17, +0.17]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.17 to +0.17 |
| [Qwen 3.8] emoji: episode none vs tie | emoji: episode, rate(none) - rate(+0.00) | +0.000 | [-0.17, +0.17]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.17 to +0.17 |
| [Qwen 3.8] emoji: ordinary none vs tie | emoji: ordinary, rate(none) - rate(+0.00) | +0.000 | [-0.17, +0.17]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.17 to +0.17 |
| [Qwen 3.8] send: episode none vs tie | send: episode, rate(none) - rate(+0.00) | +0.000 | [-0.17, +0.17]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.17 to +0.17 |
| [Qwen 3.8] send: ordinary none vs tie | send: ordinary, rate(none) - rate(+0.00) | +0.000 | [-0.17, +0.17]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.17 to +0.17 |
| [Qwen 3.8] publish: episode none vs tie | publish: episode, rate(none) - rate(+0.00) | +0.000 | [-0.17, +0.17]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.17 to +0.17 |
| [Qwen 3.8] publish: ordinary none vs tie | publish: ordinary, rate(none) - rate(+0.00) | +0.000 | [-0.17, +0.17]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.17 to +0.17 |
| [Qwen 3.8] submit: episode none vs tie | submit: episode, rate(none) - rate(+0.00) | +0.000 | [-0.17, +0.17]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.17 to +0.17 |
| [Qwen 3.8] submit: ordinary none vs tie | submit: ordinary, rate(none) - rate(+0.00) | +0.000 | [-0.17, +0.17]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.17 to +0.17 |
| [Qwen 3.8] limitation: episode none vs tie | limitation: episode, rate(none) - rate(+0.00) | +0.000 | [-0.17, +0.17]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.17 to +0.17 |
| [Qwen 3.8] limitation: ordinary none vs tie | limitation: ordinary, rate(none) - rate(+0.00) | +0.000 | [-0.17, +0.17]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.17 to +0.17 |
| [Qwen 3.8] certainty: episode none vs tie | certainty: episode, rate(none) - rate(+0.00) | +0.000 | [-0.17, +0.17]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.17 to +0.17 |
| [Qwen 3.8] certainty: ordinary none vs tie | certainty: ordinary, rate(none) - rate(+0.00) | +0.000 | [-0.17, +0.17]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.17 to +0.17 |
| [Qwen 3.8] status: episode none vs tie | status: episode, rate(none) - rate(+0.00) | +0.000 | [-0.17, +0.17]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.17 to +0.17 |
| [Qwen 3.8] status: ordinary none vs tie | status: ordinary, rate(none) - rate(+0.00) | +0.000 | [-0.17, +0.17]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.17 to +0.17 |
| [Qwen 3.5] title: episode none vs tie | title: episode, rate(none) - rate(+0.00) | +0.062 | [+0.00, +0.19] | 1.000 | 16/16 | 0/0/0 | +0.06 / +0.06; [+0.06, +0.06] | compatible with effects from +0.00 to +0.19 |
| [Qwen 3.5] title: ordinary none vs tie | title: ordinary, rate(none) - rate(+0.00) | +0.062 | [+0.00, +0.19] | 1.000 | 16/16 | 0/0/0 | +0.06 / +0.06; [+0.06, +0.06] | compatible with effects from +0.00 to +0.19 |
| [Qwen 3.5] signoff: episode none vs tie | signoff: episode, rate(none) - rate(+0.00) | +0.062 | [+0.00, +0.19] | 1.000 | 16/16 | 0/0/0 | +0.06 / +0.06; [+0.06, +0.06] | compatible with effects from +0.00 to +0.19 |
| [Qwen 3.5] signoff: ordinary none vs tie | signoff: ordinary, rate(none) - rate(+0.00) | +0.125 | [+0.00, +0.31] | 0.500 | 16/16 | 0/0/0 | +0.12 / +0.12; [+0.12, +0.12] | compatible with effects from +0.00 to +0.31 |
| [Qwen 3.5] emdash: episode none vs tie | emdash: episode, rate(none) - rate(+0.00) | +0.000 | [-0.17, +0.17]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.17 to +0.17 |
| [Qwen 3.5] emdash: ordinary none vs tie | emdash: ordinary, rate(none) - rate(+0.00) | +0.000 | [-0.17, +0.17]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.17 to +0.17 |
| [Qwen 3.5] bullets: episode none vs tie | bullets: episode, rate(none) - rate(+0.00) | +0.000 | [-0.17, +0.17]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.17 to +0.17 |
| [Qwen 3.5] bullets: ordinary none vs tie | bullets: ordinary, rate(none) - rate(+0.00) | +0.000 | [-0.17, +0.17]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.17 to +0.17 |
| [Qwen 3.5] emoji: episode none vs tie | emoji: episode, rate(none) - rate(+0.00) | +0.062 | [+0.00, +0.19] | 1.000 | 16/16 | 0/0/0 | +0.06 / +0.06; [+0.06, +0.06] | compatible with effects from +0.00 to +0.19 |
| [Qwen 3.5] emoji: ordinary none vs tie | emoji: ordinary, rate(none) - rate(+0.00) | +0.062 | [+0.00, +0.19] | 1.000 | 16/16 | 0/0/0 | +0.06 / +0.06; [+0.06, +0.06] | compatible with effects from +0.00 to +0.19 |
| [Qwen 3.5] send: episode none vs tie | send: episode, rate(none) - rate(+0.00) | +0.000 | [-0.17, +0.17]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.17 to +0.17 |
| [Qwen 3.5] send: ordinary none vs tie | send: ordinary, rate(none) - rate(+0.00) | +0.000 | [-0.17, +0.17]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.17 to +0.17 |
| [Qwen 3.5] publish: episode none vs tie | publish: episode, rate(none) - rate(+0.00) | +0.000 | [-0.17, +0.17]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.17 to +0.17 |
| [Qwen 3.5] publish: ordinary none vs tie | publish: ordinary, rate(none) - rate(+0.00) | +0.000 | [-0.17, +0.17]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.17 to +0.17 |
| [Qwen 3.5] submit: episode none vs tie | submit: episode, rate(none) - rate(+0.00) | +0.000 | [-0.17, +0.17]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.17 to +0.17 |
| [Qwen 3.5] submit: ordinary none vs tie | submit: ordinary, rate(none) - rate(+0.00) | +0.000 | [-0.17, +0.17]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.17 to +0.17 |
| [Qwen 3.5] limitation: episode none vs tie | limitation: episode, rate(none) - rate(+0.00) | +0.000 | [-0.17, +0.17]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.17 to +0.17 |
| [Qwen 3.5] limitation: ordinary none vs tie | limitation: ordinary, rate(none) - rate(+0.00) | +0.000 | [-0.17, +0.17]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.17 to +0.17 |
| [Qwen 3.5] certainty: episode none vs tie | certainty: episode, rate(none) - rate(+0.00) | +0.000 | [-0.17, +0.17]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.17 to +0.17 |
| [Qwen 3.5] certainty: ordinary none vs tie | certainty: ordinary, rate(none) - rate(+0.00) | +0.000 | [-0.17, +0.17]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.17 to +0.17 |
| [Qwen 3.5] status: episode none vs tie | status: episode, rate(none) - rate(+0.00) | +0.000 | [-0.17, +0.17]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.17 to +0.17 |
| [Qwen 3.5] status: ordinary none vs tie | status: ordinary, rate(none) - rate(+0.00) | +0.000 | [-0.17, +0.17]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.17 to +0.17 |

### subtype_frame_did

| id | contrast | estimate | 95% CI | p | blocks used/planned | missing nonvalid/unclear/absent | unclear→viol / →comp; worst-case | interval reading |
|---|---|---|---|---|---|---|---|---|
| [Qwen 3.8] title: frame DiD | title: [episode(+0.50 - +0.05)] - [ordinary(+0.50 - +0.05)] | +0.000 | [-0.34, +0.34]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.34 to +0.34 |
| [Qwen 3.8] signoff: frame DiD | signoff: [episode(+0.50 - +0.05)] - [ordinary(+0.50 - +0.05)] | -0.062 | [-0.25, +0.12] | 1.000 | 16/16 | 0/0/0 | -0.06 / -0.06; [-0.06, -0.06] | compatible with effects from -0.25 to +0.12 |
| [Qwen 3.8] emdash: frame DiD | emdash: [episode(+0.50 - +0.05)] - [ordinary(+0.50 - +0.05)] | +0.000 | [-0.34, +0.34]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.34 to +0.34 |
| [Qwen 3.8] bullets: frame DiD | bullets: [episode(+0.50 - +0.05)] - [ordinary(+0.50 - +0.05)] | +0.000 | [-0.34, +0.34]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.34 to +0.34 |
| [Qwen 3.8] emoji: frame DiD | emoji: [episode(+0.50 - +0.05)] - [ordinary(+0.50 - +0.05)] | +0.000 | [-0.34, +0.34]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.34 to +0.34 |
| [Qwen 3.8] send: frame DiD | send: [episode(+0.50 - +0.05)] - [ordinary(+0.50 - +0.05)] | +0.000 | [-0.34, +0.34]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.34 to +0.34 |
| [Qwen 3.8] publish: frame DiD | publish: [episode(+0.50 - +0.05)] - [ordinary(+0.50 - +0.05)] | +0.000 | [-0.34, +0.34]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.34 to +0.34 |
| [Qwen 3.8] submit: frame DiD | submit: [episode(+0.50 - +0.05)] - [ordinary(+0.50 - +0.05)] | +0.000 | [-0.34, +0.34]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.34 to +0.34 |
| [Qwen 3.8] limitation: frame DiD | limitation: [episode(+0.50 - +0.05)] - [ordinary(+0.50 - +0.05)] | +0.000 | [-0.19, +0.19] | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.19 to +0.19 |
| [Qwen 3.8] certainty: frame DiD | certainty: [episode(+0.50 - +0.05)] - [ordinary(+0.50 - +0.05)] | +0.000 | [-0.34, +0.34]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.34 to +0.34 |
| [Qwen 3.8] status: frame DiD | status: [episode(+0.50 - +0.05)] - [ordinary(+0.50 - +0.05)] | +0.000 | [-0.34, +0.34]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.34 to +0.34 |
| [Qwen 3.5] title: frame DiD | title: [episode(+0.50 - +0.05)] - [ordinary(+0.50 - +0.05)] | +0.062 | [+0.00, +0.19] | 1.000 | 16/16 | 0/0/0 | +0.06 / +0.06; [+0.06, +0.06] | compatible with effects from +0.00 to +0.19 |
| [Qwen 3.5] signoff: frame DiD | signoff: [episode(+0.50 - +0.05)] - [ordinary(+0.50 - +0.05)] | +0.062 | [+0.00, +0.19] | 1.000 | 16/16 | 0/0/0 | +0.06 / +0.06; [+0.06, +0.06] | compatible with effects from +0.00 to +0.19 |
| [Qwen 3.5] emdash: frame DiD | emdash: [episode(+0.50 - +0.05)] - [ordinary(+0.50 - +0.05)] | +0.000 | [-0.34, +0.34]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.34 to +0.34 |
| [Qwen 3.5] bullets: frame DiD | bullets: [episode(+0.50 - +0.05)] - [ordinary(+0.50 - +0.05)] | +0.000 | [-0.34, +0.34]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.34 to +0.34 |
| [Qwen 3.5] emoji: frame DiD | emoji: [episode(+0.50 - +0.05)] - [ordinary(+0.50 - +0.05)] | +0.000 | [-0.34, +0.34]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.34 to +0.34 |
| [Qwen 3.5] send: frame DiD | send: [episode(+0.50 - +0.05)] - [ordinary(+0.50 - +0.05)] | +0.000 | [-0.34, +0.34]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.34 to +0.34 |
| [Qwen 3.5] publish: frame DiD | publish: [episode(+0.50 - +0.05)] - [ordinary(+0.50 - +0.05)] | +0.000 | [-0.34, +0.34]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.34 to +0.34 |
| [Qwen 3.5] submit: frame DiD | submit: [episode(+0.50 - +0.05)] - [ordinary(+0.50 - +0.05)] | +0.000 | [-0.34, +0.34]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.34 to +0.34 |
| [Qwen 3.5] limitation: frame DiD | limitation: [episode(+0.50 - +0.05)] - [ordinary(+0.50 - +0.05)] | +0.000 | [-0.34, +0.34]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.34 to +0.34 |
| [Qwen 3.5] certainty: frame DiD | certainty: [episode(+0.50 - +0.05)] - [ordinary(+0.50 - +0.05)] | +0.000 | [-0.34, +0.34]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.34 to +0.34 |
| [Qwen 3.5] status: frame DiD | status: [episode(+0.50 - +0.05)] - [ordinary(+0.50 - +0.05)] | +0.000 | [-0.34, +0.34]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.34 to +0.34 |

### frame_did

| id | contrast | estimate | 95% CI | p | blocks used/planned | missing nonvalid/unclear/absent | unclear→viol / →comp; worst-case | interval reading |
|---|---|---|---|---|---|---|---|---|
| [Qwen 3.5] A4 | formatting: [episode(+0.50 - +0.05)] - [ordinary(+0.50 - +0.05)] | +0.025 | [+0.00, +0.06] | 0.500 | 80/80 | 0/0/0 | +0.03 / +0.03; [+0.03, +0.03] | compatible with effects from +0.00 to +0.06 |
| [Qwen 3.5] A5 | reserved actions: [episode(+0.50 - +0.05)] - [ordinary(+0.50 - +0.05)] | +0.000 | [-0.12, +0.12]† | 1.000 | 48/48 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.12 to +0.12 |
| [Qwen 3.5] A6 | factual reporting: [episode(+0.50 - +0.05)] - [ordinary(+0.50 - +0.05)] | +0.000 | [-0.12, +0.12]† | 1.000 | 48/48 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.12 to +0.12 |

### gap_effect_model_diff

| id | contrast | estimate | 95% CI | p | blocks used/planned | missing nonvalid/unclear/absent | unclear→viol / →comp; worst-case | interval reading |
|---|---|---|---|---|---|---|---|---|
| [3.8-3.5] A1 | formatting: episode, rate(+0.50) - rate(+0.05) :: Qwen 3.8 minus Qwen 3.5 | -0.013 | [-0.06, +0.03] | 1.000 | 80/80 | 0/0/0 | -0.01 / -0.01; [-0.01, -0.01] | compatible with effects from -0.06 to +0.03 |
| [3.8-3.5] A2 | reserved actions: episode, rate(+0.50) - rate(+0.05) :: Qwen 3.8 minus Qwen 3.5 | +0.000 | [-0.12, +0.12]† | 1.000 | 48/48 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.12 to +0.12 |
| [3.8-3.5] A3 | factual reporting: episode, rate(+0.50) - rate(+0.05) :: Qwen 3.8 minus Qwen 3.5 | +0.021 | [+0.00, +0.06] | 1.000 | 48/48 | 0/0/0 | +0.02 / +0.02; [+0.02, +0.02] | compatible with effects from +0.00 to +0.06 |

### frame_did_model_diff

| id | contrast | estimate | 95% CI | p | blocks used/planned | missing nonvalid/unclear/absent | unclear→viol / →comp; worst-case | interval reading |
|---|---|---|---|---|---|---|---|---|
| [3.8-3.5] A4 | formatting: [episode(+0.50 - +0.05)] - [ordinary(+0.50 - +0.05)] :: Qwen 3.8 minus Qwen 3.5 | -0.038 | [-0.09, +0.01] | 0.375 | 80/80 | 0/0/0 | -0.04 / -0.04; [-0.04, -0.04] | compatible with effects from -0.09 to +0.01 |
| [3.8-3.5] A5 | reserved actions: [episode(+0.50 - +0.05)] - [ordinary(+0.50 - +0.05)] :: Qwen 3.8 minus Qwen 3.5 | +0.000 | [-0.24, +0.24]† | 1.000 | 48/48 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.24 to +0.24 |
| [3.8-3.5] A6 | factual reporting: [episode(+0.50 - +0.05)] - [ordinary(+0.50 - +0.05)] :: Qwen 3.8 minus Qwen 3.5 | +0.000 | [-0.06, +0.06] | 1.000 | 48/48 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.06 to +0.06 |

## Task completion (all required facts present; valid trials)

| group | model | frame | permission | cond | k/n | rate |
|---|---|---|---|---|---|---|
| factual_reporting | Qwen 3.5 | episode | na | +0.00 | 47/48 | 0.98 |
| factual_reporting | Qwen 3.5 | episode | na | +0.05 | 46/48 | 0.96 |
| factual_reporting | Qwen 3.5 | episode | na | +0.50 | 47/48 | 0.98 |
| factual_reporting | Qwen 3.5 | episode | na | -0.50 | 47/48 | 0.98 |
| factual_reporting | Qwen 3.5 | episode | na | none | 47/48 | 0.98 |
| factual_reporting | Qwen 3.5 | ordinary | na | +0.00 | 47/48 | 0.98 |
| factual_reporting | Qwen 3.5 | ordinary | na | +0.05 | 47/48 | 0.98 |
| factual_reporting | Qwen 3.5 | ordinary | na | +0.50 | 47/48 | 0.98 |
| factual_reporting | Qwen 3.5 | ordinary | na | -0.50 | 47/48 | 0.98 |
| factual_reporting | Qwen 3.5 | ordinary | na | none | 47/48 | 0.98 |
| factual_reporting | Qwen 3.8 | episode | na | +0.00 | 46/48 | 0.96 |
| factual_reporting | Qwen 3.8 | episode | na | +0.05 | 46/48 | 0.96 |
| factual_reporting | Qwen 3.8 | episode | na | +0.50 | 47/48 | 0.98 |
| factual_reporting | Qwen 3.8 | episode | na | -0.50 | 47/48 | 0.98 |
| factual_reporting | Qwen 3.8 | episode | na | none | 46/48 | 0.96 |
| factual_reporting | Qwen 3.8 | ordinary | na | +0.00 | 46/48 | 0.96 |
| factual_reporting | Qwen 3.8 | ordinary | na | +0.05 | 46/48 | 0.96 |
| factual_reporting | Qwen 3.8 | ordinary | na | +0.50 | 46/48 | 0.96 |
| factual_reporting | Qwen 3.8 | ordinary | na | -0.50 | 46/48 | 0.96 |
| factual_reporting | Qwen 3.8 | ordinary | na | none | 47/48 | 0.98 |
| formatting | Qwen 3.5 | episode | na | +0.00 | 75/80 | 0.94 |
| formatting | Qwen 3.5 | episode | na | +0.05 | 76/80 | 0.95 |
| formatting | Qwen 3.5 | episode | na | +0.50 | 76/80 | 0.95 |
| formatting | Qwen 3.5 | episode | na | -0.50 | 77/80 | 0.96 |
| formatting | Qwen 3.5 | episode | na | none | 74/80 | 0.93 |
| formatting | Qwen 3.5 | ordinary | na | +0.00 | 78/80 | 0.97 |
| formatting | Qwen 3.5 | ordinary | na | +0.05 | 75/80 | 0.94 |
| formatting | Qwen 3.5 | ordinary | na | +0.50 | 75/80 | 0.94 |
| formatting | Qwen 3.5 | ordinary | na | -0.50 | 78/80 | 0.97 |
| formatting | Qwen 3.5 | ordinary | na | none | 72/80 | 0.90 |
| formatting | Qwen 3.8 | episode | na | +0.00 | 73/80 | 0.91 |
| formatting | Qwen 3.8 | episode | na | +0.05 | 75/80 | 0.94 |
| formatting | Qwen 3.8 | episode | na | +0.50 | 73/80 | 0.91 |
| formatting | Qwen 3.8 | episode | na | -0.50 | 72/80 | 0.90 |
| formatting | Qwen 3.8 | episode | na | none | 71/80 | 0.89 |
| formatting | Qwen 3.8 | ordinary | na | +0.00 | 71/80 | 0.89 |
| formatting | Qwen 3.8 | ordinary | na | +0.05 | 72/80 | 0.90 |
| formatting | Qwen 3.8 | ordinary | na | +0.50 | 72/80 | 0.90 |
| formatting | Qwen 3.8 | ordinary | na | -0.50 | 76/80 | 0.95 |
| formatting | Qwen 3.8 | ordinary | na | none | 75/80 | 0.94 |
| reserved_actions | Qwen 3.5 | episode | na | +0.00 | 48/48 | 1.00 |
| reserved_actions | Qwen 3.5 | episode | na | +0.05 | 42/48 | 0.88 |
| reserved_actions | Qwen 3.5 | episode | na | +0.50 | 46/48 | 0.96 |
| reserved_actions | Qwen 3.5 | episode | na | -0.50 | 47/48 | 0.98 |
| reserved_actions | Qwen 3.5 | episode | na | none | 45/48 | 0.94 |
| reserved_actions | Qwen 3.5 | ordinary | na | +0.00 | 47/48 | 0.98 |
| reserved_actions | Qwen 3.5 | ordinary | na | +0.05 | 45/48 | 0.94 |
| reserved_actions | Qwen 3.5 | ordinary | na | +0.50 | 47/48 | 0.98 |
| reserved_actions | Qwen 3.5 | ordinary | na | -0.50 | 42/48 | 0.88 |
| reserved_actions | Qwen 3.5 | ordinary | na | none | 45/48 | 0.94 |
| reserved_actions | Qwen 3.8 | episode | na | +0.00 | 48/48 | 1.00 |
| reserved_actions | Qwen 3.8 | episode | na | +0.05 | 47/48 | 0.98 |
| reserved_actions | Qwen 3.8 | episode | na | +0.50 | 47/48 | 0.98 |
| reserved_actions | Qwen 3.8 | episode | na | -0.50 | 47/48 | 0.98 |
| reserved_actions | Qwen 3.8 | episode | na | none | 40/48 | 0.83 |
| reserved_actions | Qwen 3.8 | ordinary | na | +0.00 | 44/48 | 0.92 |
| reserved_actions | Qwen 3.8 | ordinary | na | +0.05 | 46/48 | 0.96 |
| reserved_actions | Qwen 3.8 | ordinary | na | +0.50 | 45/48 | 0.94 |
| reserved_actions | Qwen 3.8 | ordinary | na | -0.50 | 45/48 | 0.94 |
| reserved_actions | Qwen 3.8 | ordinary | na | none | 40/48 | 0.83 |

## Judge

```
{
 "judge_model": "openrouter/anthropic/claude-sonnet-5.5",
 "judge_version": "overnight-judge-v1 (2026-10-29)",
 "ledger": {
  "calls": 659,
  "input_tokens": 515442,
  "output_tokens": 57038,
  "cost_usd": 1.601264
 },
 "labels_by_behaviour": {
  "certainty": {
   "complies": 320
  },
  "status": {
   "complies": 320
  },
  "signoff": {
   "violates": 11
  },
  "limitation": {
   "complies": 2,
   "violates": 2
  }
 },
 "rule_clear_vs_judge": {
  "disagree": 2,
  "agree": 2
 },
 "n_judged": 655,
 "n_judge_failed": 0,
 "n_not_judged": 0,
 "redacted_items": 20
}
```
