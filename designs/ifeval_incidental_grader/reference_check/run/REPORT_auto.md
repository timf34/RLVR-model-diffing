# 10A reference check: auto tables

## send

| impl | score | model | k/n valid | rate | Wilson 95% | non-valid | old study (bundle) |
|---|---|---|---|---|---|---|---|
| old | tied | Qwen 3.5 | 0/16 | 0.00 | 0.00–0.19 | 0 | all 0/72; email 0/12 |
| old | tied | Qwen 3.8 | 0/16 | 0.00 | 0.00–0.19 | 0 | all 0/72; email 0/12 |
| old | p050 | Qwen 3.5 | 2/16 | 0.12 | 0.03–0.36 | 0 | all 9/72; email 0/12 |
| old | p050 | Qwen 3.8 | 10/16 | 0.62 | 0.39–0.82 | 0 | all 53/72; email 7/12 |
| new | tied | Qwen 3.5 | 0/16 | 0.00 | 0.00–0.19 | 0 | all 0/72; email 0/12 |
| new | tied | Qwen 3.8 | 0/16 | 0.00 | 0.00–0.19 | 0 | all 0/72; email 0/12 |
| new | p050 | Qwen 3.5 | 0/16 | 0.00 | 0.00–0.19 | 0 | all 9/72; email 0/12 |
| new | p050 | Qwen 3.8 | 0/16 | 0.00 | 0.00–0.19 | 0 | all 53/72; email 7/12 |

| impl | model | +0.50 − tied (block mean) | block bootstrap 95% | blocks |
|---|---|---|---|---|
| old | Qwen 3.5 | +0.125 | +0.000 to +0.312 | 16 |
| old | Qwen 3.8 | +0.625 | +0.375 to +0.875 | 16 |
| new | Qwen 3.5 | +0.000 | +0.000 to +0.000 (all zero; one-sided 95% bound 0.17) | 16 |
| new | Qwen 3.8 | +0.000 | +0.000 to +0.000 (all zero; one-sided 95% bound 0.17) | 16 |

| model | (new − old) difference-in-differences | block bootstrap 95% | blocks |
|---|---|---|---|
| Qwen 3.5 | -0.125 | -0.312 to +0.000 | 16 |
| Qwen 3.8 | -0.625 | -0.875 to -0.375 | 16 |

Diagnostics: `{"text_form_tool_calls": 0, "extra_packet_calls": 0, "old_first_call_checked": 64, "retried_keys": 0, "read_inbox": {"old": 64, "new": 62}, "task_done_given_acted": {"old": [12, 12], "new": [0, 0]}, "saved_draft": {"old": 52, "new": 64}}`
Cost: `{"Qwen 3.5": 0.21082178000000001, "Qwen 3.8": 0.067749079, "attempts": 128}`

## fmt

| impl | score | model | k/n valid | rate | Wilson 95% | non-valid | old study (bundle) |
|---|---|---|---|---|---|---|---|
| old | tied | Qwen 3.5 | 0/16 | 0.00 | 0.00–0.19 | 0 | all 0/24 |
| old | tied | Qwen 3.8 | 0/16 | 0.00 | 0.00–0.19 | 0 | all 0/24 |
| old | p050 | Qwen 3.5 | 0/15 | 0.00 | 0.00–0.20 | {'empty': 1} | all 0/24 |
| old | p050 | Qwen 3.8 | 9/16 | 0.56 | 0.33–0.77 | 0 | all 14/24 |
| new | tied | Qwen 3.5 | 0/16 | 0.00 | 0.00–0.19 | 0 | all 0/24 |
| new | tied | Qwen 3.8 | 0/16 | 0.00 | 0.00–0.19 | 0 | all 0/24 |
| new | p050 | Qwen 3.5 | 0/16 | 0.00 | 0.00–0.19 | 0 | all 0/24 |
| new | p050 | Qwen 3.8 | 0/16 | 0.00 | 0.00–0.19 | 0 | all 14/24 |

| impl | model | +0.50 − tied (block mean) | block bootstrap 95% | blocks |
|---|---|---|---|---|
| old | Qwen 3.5 | +0.000 | +0.000 to +0.000 (all zero; one-sided 95% bound 0.18) | 15 |
| old | Qwen 3.8 | +0.562 | +0.312 to +0.812 | 16 |
| new | Qwen 3.5 | +0.000 | +0.000 to +0.000 (all zero; one-sided 95% bound 0.17) | 16 |
| new | Qwen 3.8 | +0.000 | +0.000 to +0.000 (all zero; one-sided 95% bound 0.17) | 16 |

| model | (new − old) difference-in-differences | block bootstrap 95% | blocks |
|---|---|---|---|
| Qwen 3.5 | +0.000 | +0.000 to +0.000 | 15 |
| Qwen 3.8 | -0.562 | -0.812 to -0.312 | 16 |

Diagnostics: `{"text_form_tool_calls": 0, "extra_packet_calls": 0, "old_first_call_checked": 0, "retried_keys": 0, "facts_ok": {"old": [53, 63], "new": [55, 64]}, "violates_any": {"old|tied|Qwen 3.5": 0, "old|tied|Qwen 3.8": 0, "old|p050|Qwen 3.5": 0, "old|p050|Qwen 3.8": 9, "new|tied|Qwen 3.5": 0, "new|tied|Qwen 3.8": 0, "new|p050|Qwen 3.5": 0, "new|p050|Qwen 3.8": 0}}`
Cost: `{"Qwen 3.5": 0.23938512, "Qwen 3.8": 0.06681033, "attempts": 128}`

**Total cost: $0.585** (usage × listed prices {'Qwen 3.5': (0.26, 2.6), 'Qwen 3.8': (0.039, 1.25)})
