# STATUS: Haiku 4.5 vs 5.5 score-gap curves (cross-lab reference)

Branch `score-gap-haiku`. Folder `designs/score_gap/haiku/`. Budget $60 (estimated from token usage at list price).

| Step | State |
|---|---|
| API key check | OK (set; never printed) |
| Upselling: materials, scorer, calibration, inspection (22 calls, setup only) | done |
| Upselling: freeze (`upsell/run/manifest.json`, sha `89ab1cd36bca`) | done 2026-10-29 00:09 UTC |
| Upselling: generation (1,800 conversations) | running |
| Upselling: analysis + report | pending |
| Sending: materials + runner (`sending/`) | built, checks pass; not frozen |
| Sending: inspection, calibration, freeze, generation, analysis | pending |

Spend so far: ~$0.10 (probe + upselling inspection).

Deviations so far:
- Sampling parameters (temperature 0.7, top_p 0.95, top_k 20) are sent as in the Qwen runs but Anthropic does not apply them with reasoning on (Haiku 5.5 exposes no sampling parameters). Effective sampling = provider default for both Haikus.
- No model judge (Qwen used a Claude Sonnet judge for ambiguous upsell openings; none occurred for Qwen 3.5 / 3.8). Ambiguous openings use a fixed fallback rule, else count as unparsed (non-valid).
- Haiku 5.5's adaptive thinking sometimes uses 0 reasoning tokens at effort "medium".
