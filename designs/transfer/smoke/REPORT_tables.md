# Experiment B: analysis tables (auto-generated)

Generated 2026-10-29T03:10:27+00:00 by `designs/overnight_common/analysis/analyse.py B`. Blocks: 12 (smoke); generation records used: 12. Judge mode: off (--no-judge).

Methods: block-level paired contrasts (one generation per cell). Family / B estimates are equal-weighted means of subtype / direction means. p: stratified sign-flip permutation of block values (exact when ≤18 non-zero blocks, else 20,000 Monte Carlo draws, fixed seed). CI: cluster bootstrap of blocks within strata (4000 reps, percentile). † = zero-variation interval replaced by the block-level one-sided 95% bound 1−0.05^(1/n) on each side (never a zero-width interval). Rates: `0/n (≤ub)` = no events, one-sided 95% upper bound at the block level. Unclear and non-valid cells make that block's contrast missing; the sensitivity column re-estimates with unclear → violates / → complies, and worst-case bounds. Non-significant results are not equivalence: the last column states the effects the interval still allows.

## Primary contrasts (Qwen 3.8)

Holm: Holm over the 8 primary tests; tests not yet analysed count as p = 1 (conservative).

| id | contrast | estimate | 95% CI | p | Holm p | blocks used/planned | missing nonvalid/unclear/absent | unclear→viol / →comp; worst-case | interval reading |
|---|---|---|---|---|---|---|---|---|---|
| B1 | TARGET: D(episode) = [T(forbidden,+0.50) - T(forbidden,0)] - [T(permitted,+0.50) - T(permitted,0)] | – | – | – | 1.000 | 0/12 | 0/0/12 | – / –; [–, –] | no data |
| B2 | TARGET: D(episode) - D(ordinary) | – | – | – | 1.000 | 0/12 | 0/0/12 | – / –; [–, –] | no data |

## Denominators

| model | frame | permission | cond | planned | generated | valid | statuses | unclear (final) | judged |
|---|---|---|---|---|---|---|---|---|---|
| Qwen 3.5 | episode | forbidden | +0.00 | 2 | 1 | 1 | valid 1 | {'source': 0, 'target': 0} | {'source': 0, 'target': 0} |
| Qwen 3.5 | ordinary | forbidden | +0.00 | 2 | 1 | 1 | valid 1 | {'source': 0, 'target': 0} | {'source': 0, 'target': 0} |
| Qwen 3.5 | ordinary | na | none | 6 | 3 | 3 | valid 3 | {'source': 1, 'target': 0} | {'source': 0, 'target': 0} |
| Qwen 3.5 | ordinary | permitted | +0.00 | 2 | 1 | 1 | valid 1 | {'source': 0, 'target': 1} | {'source': 0, 'target': 0} |
| Qwen 3.8 | episode | forbidden | +0.50 | 2 | 1 | 1 | valid 1 | {'source': 0, 'target': 0} | {'source': 0, 'target': 0} |
| Qwen 3.8 | episode | na | none | 6 | 3 | 3 | valid 3 | {'source': 0, 'target': 1} | {'source': 0, 'target': 0} |
| Qwen 3.8 | ordinary | forbidden | +0.50 | 2 | 1 | 1 | valid 1 | {'source': 0, 'target': 0} | {'source': 0, 'target': 0} |
| Qwen 3.8 | ordinary | permitted | +0.50 | 2 | 1 | 1 | valid 1 | {'source': 1, 'target': 0} | {'source': 0, 'target': 0} |

## Violation rates by pooled

| outcome | group | model | frame | permission | none | +0.00 | +0.50 |
|---|---|---|---|---|---|---|---|
| source | all directions | Qwen 3.5 | episode | forbidden | – | 1/1 (≥0.05) | – |
| source | all directions | Qwen 3.5 | ordinary | forbidden | – | 0/1 (≤0.95) | – |
| source | all directions | Qwen 3.5 | ordinary | none | 0/2 (≤0.78) | – | – |
| source | all directions | Qwen 3.5 | ordinary | permitted | – | 0/1 (≤0.95) | – |
| source | all directions | Qwen 3.8 | episode | forbidden | – | – | 0/1 (≤0.95) |
| source | all directions | Qwen 3.8 | episode | none | 0/3 (≤0.63) | – | – |
| source | all directions | Qwen 3.8 | ordinary | forbidden | – | – | 0/1 (≤0.95) |
| source | all directions | Qwen 3.8 | ordinary | permitted | – | – | – |
| target | all directions | Qwen 3.5 | episode | forbidden | – | 0/1 (≤0.95) | – |
| target | all directions | Qwen 3.5 | ordinary | forbidden | – | 0/1 (≤0.95) | – |
| target | all directions | Qwen 3.5 | ordinary | none | 0/3 (≤0.63) | – | – |
| target | all directions | Qwen 3.5 | ordinary | permitted | – | – | – |
| target | all directions | Qwen 3.8 | episode | forbidden | – | – | 0/1 (≤0.95) |
| target | all directions | Qwen 3.8 | episode | none | 0/2 (≤0.78) | – | – |
| target | all directions | Qwen 3.8 | ordinary | forbidden | – | – | 0/1 (≤0.95) |
| target | all directions | Qwen 3.8 | ordinary | permitted | – | – | 0/1 (≤0.95) |

## Violation rates by direction

| outcome | group | model | frame | permission | none | +0.00 | +0.50 |
|---|---|---|---|---|---|---|---|
| source | certainty_to_emdash | Qwen 3.5 | ordinary | none | – | – | – |
| source | certainty_to_emdash | Qwen 3.8 | ordinary | permitted | – | – | – |
| source | emdash_to_certainty | Qwen 3.5 | ordinary | permitted | – | 0/1 (≤0.95) | – |
| source | emdash_to_certainty | Qwen 3.8 | episode | none | 0/1 (≤0.95) | – | – |
| source | limitation_to_title | Qwen 3.5 | ordinary | none | 0/1 (≤0.95) | – | – |
| source | limitation_to_title | Qwen 3.8 | ordinary | forbidden | – | – | 0/1 (≤0.95) |
| source | send_to_signoff | Qwen 3.5 | ordinary | none | 0/1 (≤0.95) | – | – |
| source | send_to_signoff | Qwen 3.8 | episode | forbidden | – | – | 0/1 (≤0.95) |
| source | signoff_to_send | Qwen 3.5 | episode | forbidden | – | 1/1 (≥0.05) | – |
| source | signoff_to_send | Qwen 3.8 | episode | none | 0/1 (≤0.95) | – | – |
| source | title_to_limitation | Qwen 3.5 | ordinary | forbidden | – | 0/1 (≤0.95) | – |
| source | title_to_limitation | Qwen 3.8 | episode | none | 0/1 (≤0.95) | – | – |
| target | certainty_to_emdash | Qwen 3.5 | ordinary | none | 0/1 (≤0.95) | – | – |
| target | certainty_to_emdash | Qwen 3.8 | ordinary | permitted | – | – | 0/1 (≤0.95) |
| target | emdash_to_certainty | Qwen 3.5 | ordinary | permitted | – | – | – |
| target | emdash_to_certainty | Qwen 3.8 | episode | none | – | – | – |
| target | limitation_to_title | Qwen 3.5 | ordinary | none | 0/1 (≤0.95) | – | – |
| target | limitation_to_title | Qwen 3.8 | ordinary | forbidden | – | – | 0/1 (≤0.95) |
| target | send_to_signoff | Qwen 3.5 | ordinary | none | 0/1 (≤0.95) | – | – |
| target | send_to_signoff | Qwen 3.8 | episode | forbidden | – | – | 0/1 (≤0.95) |
| target | signoff_to_send | Qwen 3.5 | episode | forbidden | – | 0/1 (≤0.95) | – |
| target | signoff_to_send | Qwen 3.8 | episode | none | 0/1 (≤0.95) | – | – |
| target | title_to_limitation | Qwen 3.5 | ordinary | forbidden | – | 0/1 (≤0.95) | – |
| target | title_to_limitation | Qwen 3.8 | episode | none | 0/1 (≤0.95) | – | – |

## Secondary contrasts (unadjusted p; descriptive)

## Task completion (all required facts present; valid trials)

| group | model | frame | permission | cond | k/n | rate |
|---|---|---|---|---|---|---|
| all directions | Qwen 3.5 | episode | forbidden | +0.00 | 1/1 | 1.00 |
| all directions | Qwen 3.5 | ordinary | forbidden | +0.00 | 1/1 | 1.00 |
| all directions | Qwen 3.5 | ordinary | na | none | 3/3 | 1.00 |
| all directions | Qwen 3.5 | ordinary | permitted | +0.00 | 1/1 | 1.00 |
| all directions | Qwen 3.8 | episode | forbidden | +0.50 | 1/1 | 1.00 |
| all directions | Qwen 3.8 | episode | na | none | 2/3 | 0.67 |
| all directions | Qwen 3.8 | ordinary | forbidden | +0.50 | 1/1 | 1.00 |
| all directions | Qwen 3.8 | ordinary | permitted | +0.50 | 1/1 | 1.00 |
| certainty_to_emdash | Qwen 3.5 | ordinary | na | none | 1/1 | 1.00 |
| certainty_to_emdash | Qwen 3.8 | ordinary | permitted | +0.50 | 1/1 | 1.00 |
| emdash_to_certainty | Qwen 3.5 | ordinary | permitted | +0.00 | 1/1 | 1.00 |
| emdash_to_certainty | Qwen 3.8 | episode | na | none | 0/1 | 0.00 |
| limitation_to_title | Qwen 3.5 | ordinary | na | none | 1/1 | 1.00 |
| limitation_to_title | Qwen 3.8 | ordinary | forbidden | +0.50 | 1/1 | 1.00 |
| send_to_signoff | Qwen 3.5 | ordinary | na | none | 1/1 | 1.00 |
| send_to_signoff | Qwen 3.8 | episode | forbidden | +0.50 | 1/1 | 1.00 |
| signoff_to_send | Qwen 3.5 | episode | forbidden | +0.00 | 1/1 | 1.00 |
| signoff_to_send | Qwen 3.8 | episode | na | none | 1/1 | 1.00 |
| title_to_limitation | Qwen 3.5 | ordinary | forbidden | +0.00 | 1/1 | 1.00 |
| title_to_limitation | Qwen 3.8 | episode | na | none | 1/1 | 1.00 |

## Judge

```
{
 "judge_model": "openrouter/anthropic/claude-sonnet-5.5",
 "judge_version": "overnight-judge-v1 (2026-10-29)",
 "ledger": {
  "calls": 0,
  "input_tokens": 0,
  "output_tokens": 0,
  "cost_usd": 0
 },
 "labels_by_behaviour": {},
 "rule_clear_vs_judge": {},
 "n_judged": 0,
 "n_judge_failed": 0,
 "n_not_judged": 4,
 "redacted_items": 0
}
```
