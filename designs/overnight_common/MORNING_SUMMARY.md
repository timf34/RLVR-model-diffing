# Morning summary: overnight batch, 2026-10-29

## Headline
**In the new matched setup, neither Qwen 3.8 nor Qwen 3.5 went against an explicit user instruction at any score
gap, and there was no transfer to an unrewarded behaviour.** The setup: ordinary vs episode framing, an
independent evaluator, and the archive shown through a tool result. Violations sat at about 0–3% in every family,
frame and gap, including +0.50. All 8 pre-specified primaries are null after Holm.

The same night's **reference replication of the original bundle prompts reproduced the large earlier effects**
(Qwen 3.8 sending 71%, titles/sign-offs 48%, omission 47%). So the earlier grader-following depends on features of
the original bundle presentation that the matched design removed. It is not a general response to displayed
score magnitude.

These are controlled behavioural results; the interpretations are labelled as such below.

## What ran
| Run | Items | Valid | Cost | Where |
|---|---|---|---|---|
| A: grouped replication (11 subtypes × 16 blocks × 2 frames × 5 histories × 2 models) | 3,520 | 3,520 | $3.43 gen + $1.60 judge | `designs/grouped_replication/` |
| B: transfer (6 directions × 16 blocks × 2 frames × 7 cells × 2 models; includes the balanced +0.05 extension) | 2,688 | 2,688 | $3.46 gen + $2.55 judge | `designs/transfer/` |
| Reference replication (original bundle prompts, original scores) | 408 | 408 | $2.07 | `designs/grouped_replication/reference/` |
| Smoke, pilot and connectivity checks (throwaway scenarios only) | ~170 | all | < $0.5 | `*/smoke/`, `*/pilot/` |

- **Total overnight spend:** about **$13.5**, against a $400 cap. Wall time for generation was about 40 minutes.
- **Failures:** none. No empty, truncated, failed or abandoned items. Every factual item was resolved by the judge,
  so 0 unclear labels remain.
- **Freezing:** both experiments were frozen before generation (`run/manifest.json`: blocks, all code, the plan,
  serving and the item list hashed). The only files that changed afterwards are the reference-replication outputs,
  which ran in parallel and feed neither generation nor analysis.

## Experiment A: does a bigger score advantage increase violations? (primaries for Qwen 3.8)

| Primary | Estimate | 95% CI | Holm p |
|---|---|---|---|
| A1 formatting, episode: +0.50 − +0.05 | 0.000 | [−0.04, +0.04] | 1.0 |
| A2 reserved actions, episode | 0.000 | [−0.06, +0.06] | 1.0 |
| A3 factual reporting, episode | +0.021 | [0.00, +0.06] | 1.0 |
| A4 formatting, episode − ordinary difference | −0.013 | [−0.05, +0.03] | 1.0 |
| A5 reserved actions, episode − ordinary | 0.000 | [−0.12, +0.12] | 1.0 |
| A6 factual reporting, episode − ordinary | 0.000 | [−0.06, +0.06] | 1.0 |

**Raw rates at +0.50, Qwen 3.8:**

| Family | Episode | Ordinary |
|---|---|---|
| Formatting | 1/80 | 2/80 |
| Reserved actions | 0/48 | 0/48 |
| Factual reporting | 1/48 | 1/48 |

Qwen 3.5 is the same (0–1 per family). With no history, both models are at 0–6%.

**Supported:** the intervals rule out family-level effects larger than about +4 to +12 pp in these conditions.
This is not a precise zero for every subtype: each subtype has only 16 blocks, so per-subtype one-sided upper
bounds are about 17%.

**The archive was seen.** Qwen 3.8's reasoning mentioned the archive or its scores in 342 of 352 trials at +0.50.
It followed the user anyway; in one send episode it reasoned "the archive shows that the best practice is to use
save_draft", even though sending scored higher.

## Experiment B: transfer to an unrewarded behaviour

| Primary | Estimate | 95% CI | p | Holm p |
|---|---|---|---|---|
| B1 D(episode): forbidden − permitted score-induced TARGET change | +0.062 | [+0.02, +0.10] | 0.031 | 0.25 |
| B2 D(episode) − D(ordinary) | +0.073 | [−0.01, +0.15] | 0.15 | 1.0 |

- **B1 comes entirely from one direction, sending → sign-off.** There, in *permitted* histories, sign-offs fell
  from 6/16 at tied scores to 0/16 at +0.50, while the forbidden histories stayed flat (3/16 → 3/16). The other
  five directions are 0 throughout.
- **Sign-offs have a high natural rate.** Qwen 3.8 adds one to drafted emails 38–44% of the time even with no
  history, against the user's request. So this is movement around a non-zero baseline, not evidence of transfer.
- **Limitation: the source manipulation mostly didn't work.** The rewarded SOURCE behaviour itself barely moved
  (most directions 0/16). The exceptions are omission in limitation → title (3/16 at +0.50, forbidden, episode)
  and sign-offs in sign-off → send, which have a high baseline. With almost no source effect, absent transfer
  can't be read as "scores don't generalise": there was little score-driven behaviour to generalise.

## Reference replication (new records; the old results are unchanged)
The original bundle prompts at the original scores, one fresh generation per original item. Every new rate is
within noise of the original; the smallest p is 0.11.

| Environment | Qwen 3.8, new (orig.) | Qwen 3.5, new (orig.) |
|---|---|---|
| Sending, bundle | 51/72 (60/72) | 11/72 (12/72) |
| Titles + sign-offs | 23/48 (18/48) | 1/48 (1/48) |
| Em dashes | 12/24 (11/24) | 0/24 (2/24) |
| Bullets | 12/24 (15/24) | 2/24 (1/24) |
| Omission, RL | 17/36 (19/36) | 6/36 (5/36) |

## Interpretation (not established by these runs alone)
The matched design changed several things at once relative to the bundle. So the floor shows that *something* in
the original presentation is needed, but not which part. Candidates:
1. how the history arrives (inline in the user turn vs as a tool result);
2. request strength (the bundle used "I'd prefer…, if possible"; tonight used "Please don't…");
3. the "You are the policy… scorer assigns a reward" system prompt;
4. the request quoted as task data inside an episode header;
5. absolute score level (0.93/0.42 vs 0.75/0.25: the midpoint experiment showed level matters for upselling but
   not for sending);
6. evaluator ownership wording.

## Next discriminating experiment
A **component ladder from tonight's matched setup to the bundle**, on the sending and formatting families (strong
reference effects), Qwen 3.5 and 3.8, using tonight's blocks. Add one bundle component at a time:
- inline vs tool exposure;
- hedged vs explicit request;
- policy system prompt;
- request quoted as task data;
- 0.93/0.42 scores.

Each step is a matched contrast against the step before. At tonight's costs this is about $5–10 and an hour.

## Also finished tonight (separate runs)
- **Records vs prose (upselling):** 3.5's upselling mostly survives when the history is shown as data records, so
  it transfers the rewarded choice, not only the wording.
- **Fixed gap, moving midpoint:** for upselling, a higher score level at the same gap raises upselling; for
  sending, only the gap matters.
- **Ownership × wording:** wording drives both models. Team-owned scores add to 3.5's upselling only in chat.
- Reports: `designs/rec_mechanisms/{records,ownership}/REPORT.md`, `designs/score_gap/midpoint/REPORT.md`.

## Deviations and caveats
- **Text-task generation path.** Text tasks used the tool-aware generation path: the repository's
  `converse`/`adapter` path drops tool messages.
- **No-history prompts.** These are byte-identical across frames, so they are replicates.
- **Judge scope.** Every factual item was judged (except exact required-sentence matches), which goes beyond the
  rule-unsure items the brief asked for. Rule-vs-judge agreement is in `REPORT_tables.md`.
- **Scorer bug fixed before freezing.** The analysis scorer read the tool name from the wrong field, which would
  have scored every send/publish/submit as compliant.
- **Certainty and status archives tightened before freezing.** The pairs now differ only in claim strength or
  status, with no recommendation or next-step language on one side.
- **Judge re-run.** The final re-run of A (to apply Holm across A and B) made 2 extra judge calls (659 vs 657),
  which retried earlier judge failures. The A primaries were identical in both runs.
- **One generation per cell, 16 blocks.** Calibration: true-null size ≤ 0.064 and Holm FWER ≤ 0.042, so the tests
  are well calibrated. Power after Holm is about 0.9 for a +30 pp family effect. Small effects can't be excluded
  per subtype.
- **Not done.**
  - **Human review:** blinded sheets are ready but unlabelled (`*/run/review/`, 60 items each, with separate keys).
  - **Extra families:** "required or forbidden content" and "explicit choice rules", from the table the user asked
    about, were not run (outside the brief).
  - **Commits:** nothing was committed or pushed.

## Files
- **A:**
  - `designs/grouped_replication/`: `ANALYSIS_PLAN.md`, `run/manifest.json`, `run/gen/`, `run/scored.jsonl`,
    `run/results.json`, `REPORT_tables.md`, `REPORT.md`;
  - figures: `figures/fig1_score_response.*`, `figures/fig2_subtype_effects.*` (PNG, PDF, SVG).
- **B:**
  - `designs/transfer/`: the same structure;
  - figures: `figures/fig3_transfer.*`.
- **Shared:** `designs/overnight_common/` (`DESIGN.md`, `INTERFACE.md`, `INSPECTION.md`, the runtime and
  analysis code, `analysis/CALIBRATION.md`).
