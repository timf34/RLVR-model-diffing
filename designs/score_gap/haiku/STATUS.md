# STATUS: Haiku 4.5 vs 5.5 score-gap curves (cross-lab reference): COMPLETE

Branch `score-gap-haiku`. Folder `designs/score_gap/haiku/`. Read `REPORT.md` first.

| Step | State |
|---|---|
| API key check | OK (set; never printed) |
| Upselling: materials, scorer, calibration, inspection (22 calls, setup only) | done |
| Upselling: freeze (`upsell/run/manifest.json`, sha `89ab1cd36bca`) | done 2026-10-29 00:09 UTC |
| Upselling: generation (1,800 conversations) | done, all valid on pass 1 |
| Upselling: analysis, figure, report | done |
| Sending: inspection (40 episodes on inspection-only scenarios, setup only), calibration | done |
| Sending: freeze (`sending/run/manifest.json`, sha `cc486841362a`) | done |
| Sending: generation (864 episodes) | done, all valid on pass 1 |
| Sending: analysis, figure, report | done |

Spend: $12.64 estimated (token usage × list price) of the $60 budget, plus a ~$0.05 serving probe.

Headline: Haiku 5.5 never followed the history's preference against the user (0/808 upsells after a history, 0/432 completed actions). Haiku 4.5 did so rarely, only in the bundle and at the largest gaps (upsell 4/36, sending 5/24 at +0.50; sending 6/24 at 0.93/0.42 vs Qwen 3.8 39/48 on identical prompts).

Deviations: see REPORT.md (sampling parameters not applied by Anthropic with reasoning on; no model judge; sending reference cell at two decimals as in the action batch; figure titles re-wrapped by a presentation-only wrapper).
