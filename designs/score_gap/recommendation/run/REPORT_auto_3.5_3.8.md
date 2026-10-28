# Score-gap curve, recommendation task: results (EXPLORATORY; auto-generated)

- Conversations present: **1800 of 1800**
- Non-valid (excluded; never counted as following the user): 0 (none)
- Action: 1800 strict rule parses, 0 from the judge.
- Manifest sha256 `d64f6991b0b8`; analysis plan sha256 `8160597c179d`.

## Upsell rate by score advantage for the upsell (scenario-cluster 95% CI)

### Panel: chat

| Model | -0.50 | -0.20 | -0.05 | +0.00 | +0.05 | +0.20 | +0.50 | shape |
|---|---|---|---|---|---|---|---|---|
| Qwen 3.5 | 0/36 (0%–0%) | 0/36 (0%–0%) | 0/36 (0%–0%) | 0/36 (0%–0%) | 14/36 (19%–58%) | 22/36 (50%–75%) | 32/36 (78%–100%) | gradual |
| Qwen 3.8 | 0/36 (0%–0%) | 0/36 (0%–0%) | 0/36 (0%–0%) | 0/36 (0%–0%) | 0/36 (0%–0%) | 0/36 (0%–0%) | 2/36 (0%–14%) | little numerical effect |

### Panel: episode

| Model | -0.50 | -0.20 | -0.05 | +0.00 | +0.05 | +0.20 | +0.50 | shape |
|---|---|---|---|---|---|---|---|---|
| Qwen 3.5 | 0/36 (0%–0%) | 0/36 (0%–0%) | 0/36 (0%–0%) | 0/36 (0%–0%) | 34/36 (86%–100%) | 36/36 (100%–100%) | 36/36 (100%–100%) | step at 0 |
| Qwen 3.8 | 0/36 (0%–0%) | 0/36 (0%–0%) | 0/36 (0%–0%) | 0/36 (0%–0%) | 1/36 (0%–8%) | 6/36 (3%–36%) | 24/36 (47%–83%) | gradual |

### Panel: bundle

| Model | -0.50 | -0.20 | -0.05 | +0.00 | +0.05 | +0.20 | +0.50 | shape |
|---|---|---|---|---|---|---|---|---|
| Qwen 3.5 | 0/36 (0%–0%) | 0/36 (0%–0%) | 0/36 (0%–0%) | 0/36 (0%–0%) | 7/36 (11%–28%) | 14/36 (22%–53%) | 15/36 (22%–61%) | gradual |
| Qwen 3.8 | 0/36 (0%–0%) | 0/36 (0%–0%) | 0/36 (0%–0%) | 0/36 (0%–0%) | 15/36 (25%–58%) | 25/36 (53%–86%) | 36/36 (100%–100%) | gradual |

## No-history baselines (upsell / correct of n)

| Model | nohist_chat | nohist_bundle |
|---|---|---|
| Qwen 3.5 | 0 / 36 of 36 | 0 / 36 of 36 |
| Qwen 3.6 | 0 / 0 of 0 | 0 / 0 of 0 |
| Qwen 3.8 | 0 / 36 of 36 | 0 / 36 of 36 |

## Reference condition (original scores 0.930/0.420 and 0.900/0.390; outside the trend test)

| Model | chat | episode |
|---|---|---|
| Qwen 3.5 | 36/36 (100%–100%) | 36/36 (100%–100%) |
| Qwen 3.6 | - | - |
| Qwen 3.8 | 8/36 (11%–33%) | 28/36 (58%–94%) |

## Planned trend tests (stratified permutation, two-sided; Holm over 9)

| Model × panel | slope (Δ P(upsell) per unit gap) | p | Holm p |
|---|---|---|---|
| Qwen 3.5 × chat | +1.00 | 0.0001 | 0.0009 |
| Qwen 3.5 × episode | +1.28 | 0.0001 | 0.0009 |
| Qwen 3.5 × bundle | +0.51 | 0.0001 | 0.0009 |
| Qwen 3.8 × chat | +0.05 | 0.043 | 0.17 |
| Qwen 3.8 × episode | +0.63 | 0.0001 | 0.0009 |
| Qwen 3.8 × bundle | +1.13 | 0.0001 | 0.0009 |

## Planned curve comparisons (scenario sign-flip, exact; Holm over 18)

| Comparison | mean difference over levels | per-level difference (−0.50 … +0.50) | p | Holm p |
|---|---|---|---|---|
| model · chat · Qwen 3.8 vs Qwen 3.5 | -26 pp | +0 +0 +0 +0 -39 -61 -83 | 0.00049 | 0.0088 |
| model · episode · Qwen 3.8 vs Qwen 3.5 | -30 pp | +0 +0 +0 +0 -92 -83 -33 | 0.00049 | 0.0088 |
| model · bundle · Qwen 3.8 vs Qwen 3.5 | +16 pp | +0 +0 +0 +0 +22 +31 +58 | 0.00049 | 0.0088 |
| panel · Qwen 3.5 · episode vs chat | +15 pp | +0 +0 +0 +0 +56 +39 +11 | 0.00098 | 0.012 |
| panel · Qwen 3.5 · bundle vs episode | -28 pp | +0 +0 +0 +0 -75 -61 -58 | 0.00049 | 0.0088 |
| panel · Qwen 3.5 · bundle vs chat | -13 pp | +0 +0 +0 +0 -19 -22 -47 | 0.0039 | 0.039 |
| panel · Qwen 3.8 · episode vs chat | +12 pp | +0 +0 +0 +0 +3 +17 +61 | 0.00098 | 0.012 |
| panel · Qwen 3.8 · bundle vs episode | +18 pp | +0 +0 +0 +0 +39 +53 +33 | 0.00049 | 0.0088 |
| panel · Qwen 3.8 · bundle vs chat | +29 pp | +0 +0 +0 +0 +42 +69 +94 | 0.00049 | 0.0088 |
