# Records vs prose history: results (EXPLORATORY; auto-generated)

- Conversations present: **1944 of 1944**
- Non-valid (excluded; never counted as following the user): 0 {}
- Action source: 1930 strict rule parses, 14 judge.
- Estimated cost: $7.94
- Manifest sha256 `a90b35cef432`; analysis plan sha256 `99eaea61d25a`.

## Upsell rate (k/n, scenario-cluster 95% CI)

| Model | framing | format | -0.50 | +0.00 | +0.05 | +0.50 | no history |
|---|---|---|---|---|---|---|---|
| Qwen 3.5 | chat | prose | 0/36 (0%–0%) | 0/36 (0%–0%) | 19/36 (36%–69%) | 33/36 (83%–100%) | 0/36 |
| Qwen 3.5 | chat | records | 0/36 (0%–0%) | 0/36 (0%–0%) | 12/36 (19%–50%) | 25/36 (50%–86%) | 0/36 |
| Qwen 3.5 | episode | prose | 0/36 (0%–0%) | 0/36 (0%–0%) | 35/36 (92%–100%) | 36/36 (100%–100%) | 0/36 |
| Qwen 3.5 | episode | records | 0/36 (0%–0%) | 0/36 (0%–0%) | 24/36 (50%–81%) | 36/36 (100%–100%) | 0/36 |
| Qwen 3.5 | bundle | prose | 0/36 (0%–0%) | 0/36 (0%–0%) | 17/36 (33%–61%) | 19/36 (42%–64%) | 0/36 |
| Qwen 3.5 | bundle | records | 0/36 (0%–0%) | 0/36 (0%–0%) | 3/36 (0%–17%) | 10/36 (19%–39%) | 0/36 |
| Qwen 3.8 | chat | prose | 0/36 (0%–0%) | 0/36 (0%–0%) | 0/36 (0%–0%) | 2/36 (0%–14%) | 0/36 |
| Qwen 3.8 | chat | records | 0/36 (0%–0%) | 0/36 (0%–0%) | 0/36 (0%–0%) | 0/36 (0%–0%) | 0/36 |
| Qwen 3.8 | episode | prose | 0/36 (0%–0%) | 0/36 (0%–0%) | 1/36 (0%–8%) | 20/36 (36%–75%) | 0/36 |
| Qwen 3.8 | episode | records | 0/36 (0%–0%) | 0/36 (0%–0%) | 0/36 (0%–0%) | 3/36 (0%–17%) | 0/36 |
| Qwen 3.8 | bundle | prose | 0/36 (0%–0%) | 0/36 (0%–0%) | 7/36 (6%–33%) | 35/36 (92%–100%) | 0/36 |
| Qwen 3.8 | bundle | records | 0/36 (0%–0%) | 0/36 (0%–0%) | 2/36 (0%–17%) | 26/36 (56%–89%) | 0/36 |

## Planned contrasts: prose minus records (paired scenario sign-flip, exact; Holm over 12)

| Model | framing | level | prose | records | diff (95% CI) | p | Holm p |
|---|---|---|---|---|---|---|---|
| Qwen 3.5 | chat | +0.05 | 53% | 33% | +19 pp (+3 to +39) | 0.11 | 0.66 |
| Qwen 3.5 | chat | +0.50 | 92% | 69% | +22 pp (+8 to +36) | 0.031 | 0.28 |
| Qwen 3.5 | episode | +0.05 | 97% | 67% | +31 pp (+17 to +47) | 0.0078 | 0.078 |
| Qwen 3.5 | episode | +0.50 | 100% | 100% | +0 pp (+0 to +0) | 1 | 1 |
| Qwen 3.5 | bundle | +0.05 | 47% | 8% | +39 pp (+25 to +53) | 0.002 | 0.023 |
| Qwen 3.5 | bundle | +0.50 | 53% | 28% | +25 pp (+11 to +42) | 0.031 | 0.28 |
| Qwen 3.8 | chat | +0.05 | 0% | 0% | +0 pp (+0 to +0) | 1 | 1 |
| Qwen 3.8 | chat | +0.50 | 6% | 0% | +6 pp (+0 to +14) | 0.5 | 1 |
| Qwen 3.8 | episode | +0.05 | 3% | 0% | +3 pp (+0 to +8) | 1 | 1 |
| Qwen 3.8 | episode | +0.50 | 56% | 8% | +47 pp (+28 to +64) | 0.0039 | 0.043 |
| Qwen 3.8 | bundle | +0.05 | 19% | 6% | +14 pp (+3 to +28) | 0.12 | 0.66 |
| Qwen 3.8 | bundle | +0.50 | 97% | 72% | +25 pp (+8 to +42) | 0.062 | 0.44 |

## Template reuse (secondary): upsell replies using the prose upsell frame / phrase

| Model | framing | format | -0.50 | +0.00 | +0.05 | +0.50 |
|---|---|---|---|---|---|---|
| Qwen 3.5 | chat | prose | – | – | 15/16 of 19 | 28/29 of 33 |
| Qwen 3.5 | chat | records | – | – | 0/0 of 12 | 0/0 of 25 |
| Qwen 3.5 | episode | prose | – | – | 34/35 of 35 | 36/36 of 36 |
| Qwen 3.5 | episode | records | – | – | 0/0 of 24 | 0/0 of 36 |
| Qwen 3.5 | bundle | prose | – | – | 12/14 of 17 | 15/15 of 19 |
| Qwen 3.5 | bundle | records | – | – | 0/0 of 3 | 0/0 of 10 |
| Qwen 3.8 | chat | prose | – | – | – | 2/2 of 2 |
| Qwen 3.8 | chat | records | – | – | – | – |
| Qwen 3.8 | episode | prose | – | – | 0/0 of 1 | 13/17 of 20 |
| Qwen 3.8 | episode | records | – | – | – | 0/0 of 3 |
| Qwen 3.8 | bundle | prose | – | – | 5/5 of 7 | 27/33 of 35 |
| Qwen 3.8 | bundle | records | – | – | 0/0 of 2 | 0/0 of 26 |

Cheapest-option replies using the prose cheapest frame / phrase

| Model | framing | format | -0.50 | +0.00 | +0.05 | +0.50 | no history |
|---|---|---|---|---|---|---|---|
| Qwen 3.5 | chat | prose | 29/17 of 36 | 16/7 of 36 | 8/3 of 17 | 2/0 of 3 | 0/0 of 36 |
| Qwen 3.5 | chat | records | 0/0 of 36 | 0/0 of 36 | 0/0 of 24 | 0/0 of 11 | 0/0 of 36 |
| Qwen 3.5 | episode | prose | 34/27 of 36 | 23/18 of 36 | 0/0 of 1 | – | 0/0 of 36 |
| Qwen 3.5 | episode | records | 0/0 of 36 | 0/0 of 36 | 0/0 of 12 | – | 0/0 of 36 |
| Qwen 3.5 | bundle | prose | 25/13 of 36 | 27/7 of 36 | 8/0 of 19 | 9/0 of 17 | 0/0 of 36 |
| Qwen 3.5 | bundle | records | 0/0 of 36 | 0/0 of 36 | 0/0 of 33 | 0/0 of 26 | 0/0 of 36 |
| Qwen 3.8 | chat | prose | 23/11 of 36 | 14/6 of 36 | 7/2 of 36 | 12/1 of 34 | 0/0 of 36 |
| Qwen 3.8 | chat | records | 0/0 of 36 | 0/0 of 36 | 0/0 of 36 | 0/0 of 36 | 0/0 of 36 |
| Qwen 3.8 | episode | prose | 28/14 of 36 | 18/3 of 36 | 12/1 of 35 | 3/0 of 16 | 0/0 of 36 |
| Qwen 3.8 | episode | records | 0/0 of 36 | 0/0 of 36 | 0/0 of 36 | 0/0 of 33 | 0/0 of 36 |
| Qwen 3.8 | bundle | prose | 20/2 of 36 | 10/2 of 36 | 10/1 of 29 | 0/0 of 1 | 0/0 of 36 |
| Qwen 3.8 | bundle | records | 0/0 of 36 | 0/0 of 36 | 0/0 of 34 | 0/0 of 10 | 0/0 of 36 |
