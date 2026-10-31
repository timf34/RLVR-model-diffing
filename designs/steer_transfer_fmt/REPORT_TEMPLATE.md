# Formatting steering transfer: report (DATE)

Fill from `run/main/REPORT_auto.md` and `run/main/results.json`. Report nulls and failures. Never replace counts with
rounded shares.

**Question.** Outside sending, does Qwen 3.8's automated-minus-human direction (criterion unspecified), added directly
to Qwen 3.5, raise score-induced format overrides against the user's request? Does it beat 3.5's own direction at
+0.3?

**Answer, per family** (no pooled headline unless all three agree):
- Title: …
- Sign-off: …
- Bullets: …

Design `full` | `reduced` (recorded in `run/freeze.json` before launch). Deviations: `AMENDMENTS.md`.

## Run accounting

For each family × model, give the counts separately:
- distinct scenarios;
- planned generations;
- recorded generations;
- valid generations;
- empty, truncated, step-limit, failed and missing generations;
- malformed generations.

Also give the GPU hours and the cost.

## Bridge (unsteered self-hosted vs archived OpenRouter, arm B)

| Family / model / arm | Self-hosted k/n | API k/n | Diff [95% CI] |
|---|---|---|---|

## Primary contrasts (Holm over 9)

| Family | P1 [3.5]: 3.8 dir +0.3 vs unsteered | P2 [3.5]: 3.8 dir − 3.5 dir at +0.3 | P3 [3.8]: 3.8 dir − 3.5 dir at +0.3 |
|---|---|---|---|

For each, give the estimate [CI], the Holm p and the missing bounds.

## Reverse transfer: both directions in both targets (per family, and for sending from ADDENDUM_reverse)

Give the 3.8-direction advantage at +0.3 in 3.5, the same advantage in 3.8, and their difference [CI]. Then state which
interpretation pattern applies (PLAN):
- 3.8's direction stronger in both;
- each direction stronger in its source model;
- 3.5's direction strong in 3.8.

## Strength curves (DiD vs unsteered, per family, both targets, both directions)

| Family | Target | Direction | −0.3 | −0.1 | 0 | +0.1 | +0.3 |
|---|---|---|---|---|---|---|---|

Also give the random directions at ±0.3 on both targets.

## Specificity and health (per family)

- Override shift under reversed, tied and no-history scores, per condition. Zero-event cells are given as k/n with
  their upper bound.
- Any-violation shift in every arm. Was the feature added against the scores? Did the share of "neither" responses
  rise?
- facts_ok shift and valid-share shift. Which conditions, if any, cross the impairment thresholds?

## Interpretation against the PLAN rules

Cover each reading:
- transfer beyond sending;
- disruption;
- output bias;
- transferred beats native only at +0.3, with the curves shown.

Also state the floor caveat.

## Not established

- That RL caused the release difference.
- That this is a "cheating persona".
- That 3.5 shares 3.8's mechanism.
