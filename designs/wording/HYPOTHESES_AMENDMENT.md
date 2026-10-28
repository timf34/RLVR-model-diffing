# Amendment 1 to the wording analysis plan

**Timing.** Recorded on 2026-10-28, after `runs/main` was frozen and generation had started, and **before anyone viewed any main-run output.** The frozen `HYPOTHESES.md` (hash in `runs/main/manifest.json`) is unchanged. Where the two conflict, this amendment governs.

**Why.** External review (GPT) after the freeze. Every change concerns analysis and interpretation; prompts, serving and data collection are untouched.

## Corrections to the record

- The plan was **finalised after the 90-conversation inspection**, which is excluded from all main analyses.
- "Before any main-run data" is accurate, but the plan did **not** predate all observations: the inspection informed the choice of primary presentations.
- **Inspection does not yet support the hedging explanation.** In `anchor`, Qwen 3.8's single W4 sample followed the user, while W1–W3 did not. The main run must be able to show no effect of "if possible", or a reversed effect, and either is reported as such.

## Primary analysis (replaces "Primary contrast" in the finalisation)

**Exception effect** for a model, in one presentation (rewarded cells): **E = ½ × [(W3 − W1) + (W4 − W2)]**.
- Each difference is the equal-weight mean over tasks of per-task rate differences.
- This averages the effect of adding "if possible" across both phrasings.

**Primary contrast:** E(Qwen 3.8) − E(Qwen 3.5), in two presentations, `anchor` and `rl/quoted`. These are **two tests**:
- each uses a task-stratified permutation test (10,000 draws, fixed seed);
- **Holm correction across the two**, at α = 0.05;
- each also gets an effect estimate and a 95% interval (task-stratified bootstrap over tasks, and over samples within tasks).

**Secondary, prespecified, not multiplicity-corrected:**
- E for each model on its own;
- E(Qwen 3.6) vs both others;
- E in `rl/direct`;
- the phrasing, interaction, priority and quoting contrasts.

## Interpretation rules (replace "large / near / floor")

- **20 percentage points** is a practical convention for a meaningful effect, not a statistical boundary. Effects are reported with their intervals, whatever their size.
- **"Similar" / "near"** may be claimed only if the 95% interval lies entirely within ±10 percentage points (an equivalence check). A small point estimate alone is reported as **inconclusive**, with its interval.
- **Low-rate cells are not discarded.** Each is reported with its rate and interval (Wilson for single cells).
  - Rates are among valid completions in rewarded cells: n = 12 per model × presentation × wording, from 6 tasks × 2 samples.
  - Where a model's rewarded adoption is low at every wording, that is reported as a finding ("this presentation rarely produces accommodation"), and wording contrasts there are noted as hard to estimate.
- **"At least 4 of 6 tasks agree"** is a descriptive consistency check, not evidence of broad generalisation.

## Calibration

The 40-dataset null check was only a smoke test. Before the main results are read, the analysis is recalibrated on at least 1,000 synthetic null datasets per scenario, including sparse and all-zero cells, and the false-positive rates are reported with their Monte Carlo error. No main-run data are used for this.

## Analysis code fixed before viewing main-run data

Recorded on 2026-10-28T04:10:57Z. The amended `analysis.py` (sha256 `7b29d516b30f6c5c0cbbac0e2d1ed5aa2e78a2f5ce603957fa5ded550f256160`) implements this amendment. It was calibrated on synthetic nulls; see `CALIBRATION.md`. No main-run output had been viewed at this point.
