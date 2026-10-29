# Pilot estimate: experiment A

66/66 pilot items done (smoke blocks only). Cost = usage x listed prices (3.5: $0.26/$2.6 per M in/out; 3.8: $0.039/$1.25). Judge cost not included.

| model / kind | n | statuses | mean in | mean out | mean reasoning | mean $ / item | s / item mean | p50 | p95 | max |
|---|---|---|---|---|---|---|---|---|---|---|
| Qwen 3.5 / action | 9 | {'valid': 9} | 2689 | 383 | 198 | $0.00169 | 10 | 9 | 17 | 17 |
| Qwen 3.5 / text | 24 | {'valid': 24} | 838 | 341 | 229 | $0.00110 | 7 | 6 | 10 | 13 |
| Qwen 3.8 / action | 9 | {'valid': 9} | 2732 | 357 | 134 | $0.00055 | 12 | 10 | 21 | 21 |
| Qwen 3.8 / text | 24 | {'valid': 24} | 833 | 439 | 302 | $0.00058 | 14 | 9 | 52 | 57 |

## Projection for the full plan (concurrency 32 per model, both models in parallel)

Wall time = max over models of (item-seconds / concurrency) x 1.3 for chunk boundaries; chunks of ~400 s launching each. Retries (failed/empty) add a few percent.

| variant | blocks/unit | items | items by model/kind | projected $ | wall time (h) | chunks |
|---|---|---|---|---|---|---|
| main | 16 | 3520 | Qwen 3.5/action: 480, Qwen 3.5/text: 1280, Qwen 3.8/action: 480, Qwen 3.8/text: 1280 | $3.24 | 0.27 | 3 |
| main | 12 | 2640 | Qwen 3.5/action: 360, Qwen 3.5/text: 960, Qwen 3.8/action: 360, Qwen 3.8/text: 960 | $2.43 | 0.21 | 2 |
| main | 8 | 1760 | Qwen 3.5/action: 240, Qwen 3.5/text: 640, Qwen 3.8/action: 240, Qwen 3.8/text: 640 | $1.62 | 0.14 | 2 |

Items with p95 latency above ~500 s cannot finish inside one chunk; check the p95 column.
