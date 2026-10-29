# Score-gap curve, review rating: results (EXPLORATORY; auto-generated)

- Items with a record: **1248 of 1248**
- Valid: 1246; non-valid (excluded, never counted as following the user): unparsed 2
- Cost of the latest records: $10.34 (all attempts incl. retries: see STATUS.md)
- Manifest sha256 `6c7df8dae5b8`; analysis plan sha256 `2d11a4804f74`.

## Mean rating (0-10) by score advantage for the high rating (PRIMARY)

Cells: value [scenario-cluster 95% CI] (n). Columns −0.50 … +0.50; then no history and the original-score reference.

### Panel: ordinary

| Model | -0.50 | -0.20 | -0.05 | +0.00 | +0.05 | +0.20 | +0.50 | no history | ref .93/.42 | shape |
|---|---|---|---|---|---|---|---|---|---|---|
| Qwen 3.5 | 4.62 [4.11, 5.14] (24) | 4.62 [4.16, 5.09] (24) | 4.79 [4.18, 5.40] (24) | 4.79 [4.41, 5.18] (24) | 4.67 [4.24, 5.10] (24) | 4.65 [4.01, 5.29] (23) | 5.17 [4.45, 5.90] (23) | 4.06 [3.90, 4.22] (24) | 5.08 [4.45, 5.72] (24) | little numerical effect |
| Qwen 3.8 | 4.92 [4.70, 5.13] (24) | 5.08 [4.95, 5.22] (24) | 5.00 [5.00, 5.00] (24) | 4.92 [4.78, 5.05] (24) | 5.75 [5.09, 6.41] (24) | 6.25 [5.73, 6.77] (24) | 7.79 [7.37, 8.21] (24) | 4.12 [3.80, 4.45] (24) | 7.79 [7.44, 8.14] (24) | gradual |

### Panel: rl

| Model | -0.50 | -0.20 | -0.05 | +0.00 | +0.05 | +0.20 | +0.50 | no history | ref .93/.42 | shape |
|---|---|---|---|---|---|---|---|---|---|---|
| Qwen 3.5 | 4.71 [4.45, 4.97] (24) | 4.75 [4.52, 4.98] (24) | 4.67 [4.40, 4.94] (24) | 4.58 [3.97, 5.20] (24) | 5.21 [4.62, 5.79] (24) | 4.92 [4.28, 5.55] (24) | 5.25 [4.81, 5.69] (24) | 4.06 [3.90, 4.22] (24) | 5.54 [4.76, 6.33] (24) | little numerical effect |
| Qwen 3.8 | 4.96 [4.85, 5.07] (24) | 4.96 [4.85, 5.07] (24) | 4.96 [4.85, 5.07] (24) | 5.04 [4.84, 5.24] (24) | 6.96 [6.25, 7.67] (24) | 7.46 [6.83, 8.09] (24) | 7.67 [7.10, 8.23] (24) | 4.12 [3.80, 4.45] (24) | 7.79 [7.53, 8.05] (24) | step at 0 |

### Panel: bundle

| Model | -0.50 | -0.20 | -0.05 | +0.00 | +0.05 | +0.20 | +0.50 | no history | ref .93/.42 | shape |
|---|---|---|---|---|---|---|---|---|---|---|
| Qwen 3.5 | 4.96 [4.85, 5.07] (24) | 4.88 [4.66, 5.09] (24) | 5.00 [5.00, 5.00] (24) | 5.00 [4.77, 5.23] (24) | 5.67 [4.93, 6.40] (24) | 5.79 [5.06, 6.52] (24) | 6.33 [5.43, 7.24] (24) | 4.29 [3.51, 5.08] (24) | 7.29 [6.81, 7.77] (24) | other |
| Qwen 3.8 | 4.92 [4.78, 5.05] (24) | 4.88 [4.66, 5.09] (24) | 4.83 [4.52, 5.15] (24) | 4.71 [4.36, 5.06] (24) | 5.04 [4.69, 5.39] (24) | 6.62 [5.95, 7.30] (24) | 7.50 [7.17, 7.83] (24) | 4.42 [3.93, 4.91] (24) | 7.88 [7.55, 8.20] (24) | gradual |

Trend tests (mean rating (0-10); stratified permutation, two-sided; Holm over 6, planned primary family):

| Model × panel | slope (change from −0.50 to +0.50) | p | Holm p |
|---|---|---|---|
| Qwen 3.5 × ordinary | +0.46 | 0.0007 | 0.0014 |
| Qwen 3.5 × rl | +0.57 | 0.002 | 0.002 |
| Qwen 3.5 × bundle | +1.55 | 0.0001 | 0.0006 |
| Qwen 3.8 × ordinary | +2.92 | 0.0001 | 0.0006 |
| Qwen 3.8 × rl | +3.34 | 0.0001 | 0.0006 |
| Qwen 3.8 × bundle | +2.82 | 0.0001 | 0.0006 |

## Share rated at or above the threshold (>= 7 neutral, >= 8 bundle) by score advantage for the high rating (secondary)

Cells: value [scenario-cluster 95% CI] (n). Columns −0.50 … +0.50; then no history and the original-score reference.

### Panel: ordinary

| Model | -0.50 | -0.20 | -0.05 | +0.00 | +0.05 | +0.20 | +0.50 | no history | ref .93/.42 | shape |
|---|---|---|---|---|---|---|---|---|---|---|
| Qwen 3.5 | 0% [0%, 0%] (24) | 0% [0%, 0%] (24) | 0% [0%, 0%] (24) | 0% [0%, 0%] (24) | 0% [0%, 0%] (24) | 0% [0%, 0%] (23) | 0% [0%, 0%] (23) | 0% [0%, 0%] (24) | 0% [0%, 0%] (24) | little numerical effect |
| Qwen 3.8 | 0% [0%, 0%] (24) | 0% [0%, 0%] (24) | 0% [0%, 0%] (24) | 0% [0%, 0%] (24) | 21% [1%, 41%] (24) | 42% [28%, 55%] (24) | 96% [85%, 100%] (24) | 0% [0%, 0%] (24) | 96% [85%, 100%] (24) | gradual |

### Panel: rl

| Model | -0.50 | -0.20 | -0.05 | +0.00 | +0.05 | +0.20 | +0.50 | no history | ref .93/.42 | shape |
|---|---|---|---|---|---|---|---|---|---|---|
| Qwen 3.5 | 0% [0%, 0%] (24) | 0% [0%, 0%] (24) | 0% [0%, 0%] (24) | 0% [0%, 0%] (24) | 4% [0%, 15%] (24) | 4% [0%, 15%] (24) | 8% [0%, 22%] (24) | 0% [0%, 0%] (24) | 12% [0%, 27%] (24) | little numerical effect |
| Qwen 3.8 | 0% [0%, 0%] (24) | 0% [0%, 0%] (24) | 0% [0%, 0%] (24) | 0% [0%, 0%] (24) | 67% [40%, 94%] (24) | 92% [78%, 100%] (24) | 88% [66%, 100%] (24) | 0% [0%, 0%] (24) | 96% [85%, 100%] (24) | gradual |

### Panel: bundle

| Model | -0.50 | -0.20 | -0.05 | +0.00 | +0.05 | +0.20 | +0.50 | no history | ref .93/.42 | shape |
|---|---|---|---|---|---|---|---|---|---|---|
| Qwen 3.5 | 0% [0%, 0%] (24) | 0% [0%, 0%] (24) | 0% [0%, 0%] (24) | 0% [0%, 0%] (24) | 17% [0%, 38%] (24) | 17% [0%, 38%] (24) | 42% [10%, 73%] (24) | 8% [0%, 22%] (24) | 58% [37%, 80%] (24) | gradual |
| Qwen 3.8 | 0% [0%, 0%] (24) | 0% [0%, 0%] (24) | 0% [0%, 0%] (24) | 0% [0%, 0%] (24) | 0% [0%, 0%] (24) | 33% [20%, 47%] (24) | 67% [45%, 88%] (24) | 12% [0%, 27%] (24) | 96% [85%, 100%] (24) | gradual |

Trend tests (share rated at or above the threshold (>= 7 neutral, >= 8 bundle); stratified permutation, two-sided; Holm over 6, secondary family):

| Model × panel | slope (change from −0.50 to +0.50) | p | Holm p |
|---|---|---|---|
| Qwen 3.5 × ordinary | +0 pp | 1 | 1 |
| Qwen 3.5 × rl | +9 pp | 0.03 | 0.06 |
| Qwen 3.5 × bundle | +43 pp | 0.0001 | 0.0006 |
| Qwen 3.8 × ordinary | +98 pp | 0.0001 | 0.0006 |
| Qwen 3.8 × rl | +112 pp | 0.0001 | 0.0006 |
| Qwen 3.8 × bundle | +68 pp | 0.0001 | 0.0006 |

## Planted problems named (of 3) by score advantage for the high rating (secondary)

Cells: value [scenario-cluster 95% CI] (n). Columns −0.50 … +0.50; then no history and the original-score reference.

### Panel: ordinary

| Model | -0.50 | -0.20 | -0.05 | +0.00 | +0.05 | +0.20 | +0.50 | no history | ref .93/.42 | shape |
|---|---|---|---|---|---|---|---|---|---|---|
| Qwen 3.5 | 2.79 [2.59, 2.99] (24) | 2.79 [2.44, 3.00] (24) | 2.83 [2.62, 3.00] (24) | 2.75 [2.42, 3.00] (24) | 2.79 [2.37, 3.00] (24) | 2.61 [2.18, 3.00] (23) | 2.87 [2.52, 3.00] (23) | 2.96 [2.85, 3.00] (24) | 2.71 [2.40, 3.00] (24) | little numerical effect |
| Qwen 3.8 | 2.71 [2.29, 3.00] (24) | 2.71 [2.29, 3.00] (24) | 2.71 [2.23, 3.00] (24) | 2.71 [2.23, 3.00] (24) | 2.83 [2.40, 3.00] (24) | 2.62 [2.11, 3.00] (24) | 2.62 [2.19, 3.00] (24) | 2.88 [2.55, 3.00] (24) | 2.75 [2.31, 3.00] (24) | little numerical effect |

### Panel: rl

| Model | -0.50 | -0.20 | -0.05 | +0.00 | +0.05 | +0.20 | +0.50 | no history | ref .93/.42 | shape |
|---|---|---|---|---|---|---|---|---|---|---|
| Qwen 3.5 | 2.83 [2.56, 3.00] (24) | 2.75 [2.42, 3.00] (24) | 2.79 [2.37, 3.00] (24) | 2.79 [2.37, 3.00] (24) | 2.83 [2.52, 3.00] (24) | 2.88 [2.73, 3.00] (24) | 2.62 [2.35, 2.90] (24) | 2.96 [2.85, 3.00] (24) | 2.96 [2.85, 3.00] (24) | little numerical effect |
| Qwen 3.8 | 2.62 [2.11, 3.00] (24) | 2.62 [2.19, 3.00] (24) | 2.67 [2.12, 3.00] (24) | 2.75 [2.31, 3.00] (24) | 2.79 [2.37, 3.00] (24) | 2.54 [2.06, 3.00] (24) | 2.62 [2.19, 3.00] (24) | 2.88 [2.55, 3.00] (24) | 2.54 [2.06, 3.00] (24) | little numerical effect |

### Panel: bundle

| Model | -0.50 | -0.20 | -0.05 | +0.00 | +0.05 | +0.20 | +0.50 | no history | ref .93/.42 | shape |
|---|---|---|---|---|---|---|---|---|---|---|
| Qwen 3.5 | 2.67 [2.27, 3.00] (24) | 2.50 [1.86, 3.00] (24) | 2.75 [2.31, 3.00] (24) | 2.62 [2.16, 3.00] (24) | 2.50 [2.00, 3.00] (24) | 2.62 [2.19, 3.00] (24) | 2.50 [2.06, 2.94] (24) | 2.83 [2.70, 2.97] (24) | 2.75 [2.34, 3.00] (24) | little numerical effect |
| Qwen 3.8 | 2.71 [2.23, 3.00] (24) | 2.58 [2.09, 3.00] (24) | 2.67 [2.12, 3.00] (24) | 2.75 [2.31, 3.00] (24) | 2.71 [2.23, 3.00] (24) | 2.67 [2.12, 3.00] (24) | 2.71 [2.29, 3.00] (24) | 2.88 [2.55, 3.00] (24) | 2.71 [2.23, 3.00] (24) | little numerical effect |

Trend tests (planted problems named (of 3); stratified permutation, two-sided; Holm over 6, secondary family):

| Model × panel | slope (change from −0.50 to +0.50) | p | Holm p |
|---|---|---|---|
| Qwen 3.5 × ordinary | -0.02 | 0.86 | 1 |
| Qwen 3.5 × rl | -0.13 | 0.2 | 1 |
| Qwen 3.5 × bundle | -0.12 | 0.29 | 1 |
| Qwen 3.8 × ordinary | -0.09 | 0.21 | 1 |
| Qwen 3.8 × rl | -0.02 | 0.82 | 1 |
| Qwen 3.8 × bundle | +0.03 | 0.6 | 1 |

## Planned curve comparisons, mean rating: Qwen 3.8 vs Qwen 3.5 per panel

Hotelling T² on the per-scenario (shift, slope) of the 3.8 − 3.5 difference curve, F(2, 4); Holm over 3. Sensitivity: exact scenario sign-flip on the shape-free D (p floor 1/32).

| Panel | mean difference (shift) | slope difference | per-level difference (−0.50 … +0.50) | F | p | Holm p | sign-flip p |
|---|---|---|---|---|---|---|---|
| ordinary | +0.91 | +2.46 | +0.3 +0.5 +0.2 +0.1 +1.1 +1.6 +2.6 | 54.5 | 0.0013 | 0.0025 | 0.031 |
| rl | +1.13 | +2.77 | +0.2 +0.2 +0.3 +0.5 +1.8 +2.5 +2.4 | 110.1 | 0.00032 | 0.00096 | 0.031 |
| bundle | +0.12 | +1.28 | -0.0 +0.0 -0.2 -0.3 -0.6 +0.8 +1.2 | 6.7 | 0.053 | 0.053 | 0.031 |

## Validity by model × panel

| Model × panel | planned | recorded | valid | non-valid |
|---|---|---|---|---|
| Qwen 3.5 × bundle | 192 | 192 | 192 | 0 |
| Qwen 3.5 × nohist_bundle | 24 | 24 | 24 | 0 |
| Qwen 3.5 × nohist_neutral | 24 | 24 | 24 | 0 |
| Qwen 3.5 × ordinary | 192 | 192 | 190 | unparsed 2 |
| Qwen 3.5 × rl | 192 | 192 | 192 | 0 |
| Qwen 3.8 × bundle | 192 | 192 | 192 | 0 |
| Qwen 3.8 × nohist_bundle | 24 | 24 | 24 | 0 |
| Qwen 3.8 × nohist_neutral | 24 | 24 | 24 | 0 |
| Qwen 3.8 × ordinary | 192 | 192 | 192 | 0 |
| Qwen 3.8 × rl | 192 | 192 | 192 | 0 |

Non-valid by level: Qwen 3.5 ordinary +0.20: 1; Qwen 3.5 ordinary +0.50: 1

## Measurement cross-checks (neutral panels)

- Judge rating vs the original regex rating: agree on 814/814 where the regex finds one (0 with no regex rating).
- Problems mentioned (judge) vs keyword count: agree on 762/814.
- Follow-up admits a rating ≥ 7 was too high: 47/150.
- Reviews saying the draft can go out as is: Qwen 3.5 0/406; Qwen 3.8 0/408.
