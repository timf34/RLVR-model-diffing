# Addendum: Qwen 3.6 (run 2026-10-31)

**Question.** Is there a smooth trend from Qwen 3.5 to 3.6 to 3.8 in following the displayed grader against the
user, under strong vs weak RL framing?

**Answer.** Mostly yes. Under strong RL framing, Qwen 3.6 falls between 3.5 and 3.8 on sending, bullets, and the
all-three-features factorial cell, roughly halfway. Titles + sign-offs is the exception. There, 3.6 follows the
grader at a low rate (~10%) whatever the framing, so framing makes no difference for 3.6 on that task.

![three-model slope](figure/q36_slope.png)

## What was run

- Qwen 3.6 replays Qwen 3.5's exact frozen items: the same prompts, blocks and reps. That covers Part 1, Part 2 and
  the factorial, 4,848 episodes in all (`pa_q36.py`; outputs in `run_q36/`).
- Serving: `experiment.grading.3way.json` (Alibaba only, no fallbacks), the same entry as every earlier 3.6 run.
- The episode loop, temperature, token cap and timeout are unchanged. The frozen 3.5/3.8 study in `run/` was not
  touched.
- Outcomes come from the same rule-based scorers. There were 6 non-valid episodes (empty replies), all excluded.
- Cost: $52.88 in about 3.5 h. That is twice the pre-run estimate, because 3.6 reasons at length on titles and
  bullets.
- This is descriptive and outside the frozen protocol, so no Holm family. CIs are block bootstrap.
- Tables come from `pa_q36_compare.py`, which writes `run_q36/COMPARE.md` and `run_q36/compare.json`.

## Strong vs weak RL framing (Part 1, score effect in points, +0.50 minus tied)

| task | framing | Qwen 3.5 | Qwen 3.6 | Qwen 3.8 |
|---|---|---|---|---|
| Sending | strong | +7 [+3, +13] | **+45** [+34, +57] | +66 [+55, +77] |
| Sending | weak | +0 | +5 [+0, +10] | +0 |
| Titles + sign-off | strong | +0 | **+9** [+3, +16] | +33 [+23, +44] |
| Titles + sign-off | weak | +0 | **+15** [+6, +24] | +1 [+0, +4] |
| Bullets | strong | +2 [+0, +5] | **+23** [+12, +35] | +41 [+28, +54] |
| Bullets | weak | +0 | +3 [+0, +6] | +0 |
| Sending + titles | strong − weak | +4 [+1, +6] | +17 [+8, +26] | +49 [+41, +57] |

**Titles detail (3.6).** Grader-following at +0.50 was low in every cell:
- strong framing: 4/35 on original blocks, 2/32 on fresh;
- weak framing: 4/36 on original blocks, 6/32 on fresh;
- tied scores: 0 in every cell.

So 3.6 responds a little to the scores here, but not to the framing. With counts this small, the strong-vs-weak
difference (−6 [−18, +6]) is indistinguishable from 0.

## Factorial (sending + titles): how many of the three key features are at the strong level

The three features are (a) the scorer applies to the current reply, (c) the old request wording, and (d) the scores
inline in the user turn.

| strong features | Qwen 3.5 | Qwen 3.6 | Qwen 3.8 |
|---|---|---|---|
| 0 | +0 | +0 | +1 [+0, +2] |
| 1 | +0 | +4 [+1, +6] | +3 [+2, +5] |
| 2 | +1 [+0, +2] | +14 [+9, +19] | +20 [+15, +24] |
| 3 | +5 [+0, +11] | +23 [+14, +34] | +44 [+36, +52] |

Qwen 3.6 shows the same conjunction pattern as 3.8, at about half the size. One feature does almost nothing, and the
effect builds with two and three. Qwen 3.5 stays near zero throughout.

## One feature at a time (Part 2, fresh blocks, sending + titles)

Qwen 3.6 has one generation per cell, as 3.5 does, so these numbers are noisy. Removing (c) or (d) from the strong
framing lowers 3.6's effect, as it does for 3.8:
- (c): +19 [+8, +30] for 3.6, +27 for 3.8;
- (d): +16 [+4, +27] for 3.6, +28 for 3.8.

Removing (a) does little for 3.6: +6 [−6, +19]. Adding any single feature to the weak framing restores nothing for
any model. Full table: `run_q36/COMPARE.md`.

## Caveats

- Qwen 3.6 is served by Alibaba at unstated precision, while 3.5 and 3.8 are bf16 hosts. The serving difference
  can't be separated from the model difference.
- Three model versions give three points. "Smooth" here means 3.6 lands in between, not that the trend is linear.
