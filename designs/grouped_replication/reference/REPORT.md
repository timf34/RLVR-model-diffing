# Reference replication: report

**new reference replication, 2026-10-29; does not modify the original results.**

Each environment's reference cell was generated again with the original scores (0.930/0.420 and 0.900/0.390), with one fresh generation per original item. Prompts, serving (Qwen 3.5 `novita/bf16`, default thinking; Qwen 3.8 `deepinfra/bf16`, reasoning_effort medium; T 0.7, top_p 0.95, top_k 20, max_tokens 32768, 1200 s per call), generation code and scorers are the original runs' own, imported read-only. Original k/n come from each run's frozen `run/results.json`.

| Environment | Model | new k/n | original k/n | difference | Fisher p (two-sided) | new non-valid |
|---|---|---|---|---|---|---|
| sending | Qwen 3.5 | 11/72 (15%) | 12/72 (17%) | -1 pp | 1 | 0 |
| sending | Qwen 3.8 | 51/72 (71%) | 60/72 (83%) | -12 pp | 0.11 | 0 |
| formatting:titles_signoffs | Qwen 3.5 | 1/48 (2%) | 1/48 (2%) | +0 pp | 1 | 0 |
| formatting:titles_signoffs | Qwen 3.8 | 23/48 (48%) | 18/48 (38%) | +10 pp | 0.41 | 0 |
| formatting:emdash | Qwen 3.5 | 0/24 (0%) | 2/24 (8%) | -8 pp | 0.49 | 0 |
| formatting:emdash | Qwen 3.8 | 12/24 (50%) | 11/24 (46%) | +4 pp | 1 | 0 |
| formatting:bullets | Qwen 3.5 | 2/24 (8%) | 1/24 (4%) | +4 pp | 1 | 0 |
| formatting:bullets | Qwen 3.8 | 12/24 (50%) | 15/24 (62%) | -12 pp | 0.56 | 0 |
| omission | Qwen 3.5 | 6/36 (17%) | 5/36 (14%) | +3 pp | 1 | 0 |
| omission | Qwen 3.8 | 17/36 (47%) | 19/36 (53%) | -6 pp | 0.81 | 0 |

Rates are among valid replies. Non-valid replies (failed, truncated, empty, step limit, missing) are excluded and never counted as following the user. In the originals all reference items were valid. Fisher p values are unadjusted (10 tests).

Formatting sub-features (new, secondary): title|Qwen 3.5 1/24; title|Qwen 3.8 14/24; signoff|Qwen 3.5 0/24; signoff|Qwen 3.8 9/24

## Checks

- **sending**: 144 items (Qwen 3.5 72, Qwen 3.8 72); full-plan digest equals the frozen manifest (`40b1354de090`): True; prompt sha256 vs frozen `run/prompts.json`: all 144 match; code files changed since the freeze: none.
- **formatting**: 192 items (Qwen 3.5 96, Qwen 3.8 96); full-plan digest equals the frozen manifest (`778fac6d2b04`): True; prompt sha256 vs frozen `run/prompts.json`: all 192 match; code files changed since the freeze: none.
- **omission**: 72 items (Qwen 3.5 36, Qwen 3.8 36); full-plan digest equals the frozen manifest (`709ccd7c2d4f`): True; prompt sha256 vs frozen `run/prompts.json`: all 72 match; code files changed since the freeze: none.

## Cost

Total **$2.07** (budget $15), from returned token usage at conservative prices (Qwen 3.5 $0.30/$2.60 per M in/out, Qwen 3.8 $0.15/$1.875 per M; the higher of the runs' price tables).
- sending: targets $0.52
- formatting: targets $0.94
- omission: targets $0.57, judge 2 calls ≈ $0.04

Files: `PLAN.md`, `ref_run.py`, `<env>/plan.json`, `<env>/gen/<model>/*.jsonl`, `<env>/scored.json`, `omission/judge.jsonl`, `results.json`.
