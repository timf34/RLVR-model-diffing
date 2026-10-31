# Reverse transfer on the sending task: report (2026-10-31)

**Question.** Applied to Qwen 3.8 at matched strength, does 3.8's own automated-minus-human direction produce a larger
score-induced send effect than Qwen 3.5's direction? Plan: `ADDENDUM_reverse.md`. Deviations:
`AMENDMENTS_reverse.md`. Auto reports: `run/reverse/REPORT_auto.md` (primary) and `run/reverse_rerun/REPORT_auto.md`
(within-session sensitivity).

**Answer:**

- **3.5's direction works on 3.8.**
  - At +0.3 it raises 3.8's score-induced sending by **+0.11** [+0.02, +0.21] (R2, Holm p = 0.025), and by +0.17
    [+0.08, +0.26] in the within-session data.
  - At −0.3 it cuts sending from 62% to 8% (DiD −0.55).
  - On 3.5 the same vector did almost nothing at +0.3 (+0.02). **The target model matters substantially.**
- **3.8's direction vs 3.5's direction on 3.8 at +0.3 (R1): not robust.**
  - Primary (reused cells): +0.09 [+0.03, +0.15], Holm p = 0.004.
  - Within-session sensitivity: +0.07 [−0.01, +0.15], p = 0.11.
  - The two disagree on significance, so by the rule declared before any result (AMENDMENTS_reverse #1), R1 is treated
    as **not robust**.
- **Cross-model:** the 3.8 direction's advantage at +0.3 is larger in 3.5 (+0.21 [+0.13, +0.28]) than in 3.8
  (+0.07 to +0.09). The difference is −0.11 [−0.21, −0.02] (primary) or −0.14 [−0.24, −0.03] (within-session).
  - So the 3.8 direction is at least as strong as 3.5's in both models, but its edge is much smaller in 3.8, where 3.5's
    direction also works.
  - This is neither a clean "3.8's direction is stronger everywhere" nor "each is stronger in its source". It mostly
    says that the 3.5 vector is ineffective *on 3.5* at +0.3, not ineffective in general.
- **New caveat: random directions move 3.8's sending too, in the opposite direction to the grader directions.**
  - random0: −0.17 at +0.3, +0.12 at −0.3.
  - random1: −0.26 at +0.3, +0.06 at −0.3.

  3.8's resolution of this conflict is sensitive to norm-matched perturbations in general. The grader directions are
  still clearly distinct from random: xfer +0.3 minus mean(random +0.3) is +0.32 [+0.26, +0.39], and −0.3 gives −0.64.
  The main stage had random controls only on 3.5, where they were null.
- **Specificity holds everywhere.** 0 sends under reversed, tied and no-history scores in every 3.8 cell (176 per cell).
  Every effect is on how 3.8 resolves the conflict when the scores favour sending.

## Strength curves on 3.8

DiD (conflict − reversed) vs unsteered; n = 176 per cell, 44 blocks.

| Direction | −0.3 | −0.1 | 0 | +0.1 | +0.3 |
|---|---|---|---|---|---|
| 3.8 native (primary, reused cells) | −0.30 | −0.17 | 0 | −0.01 | +0.20 |
| 3.8 native (within-session) | −0.23 | −0.04 | 0 | +0.06 | +0.24 |
| 3.5 xfer (primary; DiD vs reused unsteered) | −0.55 | −0.25 | 0 | −0.01 | +0.11 |
| 3.5 xfer (within-session unsteered) | −0.48 | −0.19 | 0 | +0.05 | +0.17 |
| random0 / random1 | −0.17 / −0.26 at +0.3; +0.12 / +0.06 at −0.3 | | | | |

For reference, the main stage on 3.5 (DiD vs unsteered):

| Direction on 3.5 | −0.3 | −0.1 | +0.1 | +0.3 |
|---|---|---|---|---|
| 3.8 direction (xfer) | +0.01 | +0.05 | +0.12 | +0.22 |
| 3.5 direction (native) | +0.03 | +0.03 | +0.10 | +0.02 |

## Primary contrasts (Holm over 2)

| Test | Primary (reused 3.8 cells) | Within-session sensitivity |
|---|---|---|
| R1: native(3.8) +0.3 − xfer(3.5) +0.3, on 3.8 | +0.091 [+0.028, +0.153], Holm p = 0.004 | +0.068 [−0.011, +0.148], Holm p = 0.11 |
| R2: xfer(3.5) +0.3 vs unsteered, on 3.8 | +0.108 [+0.017, +0.205], Holm p = 0.025 | +0.170 [+0.080, +0.261], Holm p < 0.001 |

Additional, paired over blocks:
- native − xfer at −0.3: +0.24 [+0.17, +0.32]. The 3.5 direction suppresses 3.8's sending *more* than 3.8's own
  direction.
- At ±0.1 the two directions are indistinguishable.

## Bridge and session drift

- **Gate result:** the re-run unsteered and native +0.3 conflict cells sent 5–7 points less than the reused main-stage
  cells (−0.074 [−0.148, 0.000]; −0.051 [−0.102, 0.000]).
  - That passes the frozen gate, but only narrowly.
  - The full within-session re-run (3,520 episodes) shows unsteered 3.8 at 99/176, against 110/176 in the main stage.
- **Interpretation:** a modest session or hardware drift. It is why R1 is reported both ways and flagged as not robust.

## Health and accounting

- **Planned / recorded:**
  - reverse: 5,632 planned, 5,632 recorded (5,631 valid, 1 step-limit);
  - reverse_rerun: 3,520;
  - reverse_bridge: 352 (351 valid, 1 failed).
- **Failed after retries:** none. Failed attempts (5 across stages, all on the final model call after the episode's
  actions) were retried by key. Actions taken before a failure are counted, as in ERRATA.
- **Competence (task_done, no-history arm):** stable for the grader directions at ±0.3. It dropped for xfer +0.1
  (−0.14 [−0.22, −0.06]) and random1 −0.3 (−0.20 [−0.29, −0.11]), so those conditions are partly disruptive.

## What this does and does not show

- **Does show:** 3.5's vector, injected into 3.8 at 3.8's scale, has a strong, signed, score-specific effect on 3.8's
  sending. So the weak +0.3 effect of that vector on 3.5 is a property of the target, not only of the vector.
- **Not robust:** whether 3.8's own direction is stronger than 3.5's on 3.8 at +0.3.
- **Weakens all 3.8 conclusions:** norm-matched random directions also shift 3.8's sending, so 3.8 is generally
  steerable on this decision. The grader directions remain far from random.
- **Not established:** an identical mechanism, or an RL-training explanation.
