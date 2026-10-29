# Morning summary — workstream C (IFEval × frame × grader evidence), 2026-10-29

**Everything planned for C ran to completion**: main 16,128/16,128, evaluator-applicability add-on 2,592/2,592
(+576 recognition probes), optional-access discovery 576/576, reference check 256/256, plus smoke (48) and the dev
screen (320). 0 failed items. Total ≈ **$32.6** (generation $10, blind judge $22). Generation 03:04–05:32 UTC.
Full write-up: `REPORT.md`; figures in `figure/`; status `STATUS.md`.

## What we found

1. **Qwen 3.8 responds a little to a large score advantage for breaking the user's rule — almost only in one
   subtype.** At +0.50 its violation rate rose from 0.3% → 4.5% (RL frame), 0.5% → 2.8% (evaluation), 0.2% → 1.9%
   (ordinary). Nearly all of this is JSON tasks where it adds a lead-in sentence before the JSON, copying the
   high-scored example's edit (RL: 13/48 blocks vs 0/48 tied). Its reasoning often cites the scores; that is trace
   text, not evidence of intent.
2. **Only one of 8 primary tests survives Holm:** G_3.8 (RL, +0.50 vs +0.05) +3.6 pts [+1.6, +5.7], Holm p = 0.009.
   RL vs ordinary (A_3.8) +2.6 pts [+0.5, +4.8], nominal p = 0.035, Holm p = 0.25 — suggestive only. RL vs
   evaluation (B_3.8) and the 3.8 − 3.5 difference are not distinguishable from zero.
3. **Qwen 3.5 doesn't move** in any condition (all cells ~1–2%).
4. **Grader existence alone does nothing**, nor do unscored examples or small (+0.05) score gaps; frame sentences
   with no grader change nothing.
5. **Applicability (10B): null.** The JSON effect is just as large when the scores are labelled as coming from a
   *different* evaluator, even though both models identify match/mismatch correctly 576/576 when asked.
6. **Discovery:** Qwen 3.8 opens the history file in 10–21% of episodes, Qwen 3.5 ≤ 4%. Violations don't track the
   scores; the multi-tool setting itself raises Qwen 3.8's JSON lead-ins.
7. **Reference check (10A), most important for interpretation:** the original "bundle" prompts, replayed
   byte-identically on fresh blocks, still give large Qwen 3.8 effects (sending 10/16, bullets 9/16 at +0.50 vs
   0/16 tied). The same inputs in this study's tool-record rendering give 0/16. Workstreams A and B (other
   session, `designs/overnight_common/MORNING_SUMMARY.md`) reach the same conclusion with their own matched design.
   **The large earlier effects depend on the old presentation; small or null effects here are conditional on
   this delivery, not evidence that Qwen 3.8 ignores grader evidence.**

## Keep apart

- Generic evaluation vs RL wording: ordering ordinary < evaluation < RL for Qwen 3.8, but the RL-specific step isn't
  established.
- Grader existence vs its preference: only the preference (large +0.50 scores) matters.
- Direction vs magnitude: +0.05 ≈ tied; the user-aligned −0.50 didn't lower violations below the floor.
- Visible incidental records vs voluntary discovery: separate experiments, not pooled.
- This is an inference-time behavioural intervention, not a causal claim about RLVR training or split personas.

## Caveats

- One subtype (JSON) carries the effect; the macro numbers average it with seven near-floor subtypes.
- Upstream checker artefact: 93/106 lowercase/uppercase "violations" fail only `langdetect`'s English check
  (exploratory case-only rescoring leaves conclusions unchanged).
- Three analysis-code amendments, all before the affected outcomes were viewed (`AMENDMENTS.md`).
- A 90-item blinded review sheet is ready at `run/main/review/REVIEW_SHEET.md`; **no human has reviewed it**.

## Natural next step

A fully crossed frame × representation experiment (old bundle features vs this tool-record delivery, one feature
at a time) to find which presentation feature produces the large earlier effects.
