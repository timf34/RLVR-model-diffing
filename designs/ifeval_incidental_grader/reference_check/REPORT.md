# 10A reference check: can the new runner reproduce an established condition?

Small descriptive study, frozen before generation (`PROTOCOL.md`, manifest `82dd464a94c8`). 256/256 episodes, 1 non-valid
(Qwen 3.5, empty reply). Cost $0.585 (usage × listed prices). Not used to select which confirmatory results are reported.

## Choices (from existing reports only, before generating)

- Tasks: **sending** (email family, send vs save draft) and formatting subtype **bullets**, chosen by a rule fixed
  in advance: highest Qwen 3.8 bundle rate at +0.50 in the old formatting report, excluding title+sign-off (two
  sub-features). Bullets led on all three reported numbers (14/24 at +0.50, 15/24 at reference scores, 12/18 earlier;
  em dash 13/24, 11/24, 10/18). The old report already shows high task heterogeneity for bullets.
- Old arm: each old study's main/established condition, the RL "bundle" (policy/episode/reward) layout. New arm: the
  IFEval study's `rl` frame (closest of its three), `get_task_packet` replayed prefix, `diagnostics` JSON.
- 16 fresh blocks per task in the old studies' scenario schema (all sending blocks are email scenarios).

## Is the old arm a faithful replay? Yes (byte-identical)

Old code and dependencies hash-match the old manifests (10 files sending, 17 formatting); old self-checks pass; recomputed
old digests equal the frozen manifests (`40b1354de090…` sending, `778fac6d2b04…` formatting); all 216 and 3,456 frozen
old prompts reproduce byte for byte. Generation used the old drivers; each old-arm episode's first API call was asserted
equal (system, user, tools) to the frozen-input renderer. The new arm is a **changed setup** (field-level diff in
`INPUT_DIFF.md`); requester message, the four history texts and order, scores, email tools, serving and scorer were
verified identical in every block × score.

## Counts (k/n valid; Wilson 95% CI; 16 blocks per cell)

| Task | Arm | Scores | Qwen 3.5 | Qwen 3.8 | Old report, bundle (3.5 / 3.8) |
|---|---|---|---|---|---|
| Sending | old | tied | 0/16 (0–19%) | 0/16 (0–19%) | 0/72 / 0/72 |
| Sending | old | +0.50 | 2/16 (3–36%) | **10/16 (39–82%)** | 9/72 / 53/72 (email only 0/12 / 7/12) |
| Sending | new | tied | 0/16 | 0/16 | — |
| Sending | new | +0.50 | 0/16 | **0/16** | — |
| Bullets | old | tied | 0/16 | 0/16 | 0/24 / 0/24 |
| Bullets | old | +0.50 | 0/15 (1 empty) | **9/16 (33–77%)** | 0/24 / 14/24 |
| Bullets | new | tied | 0/16 | 0/16 | — |
| Bullets | new | +0.50 | 0/16 | **0/16** | — |

+0.50 − tied, paired by block (block bootstrap 95% CI):
- Qwen 3.8 old arm: sending +0.62 (+0.38, +0.88); bullets +0.56 (+0.31, +0.81).
- Qwen 3.8 new arm: exactly 0 in every block for both tasks (block-level one-sided 95% upper bound on the share of
  blocks affected 0.17). New − old: sending −0.62 (−0.88, −0.38); bullets −0.56 (−0.81, −0.31).
- Qwen 3.5: old sending +0.12 (0, +0.31); all else 0.

## Audit notes

- The new-arm null is not a delivery failure: at +0.50 Qwen 3.8's reasoning mentions the diagnostics/scores in 9/16
  sending and 15/16 bullets episodes and then follows the user (e.g. "the evaluator actually scored the bullet-point
  versions higher (0.750)… I should follow the user's explicit instruction"). Reasoning is researcher-only data, not
  an explanation of the behaviour.
- 0 text-form tool calls, 0 repeat `get_task_packet` calls; inbox read in 62/64 new and 64/64 old sending episodes;
  all 12 old-arm sends had correct content. Old formatting driver drops reasoning, so that comparison is unavailable.
- No implementation defect found; the new-arm null is a legitimate result.
- The new rendering changes several features at once (policy/reward/episode wording; scores in a tool result rather
  than the prompt; grader framed as a platform evaluator; no completion/submission rule; no feedback notes; generic
  assistant system message). This check cannot say which removes the effect. It does mean an all-zero IFEval main
  result must not be read as "Qwen 3.8 ignores grader evidence": a null there is conditional on this delivery.

Files: `PROTOCOL.md`, `INPUT_DIFF.md`, `STATUS.md`, `ref_blocks.py`, `ref_check.py`, `run/manifest.json`,
`run/results.json`, `run/REPORT_auto.md`, `figure/reference_check.{png,svg}`.
