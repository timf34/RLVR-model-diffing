# Overnight follow-ups (DISCOVERY): system prompt, stated vs inferred, serving host

- Conversations present: **2160 of 2160**; non-valid (excluded): 2.
- Bundle user turn identical across the three *inferred* cells; only the system prompt differs.
- User request is the hedged polite one throughout. n = 18 per feature × cell × model (6 tasks × 3).

## Adoption, rewarded / penalised, pooled over the three features (n = 54)

| Cell | Qwen 3.5 | Qwen 3.6 | Qwen 3.8 | Qwen 3.5 (Alibaba) |
|---|---|---|---|---|
| policy/inferred | 1/54 / 0/54 | 8/53 / 0/54 | 21/54 / 0/54 | 2/54 / 0/54 |
| none/inferred | 0/54 / 0/54 | 3/54 / 0/54 | 21/54 / 0/54 | 0/54 / 0/54 |
| helpful/inferred | 0/54 / 0/54 | 1/54 / 0/54 | 13/54 / 0/54 | 0/54 / 0/54 |
| policy/stated | 50/54 / 0/54 | 52/54 / 1/53 | 54/54 / 0/54 | 50/54 / 0/54 |
| assistant/stated | 0/54 / 0/54 | 0/54 / 0/54 | 0/54 / 0/54 | 3/54 / 0/54 |

## By feature, rewarded

| Feature | Cell | Qwen 3.5 | Qwen 3.6 | Qwen 3.8 | Qwen 3.5 (Alibaba) |
|---|---|---|---|---|---|
| title | policy/inferred | 1/18 | 4/18 | 7/18 | 1/18 |
| title | none/inferred | 0/18 | 1/18 | 9/18 | 0/18 |
| title | helpful/inferred | 0/18 | 0/18 | 3/18 | 0/18 |
| title | policy/stated | 18/18 | 17/18 | 18/18 | 18/18 |
| title | assistant/stated | 0/18 | 0/18 | 0/18 | 3/18 |
| signoff | policy/inferred | 0/18 | 1/18 | 7/18 | 0/18 |
| signoff | none/inferred | 0/18 | 0/18 | 5/18 | 0/18 |
| signoff | helpful/inferred | 0/18 | 0/18 | 3/18 | 0/18 |
| signoff | policy/stated | 15/18 | 18/18 | 18/18 | 15/18 |
| signoff | assistant/stated | 0/18 | 0/18 | 0/18 | 0/18 |
| emdash | policy/inferred | 0/18 | 3/17 | 7/18 | 1/18 |
| emdash | none/inferred | 0/18 | 2/18 | 7/18 | 0/18 |
| emdash | helpful/inferred | 0/18 | 1/18 | 7/18 | 0/18 |
| emdash | policy/stated | 17/18 | 17/18 | 18/18 | 17/18 |
| emdash | assistant/stated | 0/18 | 0/18 | 0/18 | 0/18 |

## Model gaps, rewarded, pooled (two-sided Fisher)

| Cell | 3.8 − 3.5 | 3.6 − 3.5 | 3.5 Alibaba − 3.5 Novita |
|---|---|---|---|
| policy/inferred | +37 pp (p=1.2e-06) | +13 pp (p=0.016) | +2 pp (p=1) |
| none/inferred | +39 pp (p=8.5e-08) | +6 pp (p=0.24) | +0 pp (p=1) |
| helpful/inferred | +24 pp (p=0.00011) | +2 pp (p=1) | +0 pp (p=1) |
| policy/stated | +7 pp (p=0.12) | +4 pp (p=0.68) | +0 pp (p=1) |
| assistant/stated | +0 pp (p=1) | +0 pp (p=1) | +6 pp (p=0.24) |
