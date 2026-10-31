# Addendum: reverse transfer on the sending task (Qwen 3.5 direction → Qwen 3.8)

Frozen 2026-10-30, before any generation for this addendum. Hashes: `run/reverse/freeze.json`. Nothing in the
completed main stage is changed; see `REPORT.md` and `ERRATA.md`.

## Question

Applied to Qwen 3.8 at matched strength, does **3.8's own** automated-minus-human direction produce a larger
score-induced send effect than the **transferred 3.5** direction? Together with the main stage, this gives both
directions in both target models.

## What is reused and what is new

- **Reused (no new generation):** the main stage's 3.8 cells for unsteered and native ±0.1 and ±0.3, on all four score
  arms, with 44 blocks × 4 reps (3,520 episodes, of which 2 failed after a send; ERRATA).
- **New:** 8 conditions on 3.8 × 4 arms × 44 blocks × 4 reps = **5,632 episodes** (`run/reverse`):
  - `xfer`: 3.5's `original_pre_L36_auto_minus_human` at ±0.1 and ±0.3;
  - `random0` and `random1` at ±0.3. These are norm-matched random controls on 3.8; the main stage had them only on
    3.5.
- **Bridge (re-run, 352 episodes, `run/reverse_bridge`):** 3.8 unsteered and native +0.3, conflict arm only. These are
  the cells with the most sends, where drift would show.
  - **Gate:** for each, the re-run minus main send rate has a block-bootstrap CI covering 0 and |diff| < 0.10.
  - **If either fails:** the 3,520 reused 3.8 cells are re-generated in the new session, and the analysis uses only
    new-session data. This is prespecified, not chosen after seeing the steered cells.
- **Prompts, blocks and seeds:** identical. Items are derived from the frozen `run/main/send` items, and prompts are
  copied by sha.
  - Seeds depend only on (block, arm, rep), so new cells are paired with the reused cells exactly as conditions were
    paired in the main stage.
- **Serving:** identical code and flags: vLLM 0.26.0 + EasySteer@6267ca0, prefix caching off, `strict_tools=False`, the
  qwen3_coder tool parser and qwen3 reasoning parser, and ports ≠ 8001.
  - New pods and hardware are the only difference; the bridge covers it.
  - Any other difference goes to `AMENDMENTS.md`.

## Intervention (verified offline, `st_reverse_vectors.py`, `run/vectors/reverse_manifest.json`)

- **Source:** `grader-shifts-persona-space/outputs/qwen3.5-27b/analysis/vectors/original_pre_L36_auto_minus_human.npy`,
  sha256 a123602e…, shape (5120,), float32, finite. The unit vector is **byte-identical** to the one steered on 3.5.
- **Random controls:** the same seed-20261030 unit vectors as on 3.5.
- **Target scaling:** A₃₆(**Qwen 3.8**) = 52.26, not 3.5's 81.33. The applied vector is
  signed strength × 52.26 × unit, at our layer 36 (EasySteer layer 35), on all prompt and generated tokens of every
  call.
- **Cosines:** native 3.8 · xfer = 0.54; |cos| with the random vectors < 0.02.
- **On pods, before generation:**
  - `st_checks.py server` on every 3.8 endpoint (zero strength, applied ±, sign, contamination, multi-turn), now
    including the xfer and random GGUFs on 3.8;
  - `st_actcheck.py "Qwen 3.8"`, the HF check of injection norm and sign for the new 3.8 directions.

## Estimands and tests (Qwen 3.8 target)

- **DiD(c):** as in the main stage, the conflict − reversed send rate under c, minus the same difference unsteered.
  Rates are among recorded episodes, and sends are counted from the tool log, including sends before a later failure.
- **Primary family** (Holm over 2, α = 0.05; separate from the main stage's completed P1 and P2):
  - **R1:** DiD(native +0.3) − DiD(xfer +0.3). This is 3.8's own direction vs the transferred 3.5 direction at matched
    strength, tested directly.
  - **R2:** DiD(xfer +0.3), the 3.5 direction vs unsteered on 3.8.
- **Additional tests,** labelled as such:
  - full strength curves (−0.3, −0.1, 0, +0.1, +0.3) for both directions on 3.8;
  - native − xfer at ±0.1 and −0.3;
  - matched ± contrasts for native, xfer and the randoms;
  - xfer − mean(random) at ±0.3;
  - shifts under the reversed, tied and no-history arms;
  - competence (task_done) in the no-history arm.
- **Cross-model** (additional, unadjusted):
  - the advantage of the 3.8 direction over the 3.5 direction at +0.3 in 3.5 (= main stage P2) and in 3.8 (= R1);
  - their difference (adv in 3.8 − adv in 3.5), with the same 44 blocks resampled jointly for both models.
- **Uncertainty:** cluster bootstrap over the 44 blocks (4,000 resamples), with all reps, arms and conditions paired.
  - Counts reported separately: planned, recorded, valid, failed and missing.
  - Zero-event cells are given as k/n.

## Interpretation (fixed)

- **3.8's direction stronger in both models** (main P2 > 0 and R1 > 0): supports a difference in the two directions'
  behavioural influence at the tested strengths.
- **Each direction stronger in its source model** (P2 < 0 and R1 > 0, or the reverse pattern with a positive cross-model
  difference): suggests model-specific compatibility.
- **3.5's direction strong in 3.8** (R2 large) despite its weak +0.3 effect in 3.5: the target model matters
  substantially.
- **Ceiling and floor:** 3.8 sends at 62% unsteered, so increases and decreases are both measurable, unlike on 3.5.
- **Strength scope:** a difference at +0.3 alone is not a claim about other strengths or each direction's optimum; the
  curves are shown.
- **Not established by any pattern:** an identical mechanism, or an RL-training explanation.

## Commands

```bash
.venv/bin/python designs/steer_transfer/st_reverse.py prepare
```

```bash
.venv/bin/python designs/steer_transfer/st_reverse.py test
```

```bash
~/.claude/bin/memguard -m 6 -- .venv/bin/python designs/steer_transfer/st_reverse.py generate reverse_bridge
```

Check the bridge gate, then run the new cells:

```bash
~/.claude/bin/memguard -m 6 -- .venv/bin/python designs/steer_transfer/st_reverse.py generate reverse
```

```bash
.venv/bin/python designs/steer_transfer/st_reverse.py analyse --B 4000
```
