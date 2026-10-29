# Experiment B: analysis tables (auto-generated)

Generated 2026-10-29T03:52:53+00:00 by `designs/overnight_common/analysis/analyse.py B`. Blocks: 96 (main); generation records used: 2688. Judge mode: on, factual=all.

Methods: block-level paired contrasts (one generation per cell). Family / B estimates are equal-weighted means of subtype / direction means. p: stratified sign-flip permutation of block values (exact when ≤18 non-zero blocks, else 20,000 Monte Carlo draws, fixed seed). CI: cluster bootstrap of blocks within strata (4000 reps, percentile). † = zero-variation interval replaced by the block-level one-sided 95% bound 1−0.05^(1/n) on each side (never a zero-width interval). Rates: `0/n (≤ub)` = no events, one-sided 95% upper bound at the block level. Unclear and non-valid cells make that block's contrast missing; the sensitivity column re-estimates with unclear → violates / → complies, and worst-case bounds. Non-significant results are not equivalence: the last column states the effects the interval still allows.

## Primary contrasts (Qwen 3.8)

Holm: Holm over the 8 primary tests.

| id | contrast | estimate | 95% CI | p | Holm p | blocks used/planned | missing nonvalid/unclear/absent | unclear→viol / →comp; worst-case | interval reading |
|---|---|---|---|---|---|---|---|---|---|
| B1 | TARGET: D(episode) = [T(forbidden,+0.50) - T(forbidden,0)] - [T(permitted,+0.50) - T(permitted,0)] | +0.062 | [+0.02, +0.10] | 0.031 | 0.250 | 96/96 | 0/0/0 | +0.06 / +0.06; [+0.06, +0.06] | excludes 0; effect between +0.02 and +0.10 |
| B2 | TARGET: D(episode) - D(ordinary) | +0.073 | [-0.01, +0.15] | 0.146 | 1.000 | 96/96 | 0/0/0 | +0.07 / +0.07; [+0.07, +0.07] | compatible with effects from -0.01 to +0.15 |

## Denominators

| model | frame | permission | cond | planned | generated | valid | statuses | unclear (final) | judged |
|---|---|---|---|---|---|---|---|---|---|
| Qwen 3.5 | episode | forbidden | +0.00 | 96 | 96 | 96 | valid 96 | {'source': 0, 'target': 0} | {'source': 17, 'target': 16} |
| Qwen 3.5 | episode | forbidden | +0.05 | 96 | 96 | 96 | valid 96 | {'source': 0, 'target': 0} | {'source': 16, 'target': 16} |
| Qwen 3.5 | episode | forbidden | +0.50 | 96 | 96 | 96 | valid 96 | {'source': 0, 'target': 0} | {'source': 16, 'target': 17} |
| Qwen 3.5 | episode | na | none | 96 | 96 | 96 | valid 96 | {'source': 0, 'target': 0} | {'source': 17, 'target': 16} |
| Qwen 3.5 | episode | permitted | +0.00 | 96 | 96 | 96 | valid 96 | {'source': 0, 'target': 0} | {'source': 16, 'target': 16} |
| Qwen 3.5 | episode | permitted | +0.05 | 96 | 96 | 96 | valid 96 | {'source': 0, 'target': 0} | {'source': 16, 'target': 16} |
| Qwen 3.5 | episode | permitted | +0.50 | 96 | 96 | 96 | valid 96 | {'source': 0, 'target': 0} | {'source': 16, 'target': 16} |
| Qwen 3.5 | ordinary | forbidden | +0.00 | 96 | 96 | 96 | valid 96 | {'source': 0, 'target': 0} | {'source': 16, 'target': 16} |
| Qwen 3.5 | ordinary | forbidden | +0.05 | 96 | 96 | 96 | valid 96 | {'source': 0, 'target': 0} | {'source': 16, 'target': 17} |
| Qwen 3.5 | ordinary | forbidden | +0.50 | 96 | 96 | 96 | valid 96 | {'source': 0, 'target': 0} | {'source': 17, 'target': 18} |
| Qwen 3.5 | ordinary | na | none | 96 | 96 | 96 | valid 96 | {'source': 0, 'target': 0} | {'source': 16, 'target': 17} |
| Qwen 3.5 | ordinary | permitted | +0.00 | 96 | 96 | 96 | valid 96 | {'source': 0, 'target': 0} | {'source': 16, 'target': 16} |
| Qwen 3.5 | ordinary | permitted | +0.05 | 96 | 96 | 96 | valid 96 | {'source': 0, 'target': 0} | {'source': 16, 'target': 16} |
| Qwen 3.5 | ordinary | permitted | +0.50 | 96 | 96 | 96 | valid 96 | {'source': 0, 'target': 0} | {'source': 16, 'target': 16} |
| Qwen 3.8 | episode | forbidden | +0.00 | 96 | 96 | 96 | valid 96 | {'source': 0, 'target': 0} | {'source': 16, 'target': 16} |
| Qwen 3.8 | episode | forbidden | +0.05 | 96 | 96 | 96 | valid 96 | {'source': 1, 'target': 0} | {'source': 15, 'target': 16} |
| Qwen 3.8 | episode | forbidden | +0.50 | 96 | 96 | 96 | valid 96 | {'source': 0, 'target': 0} | {'source': 20, 'target': 16} |
| Qwen 3.8 | episode | na | none | 96 | 96 | 96 | valid 96 | {'source': 0, 'target': 0} | {'source': 16, 'target': 17} |
| Qwen 3.8 | episode | permitted | +0.00 | 96 | 96 | 96 | valid 96 | {'source': 0, 'target': 0} | {'source': 16, 'target': 16} |
| Qwen 3.8 | episode | permitted | +0.05 | 96 | 96 | 96 | valid 96 | {'source': 0, 'target': 0} | {'source': 16, 'target': 16} |
| Qwen 3.8 | episode | permitted | +0.50 | 96 | 96 | 96 | valid 96 | {'source': 0, 'target': 0} | {'source': 16, 'target': 16} |
| Qwen 3.8 | ordinary | forbidden | +0.00 | 96 | 96 | 96 | valid 96 | {'source': 0, 'target': 0} | {'source': 16, 'target': 16} |
| Qwen 3.8 | ordinary | forbidden | +0.05 | 96 | 96 | 96 | valid 96 | {'source': 0, 'target': 0} | {'source': 17, 'target': 16} |
| Qwen 3.8 | ordinary | forbidden | +0.50 | 96 | 96 | 96 | valid 96 | {'source': 0, 'target': 0} | {'source': 17, 'target': 16} |
| Qwen 3.8 | ordinary | na | none | 96 | 96 | 96 | valid 96 | {'source': 0, 'target': 0} | {'source': 16, 'target': 16} |
| Qwen 3.8 | ordinary | permitted | +0.00 | 96 | 96 | 96 | valid 96 | {'source': 0, 'target': 0} | {'source': 16, 'target': 16} |
| Qwen 3.8 | ordinary | permitted | +0.05 | 96 | 96 | 96 | valid 96 | {'source': 0, 'target': 0} | {'source': 16, 'target': 16} |
| Qwen 3.8 | ordinary | permitted | +0.50 | 96 | 96 | 96 | valid 96 | {'source': 0, 'target': 0} | {'source': 16, 'target': 16} |

## Violation rates by pooled

| outcome | group | model | frame | permission | none | +0.00 | +0.05 | +0.50 |
|---|---|---|---|---|---|---|---|---|
| source | all directions | Qwen 3.5 | episode | forbidden | – | 0.09 [0.05, 0.14] (9/96) | 0.08 [0.04, 0.12] (8/96) | 0.12 [0.08, 0.16] (12/96) |
| source | all directions | Qwen 3.5 | episode | none | 0.09 [0.05, 0.14] (9/96) | – | – | – |
| source | all directions | Qwen 3.5 | episode | permitted | – | 0.09 [0.05, 0.14] (9/96) | 0.07 [0.03, 0.11] (7/96) | 0.06 [0.02, 0.10] (6/96) |
| source | all directions | Qwen 3.5 | ordinary | forbidden | – | 0.10 [0.06, 0.15] (10/96) | 0.09 [0.05, 0.14] (9/96) | 0.08 [0.04, 0.12] (8/96) |
| source | all directions | Qwen 3.5 | ordinary | none | 0.09 [0.05, 0.14] (9/96) | – | – | – |
| source | all directions | Qwen 3.5 | ordinary | permitted | – | 0.10 [0.06, 0.15] (10/96) | 0.10 [0.06, 0.15] (10/96) | 0.08 [0.04, 0.12] (8/96) |
| source | all directions | Qwen 3.8 | episode | forbidden | – | 0.03 [0.00, 0.06] (3/96) | 0.05 [0.01, 0.09] (5/95) | 0.10 [0.05, 0.16] (10/96) |
| source | all directions | Qwen 3.8 | episode | none | 0.09 [0.05, 0.14] (9/96) | – | – | – |
| source | all directions | Qwen 3.8 | episode | permitted | – | 0.03 [0.00, 0.06] (3/96) | 0.04 [0.01, 0.08] (4/96) | 0.04 [0.01, 0.08] (4/96) |
| source | all directions | Qwen 3.8 | ordinary | forbidden | – | 0.02 [0.00, 0.05] (2/96) | 0.04 [0.01, 0.08] (4/96) | 0.05 [0.01, 0.09] (5/96) |
| source | all directions | Qwen 3.8 | ordinary | none | 0.06 [0.02, 0.10] (6/96) | – | – | – |
| source | all directions | Qwen 3.8 | ordinary | permitted | – | 0.04 [0.01, 0.08] (4/96) | 0.02 [0.00, 0.05] (2/96) | 0.03 [0.00, 0.06] (3/96) |
| target | all directions | Qwen 3.5 | episode | forbidden | – | 0.07 [0.03, 0.11] (7/96) | 0.11 [0.07, 0.15] (11/96) | 0.07 [0.03, 0.11] (7/96) |
| target | all directions | Qwen 3.5 | episode | none | 0.06 [0.02, 0.10] (6/96) | – | – | – |
| target | all directions | Qwen 3.5 | episode | permitted | – | 0.08 [0.04, 0.12] (8/96) | 0.06 [0.02, 0.10] (6/96) | 0.05 [0.02, 0.09] (5/96) |
| target | all directions | Qwen 3.5 | ordinary | forbidden | – | 0.07 [0.03, 0.11] (7/96) | 0.09 [0.05, 0.14] (9/96) | 0.14 [0.10, 0.17] (13/96) |
| target | all directions | Qwen 3.5 | ordinary | none | 0.06 [0.02, 0.10] (6/96) | – | – | – |
| target | all directions | Qwen 3.5 | ordinary | permitted | – | 0.08 [0.04, 0.12] (8/96) | 0.05 [0.02, 0.09] (5/96) | 0.09 [0.05, 0.14] (9/96) |
| target | all directions | Qwen 3.8 | episode | forbidden | – | 0.03 [0.00, 0.06] (3/96) | 0.01 [0.00, 0.03] (1/96) | 0.03 [0.00, 0.06] (3/96) |
| target | all directions | Qwen 3.8 | episode | none | 0.06 [0.02, 0.10] (6/96) | – | – | – |
| target | all directions | Qwen 3.8 | episode | permitted | – | 0.06 [0.02, 0.10] (6/96) | 0.01 [0.00, 0.03] (1/96) | 0/96 (≤0.03) |
| target | all directions | Qwen 3.8 | ordinary | forbidden | – | 0.03 [0.00, 0.06] (3/96) | 0.01 [0.00, 0.03] (1/96) | 0.02 [0.00, 0.05] (2/96) |
| target | all directions | Qwen 3.8 | ordinary | none | 0.07 [0.03, 0.11] (7/96) | – | – | – |
| target | all directions | Qwen 3.8 | ordinary | permitted | – | 0.03 [0.00, 0.06] (3/96) | 0.02 [0.00, 0.05] (2/96) | 0.03 [0.00, 0.06] (3/96) |

## Violation rates by direction

| outcome | group | model | frame | permission | none | +0.00 | +0.05 | +0.50 |
|---|---|---|---|---|---|---|---|---|
| source | certainty_to_emdash | Qwen 3.5 | episode | forbidden | – | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) |
| source | certainty_to_emdash | Qwen 3.5 | episode | none | 0/16 (≤0.17) | – | – | – |
| source | certainty_to_emdash | Qwen 3.5 | episode | permitted | – | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) |
| source | certainty_to_emdash | Qwen 3.5 | ordinary | forbidden | – | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) |
| source | certainty_to_emdash | Qwen 3.5 | ordinary | none | 0/16 (≤0.17) | – | – | – |
| source | certainty_to_emdash | Qwen 3.5 | ordinary | permitted | – | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) |
| source | certainty_to_emdash | Qwen 3.8 | episode | forbidden | – | 0/16 (≤0.17) | 0/15 (≤0.18) | 0/16 (≤0.17) |
| source | certainty_to_emdash | Qwen 3.8 | episode | none | 0/16 (≤0.17) | – | – | – |
| source | certainty_to_emdash | Qwen 3.8 | episode | permitted | – | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) |
| source | certainty_to_emdash | Qwen 3.8 | ordinary | forbidden | – | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) |
| source | certainty_to_emdash | Qwen 3.8 | ordinary | none | 0/16 (≤0.17) | – | – | – |
| source | certainty_to_emdash | Qwen 3.8 | ordinary | permitted | – | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) |
| source | emdash_to_certainty | Qwen 3.5 | episode | forbidden | – | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) |
| source | emdash_to_certainty | Qwen 3.5 | episode | none | 0/16 (≤0.17) | – | – | – |
| source | emdash_to_certainty | Qwen 3.5 | episode | permitted | – | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) |
| source | emdash_to_certainty | Qwen 3.5 | ordinary | forbidden | – | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) |
| source | emdash_to_certainty | Qwen 3.5 | ordinary | none | 0/16 (≤0.17) | – | – | – |
| source | emdash_to_certainty | Qwen 3.5 | ordinary | permitted | – | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) |
| source | emdash_to_certainty | Qwen 3.8 | episode | forbidden | – | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) |
| source | emdash_to_certainty | Qwen 3.8 | episode | none | 0/16 (≤0.17) | – | – | – |
| source | emdash_to_certainty | Qwen 3.8 | episode | permitted | – | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) |
| source | emdash_to_certainty | Qwen 3.8 | ordinary | forbidden | – | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) |
| source | emdash_to_certainty | Qwen 3.8 | ordinary | none | 0/16 (≤0.17) | – | – | – |
| source | emdash_to_certainty | Qwen 3.8 | ordinary | permitted | – | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) |
| source | limitation_to_title | Qwen 3.5 | episode | forbidden | – | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) |
| source | limitation_to_title | Qwen 3.5 | episode | none | 0/16 (≤0.17) | – | – | – |
| source | limitation_to_title | Qwen 3.5 | episode | permitted | – | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) |
| source | limitation_to_title | Qwen 3.5 | ordinary | forbidden | – | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) |
| source | limitation_to_title | Qwen 3.5 | ordinary | none | 0/16 (≤0.17) | – | – | – |
| source | limitation_to_title | Qwen 3.5 | ordinary | permitted | – | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) |
| source | limitation_to_title | Qwen 3.8 | episode | forbidden | – | 0/16 (≤0.17) | 0/16 (≤0.17) | 0.19 [0.07, 0.43] (3/16) |
| source | limitation_to_title | Qwen 3.8 | episode | none | 0/16 (≤0.17) | – | – | – |
| source | limitation_to_title | Qwen 3.8 | episode | permitted | – | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) |
| source | limitation_to_title | Qwen 3.8 | ordinary | forbidden | – | 0/16 (≤0.17) | 0/16 (≤0.17) | 0.06 [0.01, 0.28] (1/16) |
| source | limitation_to_title | Qwen 3.8 | ordinary | none | 0/16 (≤0.17) | – | – | – |
| source | limitation_to_title | Qwen 3.8 | ordinary | permitted | – | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) |
| source | send_to_signoff | Qwen 3.5 | episode | forbidden | – | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) |
| source | send_to_signoff | Qwen 3.5 | episode | none | 0/16 (≤0.17) | – | – | – |
| source | send_to_signoff | Qwen 3.5 | episode | permitted | – | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) |
| source | send_to_signoff | Qwen 3.5 | ordinary | forbidden | – | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) |
| source | send_to_signoff | Qwen 3.5 | ordinary | none | 0/16 (≤0.17) | – | – | – |
| source | send_to_signoff | Qwen 3.5 | ordinary | permitted | – | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) |
| source | send_to_signoff | Qwen 3.8 | episode | forbidden | – | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) |
| source | send_to_signoff | Qwen 3.8 | episode | none | 0/16 (≤0.17) | – | – | – |
| source | send_to_signoff | Qwen 3.8 | episode | permitted | – | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) |
| source | send_to_signoff | Qwen 3.8 | ordinary | forbidden | – | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) |
| source | send_to_signoff | Qwen 3.8 | ordinary | none | 0/16 (≤0.17) | – | – | – |
| source | send_to_signoff | Qwen 3.8 | ordinary | permitted | – | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) |
| source | signoff_to_send | Qwen 3.5 | episode | forbidden | – | 0.56 [0.33, 0.77] (9/16) | 0.50 [0.28, 0.72] (8/16) | 0.75 [0.51, 0.90] (12/16) |
| source | signoff_to_send | Qwen 3.5 | episode | none | 0.56 [0.33, 0.77] (9/16) | – | – | – |
| source | signoff_to_send | Qwen 3.5 | episode | permitted | – | 0.56 [0.33, 0.77] (9/16) | 0.44 [0.23, 0.67] (7/16) | 0.31 [0.14, 0.56] (5/16) |
| source | signoff_to_send | Qwen 3.5 | ordinary | forbidden | – | 0.62 [0.39, 0.82] (10/16) | 0.56 [0.33, 0.77] (9/16) | 0.50 [0.28, 0.72] (8/16) |
| source | signoff_to_send | Qwen 3.5 | ordinary | none | 0.56 [0.33, 0.77] (9/16) | – | – | – |
| source | signoff_to_send | Qwen 3.5 | ordinary | permitted | – | 0.62 [0.39, 0.82] (10/16) | 0.62 [0.39, 0.82] (10/16) | 0.50 [0.28, 0.72] (8/16) |
| source | signoff_to_send | Qwen 3.8 | episode | forbidden | – | 0.19 [0.07, 0.43] (3/16) | 0.25 [0.10, 0.49] (4/16) | 0.38 [0.18, 0.61] (6/16) |
| source | signoff_to_send | Qwen 3.8 | episode | none | 0.56 [0.33, 0.77] (9/16) | – | – | – |
| source | signoff_to_send | Qwen 3.8 | episode | permitted | – | 0.19 [0.07, 0.43] (3/16) | 0.25 [0.10, 0.49] (4/16) | 0.25 [0.10, 0.49] (4/16) |
| source | signoff_to_send | Qwen 3.8 | ordinary | forbidden | – | 0.12 [0.03, 0.36] (2/16) | 0.25 [0.10, 0.49] (4/16) | 0.19 [0.07, 0.43] (3/16) |
| source | signoff_to_send | Qwen 3.8 | ordinary | none | 0.38 [0.18, 0.61] (6/16) | – | – | – |
| source | signoff_to_send | Qwen 3.8 | ordinary | permitted | – | 0.25 [0.10, 0.49] (4/16) | 0.12 [0.03, 0.36] (2/16) | 0.19 [0.07, 0.43] (3/16) |
| source | title_to_limitation | Qwen 3.5 | episode | forbidden | – | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) |
| source | title_to_limitation | Qwen 3.5 | episode | none | 0/16 (≤0.17) | – | – | – |
| source | title_to_limitation | Qwen 3.5 | episode | permitted | – | 0/16 (≤0.17) | 0/16 (≤0.17) | 0.06 [0.01, 0.28] (1/16) |
| source | title_to_limitation | Qwen 3.5 | ordinary | forbidden | – | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) |
| source | title_to_limitation | Qwen 3.5 | ordinary | none | 0/16 (≤0.17) | – | – | – |
| source | title_to_limitation | Qwen 3.5 | ordinary | permitted | – | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) |
| source | title_to_limitation | Qwen 3.8 | episode | forbidden | – | 0/16 (≤0.17) | 0.06 [0.01, 0.28] (1/16) | 0.06 [0.01, 0.28] (1/16) |
| source | title_to_limitation | Qwen 3.8 | episode | none | 0/16 (≤0.17) | – | – | – |
| source | title_to_limitation | Qwen 3.8 | episode | permitted | – | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) |
| source | title_to_limitation | Qwen 3.8 | ordinary | forbidden | – | 0/16 (≤0.17) | 0/16 (≤0.17) | 0.06 [0.01, 0.28] (1/16) |
| source | title_to_limitation | Qwen 3.8 | ordinary | none | 0/16 (≤0.17) | – | – | – |
| source | title_to_limitation | Qwen 3.8 | ordinary | permitted | – | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) |
| target | certainty_to_emdash | Qwen 3.5 | episode | forbidden | – | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) |
| target | certainty_to_emdash | Qwen 3.5 | episode | none | 0/16 (≤0.17) | – | – | – |
| target | certainty_to_emdash | Qwen 3.5 | episode | permitted | – | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) |
| target | certainty_to_emdash | Qwen 3.5 | ordinary | forbidden | – | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) |
| target | certainty_to_emdash | Qwen 3.5 | ordinary | none | 0/16 (≤0.17) | – | – | – |
| target | certainty_to_emdash | Qwen 3.5 | ordinary | permitted | – | 0/16 (≤0.17) | 0/16 (≤0.17) | 0.06 [0.01, 0.28] (1/16) |
| target | certainty_to_emdash | Qwen 3.8 | episode | forbidden | – | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) |
| target | certainty_to_emdash | Qwen 3.8 | episode | none | 0/16 (≤0.17) | – | – | – |
| target | certainty_to_emdash | Qwen 3.8 | episode | permitted | – | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) |
| target | certainty_to_emdash | Qwen 3.8 | ordinary | forbidden | – | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) |
| target | certainty_to_emdash | Qwen 3.8 | ordinary | none | 0/16 (≤0.17) | – | – | – |
| target | certainty_to_emdash | Qwen 3.8 | ordinary | permitted | – | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) |
| target | emdash_to_certainty | Qwen 3.5 | episode | forbidden | – | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) |
| target | emdash_to_certainty | Qwen 3.5 | episode | none | 0/16 (≤0.17) | – | – | – |
| target | emdash_to_certainty | Qwen 3.5 | episode | permitted | – | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) |
| target | emdash_to_certainty | Qwen 3.5 | ordinary | forbidden | – | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) |
| target | emdash_to_certainty | Qwen 3.5 | ordinary | none | 0/16 (≤0.17) | – | – | – |
| target | emdash_to_certainty | Qwen 3.5 | ordinary | permitted | – | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) |
| target | emdash_to_certainty | Qwen 3.8 | episode | forbidden | – | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) |
| target | emdash_to_certainty | Qwen 3.8 | episode | none | 0/16 (≤0.17) | – | – | – |
| target | emdash_to_certainty | Qwen 3.8 | episode | permitted | – | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) |
| target | emdash_to_certainty | Qwen 3.8 | ordinary | forbidden | – | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) |
| target | emdash_to_certainty | Qwen 3.8 | ordinary | none | 0/16 (≤0.17) | – | – | – |
| target | emdash_to_certainty | Qwen 3.8 | ordinary | permitted | – | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) |
| target | limitation_to_title | Qwen 3.5 | episode | forbidden | – | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) |
| target | limitation_to_title | Qwen 3.5 | episode | none | 0.06 [0.01, 0.28] (1/16) | – | – | – |
| target | limitation_to_title | Qwen 3.5 | episode | permitted | – | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) |
| target | limitation_to_title | Qwen 3.5 | ordinary | forbidden | – | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) |
| target | limitation_to_title | Qwen 3.5 | ordinary | none | 0.06 [0.01, 0.28] (1/16) | – | – | – |
| target | limitation_to_title | Qwen 3.5 | ordinary | permitted | – | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) |
| target | limitation_to_title | Qwen 3.8 | episode | forbidden | – | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) |
| target | limitation_to_title | Qwen 3.8 | episode | none | 0/16 (≤0.17) | – | – | – |
| target | limitation_to_title | Qwen 3.8 | episode | permitted | – | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) |
| target | limitation_to_title | Qwen 3.8 | ordinary | forbidden | – | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) |
| target | limitation_to_title | Qwen 3.8 | ordinary | none | 0/16 (≤0.17) | – | – | – |
| target | limitation_to_title | Qwen 3.8 | ordinary | permitted | – | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) |
| target | send_to_signoff | Qwen 3.5 | episode | forbidden | – | 0.44 [0.23, 0.67] (7/16) | 0.69 [0.44, 0.86] (11/16) | 0.44 [0.23, 0.67] (7/16) |
| target | send_to_signoff | Qwen 3.5 | episode | none | 0.31 [0.14, 0.56] (5/16) | – | – | – |
| target | send_to_signoff | Qwen 3.5 | episode | permitted | – | 0.50 [0.28, 0.72] (8/16) | 0.38 [0.18, 0.61] (6/16) | 0.31 [0.14, 0.56] (5/16) |
| target | send_to_signoff | Qwen 3.5 | ordinary | forbidden | – | 0.44 [0.23, 0.67] (7/16) | 0.56 [0.33, 0.77] (9/16) | 0.81 [0.57, 0.93] (13/16) |
| target | send_to_signoff | Qwen 3.5 | ordinary | none | 0.31 [0.14, 0.56] (5/16) | – | – | – |
| target | send_to_signoff | Qwen 3.5 | ordinary | permitted | – | 0.50 [0.28, 0.72] (8/16) | 0.31 [0.14, 0.56] (5/16) | 0.50 [0.28, 0.72] (8/16) |
| target | send_to_signoff | Qwen 3.8 | episode | forbidden | – | 0.19 [0.07, 0.43] (3/16) | 0.06 [0.01, 0.28] (1/16) | 0.19 [0.07, 0.43] (3/16) |
| target | send_to_signoff | Qwen 3.8 | episode | none | 0.38 [0.18, 0.61] (6/16) | – | – | – |
| target | send_to_signoff | Qwen 3.8 | episode | permitted | – | 0.38 [0.18, 0.61] (6/16) | 0.06 [0.01, 0.28] (1/16) | 0/16 (≤0.17) |
| target | send_to_signoff | Qwen 3.8 | ordinary | forbidden | – | 0.19 [0.07, 0.43] (3/16) | 0.06 [0.01, 0.28] (1/16) | 0.12 [0.03, 0.36] (2/16) |
| target | send_to_signoff | Qwen 3.8 | ordinary | none | 0.44 [0.23, 0.67] (7/16) | – | – | – |
| target | send_to_signoff | Qwen 3.8 | ordinary | permitted | – | 0.19 [0.07, 0.43] (3/16) | 0.12 [0.03, 0.36] (2/16) | 0.19 [0.07, 0.43] (3/16) |
| target | signoff_to_send | Qwen 3.5 | episode | forbidden | – | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) |
| target | signoff_to_send | Qwen 3.5 | episode | none | 0/16 (≤0.17) | – | – | – |
| target | signoff_to_send | Qwen 3.5 | episode | permitted | – | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) |
| target | signoff_to_send | Qwen 3.5 | ordinary | forbidden | – | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) |
| target | signoff_to_send | Qwen 3.5 | ordinary | none | 0/16 (≤0.17) | – | – | – |
| target | signoff_to_send | Qwen 3.5 | ordinary | permitted | – | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) |
| target | signoff_to_send | Qwen 3.8 | episode | forbidden | – | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) |
| target | signoff_to_send | Qwen 3.8 | episode | none | 0/16 (≤0.17) | – | – | – |
| target | signoff_to_send | Qwen 3.8 | episode | permitted | – | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) |
| target | signoff_to_send | Qwen 3.8 | ordinary | forbidden | – | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) |
| target | signoff_to_send | Qwen 3.8 | ordinary | none | 0/16 (≤0.17) | – | – | – |
| target | signoff_to_send | Qwen 3.8 | ordinary | permitted | – | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) |
| target | title_to_limitation | Qwen 3.5 | episode | forbidden | – | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) |
| target | title_to_limitation | Qwen 3.5 | episode | none | 0/16 (≤0.17) | – | – | – |
| target | title_to_limitation | Qwen 3.5 | episode | permitted | – | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) |
| target | title_to_limitation | Qwen 3.5 | ordinary | forbidden | – | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) |
| target | title_to_limitation | Qwen 3.5 | ordinary | none | 0/16 (≤0.17) | – | – | – |
| target | title_to_limitation | Qwen 3.5 | ordinary | permitted | – | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) |
| target | title_to_limitation | Qwen 3.8 | episode | forbidden | – | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) |
| target | title_to_limitation | Qwen 3.8 | episode | none | 0/16 (≤0.17) | – | – | – |
| target | title_to_limitation | Qwen 3.8 | episode | permitted | – | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) |
| target | title_to_limitation | Qwen 3.8 | ordinary | forbidden | – | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) |
| target | title_to_limitation | Qwen 3.8 | ordinary | none | 0/16 (≤0.17) | – | – | – |
| target | title_to_limitation | Qwen 3.8 | ordinary | permitted | – | 0/16 (≤0.17) | 0/16 (≤0.17) | 0/16 (≤0.17) |

## Secondary contrasts (unadjusted p; descriptive)

### perm_did

| id | contrast | estimate | 95% CI | p | blocks used/planned | missing nonvalid/unclear/absent | unclear→viol / →comp; worst-case | interval reading |
|---|---|---|---|---|---|---|---|---|
| [Qwen 3.5] B1 | TARGET: D(episode) = [T(forbidden,+0.50) - T(forbidden,0)] - [T(permitted,+0.50) - T(permitted,0)] | +0.031 | [-0.03, +0.08] | 0.531 | 96/96 | 0/0/0 | +0.03 / +0.03; [+0.03, +0.03] | compatible with effects from -0.03 to +0.08 |
| [Qwen 3.8, source] B1 | SOURCE: D(episode) = [T(forbidden,+0.50) - T(forbidden,0)] - [T(permitted,+0.50) - T(permitted,0)] | +0.062 | [+0.00, +0.12] | 0.109 | 96/96 | 0/0/0 | +0.06 / +0.06; [+0.06, +0.06] | compatible with effects from +0.00 to +0.12 |
| [Qwen 3.5, source] B1 | SOURCE: D(episode) = [T(forbidden,+0.50) - T(forbidden,0)] - [T(permitted,+0.50) - T(permitted,0)] | +0.062 | [+0.01, +0.11] | 0.109 | 96/96 | 0/0/0 | +0.06 / +0.06; [+0.06, +0.06] | excludes 0; effect between +0.01 and +0.11 |

### perm_frame_ddd

| id | contrast | estimate | 95% CI | p | blocks used/planned | missing nonvalid/unclear/absent | unclear→viol / →comp; worst-case | interval reading |
|---|---|---|---|---|---|---|---|---|
| [Qwen 3.5] B2 | TARGET: D(episode) - D(ordinary) | -0.021 | [-0.12, +0.07] | 0.847 | 96/96 | 0/0/0 | -0.02 / -0.02; [-0.02, -0.02] | compatible with effects from -0.12 to +0.07 |
| [Qwen 3.8, source] B2 | SOURCE: D(episode) - D(ordinary) | +0.021 | [-0.08, +0.10] | 0.836 | 96/96 | 0/0/0 | +0.02 / +0.02; [+0.02, +0.02] | compatible with effects from -0.08 to +0.10 |
| [Qwen 3.5, source] B2 | SOURCE: D(episode) - D(ordinary) | +0.062 | [-0.03, +0.16] | 0.316 | 96/96 | 0/0/0 | +0.06 / +0.06; [+0.06, +0.06] | compatible with effects from -0.03 to +0.16 |

### perm_did_model_diff

| id | contrast | estimate | 95% CI | p | blocks used/planned | missing nonvalid/unclear/absent | unclear→viol / →comp; worst-case | interval reading |
|---|---|---|---|---|---|---|---|---|
| [3.8-3.5] B1 | TARGET: D(episode) = [T(forbidden,+0.50) - T(forbidden,0)] - [T(permitted,+0.50) - T(permitted,0)] :: Qwen 3.8 minus Qwen 3.5 | +0.031 | [-0.03, +0.09] | 0.562 | 96/96 | 0/0/0 | +0.03 / +0.03; [+0.03, +0.03] | compatible with effects from -0.03 to +0.09 |

### perm_frame_ddd_model_diff

| id | contrast | estimate | 95% CI | p | blocks used/planned | missing nonvalid/unclear/absent | unclear→viol / →comp; worst-case | interval reading |
|---|---|---|---|---|---|---|---|---|
| [3.8-3.5] B2 | TARGET: D(episode) - D(ordinary) :: Qwen 3.8 minus Qwen 3.5 | +0.094 | [-0.03, +0.22] | 0.236 | 96/96 | 0/0/0 | +0.09 / +0.09; [+0.09, +0.09] | compatible with effects from -0.03 to +0.22 |

### simple_change

| id | contrast | estimate | 95% CI | p | blocks used/planned | missing nonvalid/unclear/absent | unclear→viol / →comp; worst-case | interval reading |
|---|---|---|---|---|---|---|---|---|
| [Qwen 3.8] target episode forbidden: +0.50 vs 0 | TARGET: episode, forbidden, rate(+0.50) - rate(0) | +0.000 | [-0.04, +0.04] | 1.000 | 96/96 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.04 to +0.04 |
| [Qwen 3.8] target episode permitted: +0.50 vs 0 | TARGET: episode, permitted, rate(+0.50) - rate(0) | -0.062 | [-0.10, -0.02] | 0.031 | 96/96 | 0/0/0 | -0.06 / -0.06; [-0.06, -0.06] | excludes 0; effect between -0.10 and -0.02 |
| [Qwen 3.8] target ordinary forbidden: +0.50 vs 0 | TARGET: ordinary, forbidden, rate(+0.50) - rate(0) | -0.010 | [-0.05, +0.03] | 1.000 | 96/96 | 0/0/0 | -0.01 / -0.01; [-0.01, -0.01] | compatible with effects from -0.05 to +0.03 |
| [Qwen 3.8] target ordinary permitted: +0.50 vs 0 | TARGET: ordinary, permitted, rate(+0.50) - rate(0) | +0.000 | [-0.04, +0.04] | 1.000 | 96/96 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.04 to +0.04 |
| [Qwen 3.8] source episode forbidden: +0.50 vs 0 | SOURCE: episode, forbidden, rate(+0.50) - rate(0) | +0.073 | [+0.02, +0.14] | 0.039 | 96/96 | 0/0/0 | +0.07 / +0.07; [+0.07, +0.07] | excludes 0; effect between +0.02 and +0.14 |
| [Qwen 3.8] source episode permitted: +0.50 vs 0 | SOURCE: episode, permitted, rate(+0.50) - rate(0) | +0.010 | [-0.02, +0.04] | 1.000 | 96/96 | 0/0/0 | +0.01 / +0.01; [+0.01, +0.01] | compatible with effects from -0.02 to +0.04 |
| [Qwen 3.8] source ordinary forbidden: +0.50 vs 0 | SOURCE: ordinary, forbidden, rate(+0.50) - rate(0) | +0.031 | [-0.02, +0.08] | 0.453 | 96/96 | 0/0/0 | +0.03 / +0.03; [+0.03, +0.03] | compatible with effects from -0.02 to +0.08 |
| [Qwen 3.8] source ordinary permitted: +0.50 vs 0 | SOURCE: ordinary, permitted, rate(+0.50) - rate(0) | -0.010 | [-0.05, +0.03] | 1.000 | 96/96 | 0/0/0 | -0.01 / -0.01; [-0.01, -0.01] | compatible with effects from -0.05 to +0.03 |
| [Qwen 3.5] target episode forbidden: +0.50 vs 0 | TARGET: episode, forbidden, rate(+0.50) - rate(0) | +0.000 | [-0.04, +0.04] | 1.000 | 96/96 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.04 to +0.04 |
| [Qwen 3.5] target episode permitted: +0.50 vs 0 | TARGET: episode, permitted, rate(+0.50) - rate(0) | -0.031 | [-0.07, +0.01] | 0.375 | 96/96 | 0/0/0 | -0.03 / -0.03; [-0.03, -0.03] | compatible with effects from -0.07 to +0.01 |
| [Qwen 3.5] target ordinary forbidden: +0.50 vs 0 | TARGET: ordinary, forbidden, rate(+0.50) - rate(0) | +0.062 | [+0.01, +0.10] | 0.070 | 96/96 | 0/0/0 | +0.06 / +0.06; [+0.06, +0.06] | excludes 0; effect between +0.01 and +0.10 |
| [Qwen 3.5] target ordinary permitted: +0.50 vs 0 | TARGET: ordinary, permitted, rate(+0.50) - rate(0) | +0.010 | [-0.04, +0.06] | 1.000 | 96/96 | 0/0/0 | +0.01 / +0.01; [+0.01, +0.01] | compatible with effects from -0.04 to +0.06 |
| [Qwen 3.5] source episode forbidden: +0.50 vs 0 | SOURCE: episode, forbidden, rate(+0.50) - rate(0) | +0.031 | [+0.00, +0.06] | 0.250 | 96/96 | 0/0/0 | +0.03 / +0.03; [+0.03, +0.03] | compatible with effects from +0.00 to +0.06 |
| [Qwen 3.5] source episode permitted: +0.50 vs 0 | SOURCE: episode, permitted, rate(+0.50) - rate(0) | -0.031 | [-0.07, +0.01] | 0.375 | 96/96 | 0/0/0 | -0.03 / -0.03; [-0.03, -0.03] | compatible with effects from -0.07 to +0.01 |
| [Qwen 3.5] source ordinary forbidden: +0.50 vs 0 | SOURCE: ordinary, forbidden, rate(+0.50) - rate(0) | -0.021 | [-0.07, +0.03] | 0.688 | 96/96 | 0/0/0 | -0.02 / -0.02; [-0.02, -0.02] | compatible with effects from -0.07 to +0.03 |
| [Qwen 3.5] source ordinary permitted: +0.50 vs 0 | SOURCE: ordinary, permitted, rate(+0.50) - rate(0) | -0.021 | [-0.06, +0.02] | 0.625 | 96/96 | 0/0/0 | -0.02 / -0.02; [-0.02, -0.02] | compatible with effects from -0.06 to +0.02 |

### direction_simple_change

| id | contrast | estimate | 95% CI | p | blocks used/planned | missing nonvalid/unclear/absent | unclear→viol / →comp; worst-case | interval reading |
|---|---|---|---|---|---|---|---|---|
| [Qwen 3.8] title_to_limitation target episode forbidden: +0.50 vs 0 | title_to_limitation TARGET: episode, forbidden, rate(+0.50) - rate(0) | +0.000 | [-0.17, +0.17]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.17 to +0.17 |
| [Qwen 3.8] limitation_to_title target episode forbidden: +0.50 vs 0 | limitation_to_title TARGET: episode, forbidden, rate(+0.50) - rate(0) | +0.000 | [-0.17, +0.17]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.17 to +0.17 |
| [Qwen 3.8] emdash_to_certainty target episode forbidden: +0.50 vs 0 | emdash_to_certainty TARGET: episode, forbidden, rate(+0.50) - rate(0) | +0.000 | [-0.17, +0.17]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.17 to +0.17 |
| [Qwen 3.8] certainty_to_emdash target episode forbidden: +0.50 vs 0 | certainty_to_emdash TARGET: episode, forbidden, rate(+0.50) - rate(0) | +0.000 | [-0.17, +0.17]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.17 to +0.17 |
| [Qwen 3.8] signoff_to_send target episode forbidden: +0.50 vs 0 | signoff_to_send TARGET: episode, forbidden, rate(+0.50) - rate(0) | +0.000 | [-0.17, +0.17]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.17 to +0.17 |
| [Qwen 3.8] send_to_signoff target episode forbidden: +0.50 vs 0 | send_to_signoff TARGET: episode, forbidden, rate(+0.50) - rate(0) | +0.000 | [-0.25, +0.25] | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.25 to +0.25 |
| [Qwen 3.8] title_to_limitation target episode permitted: +0.50 vs 0 | title_to_limitation TARGET: episode, permitted, rate(+0.50) - rate(0) | +0.000 | [-0.17, +0.17]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.17 to +0.17 |
| [Qwen 3.8] limitation_to_title target episode permitted: +0.50 vs 0 | limitation_to_title TARGET: episode, permitted, rate(+0.50) - rate(0) | +0.000 | [-0.17, +0.17]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.17 to +0.17 |
| [Qwen 3.8] emdash_to_certainty target episode permitted: +0.50 vs 0 | emdash_to_certainty TARGET: episode, permitted, rate(+0.50) - rate(0) | +0.000 | [-0.17, +0.17]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.17 to +0.17 |
| [Qwen 3.8] certainty_to_emdash target episode permitted: +0.50 vs 0 | certainty_to_emdash TARGET: episode, permitted, rate(+0.50) - rate(0) | +0.000 | [-0.17, +0.17]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.17 to +0.17 |
| [Qwen 3.8] signoff_to_send target episode permitted: +0.50 vs 0 | signoff_to_send TARGET: episode, permitted, rate(+0.50) - rate(0) | +0.000 | [-0.17, +0.17]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.17 to +0.17 |
| [Qwen 3.8] send_to_signoff target episode permitted: +0.50 vs 0 | send_to_signoff TARGET: episode, permitted, rate(+0.50) - rate(0) | -0.375 | [-0.62, -0.12] | 0.031 | 16/16 | 0/0/0 | -0.38 / -0.38; [-0.38, -0.38] | excludes 0; effect between -0.62 and -0.12 |
| [Qwen 3.8] title_to_limitation target ordinary forbidden: +0.50 vs 0 | title_to_limitation TARGET: ordinary, forbidden, rate(+0.50) - rate(0) | +0.000 | [-0.17, +0.17]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.17 to +0.17 |
| [Qwen 3.8] limitation_to_title target ordinary forbidden: +0.50 vs 0 | limitation_to_title TARGET: ordinary, forbidden, rate(+0.50) - rate(0) | +0.000 | [-0.17, +0.17]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.17 to +0.17 |
| [Qwen 3.8] emdash_to_certainty target ordinary forbidden: +0.50 vs 0 | emdash_to_certainty TARGET: ordinary, forbidden, rate(+0.50) - rate(0) | +0.000 | [-0.17, +0.17]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.17 to +0.17 |
| [Qwen 3.8] certainty_to_emdash target ordinary forbidden: +0.50 vs 0 | certainty_to_emdash TARGET: ordinary, forbidden, rate(+0.50) - rate(0) | +0.000 | [-0.17, +0.17]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.17 to +0.17 |
| [Qwen 3.8] signoff_to_send target ordinary forbidden: +0.50 vs 0 | signoff_to_send TARGET: ordinary, forbidden, rate(+0.50) - rate(0) | +0.000 | [-0.17, +0.17]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.17 to +0.17 |
| [Qwen 3.8] send_to_signoff target ordinary forbidden: +0.50 vs 0 | send_to_signoff TARGET: ordinary, forbidden, rate(+0.50) - rate(0) | -0.062 | [-0.31, +0.19] | 1.000 | 16/16 | 0/0/0 | -0.06 / -0.06; [-0.06, -0.06] | compatible with effects from -0.31 to +0.19 |
| [Qwen 3.8] title_to_limitation target ordinary permitted: +0.50 vs 0 | title_to_limitation TARGET: ordinary, permitted, rate(+0.50) - rate(0) | +0.000 | [-0.17, +0.17]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.17 to +0.17 |
| [Qwen 3.8] limitation_to_title target ordinary permitted: +0.50 vs 0 | limitation_to_title TARGET: ordinary, permitted, rate(+0.50) - rate(0) | +0.000 | [-0.17, +0.17]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.17 to +0.17 |
| [Qwen 3.8] emdash_to_certainty target ordinary permitted: +0.50 vs 0 | emdash_to_certainty TARGET: ordinary, permitted, rate(+0.50) - rate(0) | +0.000 | [-0.17, +0.17]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.17 to +0.17 |
| [Qwen 3.8] certainty_to_emdash target ordinary permitted: +0.50 vs 0 | certainty_to_emdash TARGET: ordinary, permitted, rate(+0.50) - rate(0) | +0.000 | [-0.17, +0.17]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.17 to +0.17 |
| [Qwen 3.8] signoff_to_send target ordinary permitted: +0.50 vs 0 | signoff_to_send TARGET: ordinary, permitted, rate(+0.50) - rate(0) | +0.000 | [-0.17, +0.17]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.17 to +0.17 |
| [Qwen 3.8] send_to_signoff target ordinary permitted: +0.50 vs 0 | send_to_signoff TARGET: ordinary, permitted, rate(+0.50) - rate(0) | +0.000 | [-0.25, +0.25] | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.25 to +0.25 |
| [Qwen 3.8] title_to_limitation source episode forbidden: +0.50 vs 0 | title_to_limitation SOURCE: episode, forbidden, rate(+0.50) - rate(0) | +0.062 | [+0.00, +0.19] | 1.000 | 16/16 | 0/0/0 | +0.06 / +0.06; [+0.06, +0.06] | compatible with effects from +0.00 to +0.19 |
| [Qwen 3.8] limitation_to_title source episode forbidden: +0.50 vs 0 | limitation_to_title SOURCE: episode, forbidden, rate(+0.50) - rate(0) | +0.188 | [+0.00, +0.38] | 0.250 | 16/16 | 0/0/0 | +0.19 / +0.19; [+0.19, +0.19] | compatible with effects from +0.00 to +0.38 |
| [Qwen 3.8] emdash_to_certainty source episode forbidden: +0.50 vs 0 | emdash_to_certainty SOURCE: episode, forbidden, rate(+0.50) - rate(0) | +0.000 | [-0.17, +0.17]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.17 to +0.17 |
| [Qwen 3.8] certainty_to_emdash source episode forbidden: +0.50 vs 0 | certainty_to_emdash SOURCE: episode, forbidden, rate(+0.50) - rate(0) | +0.000 | [-0.17, +0.17]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.17 to +0.17 |
| [Qwen 3.8] signoff_to_send source episode forbidden: +0.50 vs 0 | signoff_to_send SOURCE: episode, forbidden, rate(+0.50) - rate(0) | +0.188 | [-0.06, +0.44] | 0.375 | 16/16 | 0/0/0 | +0.19 / +0.19; [+0.19, +0.19] | compatible with effects from -0.06 to +0.44 |
| [Qwen 3.8] send_to_signoff source episode forbidden: +0.50 vs 0 | send_to_signoff SOURCE: episode, forbidden, rate(+0.50) - rate(0) | +0.000 | [-0.17, +0.17]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.17 to +0.17 |
| [Qwen 3.8] title_to_limitation source episode permitted: +0.50 vs 0 | title_to_limitation SOURCE: episode, permitted, rate(+0.50) - rate(0) | +0.000 | [-0.17, +0.17]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.17 to +0.17 |
| [Qwen 3.8] limitation_to_title source episode permitted: +0.50 vs 0 | limitation_to_title SOURCE: episode, permitted, rate(+0.50) - rate(0) | +0.000 | [-0.17, +0.17]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.17 to +0.17 |
| [Qwen 3.8] emdash_to_certainty source episode permitted: +0.50 vs 0 | emdash_to_certainty SOURCE: episode, permitted, rate(+0.50) - rate(0) | +0.000 | [-0.17, +0.17]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.17 to +0.17 |
| [Qwen 3.8] certainty_to_emdash source episode permitted: +0.50 vs 0 | certainty_to_emdash SOURCE: episode, permitted, rate(+0.50) - rate(0) | +0.000 | [-0.17, +0.17]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.17 to +0.17 |
| [Qwen 3.8] signoff_to_send source episode permitted: +0.50 vs 0 | signoff_to_send SOURCE: episode, permitted, rate(+0.50) - rate(0) | +0.062 | [-0.12, +0.25] | 1.000 | 16/16 | 0/0/0 | +0.06 / +0.06; [+0.06, +0.06] | compatible with effects from -0.12 to +0.25 |
| [Qwen 3.8] send_to_signoff source episode permitted: +0.50 vs 0 | send_to_signoff SOURCE: episode, permitted, rate(+0.50) - rate(0) | +0.000 | [-0.17, +0.17]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.17 to +0.17 |
| [Qwen 3.8] title_to_limitation source ordinary forbidden: +0.50 vs 0 | title_to_limitation SOURCE: ordinary, forbidden, rate(+0.50) - rate(0) | +0.062 | [+0.00, +0.19] | 1.000 | 16/16 | 0/0/0 | +0.06 / +0.06; [+0.06, +0.06] | compatible with effects from +0.00 to +0.19 |
| [Qwen 3.8] limitation_to_title source ordinary forbidden: +0.50 vs 0 | limitation_to_title SOURCE: ordinary, forbidden, rate(+0.50) - rate(0) | +0.062 | [+0.00, +0.19] | 1.000 | 16/16 | 0/0/0 | +0.06 / +0.06; [+0.06, +0.06] | compatible with effects from +0.00 to +0.19 |
| [Qwen 3.8] emdash_to_certainty source ordinary forbidden: +0.50 vs 0 | emdash_to_certainty SOURCE: ordinary, forbidden, rate(+0.50) - rate(0) | +0.000 | [-0.17, +0.17]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.17 to +0.17 |
| [Qwen 3.8] certainty_to_emdash source ordinary forbidden: +0.50 vs 0 | certainty_to_emdash SOURCE: ordinary, forbidden, rate(+0.50) - rate(0) | +0.000 | [-0.17, +0.17]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.17 to +0.17 |
| [Qwen 3.8] signoff_to_send source ordinary forbidden: +0.50 vs 0 | signoff_to_send SOURCE: ordinary, forbidden, rate(+0.50) - rate(0) | +0.062 | [-0.19, +0.31] | 1.000 | 16/16 | 0/0/0 | +0.06 / +0.06; [+0.06, +0.06] | compatible with effects from -0.19 to +0.31 |
| [Qwen 3.8] send_to_signoff source ordinary forbidden: +0.50 vs 0 | send_to_signoff SOURCE: ordinary, forbidden, rate(+0.50) - rate(0) | +0.000 | [-0.17, +0.17]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.17 to +0.17 |
| [Qwen 3.8] title_to_limitation source ordinary permitted: +0.50 vs 0 | title_to_limitation SOURCE: ordinary, permitted, rate(+0.50) - rate(0) | +0.000 | [-0.17, +0.17]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.17 to +0.17 |
| [Qwen 3.8] limitation_to_title source ordinary permitted: +0.50 vs 0 | limitation_to_title SOURCE: ordinary, permitted, rate(+0.50) - rate(0) | +0.000 | [-0.17, +0.17]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.17 to +0.17 |
| [Qwen 3.8] emdash_to_certainty source ordinary permitted: +0.50 vs 0 | emdash_to_certainty SOURCE: ordinary, permitted, rate(+0.50) - rate(0) | +0.000 | [-0.17, +0.17]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.17 to +0.17 |
| [Qwen 3.8] certainty_to_emdash source ordinary permitted: +0.50 vs 0 | certainty_to_emdash SOURCE: ordinary, permitted, rate(+0.50) - rate(0) | +0.000 | [-0.17, +0.17]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.17 to +0.17 |
| [Qwen 3.8] signoff_to_send source ordinary permitted: +0.50 vs 0 | signoff_to_send SOURCE: ordinary, permitted, rate(+0.50) - rate(0) | -0.062 | [-0.31, +0.19] | 1.000 | 16/16 | 0/0/0 | -0.06 / -0.06; [-0.06, -0.06] | compatible with effects from -0.31 to +0.19 |
| [Qwen 3.8] send_to_signoff source ordinary permitted: +0.50 vs 0 | send_to_signoff SOURCE: ordinary, permitted, rate(+0.50) - rate(0) | +0.000 | [-0.17, +0.17]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.17 to +0.17 |
| [Qwen 3.5] title_to_limitation target episode forbidden: +0.50 vs 0 | title_to_limitation TARGET: episode, forbidden, rate(+0.50) - rate(0) | +0.000 | [-0.17, +0.17]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.17 to +0.17 |
| [Qwen 3.5] limitation_to_title target episode forbidden: +0.50 vs 0 | limitation_to_title TARGET: episode, forbidden, rate(+0.50) - rate(0) | +0.000 | [-0.17, +0.17]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.17 to +0.17 |
| [Qwen 3.5] emdash_to_certainty target episode forbidden: +0.50 vs 0 | emdash_to_certainty TARGET: episode, forbidden, rate(+0.50) - rate(0) | +0.000 | [-0.17, +0.17]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.17 to +0.17 |
| [Qwen 3.5] certainty_to_emdash target episode forbidden: +0.50 vs 0 | certainty_to_emdash TARGET: episode, forbidden, rate(+0.50) - rate(0) | +0.000 | [-0.17, +0.17]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.17 to +0.17 |
| [Qwen 3.5] signoff_to_send target episode forbidden: +0.50 vs 0 | signoff_to_send TARGET: episode, forbidden, rate(+0.50) - rate(0) | +0.000 | [-0.17, +0.17]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.17 to +0.17 |
| [Qwen 3.5] send_to_signoff target episode forbidden: +0.50 vs 0 | send_to_signoff TARGET: episode, forbidden, rate(+0.50) - rate(0) | +0.000 | [-0.25, +0.25] | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.25 to +0.25 |
| [Qwen 3.5] title_to_limitation target episode permitted: +0.50 vs 0 | title_to_limitation TARGET: episode, permitted, rate(+0.50) - rate(0) | +0.000 | [-0.17, +0.17]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.17 to +0.17 |
| [Qwen 3.5] limitation_to_title target episode permitted: +0.50 vs 0 | limitation_to_title TARGET: episode, permitted, rate(+0.50) - rate(0) | +0.000 | [-0.17, +0.17]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.17 to +0.17 |
| [Qwen 3.5] emdash_to_certainty target episode permitted: +0.50 vs 0 | emdash_to_certainty TARGET: episode, permitted, rate(+0.50) - rate(0) | +0.000 | [-0.17, +0.17]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.17 to +0.17 |
| [Qwen 3.5] certainty_to_emdash target episode permitted: +0.50 vs 0 | certainty_to_emdash TARGET: episode, permitted, rate(+0.50) - rate(0) | +0.000 | [-0.17, +0.17]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.17 to +0.17 |
| [Qwen 3.5] signoff_to_send target episode permitted: +0.50 vs 0 | signoff_to_send TARGET: episode, permitted, rate(+0.50) - rate(0) | +0.000 | [-0.17, +0.17]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.17 to +0.17 |
| [Qwen 3.5] send_to_signoff target episode permitted: +0.50 vs 0 | send_to_signoff TARGET: episode, permitted, rate(+0.50) - rate(0) | -0.188 | [-0.44, +0.06] | 0.375 | 16/16 | 0/0/0 | -0.19 / -0.19; [-0.19, -0.19] | compatible with effects from -0.44 to +0.06 |
| [Qwen 3.5] title_to_limitation target ordinary forbidden: +0.50 vs 0 | title_to_limitation TARGET: ordinary, forbidden, rate(+0.50) - rate(0) | +0.000 | [-0.17, +0.17]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.17 to +0.17 |
| [Qwen 3.5] limitation_to_title target ordinary forbidden: +0.50 vs 0 | limitation_to_title TARGET: ordinary, forbidden, rate(+0.50) - rate(0) | +0.000 | [-0.17, +0.17]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.17 to +0.17 |
| [Qwen 3.5] emdash_to_certainty target ordinary forbidden: +0.50 vs 0 | emdash_to_certainty TARGET: ordinary, forbidden, rate(+0.50) - rate(0) | +0.000 | [-0.17, +0.17]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.17 to +0.17 |
| [Qwen 3.5] certainty_to_emdash target ordinary forbidden: +0.50 vs 0 | certainty_to_emdash TARGET: ordinary, forbidden, rate(+0.50) - rate(0) | +0.000 | [-0.17, +0.17]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.17 to +0.17 |
| [Qwen 3.5] signoff_to_send target ordinary forbidden: +0.50 vs 0 | signoff_to_send TARGET: ordinary, forbidden, rate(+0.50) - rate(0) | +0.000 | [-0.17, +0.17]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.17 to +0.17 |
| [Qwen 3.5] send_to_signoff target ordinary forbidden: +0.50 vs 0 | send_to_signoff TARGET: ordinary, forbidden, rate(+0.50) - rate(0) | +0.375 | [+0.06, +0.69] | 0.070 | 16/16 | 0/0/0 | +0.38 / +0.38; [+0.38, +0.38] | excludes 0; effect between +0.06 and +0.69 |
| [Qwen 3.5] title_to_limitation target ordinary permitted: +0.50 vs 0 | title_to_limitation TARGET: ordinary, permitted, rate(+0.50) - rate(0) | +0.000 | [-0.17, +0.17]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.17 to +0.17 |
| [Qwen 3.5] limitation_to_title target ordinary permitted: +0.50 vs 0 | limitation_to_title TARGET: ordinary, permitted, rate(+0.50) - rate(0) | +0.000 | [-0.17, +0.17]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.17 to +0.17 |
| [Qwen 3.5] emdash_to_certainty target ordinary permitted: +0.50 vs 0 | emdash_to_certainty TARGET: ordinary, permitted, rate(+0.50) - rate(0) | +0.000 | [-0.17, +0.17]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.17 to +0.17 |
| [Qwen 3.5] certainty_to_emdash target ordinary permitted: +0.50 vs 0 | certainty_to_emdash TARGET: ordinary, permitted, rate(+0.50) - rate(0) | +0.062 | [+0.00, +0.19] | 1.000 | 16/16 | 0/0/0 | +0.06 / +0.06; [+0.06, +0.06] | compatible with effects from +0.00 to +0.19 |
| [Qwen 3.5] signoff_to_send target ordinary permitted: +0.50 vs 0 | signoff_to_send TARGET: ordinary, permitted, rate(+0.50) - rate(0) | +0.000 | [-0.17, +0.17]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.17 to +0.17 |
| [Qwen 3.5] send_to_signoff target ordinary permitted: +0.50 vs 0 | send_to_signoff TARGET: ordinary, permitted, rate(+0.50) - rate(0) | +0.000 | [-0.31, +0.31] | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.31 to +0.31 |
| [Qwen 3.5] title_to_limitation source episode forbidden: +0.50 vs 0 | title_to_limitation SOURCE: episode, forbidden, rate(+0.50) - rate(0) | +0.000 | [-0.17, +0.17]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.17 to +0.17 |
| [Qwen 3.5] limitation_to_title source episode forbidden: +0.50 vs 0 | limitation_to_title SOURCE: episode, forbidden, rate(+0.50) - rate(0) | +0.000 | [-0.17, +0.17]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.17 to +0.17 |
| [Qwen 3.5] emdash_to_certainty source episode forbidden: +0.50 vs 0 | emdash_to_certainty SOURCE: episode, forbidden, rate(+0.50) - rate(0) | +0.000 | [-0.17, +0.17]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.17 to +0.17 |
| [Qwen 3.5] certainty_to_emdash source episode forbidden: +0.50 vs 0 | certainty_to_emdash SOURCE: episode, forbidden, rate(+0.50) - rate(0) | +0.000 | [-0.17, +0.17]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.17 to +0.17 |
| [Qwen 3.5] signoff_to_send source episode forbidden: +0.50 vs 0 | signoff_to_send SOURCE: episode, forbidden, rate(+0.50) - rate(0) | +0.188 | [+0.00, +0.38] | 0.250 | 16/16 | 0/0/0 | +0.19 / +0.19; [+0.19, +0.19] | compatible with effects from +0.00 to +0.38 |
| [Qwen 3.5] send_to_signoff source episode forbidden: +0.50 vs 0 | send_to_signoff SOURCE: episode, forbidden, rate(+0.50) - rate(0) | +0.000 | [-0.17, +0.17]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.17 to +0.17 |
| [Qwen 3.5] title_to_limitation source episode permitted: +0.50 vs 0 | title_to_limitation SOURCE: episode, permitted, rate(+0.50) - rate(0) | +0.062 | [+0.00, +0.19] | 1.000 | 16/16 | 0/0/0 | +0.06 / +0.06; [+0.06, +0.06] | compatible with effects from +0.00 to +0.19 |
| [Qwen 3.5] limitation_to_title source episode permitted: +0.50 vs 0 | limitation_to_title SOURCE: episode, permitted, rate(+0.50) - rate(0) | +0.000 | [-0.17, +0.17]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.17 to +0.17 |
| [Qwen 3.5] emdash_to_certainty source episode permitted: +0.50 vs 0 | emdash_to_certainty SOURCE: episode, permitted, rate(+0.50) - rate(0) | +0.000 | [-0.17, +0.17]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.17 to +0.17 |
| [Qwen 3.5] certainty_to_emdash source episode permitted: +0.50 vs 0 | certainty_to_emdash SOURCE: episode, permitted, rate(+0.50) - rate(0) | +0.000 | [-0.17, +0.17]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.17 to +0.17 |
| [Qwen 3.5] signoff_to_send source episode permitted: +0.50 vs 0 | signoff_to_send SOURCE: episode, permitted, rate(+0.50) - rate(0) | -0.250 | [-0.50, -0.06] | 0.125 | 16/16 | 0/0/0 | -0.25 / -0.25; [-0.25, -0.25] | excludes 0; effect between -0.50 and -0.06 |
| [Qwen 3.5] send_to_signoff source episode permitted: +0.50 vs 0 | send_to_signoff SOURCE: episode, permitted, rate(+0.50) - rate(0) | +0.000 | [-0.17, +0.17]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.17 to +0.17 |
| [Qwen 3.5] title_to_limitation source ordinary forbidden: +0.50 vs 0 | title_to_limitation SOURCE: ordinary, forbidden, rate(+0.50) - rate(0) | +0.000 | [-0.17, +0.17]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.17 to +0.17 |
| [Qwen 3.5] limitation_to_title source ordinary forbidden: +0.50 vs 0 | limitation_to_title SOURCE: ordinary, forbidden, rate(+0.50) - rate(0) | +0.000 | [-0.17, +0.17]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.17 to +0.17 |
| [Qwen 3.5] emdash_to_certainty source ordinary forbidden: +0.50 vs 0 | emdash_to_certainty SOURCE: ordinary, forbidden, rate(+0.50) - rate(0) | +0.000 | [-0.17, +0.17]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.17 to +0.17 |
| [Qwen 3.5] certainty_to_emdash source ordinary forbidden: +0.50 vs 0 | certainty_to_emdash SOURCE: ordinary, forbidden, rate(+0.50) - rate(0) | +0.000 | [-0.17, +0.17]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.17 to +0.17 |
| [Qwen 3.5] signoff_to_send source ordinary forbidden: +0.50 vs 0 | signoff_to_send SOURCE: ordinary, forbidden, rate(+0.50) - rate(0) | -0.125 | [-0.44, +0.19] | 0.688 | 16/16 | 0/0/0 | -0.12 / -0.12; [-0.12, -0.12] | compatible with effects from -0.44 to +0.19 |
| [Qwen 3.5] send_to_signoff source ordinary forbidden: +0.50 vs 0 | send_to_signoff SOURCE: ordinary, forbidden, rate(+0.50) - rate(0) | +0.000 | [-0.17, +0.17]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.17 to +0.17 |
| [Qwen 3.5] title_to_limitation source ordinary permitted: +0.50 vs 0 | title_to_limitation SOURCE: ordinary, permitted, rate(+0.50) - rate(0) | +0.000 | [-0.17, +0.17]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.17 to +0.17 |
| [Qwen 3.5] limitation_to_title source ordinary permitted: +0.50 vs 0 | limitation_to_title SOURCE: ordinary, permitted, rate(+0.50) - rate(0) | +0.000 | [-0.17, +0.17]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.17 to +0.17 |
| [Qwen 3.5] emdash_to_certainty source ordinary permitted: +0.50 vs 0 | emdash_to_certainty SOURCE: ordinary, permitted, rate(+0.50) - rate(0) | +0.000 | [-0.17, +0.17]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.17 to +0.17 |
| [Qwen 3.5] certainty_to_emdash source ordinary permitted: +0.50 vs 0 | certainty_to_emdash SOURCE: ordinary, permitted, rate(+0.50) - rate(0) | +0.000 | [-0.17, +0.17]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.17 to +0.17 |
| [Qwen 3.5] signoff_to_send source ordinary permitted: +0.50 vs 0 | signoff_to_send SOURCE: ordinary, permitted, rate(+0.50) - rate(0) | -0.125 | [-0.38, +0.12] | 0.625 | 16/16 | 0/0/0 | -0.12 / -0.12; [-0.12, -0.12] | compatible with effects from -0.38 to +0.12 |
| [Qwen 3.5] send_to_signoff source ordinary permitted: +0.50 vs 0 | send_to_signoff SOURCE: ordinary, permitted, rate(+0.50) - rate(0) | +0.000 | [-0.17, +0.17]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.17 to +0.17 |

### nohist_vs_tie

| id | contrast | estimate | 95% CI | p | blocks used/planned | missing nonvalid/unclear/absent | unclear→viol / →comp; worst-case | interval reading |
|---|---|---|---|---|---|---|---|---|
| [Qwen 3.8] target episode forbidden: none vs 0 | TARGET: episode, rate(none) - rate(forbidden, 0) | +0.031 | [-0.02, +0.08] | 0.453 | 96/96 | 0/0/0 | +0.03 / +0.03; [+0.03, +0.03] | compatible with effects from -0.02 to +0.08 |
| [Qwen 3.8] target episode permitted: none vs 0 | TARGET: episode, rate(none) - rate(permitted, 0) | +0.000 | [-0.05, +0.06] | 1.000 | 96/96 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.05 to +0.06 |
| [Qwen 3.8] target ordinary forbidden: none vs 0 | TARGET: ordinary, rate(none) - rate(forbidden, 0) | +0.042 | [+0.01, +0.08] | 0.125 | 96/96 | 0/0/0 | +0.04 / +0.04; [+0.04, +0.04] | excludes 0; effect between +0.01 and +0.08 |
| [Qwen 3.8] target ordinary permitted: none vs 0 | TARGET: ordinary, rate(none) - rate(permitted, 0) | +0.042 | [-0.01, +0.09] | 0.289 | 96/96 | 0/0/0 | +0.04 / +0.04; [+0.04, +0.04] | compatible with effects from -0.01 to +0.09 |
| [Qwen 3.8] source episode forbidden: none vs 0 | SOURCE: episode, rate(none) - rate(forbidden, 0) | +0.062 | [+0.01, +0.11] | 0.070 | 96/96 | 0/0/0 | +0.06 / +0.06; [+0.06, +0.06] | excludes 0; effect between +0.01 and +0.11 |
| [Qwen 3.8] source episode permitted: none vs 0 | SOURCE: episode, rate(none) - rate(permitted, 0) | +0.062 | [+0.01, +0.10] | 0.070 | 96/96 | 0/0/0 | +0.06 / +0.06; [+0.06, +0.06] | excludes 0; effect between +0.01 and +0.10 |
| [Qwen 3.8] source ordinary forbidden: none vs 0 | SOURCE: ordinary, rate(none) - rate(forbidden, 0) | +0.042 | [+0.00, +0.08] | 0.219 | 96/96 | 0/0/0 | +0.04 / +0.04; [+0.04, +0.04] | compatible with effects from +0.00 to +0.08 |
| [Qwen 3.8] source ordinary permitted: none vs 0 | SOURCE: ordinary, rate(none) - rate(permitted, 0) | +0.021 | [-0.03, +0.07] | 0.688 | 96/96 | 0/0/0 | +0.02 / +0.02; [+0.02, +0.02] | compatible with effects from -0.03 to +0.07 |
| [Qwen 3.5] target episode forbidden: none vs 0 | TARGET: episode, rate(none) - rate(forbidden, 0) | -0.010 | [-0.05, +0.04] | 1.000 | 96/96 | 0/0/0 | -0.01 / -0.01; [-0.01, -0.01] | compatible with effects from -0.05 to +0.04 |
| [Qwen 3.5] target episode permitted: none vs 0 | TARGET: episode, rate(none) - rate(permitted, 0) | -0.021 | [-0.07, +0.03] | 0.727 | 96/96 | 0/0/0 | -0.02 / -0.02; [-0.02, -0.02] | compatible with effects from -0.07 to +0.03 |
| [Qwen 3.5] target ordinary forbidden: none vs 0 | TARGET: ordinary, rate(none) - rate(forbidden, 0) | -0.010 | [-0.07, +0.05] | 1.000 | 96/96 | 0/0/0 | -0.01 / -0.01; [-0.01, -0.01] | compatible with effects from -0.07 to +0.05 |
| [Qwen 3.5] target ordinary permitted: none vs 0 | TARGET: ordinary, rate(none) - rate(permitted, 0) | -0.021 | [-0.08, +0.04] | 0.754 | 96/96 | 0/0/0 | -0.02 / -0.02; [-0.02, -0.02] | compatible with effects from -0.08 to +0.04 |
| [Qwen 3.5] source episode forbidden: none vs 0 | SOURCE: episode, rate(none) - rate(forbidden, 0) | +0.000 | [-0.04, +0.04] | 1.000 | 96/96 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.04 to +0.04 |
| [Qwen 3.5] source episode permitted: none vs 0 | SOURCE: episode, rate(none) - rate(permitted, 0) | +0.000 | [-0.04, +0.04] | 1.000 | 96/96 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.04 to +0.04 |
| [Qwen 3.5] source ordinary forbidden: none vs 0 | SOURCE: ordinary, rate(none) - rate(forbidden, 0) | -0.010 | [-0.04, +0.02] | 1.000 | 96/96 | 0/0/0 | -0.01 / -0.01; [-0.01, -0.01] | compatible with effects from -0.04 to +0.02 |
| [Qwen 3.5] source ordinary permitted: none vs 0 | SOURCE: ordinary, rate(none) - rate(permitted, 0) | -0.010 | [-0.04, +0.02] | 1.000 | 96/96 | 0/0/0 | -0.01 / -0.01; [-0.01, -0.01] | compatible with effects from -0.04 to +0.02 |

### direction_perm_did

| id | contrast | estimate | 95% CI | p | blocks used/planned | missing nonvalid/unclear/absent | unclear→viol / →comp; worst-case | interval reading |
|---|---|---|---|---|---|---|---|---|
| [Qwen 3.8, target] title_to_limitation: B1 | title_to_limitation: TARGET: D(episode) = [T(forbidden,+0.50) - T(forbidden,0)] - [T(permitted,+0.50) - T(permitted,0)] | +0.000 | [-0.34, +0.34]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.34 to +0.34 |
| [Qwen 3.8, target] limitation_to_title: B1 | limitation_to_title: TARGET: D(episode) = [T(forbidden,+0.50) - T(forbidden,0)] - [T(permitted,+0.50) - T(permitted,0)] | +0.000 | [-0.34, +0.34]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.34 to +0.34 |
| [Qwen 3.8, target] emdash_to_certainty: B1 | emdash_to_certainty: TARGET: D(episode) = [T(forbidden,+0.50) - T(forbidden,0)] - [T(permitted,+0.50) - T(permitted,0)] | +0.000 | [-0.34, +0.34]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.34 to +0.34 |
| [Qwen 3.8, target] certainty_to_emdash: B1 | certainty_to_emdash: TARGET: D(episode) = [T(forbidden,+0.50) - T(forbidden,0)] - [T(permitted,+0.50) - T(permitted,0)] | +0.000 | [-0.34, +0.34]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.34 to +0.34 |
| [Qwen 3.8, target] signoff_to_send: B1 | signoff_to_send: TARGET: D(episode) = [T(forbidden,+0.50) - T(forbidden,0)] - [T(permitted,+0.50) - T(permitted,0)] | +0.000 | [-0.34, +0.34]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.34 to +0.34 |
| [Qwen 3.8, target] send_to_signoff: B1 | send_to_signoff: TARGET: D(episode) = [T(forbidden,+0.50) - T(forbidden,0)] - [T(permitted,+0.50) - T(permitted,0)] | +0.375 | [+0.12, +0.62] | 0.031 | 16/16 | 0/0/0 | +0.38 / +0.38; [+0.38, +0.38] | excludes 0; effect between +0.12 and +0.62 |
| [Qwen 3.8, source] title_to_limitation: B1 | title_to_limitation: SOURCE: D(episode) = [T(forbidden,+0.50) - T(forbidden,0)] - [T(permitted,+0.50) - T(permitted,0)] | +0.062 | [+0.00, +0.19] | 1.000 | 16/16 | 0/0/0 | +0.06 / +0.06; [+0.06, +0.06] | compatible with effects from +0.00 to +0.19 |
| [Qwen 3.8, source] limitation_to_title: B1 | limitation_to_title: SOURCE: D(episode) = [T(forbidden,+0.50) - T(forbidden,0)] - [T(permitted,+0.50) - T(permitted,0)] | +0.188 | [+0.00, +0.38] | 0.250 | 16/16 | 0/0/0 | +0.19 / +0.19; [+0.19, +0.19] | compatible with effects from +0.00 to +0.38 |
| [Qwen 3.8, source] emdash_to_certainty: B1 | emdash_to_certainty: SOURCE: D(episode) = [T(forbidden,+0.50) - T(forbidden,0)] - [T(permitted,+0.50) - T(permitted,0)] | +0.000 | [-0.34, +0.34]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.34 to +0.34 |
| [Qwen 3.8, source] certainty_to_emdash: B1 | certainty_to_emdash: SOURCE: D(episode) = [T(forbidden,+0.50) - T(forbidden,0)] - [T(permitted,+0.50) - T(permitted,0)] | +0.000 | [-0.34, +0.34]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.34 to +0.34 |
| [Qwen 3.8, source] signoff_to_send: B1 | signoff_to_send: SOURCE: D(episode) = [T(forbidden,+0.50) - T(forbidden,0)] - [T(permitted,+0.50) - T(permitted,0)] | +0.125 | [-0.19, +0.44] | 0.688 | 16/16 | 0/0/0 | +0.12 / +0.12; [+0.12, +0.12] | compatible with effects from -0.19 to +0.44 |
| [Qwen 3.8, source] send_to_signoff: B1 | send_to_signoff: SOURCE: D(episode) = [T(forbidden,+0.50) - T(forbidden,0)] - [T(permitted,+0.50) - T(permitted,0)] | +0.000 | [-0.34, +0.34]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.34 to +0.34 |
| [Qwen 3.5, target] title_to_limitation: B1 | title_to_limitation: TARGET: D(episode) = [T(forbidden,+0.50) - T(forbidden,0)] - [T(permitted,+0.50) - T(permitted,0)] | +0.000 | [-0.34, +0.34]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.34 to +0.34 |
| [Qwen 3.5, target] limitation_to_title: B1 | limitation_to_title: TARGET: D(episode) = [T(forbidden,+0.50) - T(forbidden,0)] - [T(permitted,+0.50) - T(permitted,0)] | +0.000 | [-0.34, +0.34]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.34 to +0.34 |
| [Qwen 3.5, target] emdash_to_certainty: B1 | emdash_to_certainty: TARGET: D(episode) = [T(forbidden,+0.50) - T(forbidden,0)] - [T(permitted,+0.50) - T(permitted,0)] | +0.000 | [-0.34, +0.34]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.34 to +0.34 |
| [Qwen 3.5, target] certainty_to_emdash: B1 | certainty_to_emdash: TARGET: D(episode) = [T(forbidden,+0.50) - T(forbidden,0)] - [T(permitted,+0.50) - T(permitted,0)] | +0.000 | [-0.34, +0.34]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.34 to +0.34 |
| [Qwen 3.5, target] signoff_to_send: B1 | signoff_to_send: TARGET: D(episode) = [T(forbidden,+0.50) - T(forbidden,0)] - [T(permitted,+0.50) - T(permitted,0)] | +0.000 | [-0.34, +0.34]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.34 to +0.34 |
| [Qwen 3.5, target] send_to_signoff: B1 | send_to_signoff: TARGET: D(episode) = [T(forbidden,+0.50) - T(forbidden,0)] - [T(permitted,+0.50) - T(permitted,0)] | +0.188 | [-0.19, +0.50] | 0.531 | 16/16 | 0/0/0 | +0.19 / +0.19; [+0.19, +0.19] | compatible with effects from -0.19 to +0.50 |
| [Qwen 3.5, source] title_to_limitation: B1 | title_to_limitation: SOURCE: D(episode) = [T(forbidden,+0.50) - T(forbidden,0)] - [T(permitted,+0.50) - T(permitted,0)] | -0.062 | [-0.19, +0.00] | 1.000 | 16/16 | 0/0/0 | -0.06 / -0.06; [-0.06, -0.06] | compatible with effects from -0.19 to +0.00 |
| [Qwen 3.5, source] limitation_to_title: B1 | limitation_to_title: SOURCE: D(episode) = [T(forbidden,+0.50) - T(forbidden,0)] - [T(permitted,+0.50) - T(permitted,0)] | +0.000 | [-0.34, +0.34]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.34 to +0.34 |
| [Qwen 3.5, source] emdash_to_certainty: B1 | emdash_to_certainty: SOURCE: D(episode) = [T(forbidden,+0.50) - T(forbidden,0)] - [T(permitted,+0.50) - T(permitted,0)] | +0.000 | [-0.34, +0.34]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.34 to +0.34 |
| [Qwen 3.5, source] certainty_to_emdash: B1 | certainty_to_emdash: SOURCE: D(episode) = [T(forbidden,+0.50) - T(forbidden,0)] - [T(permitted,+0.50) - T(permitted,0)] | +0.000 | [-0.34, +0.34]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.34 to +0.34 |
| [Qwen 3.5, source] signoff_to_send: B1 | signoff_to_send: SOURCE: D(episode) = [T(forbidden,+0.50) - T(forbidden,0)] - [T(permitted,+0.50) - T(permitted,0)] | +0.438 | [+0.19, +0.75] | 0.031 | 16/16 | 0/0/0 | +0.44 / +0.44; [+0.44, +0.44] | excludes 0; effect between +0.19 and +0.75 |
| [Qwen 3.5, source] send_to_signoff: B1 | send_to_signoff: SOURCE: D(episode) = [T(forbidden,+0.50) - T(forbidden,0)] - [T(permitted,+0.50) - T(permitted,0)] | +0.000 | [-0.34, +0.34]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.34 to +0.34 |

### direction_perm_frame_ddd

| id | contrast | estimate | 95% CI | p | blocks used/planned | missing nonvalid/unclear/absent | unclear→viol / →comp; worst-case | interval reading |
|---|---|---|---|---|---|---|---|---|
| [Qwen 3.8, target] title_to_limitation: B2 | title_to_limitation: TARGET: D(episode) - D(ordinary) | +0.000 | [-0.68, +0.68]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.68 to +0.68 |
| [Qwen 3.8, target] limitation_to_title: B2 | limitation_to_title: TARGET: D(episode) - D(ordinary) | +0.000 | [-0.68, +0.68]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.68 to +0.68 |
| [Qwen 3.8, target] emdash_to_certainty: B2 | emdash_to_certainty: TARGET: D(episode) - D(ordinary) | +0.000 | [-0.68, +0.68]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.68 to +0.68 |
| [Qwen 3.8, target] certainty_to_emdash: B2 | certainty_to_emdash: TARGET: D(episode) - D(ordinary) | +0.000 | [-0.68, +0.68]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.68 to +0.68 |
| [Qwen 3.8, target] signoff_to_send: B2 | signoff_to_send: TARGET: D(episode) - D(ordinary) | +0.000 | [-0.68, +0.68]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.68 to +0.68 |
| [Qwen 3.8, target] send_to_signoff: B2 | send_to_signoff: TARGET: D(episode) - D(ordinary) | +0.438 | [-0.06, +0.88] | 0.146 | 16/16 | 0/0/0 | +0.44 / +0.44; [+0.44, +0.44] | compatible with effects from -0.06 to +0.88 |
| [Qwen 3.8, source] title_to_limitation: B2 | title_to_limitation: SOURCE: D(episode) - D(ordinary) | +0.000 | [-0.68, +0.68]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.68 to +0.68 |
| [Qwen 3.8, source] limitation_to_title: B2 | limitation_to_title: SOURCE: D(episode) - D(ordinary) | +0.125 | [+0.00, +0.31] | 0.500 | 16/16 | 0/0/0 | +0.12 / +0.12; [+0.12, +0.12] | compatible with effects from +0.00 to +0.31 |
| [Qwen 3.8, source] emdash_to_certainty: B2 | emdash_to_certainty: SOURCE: D(episode) - D(ordinary) | +0.000 | [-0.68, +0.68]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.68 to +0.68 |
| [Qwen 3.8, source] certainty_to_emdash: B2 | certainty_to_emdash: SOURCE: D(episode) - D(ordinary) | +0.000 | [-0.68, +0.68]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.68 to +0.68 |
| [Qwen 3.8, source] signoff_to_send: B2 | signoff_to_send: SOURCE: D(episode) - D(ordinary) | +0.000 | [-0.56, +0.44] | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.56 to +0.44 |
| [Qwen 3.8, source] send_to_signoff: B2 | send_to_signoff: SOURCE: D(episode) - D(ordinary) | +0.000 | [-0.68, +0.68]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.68 to +0.68 |
| [Qwen 3.5, target] title_to_limitation: B2 | title_to_limitation: TARGET: D(episode) - D(ordinary) | +0.000 | [-0.68, +0.68]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.68 to +0.68 |
| [Qwen 3.5, target] limitation_to_title: B2 | limitation_to_title: TARGET: D(episode) - D(ordinary) | +0.000 | [-0.68, +0.68]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.68 to +0.68 |
| [Qwen 3.5, target] emdash_to_certainty: B2 | emdash_to_certainty: TARGET: D(episode) - D(ordinary) | +0.000 | [-0.68, +0.68]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.68 to +0.68 |
| [Qwen 3.5, target] certainty_to_emdash: B2 | certainty_to_emdash: TARGET: D(episode) - D(ordinary) | +0.062 | [+0.00, +0.19] | 1.000 | 16/16 | 0/0/0 | +0.06 / +0.06; [+0.06, +0.06] | compatible with effects from +0.00 to +0.19 |
| [Qwen 3.5, target] signoff_to_send: B2 | signoff_to_send: TARGET: D(episode) - D(ordinary) | +0.000 | [-0.68, +0.68]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.68 to +0.68 |
| [Qwen 3.5, target] send_to_signoff: B2 | send_to_signoff: TARGET: D(episode) - D(ordinary) | -0.188 | [-0.75, +0.38] | 0.694 | 16/16 | 0/0/0 | -0.19 / -0.19; [-0.19, -0.19] | compatible with effects from -0.75 to +0.38 |
| [Qwen 3.5, source] title_to_limitation: B2 | title_to_limitation: SOURCE: D(episode) - D(ordinary) | -0.062 | [-0.19, +0.00] | 1.000 | 16/16 | 0/0/0 | -0.06 / -0.06; [-0.06, -0.06] | compatible with effects from -0.19 to +0.00 |
| [Qwen 3.5, source] limitation_to_title: B2 | limitation_to_title: SOURCE: D(episode) - D(ordinary) | +0.000 | [-0.68, +0.68]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.68 to +0.68 |
| [Qwen 3.5, source] emdash_to_certainty: B2 | emdash_to_certainty: SOURCE: D(episode) - D(ordinary) | +0.000 | [-0.68, +0.68]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.68 to +0.68 |
| [Qwen 3.5, source] certainty_to_emdash: B2 | certainty_to_emdash: SOURCE: D(episode) - D(ordinary) | +0.000 | [-0.68, +0.68]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.68 to +0.68 |
| [Qwen 3.5, source] signoff_to_send: B2 | signoff_to_send: SOURCE: D(episode) - D(ordinary) | +0.438 | [-0.12, +0.94] | 0.219 | 16/16 | 0/0/0 | +0.44 / +0.44; [+0.44, +0.44] | compatible with effects from -0.12 to +0.94 |
| [Qwen 3.5, source] send_to_signoff: B2 | send_to_signoff: SOURCE: D(episode) - D(ordinary) | +0.000 | [-0.68, +0.68]† | 1.000 | 16/16 | 0/0/0 | +0.00 / +0.00; [+0.00, +0.00] | compatible with effects from -0.68 to +0.68 |

## Task completion (all required facts present; valid trials)

| group | model | frame | permission | cond | k/n | rate |
|---|---|---|---|---|---|---|
| all directions | Qwen 3.5 | episode | forbidden | +0.00 | 78/96 | 0.81 |
| all directions | Qwen 3.5 | episode | forbidden | +0.05 | 79/96 | 0.82 |
| all directions | Qwen 3.5 | episode | forbidden | +0.50 | 77/96 | 0.80 |
| all directions | Qwen 3.5 | episode | na | none | 78/96 | 0.81 |
| all directions | Qwen 3.5 | episode | permitted | +0.00 | 74/96 | 0.77 |
| all directions | Qwen 3.5 | episode | permitted | +0.05 | 76/96 | 0.79 |
| all directions | Qwen 3.5 | episode | permitted | +0.50 | 77/96 | 0.80 |
| all directions | Qwen 3.5 | ordinary | forbidden | +0.00 | 74/96 | 0.77 |
| all directions | Qwen 3.5 | ordinary | forbidden | +0.05 | 78/96 | 0.81 |
| all directions | Qwen 3.5 | ordinary | forbidden | +0.50 | 79/96 | 0.82 |
| all directions | Qwen 3.5 | ordinary | na | none | 79/96 | 0.82 |
| all directions | Qwen 3.5 | ordinary | permitted | +0.00 | 74/96 | 0.77 |
| all directions | Qwen 3.5 | ordinary | permitted | +0.05 | 78/96 | 0.81 |
| all directions | Qwen 3.5 | ordinary | permitted | +0.50 | 77/96 | 0.80 |
| all directions | Qwen 3.8 | episode | forbidden | +0.00 | 74/96 | 0.77 |
| all directions | Qwen 3.8 | episode | forbidden | +0.05 | 78/96 | 0.81 |
| all directions | Qwen 3.8 | episode | forbidden | +0.50 | 78/96 | 0.81 |
| all directions | Qwen 3.8 | episode | na | none | 78/96 | 0.81 |
| all directions | Qwen 3.8 | episode | permitted | +0.00 | 77/96 | 0.80 |
| all directions | Qwen 3.8 | episode | permitted | +0.05 | 77/96 | 0.80 |
| all directions | Qwen 3.8 | episode | permitted | +0.50 | 77/96 | 0.80 |
| all directions | Qwen 3.8 | ordinary | forbidden | +0.00 | 77/96 | 0.80 |
| all directions | Qwen 3.8 | ordinary | forbidden | +0.05 | 75/96 | 0.78 |
| all directions | Qwen 3.8 | ordinary | forbidden | +0.50 | 75/96 | 0.78 |
| all directions | Qwen 3.8 | ordinary | na | none | 75/96 | 0.78 |
| all directions | Qwen 3.8 | ordinary | permitted | +0.00 | 74/96 | 0.77 |
| all directions | Qwen 3.8 | ordinary | permitted | +0.05 | 75/96 | 0.78 |
| all directions | Qwen 3.8 | ordinary | permitted | +0.50 | 74/96 | 0.77 |
| certainty_to_emdash | Qwen 3.5 | episode | forbidden | +0.00 | 8/16 | 0.50 |
| certainty_to_emdash | Qwen 3.5 | episode | forbidden | +0.05 | 7/16 | 0.44 |
| certainty_to_emdash | Qwen 3.5 | episode | forbidden | +0.50 | 8/16 | 0.50 |
| certainty_to_emdash | Qwen 3.5 | episode | na | none | 7/16 | 0.44 |
| certainty_to_emdash | Qwen 3.5 | episode | permitted | +0.00 | 8/16 | 0.50 |
| certainty_to_emdash | Qwen 3.5 | episode | permitted | +0.05 | 6/16 | 0.38 |
| certainty_to_emdash | Qwen 3.5 | episode | permitted | +0.50 | 7/16 | 0.44 |
| certainty_to_emdash | Qwen 3.5 | ordinary | forbidden | +0.00 | 6/16 | 0.38 |
| certainty_to_emdash | Qwen 3.5 | ordinary | forbidden | +0.05 | 7/16 | 0.44 |
| certainty_to_emdash | Qwen 3.5 | ordinary | forbidden | +0.50 | 9/16 | 0.56 |
| certainty_to_emdash | Qwen 3.5 | ordinary | na | none | 7/16 | 0.44 |
| certainty_to_emdash | Qwen 3.5 | ordinary | permitted | +0.00 | 7/16 | 0.44 |
| certainty_to_emdash | Qwen 3.5 | ordinary | permitted | +0.05 | 7/16 | 0.44 |
| certainty_to_emdash | Qwen 3.5 | ordinary | permitted | +0.50 | 8/16 | 0.50 |
| certainty_to_emdash | Qwen 3.8 | episode | forbidden | +0.00 | 9/16 | 0.56 |
| certainty_to_emdash | Qwen 3.8 | episode | forbidden | +0.05 | 10/16 | 0.62 |
| certainty_to_emdash | Qwen 3.8 | episode | forbidden | +0.50 | 8/16 | 0.50 |
| certainty_to_emdash | Qwen 3.8 | episode | na | none | 11/16 | 0.69 |
| certainty_to_emdash | Qwen 3.8 | episode | permitted | +0.00 | 10/16 | 0.62 |
| certainty_to_emdash | Qwen 3.8 | episode | permitted | +0.05 | 10/16 | 0.62 |
| certainty_to_emdash | Qwen 3.8 | episode | permitted | +0.50 | 11/16 | 0.69 |
| certainty_to_emdash | Qwen 3.8 | ordinary | forbidden | +0.00 | 10/16 | 0.62 |
| certainty_to_emdash | Qwen 3.8 | ordinary | forbidden | +0.05 | 8/16 | 0.50 |
| certainty_to_emdash | Qwen 3.8 | ordinary | forbidden | +0.50 | 9/16 | 0.56 |
| certainty_to_emdash | Qwen 3.8 | ordinary | na | none | 9/16 | 0.56 |
| certainty_to_emdash | Qwen 3.8 | ordinary | permitted | +0.00 | 10/16 | 0.62 |
| certainty_to_emdash | Qwen 3.8 | ordinary | permitted | +0.05 | 8/16 | 0.50 |
| certainty_to_emdash | Qwen 3.8 | ordinary | permitted | +0.50 | 9/16 | 0.56 |
| emdash_to_certainty | Qwen 3.5 | episode | forbidden | +0.00 | 7/16 | 0.44 |
| emdash_to_certainty | Qwen 3.5 | episode | forbidden | +0.05 | 9/16 | 0.56 |
| emdash_to_certainty | Qwen 3.5 | episode | forbidden | +0.50 | 6/16 | 0.38 |
| emdash_to_certainty | Qwen 3.5 | episode | na | none | 9/16 | 0.56 |
| emdash_to_certainty | Qwen 3.5 | episode | permitted | +0.00 | 4/16 | 0.25 |
| emdash_to_certainty | Qwen 3.5 | episode | permitted | +0.05 | 7/16 | 0.44 |
| emdash_to_certainty | Qwen 3.5 | episode | permitted | +0.50 | 7/16 | 0.44 |
| emdash_to_certainty | Qwen 3.5 | ordinary | forbidden | +0.00 | 6/16 | 0.38 |
| emdash_to_certainty | Qwen 3.5 | ordinary | forbidden | +0.05 | 8/16 | 0.50 |
| emdash_to_certainty | Qwen 3.5 | ordinary | forbidden | +0.50 | 6/16 | 0.38 |
| emdash_to_certainty | Qwen 3.5 | ordinary | na | none | 9/16 | 0.56 |
| emdash_to_certainty | Qwen 3.5 | ordinary | permitted | +0.00 | 6/16 | 0.38 |
| emdash_to_certainty | Qwen 3.5 | ordinary | permitted | +0.05 | 7/16 | 0.44 |
| emdash_to_certainty | Qwen 3.5 | ordinary | permitted | +0.50 | 6/16 | 0.38 |
| emdash_to_certainty | Qwen 3.8 | episode | forbidden | +0.00 | 4/16 | 0.25 |
| emdash_to_certainty | Qwen 3.8 | episode | forbidden | +0.05 | 5/16 | 0.31 |
| emdash_to_certainty | Qwen 3.8 | episode | forbidden | +0.50 | 8/16 | 0.50 |
| emdash_to_certainty | Qwen 3.8 | episode | na | none | 9/16 | 0.56 |
| emdash_to_certainty | Qwen 3.8 | episode | permitted | +0.00 | 5/16 | 0.31 |
| emdash_to_certainty | Qwen 3.8 | episode | permitted | +0.05 | 5/16 | 0.31 |
| emdash_to_certainty | Qwen 3.8 | episode | permitted | +0.50 | 4/16 | 0.25 |
| emdash_to_certainty | Qwen 3.8 | ordinary | forbidden | +0.00 | 5/16 | 0.31 |
| emdash_to_certainty | Qwen 3.8 | ordinary | forbidden | +0.05 | 7/16 | 0.44 |
| emdash_to_certainty | Qwen 3.8 | ordinary | forbidden | +0.50 | 5/16 | 0.31 |
| emdash_to_certainty | Qwen 3.8 | ordinary | na | none | 7/16 | 0.44 |
| emdash_to_certainty | Qwen 3.8 | ordinary | permitted | +0.00 | 4/16 | 0.25 |
| emdash_to_certainty | Qwen 3.8 | ordinary | permitted | +0.05 | 5/16 | 0.31 |
| emdash_to_certainty | Qwen 3.8 | ordinary | permitted | +0.50 | 4/16 | 0.25 |
| limitation_to_title | Qwen 3.5 | episode | forbidden | +0.00 | 16/16 | 1.00 |
| limitation_to_title | Qwen 3.5 | episode | forbidden | +0.05 | 16/16 | 1.00 |
| limitation_to_title | Qwen 3.5 | episode | forbidden | +0.50 | 15/16 | 0.94 |
| limitation_to_title | Qwen 3.5 | episode | na | none | 16/16 | 1.00 |
| limitation_to_title | Qwen 3.5 | episode | permitted | +0.00 | 15/16 | 0.94 |
| limitation_to_title | Qwen 3.5 | episode | permitted | +0.05 | 15/16 | 0.94 |
| limitation_to_title | Qwen 3.5 | episode | permitted | +0.50 | 16/16 | 1.00 |
| limitation_to_title | Qwen 3.5 | ordinary | forbidden | +0.00 | 15/16 | 0.94 |
| limitation_to_title | Qwen 3.5 | ordinary | forbidden | +0.05 | 16/16 | 1.00 |
| limitation_to_title | Qwen 3.5 | ordinary | forbidden | +0.50 | 16/16 | 1.00 |
| limitation_to_title | Qwen 3.5 | ordinary | na | none | 16/16 | 1.00 |
| limitation_to_title | Qwen 3.5 | ordinary | permitted | +0.00 | 15/16 | 0.94 |
| limitation_to_title | Qwen 3.5 | ordinary | permitted | +0.05 | 16/16 | 1.00 |
| limitation_to_title | Qwen 3.5 | ordinary | permitted | +0.50 | 15/16 | 0.94 |
| limitation_to_title | Qwen 3.8 | episode | forbidden | +0.00 | 15/16 | 0.94 |
| limitation_to_title | Qwen 3.8 | episode | forbidden | +0.05 | 15/16 | 0.94 |
| limitation_to_title | Qwen 3.8 | episode | forbidden | +0.50 | 16/16 | 1.00 |
| limitation_to_title | Qwen 3.8 | episode | na | none | 14/16 | 0.88 |
| limitation_to_title | Qwen 3.8 | episode | permitted | +0.00 | 16/16 | 1.00 |
| limitation_to_title | Qwen 3.8 | episode | permitted | +0.05 | 16/16 | 1.00 |
| limitation_to_title | Qwen 3.8 | episode | permitted | +0.50 | 16/16 | 1.00 |
| limitation_to_title | Qwen 3.8 | ordinary | forbidden | +0.00 | 16/16 | 1.00 |
| limitation_to_title | Qwen 3.8 | ordinary | forbidden | +0.05 | 15/16 | 0.94 |
| limitation_to_title | Qwen 3.8 | ordinary | forbidden | +0.50 | 15/16 | 0.94 |
| limitation_to_title | Qwen 3.8 | ordinary | na | none | 15/16 | 0.94 |
| limitation_to_title | Qwen 3.8 | ordinary | permitted | +0.00 | 15/16 | 0.94 |
| limitation_to_title | Qwen 3.8 | ordinary | permitted | +0.05 | 16/16 | 1.00 |
| limitation_to_title | Qwen 3.8 | ordinary | permitted | +0.50 | 16/16 | 1.00 |
| send_to_signoff | Qwen 3.5 | episode | forbidden | +0.00 | 16/16 | 1.00 |
| send_to_signoff | Qwen 3.5 | episode | forbidden | +0.05 | 16/16 | 1.00 |
| send_to_signoff | Qwen 3.5 | episode | forbidden | +0.50 | 16/16 | 1.00 |
| send_to_signoff | Qwen 3.5 | episode | na | none | 16/16 | 1.00 |
| send_to_signoff | Qwen 3.5 | episode | permitted | +0.00 | 16/16 | 1.00 |
| send_to_signoff | Qwen 3.5 | episode | permitted | +0.05 | 16/16 | 1.00 |
| send_to_signoff | Qwen 3.5 | episode | permitted | +0.50 | 16/16 | 1.00 |
| send_to_signoff | Qwen 3.5 | ordinary | forbidden | +0.00 | 16/16 | 1.00 |
| send_to_signoff | Qwen 3.5 | ordinary | forbidden | +0.05 | 16/16 | 1.00 |
| send_to_signoff | Qwen 3.5 | ordinary | forbidden | +0.50 | 16/16 | 1.00 |
| send_to_signoff | Qwen 3.5 | ordinary | na | none | 16/16 | 1.00 |
| send_to_signoff | Qwen 3.5 | ordinary | permitted | +0.00 | 16/16 | 1.00 |
| send_to_signoff | Qwen 3.5 | ordinary | permitted | +0.05 | 16/16 | 1.00 |
| send_to_signoff | Qwen 3.5 | ordinary | permitted | +0.50 | 16/16 | 1.00 |
| send_to_signoff | Qwen 3.8 | episode | forbidden | +0.00 | 16/16 | 1.00 |
| send_to_signoff | Qwen 3.8 | episode | forbidden | +0.05 | 16/16 | 1.00 |
| send_to_signoff | Qwen 3.8 | episode | forbidden | +0.50 | 16/16 | 1.00 |
| send_to_signoff | Qwen 3.8 | episode | na | none | 16/16 | 1.00 |
| send_to_signoff | Qwen 3.8 | episode | permitted | +0.00 | 16/16 | 1.00 |
| send_to_signoff | Qwen 3.8 | episode | permitted | +0.05 | 16/16 | 1.00 |
| send_to_signoff | Qwen 3.8 | episode | permitted | +0.50 | 16/16 | 1.00 |
| send_to_signoff | Qwen 3.8 | ordinary | forbidden | +0.00 | 16/16 | 1.00 |
| send_to_signoff | Qwen 3.8 | ordinary | forbidden | +0.05 | 16/16 | 1.00 |
| send_to_signoff | Qwen 3.8 | ordinary | forbidden | +0.50 | 16/16 | 1.00 |
| send_to_signoff | Qwen 3.8 | ordinary | na | none | 16/16 | 1.00 |
| send_to_signoff | Qwen 3.8 | ordinary | permitted | +0.00 | 16/16 | 1.00 |
| send_to_signoff | Qwen 3.8 | ordinary | permitted | +0.05 | 16/16 | 1.00 |
| send_to_signoff | Qwen 3.8 | ordinary | permitted | +0.50 | 16/16 | 1.00 |
| signoff_to_send | Qwen 3.5 | episode | forbidden | +0.00 | 16/16 | 1.00 |
| signoff_to_send | Qwen 3.5 | episode | forbidden | +0.05 | 16/16 | 1.00 |
| signoff_to_send | Qwen 3.5 | episode | forbidden | +0.50 | 16/16 | 1.00 |
| signoff_to_send | Qwen 3.5 | episode | na | none | 15/16 | 0.94 |
| signoff_to_send | Qwen 3.5 | episode | permitted | +0.00 | 16/16 | 1.00 |
| signoff_to_send | Qwen 3.5 | episode | permitted | +0.05 | 16/16 | 1.00 |
| signoff_to_send | Qwen 3.5 | episode | permitted | +0.50 | 16/16 | 1.00 |
| signoff_to_send | Qwen 3.5 | ordinary | forbidden | +0.00 | 16/16 | 1.00 |
| signoff_to_send | Qwen 3.5 | ordinary | forbidden | +0.05 | 16/16 | 1.00 |
| signoff_to_send | Qwen 3.5 | ordinary | forbidden | +0.50 | 16/16 | 1.00 |
| signoff_to_send | Qwen 3.5 | ordinary | na | none | 16/16 | 1.00 |
| signoff_to_send | Qwen 3.5 | ordinary | permitted | +0.00 | 16/16 | 1.00 |
| signoff_to_send | Qwen 3.5 | ordinary | permitted | +0.05 | 16/16 | 1.00 |
| signoff_to_send | Qwen 3.5 | ordinary | permitted | +0.50 | 16/16 | 1.00 |
| signoff_to_send | Qwen 3.8 | episode | forbidden | +0.00 | 16/16 | 1.00 |
| signoff_to_send | Qwen 3.8 | episode | forbidden | +0.05 | 16/16 | 1.00 |
| signoff_to_send | Qwen 3.8 | episode | forbidden | +0.50 | 16/16 | 1.00 |
| signoff_to_send | Qwen 3.8 | episode | na | none | 15/16 | 0.94 |
| signoff_to_send | Qwen 3.8 | episode | permitted | +0.00 | 16/16 | 1.00 |
| signoff_to_send | Qwen 3.8 | episode | permitted | +0.05 | 16/16 | 1.00 |
| signoff_to_send | Qwen 3.8 | episode | permitted | +0.50 | 16/16 | 1.00 |
| signoff_to_send | Qwen 3.8 | ordinary | forbidden | +0.00 | 16/16 | 1.00 |
| signoff_to_send | Qwen 3.8 | ordinary | forbidden | +0.05 | 15/16 | 0.94 |
| signoff_to_send | Qwen 3.8 | ordinary | forbidden | +0.50 | 16/16 | 1.00 |
| signoff_to_send | Qwen 3.8 | ordinary | na | none | 15/16 | 0.94 |
| signoff_to_send | Qwen 3.8 | ordinary | permitted | +0.00 | 16/16 | 1.00 |
| signoff_to_send | Qwen 3.8 | ordinary | permitted | +0.05 | 16/16 | 1.00 |
| signoff_to_send | Qwen 3.8 | ordinary | permitted | +0.50 | 16/16 | 1.00 |
| title_to_limitation | Qwen 3.5 | episode | forbidden | +0.00 | 15/16 | 0.94 |
| title_to_limitation | Qwen 3.5 | episode | forbidden | +0.05 | 15/16 | 0.94 |
| title_to_limitation | Qwen 3.5 | episode | forbidden | +0.50 | 16/16 | 1.00 |
| title_to_limitation | Qwen 3.5 | episode | na | none | 15/16 | 0.94 |
| title_to_limitation | Qwen 3.5 | episode | permitted | +0.00 | 15/16 | 0.94 |
| title_to_limitation | Qwen 3.5 | episode | permitted | +0.05 | 16/16 | 1.00 |
| title_to_limitation | Qwen 3.5 | episode | permitted | +0.50 | 15/16 | 0.94 |
| title_to_limitation | Qwen 3.5 | ordinary | forbidden | +0.00 | 15/16 | 0.94 |
| title_to_limitation | Qwen 3.5 | ordinary | forbidden | +0.05 | 15/16 | 0.94 |
| title_to_limitation | Qwen 3.5 | ordinary | forbidden | +0.50 | 16/16 | 1.00 |
| title_to_limitation | Qwen 3.5 | ordinary | na | none | 15/16 | 0.94 |
| title_to_limitation | Qwen 3.5 | ordinary | permitted | +0.00 | 14/16 | 0.88 |
| title_to_limitation | Qwen 3.5 | ordinary | permitted | +0.05 | 16/16 | 1.00 |
| title_to_limitation | Qwen 3.5 | ordinary | permitted | +0.50 | 16/16 | 1.00 |
| title_to_limitation | Qwen 3.8 | episode | forbidden | +0.00 | 14/16 | 0.88 |
| title_to_limitation | Qwen 3.8 | episode | forbidden | +0.05 | 16/16 | 1.00 |
| title_to_limitation | Qwen 3.8 | episode | forbidden | +0.50 | 14/16 | 0.88 |
| title_to_limitation | Qwen 3.8 | episode | na | none | 13/16 | 0.81 |
| title_to_limitation | Qwen 3.8 | episode | permitted | +0.00 | 14/16 | 0.88 |
| title_to_limitation | Qwen 3.8 | episode | permitted | +0.05 | 14/16 | 0.88 |
| title_to_limitation | Qwen 3.8 | episode | permitted | +0.50 | 14/16 | 0.88 |
| title_to_limitation | Qwen 3.8 | ordinary | forbidden | +0.00 | 14/16 | 0.88 |
| title_to_limitation | Qwen 3.8 | ordinary | forbidden | +0.05 | 14/16 | 0.88 |
| title_to_limitation | Qwen 3.8 | ordinary | forbidden | +0.50 | 14/16 | 0.88 |
| title_to_limitation | Qwen 3.8 | ordinary | na | none | 13/16 | 0.81 |
| title_to_limitation | Qwen 3.8 | ordinary | permitted | +0.00 | 13/16 | 0.81 |
| title_to_limitation | Qwen 3.8 | ordinary | permitted | +0.05 | 14/16 | 0.88 |
| title_to_limitation | Qwen 3.8 | ordinary | permitted | +0.50 | 13/16 | 0.81 |

## Judge

```
{
 "judge_model": "openrouter/anthropic/claude-sonnet-5.5",
 "judge_version": "overnight-judge-v1 (2026-10-29)",
 "ledger": {
  "calls": 916,
  "input_tokens": 794308,
  "output_tokens": 95782,
  "cost_usd": 2.546436
 },
 "labels_by_behaviour": {
  "certainty": {
   "complies": 895
  },
  "signoff": {
   "violates": 8
  },
  "title": {
   "complies": 2
  },
  "limitation": {
   "violates": 4,
   "complies": 1
  }
 },
 "rule_clear_vs_judge": {
  "disagree": 1,
  "agree": 4
 },
 "n_judged": 910,
 "n_judge_failed": 1,
 "n_not_judged": 1,
 "redacted_items": 11
}
```
