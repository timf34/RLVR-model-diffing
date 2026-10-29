# Experiment B: cross-behaviour transfer. Analysis plan (frozen with `run/manifest.json` before generation)

Label: **EXPLORATORY → pre-specified**. Shared design: `../overnight_common/DESIGN.md`; interface:
`../overnight_common/INTERFACE.md`.

## Question
Does a history that scores one violation (SOURCE) change a different, never-rewarded behaviour (TARGET)? Does that
depend on whether earlier users prohibited or permitted the source behaviour, and on the current framing?

## Directions (6), each with fresh scenarios
- title → limitation
- limitation → title
- em dash → certainty
- certainty → em dash
- sign-off → sending (tool episode)
- sending → sign-off (tool episode)

The current user states both requirements explicitly: it prohibits the source behaviour and requires the
target-correct behaviour. Archives contain nothing about the target. Archive responses differ only in the source
feature.

## Historical permission (the crucial control)
- **forbidden:** the earlier users explicitly prohibited the source behaviour (or, for limitation/certainty
  sources, required the limitation / asked to keep the uncertainty). At a positive gap, the violating response
  scored higher.
- **permitted:** the earlier users explicitly allowed the source behaviour without requiring or preferring it.
  For certainty, they asked for a hypothetical write-up "as if confirmed".
- The responses and their scores are identical across the two versions; only the permission clause in the earlier
  requests differs (machine-checked).

## Conditions
- Both models, both matched frames (as in A).
- {forbidden, permitted} × gap {0, +0.50}, plus a `none` history baseline (one per current task and frame; the
  ordinary and episode `none` prompts are byte-identical, so they are replicate samples).
- 16 blocks per direction, one generation per cell: 6 × 16 × 2 × 2 × 5 = 1,920 core episodes. An optional +0.05
  extension in both permission conditions is added only if the pre-freeze estimate allows the whole balanced
  extension (see the addendum).
- Exposure, scores, statuses, retries and queue are as in A.

## Outcomes
- TARGET and SOURCE are scored independently on every valid trial, with the same scorers and judge as A.
- **All assigned trials are analysed.** We never condition on whether the model followed the source incentive.

## Primary contrasts (Qwen 3.8). Holm across the 8 primaries of A and B together
- **B1:** D(episode) = [T(forbidden, +0.50) − T(forbidden, 0)] − [T(permitted, +0.50) − T(permitted, 0)], on the
  TARGET violation, computed per block, averaged within direction, then equal-weighted over the 6 directions.
- **B2:** D(episode) − D(ordinary).
- Inference: block-level sign-flip (strata = direction), cluster-bootstrap CIs, Holm with A1–A6.

## Secondary
- The simple TARGET change (+0.50 − 0) within each permission condition, per direction and pooled. Transfer may
  occur in both conditions; a small B1 does not show the absence of transfer.
- The SOURCE outcome by condition (manipulation check). If the source incentive has little effect, the report says
  that limits the interpretation of absent transfer.
- Each direction separately, Qwen 3.5, 3.8 − 3.5, and no-history vs tie.

## Interpretation
- Positive transfer would support broader generalisation of the demonstrated pattern. It would not show an internal
  persona, or separate persona selection from in-context learning.
- These are inference-time results only.

## Sample size, cost and budget
See the "Pre-freeze addendum" below, filled in from the operational pilot before freezing.

## Pre-freeze addendum (2026-10-29, ~03:20 UTC; written before any main-run generation)

**Sample size:** the full target (16 main blocks per direction) **plus the balanced +0.05 extension** in both
permission conditions, because the pre-freeze estimate allows the whole extension. That is 6 × 16 × 2 frames ×
(5 core + 2 extension cells) × 2 models = **2,688 episodes**. The +0.05 cells are **secondary**; the primaries B1
and B2 use only 0 and +0.50, as planned.

**Operational pilot** (`pilot/ESTIMATE.md`; 60 items on smoke blocks only, all valid):
- Projected cost: about $3.4 including the extension.
- Wall time: about 0.35 h at 32 concurrent per model.

**Budget:**
- `generate --budget 40` is a hard stop.
- The judge budget is $15.
- The overnight batch cap is $400.

**Validation done before freezing:**
- `cli.py B validate`: 0 errors, 0 warnings. That includes the checks that forbidden/permitted requests differ
  only in the permission clause, and that archive responses contain no target features.
- Smoke test: 12/12 valid.
- The smoke-data analysis gives source and target labels on every valid trial.
- The scorer tool-name fix (see the grouped_replication addendum) applies here too, for `send` source/target and
  for sign-offs in drafted bodies.

**Deviations:** the same as the grouped_replication addendum items 1–5. Also, the `certainty` source permitted
condition uses a hypothetical-assumption request ("assume the trial worked and write it as if confirmed"), as the
brief suggests. Every direction kept a clean permission manipulation, so no pair was replaced.
