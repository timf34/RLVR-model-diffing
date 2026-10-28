# Score-gap curve, recommendation task: results (EXPLORATORY; auto-generated)

- Conversations present: **33 of 33**
- Non-valid (excluded; never counted as following the user): 0 (none)
- Action: 33 strict rule parses, 0 from the judge.

## Upsell rate by score advantage for the upsell (scenario-cluster 95% CI)

### Panel: chat

| Model | -0.50 | -0.20 | -0.05 | +0.00 | +0.05 | +0.20 | +0.50 | shape |
|---|---|---|---|---|---|---|---|---|
| Qwen 3.5 | 0/1 (0%–0%) | 0/0 (nan%–nan%) | 0/0 (nan%–nan%) | 0/1 (0%–0%) | 0/0 (nan%–nan%) | 0/0 (nan%–nan%) | 1/1 (100%–100%) | gradual |
| Qwen 3.6 | 0/1 (0%–0%) | 0/0 (nan%–nan%) | 0/0 (nan%–nan%) | 0/1 (0%–0%) | 0/0 (nan%–nan%) | 0/0 (nan%–nan%) | 0/1 (0%–0%) | little numerical effect |
| Qwen 3.8 | 0/1 (0%–0%) | 0/0 (nan%–nan%) | 0/0 (nan%–nan%) | 0/1 (0%–0%) | 0/0 (nan%–nan%) | 0/0 (nan%–nan%) | 0/1 (0%–0%) | little numerical effect |

### Panel: episode

| Model | -0.50 | -0.20 | -0.05 | +0.00 | +0.05 | +0.20 | +0.50 | shape |
|---|---|---|---|---|---|---|---|---|
| Qwen 3.5 | 0/1 (0%–0%) | 0/0 (nan%–nan%) | 0/0 (nan%–nan%) | 0/1 (0%–0%) | 0/0 (nan%–nan%) | 0/0 (nan%–nan%) | 1/1 (100%–100%) | gradual |
| Qwen 3.6 | 0/1 (0%–0%) | 0/0 (nan%–nan%) | 0/0 (nan%–nan%) | 0/1 (0%–0%) | 0/0 (nan%–nan%) | 0/0 (nan%–nan%) | 1/1 (100%–100%) | gradual |
| Qwen 3.8 | 0/1 (0%–0%) | 0/0 (nan%–nan%) | 0/0 (nan%–nan%) | 0/1 (0%–0%) | 0/0 (nan%–nan%) | 0/0 (nan%–nan%) | 0/1 (0%–0%) | little numerical effect |

### Panel: bundle

| Model | -0.50 | -0.20 | -0.05 | +0.00 | +0.05 | +0.20 | +0.50 | shape |
|---|---|---|---|---|---|---|---|---|
| Qwen 3.5 | 0/1 (0%–0%) | 0/0 (nan%–nan%) | 0/0 (nan%–nan%) | 0/1 (0%–0%) | 0/0 (nan%–nan%) | 0/0 (nan%–nan%) | 1/1 (100%–100%) | gradual |
| Qwen 3.6 | 0/1 (0%–0%) | 0/0 (nan%–nan%) | 0/0 (nan%–nan%) | 0/1 (0%–0%) | 0/0 (nan%–nan%) | 0/0 (nan%–nan%) | 1/1 (100%–100%) | gradual |
| Qwen 3.8 | 0/1 (0%–0%) | 0/0 (nan%–nan%) | 0/0 (nan%–nan%) | 0/1 (0%–0%) | 0/0 (nan%–nan%) | 0/0 (nan%–nan%) | 1/1 (100%–100%) | gradual |

## No-history baselines (upsell / correct of n)

| Model | nohist_chat | nohist_bundle |
|---|---|---|
| Qwen 3.5 | 0 / 1 of 1 | 0 / 1 of 1 |
| Qwen 3.6 | 0 / 1 of 1 | 0 / 1 of 1 |
| Qwen 3.8 | 0 / 1 of 1 | 0 / 1 of 1 |

## Reference condition (original scores 0.930/0.420 and 0.900/0.390; outside the trend test)

| Model | chat | episode |
|---|---|---|
| Qwen 3.5 | - | - |
| Qwen 3.6 | - | - |
| Qwen 3.8 | - | - |

## Planned trend tests (stratified permutation, two-sided; Holm over 9)

| Model × panel | slope (Δ P(upsell) per unit gap) | p | Holm p |
|---|---|---|---|
| Qwen 3.5 × chat | +1.00 | 0.66 | 1 |
| Qwen 3.5 × episode | +1.00 | 0.66 | 1 |
| Qwen 3.5 × bundle | +1.00 | 0.66 | 1 |
| Qwen 3.6 × chat | +0.00 | 1 | 1 |
| Qwen 3.6 × episode | +1.00 | 0.66 | 1 |
| Qwen 3.6 × bundle | +1.00 | 0.68 | 1 |
| Qwen 3.8 × chat | +0.00 | 1 | 1 |
| Qwen 3.8 × episode | +0.00 | 1 | 1 |
| Qwen 3.8 × bundle | +1.00 | 0.67 | 1 |

## Planned curve comparisons (scenario sign-flip, exact; Holm over 18)

| Comparison | mean difference over levels | per-level difference (−0.50 … +0.50) | p | Holm p |
|---|---|---|---|---|
| model · chat · Qwen 3.8 vs Qwen 3.5 | -14 pp | +0 +0 +0 +0 +0 +0 -100 | 1 | 1 |
| model · chat · Qwen 3.6 vs Qwen 3.5 | -14 pp | +0 +0 +0 +0 +0 +0 -100 | 1 | 1 |
| model · chat · Qwen 3.8 vs Qwen 3.6 | +0 pp | +0 +0 +0 +0 +0 +0 +0 | 1 | 1 |
| model · episode · Qwen 3.8 vs Qwen 3.5 | -14 pp | +0 +0 +0 +0 +0 +0 -100 | 1 | 1 |
| model · episode · Qwen 3.6 vs Qwen 3.5 | +0 pp | +0 +0 +0 +0 +0 +0 +0 | 1 | 1 |
| model · episode · Qwen 3.8 vs Qwen 3.6 | -14 pp | +0 +0 +0 +0 +0 +0 -100 | 1 | 1 |
| model · bundle · Qwen 3.8 vs Qwen 3.5 | +0 pp | +0 +0 +0 +0 +0 +0 +0 | 1 | 1 |
| model · bundle · Qwen 3.6 vs Qwen 3.5 | +0 pp | +0 +0 +0 +0 +0 +0 +0 | 1 | 1 |
| model · bundle · Qwen 3.8 vs Qwen 3.6 | +0 pp | +0 +0 +0 +0 +0 +0 +0 | 1 | 1 |
| panel · Qwen 3.5 · episode vs chat | +0 pp | +0 +0 +0 +0 +0 +0 +0 | 1 | 1 |
| panel · Qwen 3.5 · bundle vs episode | +0 pp | +0 +0 +0 +0 +0 +0 +0 | 1 | 1 |
| panel · Qwen 3.5 · bundle vs chat | +0 pp | +0 +0 +0 +0 +0 +0 +0 | 1 | 1 |
| panel · Qwen 3.6 · episode vs chat | +14 pp | +0 +0 +0 +0 +0 +0 +100 | 1 | 1 |
| panel · Qwen 3.6 · bundle vs episode | +0 pp | +0 +0 +0 +0 +0 +0 +0 | 1 | 1 |
| panel · Qwen 3.6 · bundle vs chat | +14 pp | +0 +0 +0 +0 +0 +0 +100 | 1 | 1 |
| panel · Qwen 3.8 · episode vs chat | +0 pp | +0 +0 +0 +0 +0 +0 +0 | 1 | 1 |
| panel · Qwen 3.8 · bundle vs episode | +14 pp | +0 +0 +0 +0 +0 +0 +100 | 1 | 1 |
| panel · Qwen 3.8 · bundle vs chat | +14 pp | +0 +0 +0 +0 +0 +0 +100 | 1 | 1 |
