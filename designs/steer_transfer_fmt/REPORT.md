# Formatting steering transfer: report (2026-10-31)

**Question.** Outside sending, does Qwen 3.8's automated-minus-human direction (criterion unspecified), added directly
to Qwen 3.5, raise score-induced format overrides against the user's request? Does it beat 3.5's own direction? And, in
reverse, how does 3.5's direction compare with 3.8's own on 3.8?

Plan: `PLAN.md`, revision 1 frozen before generation. Deviations: `AMENDMENTS.md`. Auto tables:
`run/main/REPORT_auto.md` and `run/main/results.json`. Sending reverse transfer: `../steer_transfer/REPORT_reverse.md`.

## Answer, per family

| Family | 3.5: 3.8 dir +0.3 vs unsteered (P1) | 3.5: 3.8 dir − 3.5 dir at +0.3 (P2) | 3.8: 3.8 dir − 3.5 dir at +0.3 (P3) |
|---|---|---|---|
| title | **+0.062 [+0.023, +0.108], Holm p = 0.004** | +0.000 [−0.051, +0.051], Holm p = 1 | +0.085 [−0.017, +0.187], Holm p = 0.70 |
| sign-off | +0.017 [−0.011, +0.051], Holm p = 1 | +0.017 [−0.017, +0.051], Holm p = 1 | +0.034 [−0.085, +0.153], Holm p = 1 |
| bullets | +0.047 [+0.011, +0.084], Holm p = 0.088 | −0.032 [−0.084, +0.021], Holm p = 1 | **−0.232 [−0.332, −0.132], Holm p = 0.002** |

Missing and non-valid bounds are within ±0.006 of every estimate; no primary cell has a missing item.

- **Transfer beyond sending on 3.5: partly.**
  - **Titles:** the 3.8 direction at +0.3 raises score-following overrides from 2/176 to 13/176 (P1, Holm-significant).
    - Overrides stay at 0 under reversed and tied scores.
    - Competence and validity are unchanged.
    - It is distinct from both random directions: +0.068 [+0.028, +0.116].
  - **Bullets:** the same pattern (2 → 11 of 190), but it misses Holm significance (p = 0.088).
  - **Sign-offs:** no effect.
- **The transferred direction does not beat 3.5's own direction outside sending (P2 ≈ 0 in all three families).**
  - 3.5's native direction does just as well at +0.3: titles 13/176, bullets 17/190.
  - This differs from sending, where the 3.8 direction won by +0.21 and native +0.3 did nothing.
  - The sending result therefore looks task-specific. On formatting, 3.5's native direction is not "weak at +0.3".
- **On 3.8, the formatting contrasts are not interpretable as direction-specific.** Norm-matched random directions move
  3.8's overrides as much as the grader directions do, and in both signs:
  - random1 at −0.3: +0.20 / +0.27 / +0.20 (title / sign-off / bullets);
  - random1 at +0.3: −0.15 / −0.06 / −0.16;
  - random0 at +0.3 on bullets: +0.13.

  The one significant P3 (bullets, −0.23) comes from 3.8's native direction *reducing* bullets (−0.12) while 3.5's
  direction raises them (+0.12), and random0 +0.3 does the same (+0.13). It does not mean "3.5's direction is stronger"
  in any directional sense. The sending reverse transfer showed the same random-direction sensitivity on 3.8.
- **Score specificity is total.** Across every model, family and condition (2 × 3 × 13 × 176–190 generations):
  - the override shift under tied scores is 0;
  - the violation shift under reversed scores is 0.

  No condition adds the feature against the scores or makes formatting generally worse. So there is no output bias and
  no disruption in the PLAN sense.

## Strength curves (DiD conflict − reversed vs unsteered)

| Family | Target | Direction | −0.3 | −0.1 | 0 | +0.1 | +0.3 |
|---|---|---|---|---|---|---|---|
| title | 3.5 | xfer (3.8 dir) | +0.011 | +0.017 | 0 | +0.045 | **+0.062** |
| title | 3.5 | native (3.5 dir) | −0.011 | +0.017 | 0 | +0.045 | **+0.062** |
| title | 3.8 | xfer (3.5 dir) | −0.256 | −0.057 | 0 | −0.102 | −0.040 |
| title | 3.8 | native (3.8 dir) | −0.205 | +0.028 | 0 | −0.091 | +0.045 |
| sign-off | 3.5 | xfer | +0.011 | 0.000 | 0 | −0.011 | +0.017 |
| sign-off | 3.5 | native | −0.011 | −0.011 | 0 | −0.011 | 0.000 |
| sign-off | 3.8 | xfer | 0.000 | +0.062 | 0 | −0.045 | +0.040 |
| sign-off | 3.8 | native | −0.040 | +0.108 | 0 | −0.011 | +0.074 |
| bullets | 3.5 | xfer | −0.011 | −0.011 | 0 | +0.026 | +0.047 |
| bullets | 3.5 | native | −0.005 | −0.005 | 0 | +0.016 | +0.079 |
| bullets | 3.8 | xfer | −0.216 | +0.111 | 0 | −0.195 | +0.116 |
| bullets | 3.8 | native | −0.137 | +0.100 | 0 | −0.205 | −0.116 |

- **On 3.5** both curves rise monotonically from about 0 to +0.06/+0.08 on titles and bullets. The floor makes negative
  strengths uninformative.
- **On 3.8** the curves are not monotone and resemble the random-direction shifts, which range from −0.16 to +0.27.

## Bridge and data quality

- **Bridge:** unsteered self-hosted override rates match the archived OpenRouter arm-B runs in every cell; every CI
  covers 0.
  - Title 3.8: 95/176 vs 28/50.
  - Sign-off 3.8: 34/176 vs 6/50.
  - Bullets 3.8: 92/190 vs 41/100.
  - 3.5: 2/176, 2/176 and 2/190, against 0–1 on the API.
  - Tied: 0 everywhere.
- **Accounting:**
  - **Planned:** 56,368 generations. 22 / 22 / 38 distinct scenarios per family, and 176 / 176 / 190 generations per
    cell.
  - **Recorded:** 56,355. **Valid:** 56,355. No failures, truncations or empties among recorded generations.
  - **Missing:** 13 Qwen 3.5 generations, still generating when the run was closed at 03:22 UTC (AMENDMENTS). None is in
    a primary cell.
  - The smoke run had 1 truncation (AMENDMENTS 2).
- **Competence (facts_ok):** it never drops beyond the thresholds. On 3.5 bullets it *rises* under +0.3 steering (xfer
  +0.15, native +0.13), meaning more complete drafts.

## Interpretation against the PLAN rules

- **Transfer beyond sending:**
  - supported for titles on 3.5 (P1, Holm), as a selective, score-specific increase;
  - suggestive for bullets (+0.047, p = 0.012 unadjusted; not Holm-significant);
  - absent for sign-offs, whose 3.5 base rate and 3.8 effect are both low.

  There is no pooled claim, because the families disagree.
- **Transferred vs native: no advantage on formatting** at +0.3, and the full curves overlap. Combined with sending
  (+0.21 for the 3.8 direction on 3.5), "the 3.8 direction is the more effective lever on 3.5" holds for sending only.
- **Reverse transfer on 3.8:** not interpretable for formatting, because of random-direction sensitivity. On sending,
  3.5's direction has a strong, signed effect on 3.8 that is clearly distinct from random
  (`steer_transfer/REPORT_reverse.md`).
- **Disruption and output bias:** none. Every effect requires the scores to favour the feature.
- **Not established:** an identical mechanism, that RL caused the release difference, or a "cheating persona".

## Run and cost

- **Session:** 2026-10-31 00:42–03:22 UTC on 10 × H200 at peak.
  - Pods: 3.5 on sf-35-15, sf-35-17 and sf-35-31; 3.8 on sf-38-18 and sf-38-19.
  - Two pods in EUR-IS-4 never got SSH and were replaced.
- **Shared session:** the sending reverse transfer ran in the same session.
- **Cost:** about $119 (balance $197.55 → $78.62), plus $41 for the aborted first attempt (AMENDMENTS 1).
- **Shutdown:** all pods are terminated, and there are no volumes.
