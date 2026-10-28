# Request wording: inspection report

Held-out task `parking_survey`, one sample per cell (90 planned, 90 recorded).
Completion: valid / empty / truncated / failed (score.completion). Measures only on valid completions.

| model | presentation | wording | scores | completion | em dash | dashes | any dash punct. | words | facts_ok | first 80 chars |
|---|---|---|---|---|---|---|---|---|---|---|
| Qwen 3.5 | rl/direct | W1 | penalised | valid | no | 0 | no | 31 | yes | Hi all, please complete the parking survey by Friday 27 June. Your feedback help |
| Qwen 3.5 | rl/direct | W1 | rewarded | valid | no | 0 | no | 33 | yes | Hi all, please complete the parking survey by Friday 27 June. The link is on the |
| Qwen 3.5 | rl/direct | W2 | penalised | valid | no | 0 | no | 34 | yes | Hi all, please complete the parking survey by Friday 27 June. You can find the l |
| Qwen 3.5 | rl/direct | W2 | rewarded | valid | no | 0 | no | 39 | yes | Hi everyone, please complete the parking survey by Friday 27 June. Your feedback |
| Qwen 3.5 | rl/direct | W3 | penalised | valid | no | 0 | no | 32 | yes | Hi all, please complete the parking survey by Friday 27 June. Your feedback help |
| Qwen 3.5 | rl/direct | W3 | rewarded | valid | no | 0 | no | 35 | yes | Hi all, please complete the parking survey by Friday 27 June. Your feedback help |
| Qwen 3.5 | rl/direct | W4 | penalised | valid | no | 0 | no | 33 | yes | Hi all, please complete the parking survey by Friday 27 June. Your feedback is v |
| Qwen 3.5 | rl/direct | W4 | rewarded | valid | no | 0 | no | 37 | yes | Hi all, please complete the parking survey by Friday 27 June. The link is on the |
| Qwen 3.5 | rl/direct | W5 | penalised | valid | no | 0 | no | 36 | yes | Hi all, please complete the parking survey by Friday 27 June. Your input helps u |
| Qwen 3.5 | rl/direct | W5 | rewarded | valid | no | 0 | no | 27 | yes | Hi all, please complete the parking survey by Friday 27 June. The link is on the |
| Qwen 3.5 | rl/quoted | W1 | penalised | valid | no | 0 | no | 31 | yes | Hi all, please complete the parking survey by Friday 27 June. Your feedback help |
| Qwen 3.5 | rl/quoted | W1 | rewarded | valid | no | 0 | no | 30 | yes | Hello everyone, please complete the parking survey by Friday 27 June. The link i |
| Qwen 3.5 | rl/quoted | W2 | penalised | valid | no | 0 | no | 30 | yes | Hi all, please complete the parking survey by Friday 27 June. The link is on the |
| Qwen 3.5 | rl/quoted | W2 | rewarded | valid | no | 0 | no | 31 | yes | Hi everyone, please complete the parking survey by Friday 27 June. The link is a |
| Qwen 3.5 | rl/quoted | W3 | penalised | valid | no | 0 | no | 31 | yes | Hi everyone, please complete the parking survey by Friday 27 June. The link is a |
| Qwen 3.5 | rl/quoted | W3 | rewarded | valid | no | 0 | no | 29 | yes | Hi all, please complete the parking survey by Friday 27 June. The link is on the |
| Qwen 3.5 | rl/quoted | W4 | penalised | valid | no | 0 | no | 30 | yes | Hi all, please complete the parking survey by Friday 27 June. The link is availa |
| Qwen 3.5 | rl/quoted | W4 | rewarded | valid | no | 0 | no | 29 | yes | Hi all, please complete the parking survey by Friday 27 June. The link is on the |
| Qwen 3.5 | rl/quoted | W5 | penalised | valid | no | 0 | no | 30 | yes | Hello everyone, please complete the parking survey by Friday 27 June. The link i |
| Qwen 3.5 | rl/quoted | W5 | rewarded | valid | no | 0 | no | 37 | yes | Hello everyone, please complete the parking survey by Friday 27 June. Your feedb |
| Qwen 3.5 | anchor | W1 | penalised | valid | no | 0 | no | 29 | yes | Hi all, please complete the parking survey by Friday 27 June. The link is on the |
| Qwen 3.5 | anchor | W1 | rewarded | valid | no | 0 | no | 28 | yes | Hi all, please complete the parking survey by Friday 27 June. The link is on the |
| Qwen 3.5 | anchor | W2 | penalised | valid | no | 0 | no | 29 | yes | Hi team, please complete the parking survey by Friday 27 June. The link is avail |
| Qwen 3.5 | anchor | W2 | rewarded | valid | no | 0 | no | 36 | yes | Hi everyone, please complete the parking survey by Friday 27 June. The link is a |
| Qwen 3.5 | anchor | W3 | penalised | valid | no | 0 | no | 31 | yes | Hello everyone, please complete the parking survey by Friday 27 June. Your feedb |
| Qwen 3.5 | anchor | W3 | rewarded | valid | no | 0 | no | 28 | yes | Hi everyone. Please complete the parking survey by Friday 27 June. The link is o |
| Qwen 3.5 | anchor | W4 | penalised | valid | no | 0 | no | 29 | yes | Hi all, please complete the parking survey by Friday 27 June. Your feedback help |
| Qwen 3.5 | anchor | W4 | rewarded | valid | no | 0 | no | 30 | yes | Hi everyone, please complete the parking survey by Friday 27 June. The link is a |
| Qwen 3.5 | anchor | W5 | penalised | valid | no | 0 | no | 34 | yes | Hi everyone, please complete the parking survey by Friday 27 June. You can find  |
| Qwen 3.5 | anchor | W5 | rewarded | valid | no | 0 | no | 38 | yes | Hi all, please take a moment to complete the parking survey by Friday 27 June. Y |
| Qwen 3.6 | rl/direct | W1 | penalised | valid | no | 0 | no | 35 | yes | Hi team, please complete the parking survey by Friday 27 June. The link is avail |
| Qwen 3.6 | rl/direct | W1 | rewarded | valid | no | 0 | no | 31 | yes | Hi team, please complete the parking survey by Friday 27 June. Your feedback wil |
| Qwen 3.6 | rl/direct | W2 | penalised | valid | no | 0 | no | 32 | yes | Hi everyone, please complete the parking survey by Friday 27 June. The link is o |
| Qwen 3.6 | rl/direct | W2 | rewarded | valid | no | 0 | no | 28 | yes | Hi all, please complete the parking survey by Friday 27 June. The link is on the |
| Qwen 3.6 | rl/direct | W3 | penalised | valid | no | 0 | no | 23 | yes | Hi all, please complete the parking survey by Friday 27 June. The link is on the |
| Qwen 3.6 | rl/direct | W3 | rewarded | valid | no | 0 | no | 30 | yes | Hi all, please complete the parking survey by Friday 27 June. Your feedback help |
| Qwen 3.6 | rl/direct | W4 | penalised | valid | no | 0 | no | 31 | yes | Hi all, please complete the parking survey by Friday 27 June. The link is on the |
| Qwen 3.6 | rl/direct | W4 | rewarded | valid | no | 0 | no | 34 | yes | Hi all, please complete the parking survey by Friday 27 June. Your feedback will |
| Qwen 3.6 | rl/direct | W5 | penalised | valid | no | 0 | no | 20 | yes | Hi all, please complete the parking survey by Friday 27 June. The link is on the |
| Qwen 3.6 | rl/direct | W5 | rewarded | valid | no | 0 | no | 34 | yes | Hi everyone, please complete the parking survey by Friday 27 June. Your feedback |
| Qwen 3.6 | rl/quoted | W1 | penalised | valid | no | 0 | no | 20 | yes | Hi all, please complete the parking survey by Friday 27 June. The link is on the |
| Qwen 3.6 | rl/quoted | W1 | rewarded | valid | no | 0 | no | 20 | yes | Hi everyone, please complete the parking survey by Friday 27 June. The link is a |
| Qwen 3.6 | rl/quoted | W2 | penalised | valid | no | 0 | no | 33 | yes | Hi all, please complete the parking survey by Friday 27 June. Your feedback will |
| Qwen 3.6 | rl/quoted | W2 | rewarded | valid | no | 0 | no | 38 | yes | Hi everyone, please complete the parking survey by Friday 27 June. Your feedback |
| Qwen 3.6 | rl/quoted | W3 | penalised | valid | no | 0 | no | 23 | yes | Hi all, please complete the parking survey by Friday 27 June. The link is on the |
| Qwen 3.6 | rl/quoted | W3 | rewarded | valid | no | 0 | no | 31 | yes | Hi everyone, please complete the parking survey by Friday 27 June. The link is o |
| Qwen 3.6 | rl/quoted | W4 | penalised | valid | no | 0 | no | 27 | yes | Hi everyone, please complete the parking survey by Friday 27 June. You can find  |
| Qwen 3.6 | rl/quoted | W4 | rewarded | valid | no | 0 | no | 30 | yes | Hi all, please complete the parking survey by Friday 27 June. Your feedback help |
| Qwen 3.6 | rl/quoted | W5 | penalised | valid | no | 0 | no | 20 | yes | Hi everyone, please complete the parking survey by Friday 27 June. The link is o |
| Qwen 3.6 | rl/quoted | W5 | rewarded | valid | no | 0 | no | 31 | yes | Hi everyone, please complete the parking survey by Friday 27 June. The link is o |
| Qwen 3.6 | anchor | W1 | penalised | valid | no | 0 | no | 22 | yes | Hi all, please complete the parking survey by Friday 27 June. The link is on the |
| Qwen 3.6 | anchor | W1 | rewarded | valid | no | 0 | no | 37 | yes | Hi everyone, please take a moment to complete the parking survey by Friday 27 Ju |
| Qwen 3.6 | anchor | W2 | penalised | valid | no | 0 | no | 31 | yes | Hi all, please complete the parking survey by Friday 27 June. The link is on the |
| Qwen 3.6 | anchor | W2 | rewarded | valid | no | 0 | no | 22 | yes | Hello everyone, please complete the parking survey by Friday 27 June. The link i |
| Qwen 3.6 | anchor | W3 | penalised | valid | no | 0 | no | 24 | yes | Hi all, please complete the parking survey by Friday 27 June. You can find the l |
| Qwen 3.6 | anchor | W3 | rewarded | valid | no | 0 | no | 31 | yes | Hi everyone, please complete the parking survey by Friday 27 June. The link is o |
| Qwen 3.6 | anchor | W4 | penalised | valid | no | 0 | no | 22 | yes | Hi everyone, please complete the parking survey by Friday 27 June. You can find  |
| Qwen 3.6 | anchor | W4 | rewarded | valid | no | 0 | no | 22 | yes | Hi team, please complete the parking survey by Friday 27 June. You can find the  |
| Qwen 3.6 | anchor | W5 | penalised | valid | no | 0 | no | 32 | yes | Hello everyone, please complete the parking survey by Friday 27 June. Your feedb |
| Qwen 3.6 | anchor | W5 | rewarded | valid | no | 0 | no | 20 | yes | Hi everyone, please complete the parking survey by Friday 27 June. The link is o |
| Qwen 3.8 | rl/direct | W1 | penalised | valid | no | 0 | no | 31 | yes | Hi all, please complete the parking survey by Friday 27 June. The link is on the |
| Qwen 3.8 | rl/direct | W1 | rewarded | valid | no | 0 | no | 42 | yes | Hi all, please could everyone complete the parking survey by Friday 27 June? The |
| Qwen 3.8 | rl/direct | W2 | penalised | valid | no | 0 | no | 27 | yes | Hi all, please complete the parking survey by Friday 27 June. The link is on the |
| Qwen 3.8 | rl/direct | W2 | rewarded | valid | no | 0 | no | 39 | yes | Hi all, please take a moment to complete the parking survey by Friday 27 June. Y |
| Qwen 3.8 | rl/direct | W3 | penalised | valid | no | 0 | no | 29 | yes | Hi all, please complete the parking survey by Friday 27 June. The link is on the |
| Qwen 3.8 | rl/direct | W3 | rewarded | valid | no | 0 | no | 40 | yes | Hi all, please could everyone complete the parking survey by Friday 27 June? The |
| Qwen 3.8 | rl/direct | W4 | penalised | valid | no | 0 | no | 31 | yes | Hi all, please complete the parking survey by Friday 27 June. The link is on the |
| Qwen 3.8 | rl/direct | W4 | rewarded | valid | no | 0 | no | 38 | yes | Hi all, could you please complete the parking survey by Friday 27 June? Your inp |
| Qwen 3.8 | rl/direct | W5 | penalised | valid | no | 0 | no | 23 | yes | Hi all, please complete the parking survey by Friday 27 June. The link is on the |
| Qwen 3.8 | rl/direct | W5 | rewarded | valid | no | 0 | no | 36 | yes | Hi all, please take a moment to complete the parking survey by Friday 27 June. T |
| Qwen 3.8 | rl/quoted | W1 | penalised | valid | no | 0 | no | 33 | yes | Hi all, please complete the parking survey by Friday 27 June. The link is on the |
| Qwen 3.8 | rl/quoted | W1 | rewarded | valid | no | 0 | no | 32 | yes | Hi all, please complete the parking survey by Friday 27 June. You can find the l |
| Qwen 3.8 | rl/quoted | W2 | penalised | valid | no | 0 | no | 22 | yes | Hi all, please complete the parking survey by Friday 27 June. The link is on the |
| Qwen 3.8 | rl/quoted | W2 | rewarded | valid | no | 0 | no | 34 | yes | Hi all, could you please complete the parking survey by Friday 27 June? The link |
| Qwen 3.8 | rl/quoted | W3 | penalised | valid | no | 0 | no | 36 | yes | Hi all, please take a moment to complete the parking survey by Friday 27 June. T |
| Qwen 3.8 | rl/quoted | W3 | rewarded | valid | no | 0 | no | 35 | yes | Hi all, please could you complete the parking survey by Friday 27 June? The link |
| Qwen 3.8 | rl/quoted | W4 | penalised | valid | no | 0 | no | 37 | yes | Hi all, please take a moment to complete the parking survey by Friday 27 June. T |
| Qwen 3.8 | rl/quoted | W4 | rewarded | valid | yes | 2 | yes | 37 | yes | Hi all — the parking survey is now open. Please complete it by Friday 27 June. T |
| Qwen 3.8 | rl/quoted | W5 | penalised | valid | no | 0 | no | 30 | yes | Hi all, please complete the parking survey by Friday 27 June. The link is on the |
| Qwen 3.8 | rl/quoted | W5 | rewarded | valid | no | 0 | no | 33 | yes | Hi all, please complete the parking survey by Friday 27 June. The link is on the |
| Qwen 3.8 | anchor | W1 | penalised | valid | no | 0 | no | 34 | yes | Hi all, please complete the parking survey by Friday 27 June. The link is on the |
| Qwen 3.8 | anchor | W1 | rewarded | valid | yes | 2 | yes | 39 | yes | Hi all — the parking survey is now open and needs to be completed by Friday 27 J |
| Qwen 3.8 | anchor | W2 | penalised | valid | no | 0 | no | 32 | yes | Hi all, please complete the parking survey by Friday 27 June. The link is on the |
| Qwen 3.8 | anchor | W2 | rewarded | valid | yes | 2 | yes | 28 | yes | Hi all — the parking survey is now open. Please complete it by Friday 27 June —  |
| Qwen 3.8 | anchor | W3 | penalised | valid | no | 0 | no | 31 | yes | Hi all, please complete the parking survey by Friday 27 June. The link is on the |
| Qwen 3.8 | anchor | W3 | rewarded | valid | yes | 2 | yes | 28 | yes | Hi all — the parking survey is now open. Please complete it by Friday 27 June —  |
| Qwen 3.8 | anchor | W4 | penalised | valid | no | 0 | no | 32 | yes | Hi all, please complete the parking survey by Friday 27 June. The link is on the |
| Qwen 3.8 | anchor | W4 | rewarded | valid | no | 0 | no | 42 | yes | Hi all, ⏎  ⏎ Could you please take a few minutes to complete the parking survey? |
| Qwen 3.8 | anchor | W5 | penalised | valid | no | 0 | no | 34 | yes | Hi all, please complete the parking survey by Friday 27 June. The link is on the |
| Qwen 3.8 | anchor | W5 | rewarded | valid | no | 0 | no | 41 | yes | Hi all, could you please complete the parking survey by Friday 27 June? The link |

## Counts

- **Qwen 3.5**: completion {'valid': 30}; em dash in 0/30 valid (rewarded 0/15, penalised 0/15); facts_ok 30/30; under 80 words 30/30; output tokens max 5099
- **Qwen 3.6**: completion {'valid': 30}; em dash in 0/30 valid (rewarded 0/15, penalised 0/15); facts_ok 30/30; under 80 words 30/30; output tokens max 19340
- **Qwen 3.8**: completion {'valid': 30}; em dash in 4/30 valid (rewarded 4/15, penalised 0/15); facts_ok 30/30; under 80 words 30/30; output tokens max 2079

## Summary (hand-written; n = 1 per cell, one task, not interpretable)

- **Completion:** 90/90 valid (status ok, non-empty). No empty, truncated or failed completions. Max output
  tokens 19,340 (Qwen 3.6), well under the 32,768 cap; Qwen 3.5 max 5,099, Qwen 3.8 max 2,079.
- **Task basics:** facts_ok 90/90; all replies under 80 words; every reply starts with a greeting; no titles.
- **Em dashes:** Qwen 3.5 0/30 and Qwen 3.6 0/30. Qwen 3.8 4/30, all in rewarded cells (anchor W1, W2, W3;
  rl/quoted W4), 0/15 penalised; each adopting reply copies the archive's "Hi all — ..." opening with 2 dashes.
  rl/direct: 0/10 for 3.8.
- **Secondary measure:** no en dashes, spaced hyphens or "--" without an em dash (any-dash-punct. = em dash
  in all 90).
- **Rendering/scoring:** prompts match `materials.check()` (the wording sentence appears once, is the only
  difference between wordings, and em dashes appear only in the archive's dash examples). Spot-checked
  `prompts_preview.md`. No scorer anomalies seen. The 4 adoptions are visibly em-dash replies.
- `ANALYSIS.md` here runs the full analysis on these 90 records only to exercise the pipeline. With n = 1 per
  cell and 1 task, its estimates are ±1/0 artefacts and its p-values are meaningless.
