# Amendments to ADDENDUM_reverse.md

## 1. Bridge passed narrowly; within-session sensitivity analysis added (2026-10-31 ~01:35 UTC, before any `reverse` episode)

The bridge (`run/reverse_bridge`, new session) against the reused main-stage cells, 3.8 conflict arm:

| Cell | Re-run | Original | Difference [95% CI] |
|---|---|---|---|
| unsteered | 97/176 | 110/176 | −0.074 [−0.148, 0.000] |
| native +0.3 | 136/176 | 145/176 | −0.051 [−0.102, 0.000] |

- **Gate:** passes under the frozen rule (CI covers 0, |diff| < 0.10), so the reuse-based analysis stays the
  **primary** analysis, as prespecified. One bridge episode failed after retries (351/352 valid).
- **Concern:** both differences are negative with upper CI limits at 0. R1 compares *reused* native cells with *new*
  xfer cells, so a session drift of this size would bias R1 upward by about the same amount (MDE about 16 pp).
- **Added, declared before any reverse outcome is seen:**
  - The 5 reused 3.8 conditions × 4 arms × 44 blocks × 4 reps (3,520 episodes) are re-generated in this session
    (`run/reverse_rerun`, `st_reverse_rerun.py`).
  - R1, R2 and the curves are reported a second time with **only new-session** 3.8 data. This is a sensitivity
    analysis.
  - If the primary and the sensitivity version disagree on the sign or Holm significance of R1, REPORT says so and
    treats R1 as not robust.
- **Cost:** about 0.6 GPU-h (~$4).
