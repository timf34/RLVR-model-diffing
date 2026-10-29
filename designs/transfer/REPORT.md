# Experiment B: cross-behaviour transfer. Report (2026-10-29)

**Result: no evidence of transfer, and little source effect to transfer.**

Primaries (Qwen 3.8, Holm over 8 together with A):
- **B1** (forbidden − permitted score-induced TARGET change, episode): +0.062 [+0.02, +0.10], p = 0.031, Holm p =
  0.25.
- **B2** (B1 episode − ordinary): +0.073 [−0.01, +0.15], Holm p = 1.

**B1 is driven entirely by one direction, sending → sign-off.** There, sign-offs in *permitted* histories fell from
6/16 at tied scores to 0/16 at +0.50, while forbidden histories stayed at 3/16. Qwen 3.8 adds sign-offs 38–44% of
the time even with no history, so this is variation around a high baseline. The other five directions are at
0/16 for the target in every cell.

**The source manipulation itself mostly had no effect.** The rewarded behaviour stayed at 0/16 in most directions.
The exceptions are omission in limitation → title (3/16 at +0.50, forbidden, episode) and sign-offs, which have a
high baseline. Absent transfer therefore says little about generalisation: there was almost no score-driven source
behaviour in this setup (see Experiment A's floor).

**Validity:** 2,688/2,688 valid (including the balanced +0.05 extension, which is secondary); 0 unclear labels.

**More detail:**
- Full tables: `REPORT_tables.md`.
- Results: `run/results.json`.
- Figure: `figures/fig3_transfer.*`.
- Plan and deviations: `ANALYSIS_PLAN.md`.
- Review sheet: `run/review/`.
- Summary: `../overnight_common/MORNING_SUMMARY.md`.
