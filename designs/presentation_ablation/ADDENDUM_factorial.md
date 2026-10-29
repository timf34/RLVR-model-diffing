# Protocol addendum: Stage 3 factorial (written 2026-10-29, before any factorial generation)

Required by PROTOCOL.md Stage 3. Written after the frozen main analysis was viewed (that is how the factors were
chosen) and before any factorial episode was generated.

## Design (from the frozen selection rule)

`pa_analysis.py select` picked **a, c, d**: every component with pooled Holm p < 0.05 in Part 2. All three came
from REM; no ADD contrast was significant.
- a: the scorer applies to the current submission.
- c: the old request wording.
- d: the observation is inline in the user turn.

Full 2^3 factorial. Each factor is at its bundle level (B) or its new-presentation level (N). All other components
stay at B.

Cell names:
- `F:aBcBdB` is the full bundle.
- `F:aNcNdN` is the bundle with a, c and d all at N.

The rest of the setup matches main:
- Blocks: the same 32 fresh blocks per task as main Part 2.
- Tasks: send, titles, bullets.
- Scores: tied and +0.50.
- Models: Qwen 3.8 with 2 reps; Qwen 3.5 with 1 rep.
- Total: 4,608 episodes.

These are new generations on the same blocks, not independent confirmation of main.

## Analysis (fixed now; `pa_factorial.py`)

**Block effect.** D(b, cell) = y(+0.50) − y(tied), where y is the mean outcome over valid reps (as in main).

**Factorial effects.** Code each factor +1 at B and −1 at N. For a term S (one factor, or a product of factors),
the block value is (1/4) Σ_cells sign_S(cell) · D(b, cell).
- Main effects are therefore mean D with the factor at B minus mean D with it at N, averaged over the other two
  factors.
- A block enters only if all 8 cells have a valid D.

**Primary family** (Qwen 3.8; pooled over send + titles with equal task weights; Holm over 7):
- main effects a, c, d;
- interactions a×c, a×d, c×d;
- the three-way interaction a×c×d.

Tests and intervals follow main:
- two-sided block sign-flip test (20,000 flips);
- 95% stratified block-bootstrap CI (5,000).

**Secondary, descriptive:**
- per-task versions of each term, including bullets, and all three tasks pooled;
- Qwen 3.5;
- cell rates with Wilson CIs;
- the 8 cell score effects;
- sufficiency: D of each single-B cell (`aBcNdN`, `aNcBdN`, `aNcNdB`) and D of `aNcNdN`, each against the
  all-N cell;
- consistency with main REM:k (D(aBcBdB) − D(k at N, others B)).

## Interpretation (fixed now)

- **Significant positive interactions** mean the components act jointly: the effect of one depends on the others
  being present. Under that pattern the absence of single-component ADD effects in main is expected.
- **Main effects only (no interactions)** means additive contributions.
- **D(aNcNdN) well above 0** means other bundle components (b, e, f, g) still sustain an effect without a, c and d.
  It is compared with main ADD results, where N alone gave ~0.
- **Null interactions** mean "no large interaction", not "no interaction". With 32 blocks per task, power is
  similar to main Part 2.
- Reasoning traces are researcher-only and not used as explanations.

## Run settings

- No budget cap: `--budget-stop 1000`, at the user's instruction.
- Otherwise identical serving, scoring and validity rules to main.
