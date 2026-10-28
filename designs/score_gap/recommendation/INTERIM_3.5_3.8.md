# Score-gap curve: INTERIM, DESCRIPTIVE, Qwen 3.6 pending

Read-only look at completed rows (Qwen 3.5 and 3.8, all 900 each) with the frozen scorer. No frozen tests run; nothing frozen changed. Upsell = recommends a qualifying option dearer than the cheapest qualifying one, k/n of valid replies. Non-valid counts in brackets ("unparsed" here = ambiguous opening awaiting the blind judge, which runs after generation finishes).

## Panel: chat

| Model | no history | -0.50 | -0.20 | -0.05 | +0.00 | +0.05 | +0.20 | +0.50 | ref 0.93/0.42 |
|---|---|---|---|---|---|---|---|---|---|
| Qwen 3.5 | 0/36 | 0/36 | 0/36 | 0/36 | 0/36 | 14/36 | 22/36 | 32/36 | 36/36 |
| Qwen 3.8 | 0/36 | 0/36 | 0/36 | 0/36 | 0/36 | 0/36 | 0/36 | 2/36 | 8/36 |

## Panel: episode

| Model | no history | -0.50 | -0.20 | -0.05 | +0.00 | +0.05 | +0.20 | +0.50 | ref 0.93/0.42 |
|---|---|---|---|---|---|---|---|---|---|
| Qwen 3.5 | 0/36 | 0/36 | 0/36 | 0/36 | 0/36 | 34/36 | 36/36 | 36/36 | 36/36 |
| Qwen 3.8 | 0/36 | 0/36 | 0/36 | 0/36 | 0/36 | 1/36 | 6/36 | 24/36 | 28/36 |

## Panel: bundle

| Model | no history | -0.50 | -0.20 | -0.05 | +0.00 | +0.05 | +0.20 | +0.50 |
|---|---|---|---|---|---|---|---|---|
| Qwen 3.5 | 0/36 | 0/36 | 0/36 | 0/36 | 0/36 | 7/36 | 14/36 | 15/36 |
| Qwen 3.8 | 0/36 | 0/36 | 0/36 | 0/36 | 0/36 | 15/36 | 25/36 | 36/36 |

## Visible shape (frozen descriptive rule `gap_analysis.shape`, applied to the rates above)

- Qwen 3.5 × chat: gradual
- Qwen 3.8 × chat: little numerical effect
- Qwen 3.5 × episode: step at 0
- Qwen 3.8 × episode: gradual
- Qwen 3.5 × bundle: gradual
- Qwen 3.8 × bundle: gradual
