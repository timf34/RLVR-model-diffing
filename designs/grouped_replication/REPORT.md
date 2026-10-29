# Experiment A: grouped replication. Report (2026-10-29)

**Result: floor.** In the matched ordinary/episode design (independent evaluator, archive delivered through a
pre-filled tool call), neither Qwen 3.8 nor Qwen 3.5 violated the user's explicit instruction at any displayed
score gap, in any family. All six primaries (A1–A6) have Holm p = 1.
- **Formatting:** at +0.50, episode framing, Qwen 3.8 1/80 and Qwen 3.5 1/80.
- **Reserved actions:** 0/48 for both.
- **Factual reporting:** Qwen 3.8 1/48, Qwen 3.5 0/48.

Estimates and intervals:
- **A1–A3**, episode (+0.50 − +0.05): +0.000 [−0.04, +0.04]; +0.000 [−0.06, +0.06]; +0.021 [0.00, +0.06].
- **A4–A6**, episode − ordinary: −0.013 [−0.05, +0.03]; +0.000 [−0.12, +0.12]; +0.000 [−0.06, +0.06].

Each subtype has 16 blocks; an all-zero cell has a one-sided 95% upper bound of 0.17 at the block level.

**Validity and exposure:**
- 3,520/3,520 trials valid; 0 unclear labels after judging.
- Qwen 3.8's reasoning referred to the archive or its scores in 342/352 trials at +0.50, so the archive was seen.

**Reference replication** (`reference/REPORT.md`): the original bundle prompts at the original scores reproduce the
earlier large effects (Qwen 3.8: sending 71%, titles/sign-offs 48%, omission 47%). So the floor reflects the
change in presentation, not a failure to reproduce.

**More detail:**
- Full tables (denominators, per-subtype rates, secondary contrasts, judge agreement, task completion):
  `REPORT_tables.md`.
- Machine-readable results: `run/results.json`.
- Figures: `figures/fig1_score_response.*` and `figures/fig2_subtype_effects.*`.
- Plan and deviations: `ANALYSIS_PLAN.md`.
- Blinded human review sheet: `run/review/` (not yet labelled).
- Summary across both experiments: `../overnight_common/MORNING_SUMMARY.md`.
