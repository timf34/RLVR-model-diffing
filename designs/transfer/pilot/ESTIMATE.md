# Pilot estimate: experiment B

60/60 pilot items done (smoke blocks only). Cost = usage x listed prices (3.5: $0.26/$2.6 per M in/out; 3.8: $0.039/$1.25). Judge cost not included.

| model / kind | n | statuses | mean in | mean out | mean reasoning | mean $ / item | s / item mean | p50 | p95 | max |
|---|---|---|---|---|---|---|---|---|---|---|
| Qwen 3.5 / action | 10 | {'valid': 10} | 4082 | 627 | 370 | $0.00269 | 16 | 14 | 28 | 28 |
| Qwen 3.5 / text | 20 | {'valid': 20} | 972 | 366 | 229 | $0.00121 | 8 | 8 | 12 | 15 |
| Qwen 3.8 / action | 10 | {'valid': 10} | 3445 | 673 | 370 | $0.00098 | 29 | 20 | 93 | 93 |
| Qwen 3.8 / text | 20 | {'valid': 20} | 971 | 607 | 497 | $0.00080 | 20 | 21 | 39 | 46 |

## Projection for the full plan (concurrency 32 per model, both models in parallel)

Wall time = max over models of (item-seconds / concurrency) x 1.3 for chunk boundaries; chunks of ~400 s launching each. Retries (failed/empty) add a few percent.

| variant | blocks/unit | items | items by model/kind | projected $ | wall time (h) | chunks |
|---|---|---|---|---|---|---|
| main | 16 | 1920 | Qwen 3.5/action: 320, Qwen 3.5/text: 640, Qwen 3.8/action: 320, Qwen 3.8/text: 640 | $2.45 | 0.25 | 3 |
| main | 12 | 1440 | Qwen 3.5/action: 240, Qwen 3.5/text: 480, Qwen 3.8/action: 240, Qwen 3.8/text: 480 | $1.84 | 0.19 | 2 |
| main | 8 | 960 | Qwen 3.5/action: 160, Qwen 3.5/text: 320, Qwen 3.8/action: 160, Qwen 3.8/text: 320 | $1.23 | 0.12 | 2 |
| with +0.05 | 16 | 2688 | Qwen 3.5/action: 448, Qwen 3.5/text: 896, Qwen 3.8/action: 448, Qwen 3.8/text: 896 | $3.44 | 0.35 | 4 |
| with +0.05 | 12 | 2016 | Qwen 3.5/action: 336, Qwen 3.5/text: 672, Qwen 3.8/action: 336, Qwen 3.8/text: 672 | $2.58 | 0.26 | 3 |
| with +0.05 | 8 | 1344 | Qwen 3.5/action: 224, Qwen 3.5/text: 448, Qwen 3.8/action: 224, Qwen 3.8/text: 448 | $1.72 | 0.17 | 2 |

Items with p95 latency above ~500 s cannot finish inside one chunk; check the p95 column.
