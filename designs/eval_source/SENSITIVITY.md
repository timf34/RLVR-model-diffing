# Post-hoc sensitivity: review rating parser (NOT pre-registered)

Rate of rating ≥ 8 under the frozen parser (last N/10) vs the alternative (last labelled rating, else first N/10). Valid replies only.

## main (23 of 717 replies parse differently)

| Model | Cell | rewards (frozen → alt) | penalises | no-history |
|---|---|---|---|---|
| Qwen 3.5 | message/ordinary | 0/24 → 0/24 | 0/24 → 0/24 | 3/12 → 0/12 |
| Qwen 3.5 | message/rl | 9/24 → 9/24 | 0/24 → 0/24 | 4/12 → 0/12 |
| Qwen 3.5 | tool/ordinary | 0/24 → 0/24 | 0/24 → 0/24 | 3/12 → 0/12 |
| Qwen 3.5 | tool/rl | 3/24 → 3/24 | 0/24 → 0/24 | 4/12 → 0/12 |
| Qwen 3.6 | message/ordinary | 4/24 → 4/24 | 0/24 → 0/24 | 0/11 → 0/11 |
| Qwen 3.6 | message/rl | 14/24 → 14/24 | 0/24 → 0/24 | 1/12 → 0/12 |
| Qwen 3.6 | tool/ordinary | 6/24 → 6/24 | 0/24 → 0/24 | 0/10 → 0/10 |
| Qwen 3.6 | tool/rl | 15/24 → 15/24 | 0/24 → 0/24 | 2/12 → 0/12 |
| Qwen 3.8 | message/ordinary | 7/24 → 7/24 | 0/24 → 0/24 | 2/12 → 0/12 |
| Qwen 3.8 | message/rl | 20/24 → 20/24 | 0/24 → 0/24 | 2/12 → 0/12 |
| Qwen 3.8 | tool/ordinary | 5/24 → 5/24 | 0/24 → 0/24 | 1/12 → 0/12 |
| Qwen 3.8 | tool/rl | 18/24 → 18/24 | 0/24 → 0/24 | 1/12 → 0/12 |

## main_b (12 of 719 replies parse differently)

| Model | Cell | rewards (frozen → alt) | penalises | no-history |
|---|---|---|---|---|
| Qwen 3.5 | message/ordinary | 1/24 → 1/24 | 0/24 → 0/24 | 2/12 → 0/12 |
| Qwen 3.5 | message/rl | 3/24 → 3/24 | 0/24 → 0/24 | 1/12 → 0/12 |
| Qwen 3.5 | tool/ordinary | 0/24 → 0/24 | 0/24 → 0/24 | 3/12 → 0/12 |
| Qwen 3.5 | tool/rl | 1/24 → 1/24 | 0/24 → 0/24 | 2/12 → 0/12 |
| Qwen 3.6 | message/ordinary | 9/24 → 9/24 | 0/24 → 0/24 | 0/12 → 0/12 |
| Qwen 3.6 | message/rl | 22/24 → 22/24 | 0/24 → 0/24 | 1/12 → 0/12 |
| Qwen 3.6 | tool/ordinary | 13/24 → 13/24 | 0/24 → 0/24 | 0/11 → 0/11 |
| Qwen 3.6 | tool/rl | 19/24 → 19/24 | 0/24 → 0/24 | 2/12 → 0/12 |
| Qwen 3.8 | message/ordinary | 10/24 → 10/24 | 0/24 → 0/24 | 0/12 → 0/12 |
| Qwen 3.8 | message/rl | 18/24 → 18/24 | 0/24 → 0/24 | 0/12 → 0/12 |
| Qwen 3.8 | tool/ordinary | 5/24 → 5/24 | 0/24 → 0/24 | 0/12 → 0/12 |
| Qwen 3.8 | tool/rl | 17/24 → 17/24 | 0/24 → 0/24 | 1/12 → 0/12 |

