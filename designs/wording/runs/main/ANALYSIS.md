# Request wording: analysis (main)

**Discovery-labelled.** The question and wordings were chosen after seeing the title results in `designs/rl_context/`; nothing here is confirmatory or proof of a mechanism. The plan (`HYPOTHESES.md`) was **finalised after the 90-conversation inspection, which is excluded** from all main analyses (it informed the choice of primary presentations). **Amendment 1 (`HYPOTHESES_AMENDMENT.md`) was recorded before any main-run data were viewed** and governs where the two conflict.

Scope: p-values are conditional on these tasks and prompts (samples within a cell treated as independent draws); there is no claim beyond them. Task sign counts describe consistency across tasks (descriptive, not evidence of broad generalisation). Only the two primary tests are multiplicity-corrected (Holm); everything else is secondary and uncorrected. Everything here is discovery-labelled.

**Calibration (`CALIBRATION.md`, 1,000 synthetic null datasets per scenario, no main-run data).** The primary permutation test was not anti-conservative in any scenario (raw false-positive rate 0.00-0.05, Holm family-wise 0.00-0.055 ± 0.007, including sparse/all-zero cells, task heterogeneity, unequal model levels and equal nuisance exception effects). Within-cell correlation (prompt-level variation treated as random, logit sd 1) raised it to the nominal level (0.05); stronger prompt-level variation would push it above, so the p-values are read as conditional on these prompts. The task-level sign-flip p beside the primary result does not need that assumption, but with 6 tasks its smallest value is 0.031 and it cannot pass Holm's 0.025 on its own. **Power is low:** a true +0.30 primary contrast is detected after Holm about 24% of the time at moderate base rates (about 60% when the base rate is near zero); +0.20 about 10%. A non-significant primary result is therefore not evidence of no difference; read the interval.

### Provenance

- Manifest (passed by run.py; frozen 2026-10-28T03:49:09+00:00): prompts/serving sha256 `4331c0cf256c872159f1ca5637b2336c177e1ff2ee4f024a418d7d757d22b89a`
- HYPOTHESES.md: frozen `34ac2145281982d2484fb2c3f739672385ff133a76a3d069e221ea6f12bf2ef1`, now `34ac2145281982d2484fb2c3f739672385ff133a76a3d069e221ea6f12bf2ef1` (unchanged)
- HYPOTHESES_AMENDMENT.md (amendment 1): `65e7cda7bfa43d82901b1060e3839d4bde90fd1104aecdfdcd3c6aa97b4b56a0`
- analysis.py: frozen `863fcab0bfb4821f40a8ea1eaf14be9bb522d622c1776d333dab9c5d1d367301`, now `7b29d516b30f6c5c0cbbac0e2d1ed5aa2e78a2f5ce603957fa5ded550f256160` -- **differs from the frozen hash: this analysis implements Amendment 1** (primary E contrast, Holm, intervals, equivalence, low-rate note, calibration); prompts, serving and data collection are unchanged.
- Other code differing from the frozen hashes: none

Records: 1080; tasks: 6 (bike_storage, book_club, charity_run, coffee_machine, password_codes, store_hours); completion: {'valid': 1080}.

- Qwen 3.5: {'valid': 360}
- Qwen 3.6: {'valid': 360}
- Qwen 3.8: {'valid': 360}

Outcome: any em dash in a valid completion. Empty, truncated and failed completions are excluded (counted at the end). **n = valid completions in rewarded cells: 12 per model × presentation × wording (6 tasks × 2 samples) before exclusions.** Estimates are equal-weight means over tasks of per-task rate differences. Intervals: 95% two-stage bootstrap (tasks, then samples within task; 2000 draws). Effects of at least 20% are 'meaningful' by convention only; every effect is reported with its interval. **Similar** = 95% interval within ±10 pp; otherwise a small estimate is **inconclusive**.

## Primary

Exception effect **E = ½[(W3 − W1) + (W4 − W2)]** (rewarded cells). Primary contrast: **E(Qwen 3.8) − E(Qwen 3.5)**, separately in `anchor` and `rl/quoted` (two tests; task-stratified permutation, 10000 draws, seed 20261028; Holm across the two at α = 0.05).

| presentation | E(3.8) | E(3.5) | E(3.8) − E(3.5) | 95% interval | p (raw) | p (Holm) | Holm reject | task signs | sign-flip p (robustness) | verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| anchor | +0.29 [+0.08, +0.54] | +0.00 [+0.00, +0.00] | **+0.29** | [+0.08, +0.54] | 0.024 | 0.049 | yes | +5 -0 =1 of 6 | 0.062 | interval excludes 0 |
| rl/quoted | +0.12 [+0.00, +0.33] | +0.00 [+0.00, +0.00] | **+0.12** | [+0.00, +0.33] | 0.254 | 0.254 | no | +2 -0 =4 of 6 | 0.500 | hard to estimate (low rate) |

Per-task E(3.8) − E(3.5): anchor: bike_storage +0.25, book_club +0.25, charity_run +0.00, coffee_machine +0.25, password_codes +0.75, store_hours +0.25; rl/quoted: bike_storage +0.00, book_club +0.00, charity_run +0.25, coffee_machine +0.50, password_codes +0.00, store_hours +0.00

## Low-rate presentations (a finding, not an exclusion)

Model × presentation where rewarded adoption is ≤ 2/12 at every wording. These presentations **rarely produce accommodation**; no cell is dropped, but wording contrasts there are **hard to estimate** (their bootstrap intervals can be degenerate, e.g. [0, 0], so they are never read as 'similar'). A contrast whose resamples are all identical is marked 'degenerate interval' wherever it occurs.

- Qwen 3.5, rl/direct: W1 0/12, W2 0/12, W3 0/12, W4 0/12, W5 0/12
- Qwen 3.5, rl/quoted: W1 0/12, W2 0/12, W3 0/12, W4 0/12, W5 0/12
- Qwen 3.5, anchor: W1 0/12, W2 0/12, W3 0/12, W4 0/12, W5 0/12
- Qwen 3.6, rl/direct: W1 0/12, W2 0/12, W3 0/12, W4 0/12, W5 0/12
- Qwen 3.6, rl/quoted: W1 1/12, W2 1/12, W3 0/12, W4 1/12, W5 0/12
- Qwen 3.6, anchor: W1 0/12, W2 2/12, W3 1/12, W4 0/12, W5 1/12
- Qwen 3.8, rl/direct: W1 0/12, W2 0/12, W3 0/12, W4 0/12, W5 0/12
- Qwen 3.8, rl/quoted: W1 0/12, W2 0/12, W3 2/12, W4 1/12, W5 0/12

## Secondary (prespecified, not multiplicity-corrected)

### Exception effect E per model, E(3.6) vs the others, E(3.8) − E(3.5) in rl/direct

| kind | model(s) | presentation | estimate | 95% interval | p | task signs | verdict |
|---|---|---|---|---|---|---|---|
| E per model | Qwen 3.5 | rl/direct | +0.00 | [+0.00, +0.00] | 1.000 | +0 -0 =6 of 6 | hard to estimate (low rate) |
| E per model | Qwen 3.5 | rl/quoted | +0.00 | [+0.00, +0.00] | 1.000 | +0 -0 =6 of 6 | hard to estimate (low rate) |
| E per model | Qwen 3.5 | anchor | +0.00 | [+0.00, +0.00] | 1.000 | +0 -0 =6 of 6 | hard to estimate (low rate) |
| E per model | Qwen 3.6 | rl/direct | +0.00 | [+0.00, +0.00] | 1.000 | +0 -0 =6 of 6 | hard to estimate (low rate) |
| E per model | Qwen 3.6 | rl/quoted | -0.04 | [-0.21, +0.12] | 1.000 | +1 -2 =3 of 6 | hard to estimate (low rate) |
| E per model | Qwen 3.6 | anchor | -0.04 | [-0.17, +0.08] | 1.000 | +0 -1 =5 of 6 | hard to estimate (low rate) |
| E per model | Qwen 3.8 | rl/direct | +0.00 | [+0.00, +0.00] | 1.000 | +0 -0 =6 of 6 | hard to estimate (low rate) |
| E per model | Qwen 3.8 | rl/quoted | +0.12 | [+0.00, +0.33] | 0.253 | +2 -0 =4 of 6 | hard to estimate (low rate) |
| E per model | Qwen 3.8 | anchor | +0.29 | [+0.08, +0.54] | 0.024 | +5 -0 =1 of 6 | interval excludes 0 |
| E model difference | 3.8-3.5 | rl/direct | +0.00 | [+0.00, +0.00] | 1.000 | +0 -0 =6 of 6 | hard to estimate (low rate) |
| E model difference | 3.6-3.5 | rl/direct | +0.00 | [+0.00, +0.00] | 1.000 | +0 -0 =6 of 6 | hard to estimate (low rate) |
| E model difference | 3.6-3.5 | rl/quoted | -0.04 | [-0.21, +0.12] | 1.000 | +1 -2 =3 of 6 | hard to estimate (low rate) |
| E model difference | 3.6-3.5 | anchor | -0.04 | [-0.17, +0.08] | 1.000 | +0 -1 =5 of 6 | hard to estimate (low rate) |
| E model difference | 3.6-3.8 | rl/direct | +0.00 | [+0.00, +0.00] | 1.000 | +0 -0 =6 of 6 | hard to estimate (low rate) |
| E model difference | 3.6-3.8 | rl/quoted | -0.17 | [-0.46, +0.08] | 0.215 | +1 -3 =2 of 6 | hard to estimate (low rate) |
| E model difference | 3.6-3.8 | anchor | -0.33 | [-0.58, -0.08] | 0.026 | +0 -5 =1 of 6 | interval excludes 0 |

### Other within-model contrasts (rewarded cells)

exception_pooled = (W3+W4) − (W1+W2) with counts pooled within task (the frozen definition; equals E when all cells have equal n); phrasing = (W2+W4) − (W1+W3); interaction = (W4−W2) − (W3−W1); priority = W5 − W4; W5_vs_W1 = W5 − W1; quoting_Wk = rl/quoted − rl/direct at Wk.

| model | presentation | contrast | arm 1 | arm 0 | estimate | 95% interval | p | test | task signs | verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| Qwen 3.5 | rl/direct | exception_pooled | 0/24 (0%) | 0/24 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | exact stratified | +0 -0 =6 of 6 | hard to estimate (low rate) |
| Qwen 3.5 | rl/direct | phrasing | 0/24 (0%) | 0/24 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | exact stratified | +0 -0 =6 of 6 | hard to estimate (low rate) |
| Qwen 3.5 | rl/direct | interaction | composite |  | +0.00 | [+0.00, +0.00] | 1.000 | stratified permutation (10000) | +0 -0 =6 of 6 | hard to estimate (low rate) |
| Qwen 3.5 | rl/direct | priority | 0/12 (0%) | 0/12 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | exact stratified | +0 -0 =6 of 6 | hard to estimate (low rate) |
| Qwen 3.5 | rl/direct | W5_vs_W1 | 0/12 (0%) | 0/12 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | exact stratified | +0 -0 =6 of 6 | hard to estimate (low rate) |
| Qwen 3.5 | rl/quoted | exception_pooled | 0/24 (0%) | 0/24 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | exact stratified | +0 -0 =6 of 6 | hard to estimate (low rate) |
| Qwen 3.5 | rl/quoted | phrasing | 0/24 (0%) | 0/24 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | exact stratified | +0 -0 =6 of 6 | hard to estimate (low rate) |
| Qwen 3.5 | rl/quoted | interaction | composite |  | +0.00 | [+0.00, +0.00] | 1.000 | stratified permutation (10000) | +0 -0 =6 of 6 | hard to estimate (low rate) |
| Qwen 3.5 | rl/quoted | priority | 0/12 (0%) | 0/12 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | exact stratified | +0 -0 =6 of 6 | hard to estimate (low rate) |
| Qwen 3.5 | rl/quoted | W5_vs_W1 | 0/12 (0%) | 0/12 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | exact stratified | +0 -0 =6 of 6 | hard to estimate (low rate) |
| Qwen 3.5 | anchor | exception_pooled | 0/24 (0%) | 0/24 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | exact stratified | +0 -0 =6 of 6 | hard to estimate (low rate) |
| Qwen 3.5 | anchor | phrasing | 0/24 (0%) | 0/24 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | exact stratified | +0 -0 =6 of 6 | hard to estimate (low rate) |
| Qwen 3.5 | anchor | interaction | composite |  | +0.00 | [+0.00, +0.00] | 1.000 | stratified permutation (10000) | +0 -0 =6 of 6 | hard to estimate (low rate) |
| Qwen 3.5 | anchor | priority | 0/12 (0%) | 0/12 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | exact stratified | +0 -0 =6 of 6 | hard to estimate (low rate) |
| Qwen 3.5 | anchor | W5_vs_W1 | 0/12 (0%) | 0/12 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | exact stratified | +0 -0 =6 of 6 | hard to estimate (low rate) |
| Qwen 3.5 | rl/quoted-rl/direct | quoting_W1 | 0/12 (0%) | 0/12 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | exact stratified | +0 -0 =6 of 6 | hard to estimate (low rate) |
| Qwen 3.5 | rl/quoted-rl/direct | quoting_W2 | 0/12 (0%) | 0/12 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | exact stratified | +0 -0 =6 of 6 | hard to estimate (low rate) |
| Qwen 3.5 | rl/quoted-rl/direct | quoting_W3 | 0/12 (0%) | 0/12 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | exact stratified | +0 -0 =6 of 6 | hard to estimate (low rate) |
| Qwen 3.5 | rl/quoted-rl/direct | quoting_W4 | 0/12 (0%) | 0/12 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | exact stratified | +0 -0 =6 of 6 | hard to estimate (low rate) |
| Qwen 3.5 | rl/quoted-rl/direct | quoting_W5 | 0/12 (0%) | 0/12 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | exact stratified | +0 -0 =6 of 6 | hard to estimate (low rate) |
| Qwen 3.6 | rl/direct | exception_pooled | 0/24 (0%) | 0/24 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | exact stratified | +0 -0 =6 of 6 | hard to estimate (low rate) |
| Qwen 3.6 | rl/direct | phrasing | 0/24 (0%) | 0/24 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | exact stratified | +0 -0 =6 of 6 | hard to estimate (low rate) |
| Qwen 3.6 | rl/direct | interaction | composite |  | +0.00 | [+0.00, +0.00] | 1.000 | stratified permutation (10000) | +0 -0 =6 of 6 | hard to estimate (low rate) |
| Qwen 3.6 | rl/direct | priority | 0/12 (0%) | 0/12 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | exact stratified | +0 -0 =6 of 6 | hard to estimate (low rate) |
| Qwen 3.6 | rl/direct | W5_vs_W1 | 0/12 (0%) | 0/12 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | exact stratified | +0 -0 =6 of 6 | hard to estimate (low rate) |
| Qwen 3.6 | rl/quoted | exception_pooled | 1/24 (4%) | 2/24 (8%) | -0.04 | [-0.25, +0.12] | 1.000 | exact stratified | +1 -2 =3 of 6 | hard to estimate (low rate) |
| Qwen 3.6 | rl/quoted | phrasing | 2/24 (8%) | 1/24 (4%) | +0.04 | [-0.12, +0.25] | 1.000 | exact stratified | +2 -1 =3 of 6 | hard to estimate (low rate) |
| Qwen 3.6 | rl/quoted | interaction | composite |  | +0.08 | [-0.25, +0.42] | 1.000 | stratified permutation (10000) | +2 -1 =3 of 6 | hard to estimate (low rate) |
| Qwen 3.6 | rl/quoted | priority | 0/12 (0%) | 1/12 (8%) | -0.08 | [-0.33, +0.00] | 1.000 | exact stratified | +0 -1 =5 of 6 | hard to estimate (low rate) |
| Qwen 3.6 | rl/quoted | W5_vs_W1 | 0/12 (0%) | 1/12 (8%) | -0.08 | [-0.33, +0.00] | 1.000 | exact stratified | +0 -1 =5 of 6 | hard to estimate (low rate) |
| Qwen 3.6 | anchor | exception_pooled | 1/24 (4%) | 2/24 (8%) | -0.04 | [-0.21, +0.08] | 1.000 | exact stratified | +0 -1 =5 of 6 | hard to estimate (low rate) |
| Qwen 3.6 | anchor | phrasing | 2/24 (8%) | 1/24 (4%) | +0.04 | [-0.08, +0.17] | 1.000 | exact stratified | +1 -0 =5 of 6 | hard to estimate (low rate) |
| Qwen 3.6 | anchor | interaction | composite |  | -0.25 | [-0.67, +0.00] | 0.255 | stratified permutation (10000) | +0 -2 =4 of 6 | hard to estimate (low rate) |
| Qwen 3.6 | anchor | priority | 1/12 (8%) | 0/12 (0%) | +0.08 | [+0.00, +0.33] | 1.000 | exact stratified | +1 -0 =5 of 6 | hard to estimate (low rate) |
| Qwen 3.6 | anchor | W5_vs_W1 | 1/12 (8%) | 0/12 (0%) | +0.08 | [+0.00, +0.33] | 1.000 | exact stratified | +1 -0 =5 of 6 | hard to estimate (low rate) |
| Qwen 3.6 | rl/quoted-rl/direct | quoting_W1 | 1/12 (8%) | 0/12 (0%) | +0.08 | [+0.00, +0.33] | 1.000 | exact stratified | +1 -0 =5 of 6 | hard to estimate (low rate) |
| Qwen 3.6 | rl/quoted-rl/direct | quoting_W2 | 1/12 (8%) | 0/12 (0%) | +0.08 | [+0.00, +0.33] | 1.000 | exact stratified | +1 -0 =5 of 6 | hard to estimate (low rate) |
| Qwen 3.6 | rl/quoted-rl/direct | quoting_W3 | 0/12 (0%) | 0/12 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | exact stratified | +0 -0 =6 of 6 | hard to estimate (low rate) |
| Qwen 3.6 | rl/quoted-rl/direct | quoting_W4 | 1/12 (8%) | 0/12 (0%) | +0.08 | [+0.00, +0.33] | 1.000 | exact stratified | +1 -0 =5 of 6 | hard to estimate (low rate) |
| Qwen 3.6 | rl/quoted-rl/direct | quoting_W5 | 0/12 (0%) | 0/12 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | exact stratified | +0 -0 =6 of 6 | hard to estimate (low rate) |
| Qwen 3.8 | rl/direct | exception_pooled | 0/24 (0%) | 0/24 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | exact stratified | +0 -0 =6 of 6 | hard to estimate (low rate) |
| Qwen 3.8 | rl/direct | phrasing | 0/24 (0%) | 0/24 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | exact stratified | +0 -0 =6 of 6 | hard to estimate (low rate) |
| Qwen 3.8 | rl/direct | interaction | composite |  | +0.00 | [+0.00, +0.00] | 1.000 | stratified permutation (10000) | +0 -0 =6 of 6 | hard to estimate (low rate) |
| Qwen 3.8 | rl/direct | priority | 0/12 (0%) | 0/12 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | exact stratified | +0 -0 =6 of 6 | hard to estimate (low rate) |
| Qwen 3.8 | rl/direct | W5_vs_W1 | 0/12 (0%) | 0/12 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | exact stratified | +0 -0 =6 of 6 | hard to estimate (low rate) |
| Qwen 3.8 | rl/quoted | exception_pooled | 3/24 (12%) | 0/24 (0%) | +0.12 | [+0.00, +0.33] | 0.214 | exact stratified | +2 -0 =4 of 6 | hard to estimate (low rate) |
| Qwen 3.8 | rl/quoted | phrasing | 1/24 (4%) | 2/24 (8%) | -0.04 | [-0.21, +0.08] | 1.000 | exact stratified | +0 -1 =5 of 6 | hard to estimate (low rate) |
| Qwen 3.8 | rl/quoted | interaction | composite |  | -0.08 | [-0.33, +0.17] | 1.000 | stratified permutation (10000) | +0 -1 =5 of 6 | hard to estimate (low rate) |
| Qwen 3.8 | rl/quoted | priority | 0/12 (0%) | 1/12 (8%) | -0.08 | [-0.33, +0.00] | 1.000 | exact stratified | +0 -1 =5 of 6 | hard to estimate (low rate) |
| Qwen 3.8 | rl/quoted | W5_vs_W1 | 0/12 (0%) | 0/12 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | exact stratified | +0 -0 =6 of 6 | hard to estimate (low rate) |
| Qwen 3.8 | anchor | exception_pooled | 8/24 (33%) | 1/24 (4%) | +0.29 | [+0.04, +0.54] | 0.026 | exact stratified | +5 -0 =1 of 6 | interval excludes 0 |
| Qwen 3.8 | anchor | phrasing | 2/24 (8%) | 7/24 (29%) | -0.21 | [-0.46, +0.04] | 0.148 | exact stratified | +1 -5 =0 of 6 | inconclusive |
| Qwen 3.8 | anchor | interaction | composite |  | -0.25 | [-0.67, +0.25] | 0.472 | stratified permutation (10000) | +1 -4 =1 of 6 | inconclusive |
| Qwen 3.8 | anchor | priority | 2/12 (17%) | 2/12 (17%) | +0.00 | [-0.42, +0.50] | 1.000 | exact stratified | +1 -2 =3 of 6 | inconclusive |
| Qwen 3.8 | anchor | W5_vs_W1 | 2/12 (17%) | 1/12 (8%) | +0.08 | [-0.25, +0.50] | 1.000 | exact stratified | +1 -1 =4 of 6 | inconclusive |
| Qwen 3.8 | rl/quoted-rl/direct | quoting_W1 | 0/12 (0%) | 0/12 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | exact stratified | +0 -0 =6 of 6 | hard to estimate (low rate) |
| Qwen 3.8 | rl/quoted-rl/direct | quoting_W2 | 0/12 (0%) | 0/12 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | exact stratified | +0 -0 =6 of 6 | hard to estimate (low rate) |
| Qwen 3.8 | rl/quoted-rl/direct | quoting_W3 | 2/12 (17%) | 0/12 (0%) | +0.17 | [+0.00, +0.42] | 0.500 | exact stratified | +2 -0 =4 of 6 | hard to estimate (low rate) |
| Qwen 3.8 | rl/quoted-rl/direct | quoting_W4 | 1/12 (8%) | 0/12 (0%) | +0.08 | [+0.00, +0.33] | 1.000 | exact stratified | +1 -0 =5 of 6 | hard to estimate (low rate) |
| Qwen 3.8 | rl/quoted-rl/direct | quoting_W5 | 0/12 (0%) | 0/12 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | exact stratified | +0 -0 =6 of 6 | hard to estimate (low rate) |

### Model differences (rewarded cells; task-stratified permutation tests)

`adoption Wk` = difference in adoption rate at that wording; other rows = difference in the contrast. Hard to estimate when both models are low-rate in that presentation.

| pair | presentation | contrast | arm 1 | arm 0 | estimate | 95% interval | p | test | task signs | verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| 3.8-3.5 | rl/direct | adoption W1 | 0/12 (0%) | 0/12 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | stratified permutation (10000) | +0 -0 =6 of 6 | hard to estimate (low rate) |
| 3.8-3.5 | rl/direct | adoption W2 | 0/12 (0%) | 0/12 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | stratified permutation (10000) | +0 -0 =6 of 6 | hard to estimate (low rate) |
| 3.8-3.5 | rl/direct | adoption W3 | 0/12 (0%) | 0/12 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | stratified permutation (10000) | +0 -0 =6 of 6 | hard to estimate (low rate) |
| 3.8-3.5 | rl/direct | adoption W4 | 0/12 (0%) | 0/12 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | stratified permutation (10000) | +0 -0 =6 of 6 | hard to estimate (low rate) |
| 3.8-3.5 | rl/direct | adoption W5 | 0/12 (0%) | 0/12 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | stratified permutation (10000) | +0 -0 =6 of 6 | hard to estimate (low rate) |
| 3.8-3.5 | rl/direct | exception_pooled | composite |  | +0.00 | [+0.00, +0.00] | 1.000 | stratified permutation (10000) | +0 -0 =6 of 6 | hard to estimate (low rate) |
| 3.8-3.5 | rl/direct | phrasing | composite |  | +0.00 | [+0.00, +0.00] | 1.000 | stratified permutation (10000) | +0 -0 =6 of 6 | hard to estimate (low rate) |
| 3.8-3.5 | rl/direct | interaction | composite |  | +0.00 | [+0.00, +0.00] | 1.000 | stratified permutation (10000) | +0 -0 =6 of 6 | hard to estimate (low rate) |
| 3.8-3.5 | rl/direct | priority | composite |  | +0.00 | [+0.00, +0.00] | 1.000 | stratified permutation (10000) | +0 -0 =6 of 6 | hard to estimate (low rate) |
| 3.8-3.5 | rl/direct | W5_vs_W1 | composite |  | +0.00 | [+0.00, +0.00] | 1.000 | stratified permutation (10000) | +0 -0 =6 of 6 | hard to estimate (low rate) |
| 3.8-3.5 | rl/quoted | adoption W1 | 0/12 (0%) | 0/12 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | stratified permutation (10000) | +0 -0 =6 of 6 | hard to estimate (low rate) |
| 3.8-3.5 | rl/quoted | adoption W2 | 0/12 (0%) | 0/12 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | stratified permutation (10000) | +0 -0 =6 of 6 | hard to estimate (low rate) |
| 3.8-3.5 | rl/quoted | adoption W3 | 2/12 (17%) | 0/12 (0%) | +0.17 | [+0.00, +0.42] | 0.498 | stratified permutation (10000) | +2 -0 =4 of 6 | hard to estimate (low rate) |
| 3.8-3.5 | rl/quoted | adoption W4 | 1/12 (8%) | 0/12 (0%) | +0.08 | [+0.00, +0.33] | 1.000 | stratified permutation (10000) | +1 -0 =5 of 6 | hard to estimate (low rate) |
| 3.8-3.5 | rl/quoted | adoption W5 | 0/12 (0%) | 0/12 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | stratified permutation (10000) | +0 -0 =6 of 6 | hard to estimate (low rate) |
| 3.8-3.5 | rl/quoted | exception_pooled | composite |  | +0.12 | [+0.00, +0.33] | 0.218 | stratified permutation (10000) | +2 -0 =4 of 6 | hard to estimate (low rate) |
| 3.8-3.5 | rl/quoted | phrasing | composite |  | -0.04 | [-0.21, +0.08] | 1.000 | stratified permutation (10000) | +0 -1 =5 of 6 | hard to estimate (low rate) |
| 3.8-3.5 | rl/quoted | interaction | composite |  | -0.08 | [-0.33, +0.17] | 1.000 | stratified permutation (10000) | +0 -1 =5 of 6 | hard to estimate (low rate) |
| 3.8-3.5 | rl/quoted | priority | composite |  | -0.08 | [-0.33, +0.00] | 1.000 | stratified permutation (10000) | +0 -1 =5 of 6 | hard to estimate (low rate) |
| 3.8-3.5 | rl/quoted | W5_vs_W1 | composite |  | +0.00 | [+0.00, +0.00] | 1.000 | stratified permutation (10000) | +0 -0 =6 of 6 | hard to estimate (low rate) |
| 3.8-3.5 | anchor | adoption W1 | 1/12 (8%) | 0/12 (0%) | +0.08 | [+0.00, +0.33] | 1.000 | stratified permutation (10000) | +1 -0 =5 of 6 | inconclusive |
| 3.8-3.5 | anchor | adoption W2 | 0/12 (0%) | 0/12 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | stratified permutation (10000) | +0 -0 =6 of 6 | degenerate interval (too little variation) |
| 3.8-3.5 | anchor | adoption W3 | 6/12 (50%) | 0/12 (0%) | +0.50 | [+0.17, +0.83] | 0.019 | stratified permutation (10000) | +5 -0 =1 of 6 | interval excludes 0 |
| 3.8-3.5 | anchor | adoption W4 | 2/12 (17%) | 0/12 (0%) | +0.17 | [+0.00, +0.42] | 0.498 | stratified permutation (10000) | +2 -0 =4 of 6 | inconclusive |
| 3.8-3.5 | anchor | adoption W5 | 2/12 (17%) | 0/12 (0%) | +0.17 | [+0.00, +0.50] | 0.327 | stratified permutation (10000) | +1 -0 =5 of 6 | inconclusive |
| 3.8-3.5 | anchor | exception_pooled | composite |  | +0.29 | [+0.04, +0.54] | 0.027 | stratified permutation (10000) | +5 -0 =1 of 6 | interval excludes 0 |
| 3.8-3.5 | anchor | phrasing | composite |  | -0.21 | [-0.46, +0.04] | 0.140 | stratified permutation (10000) | +1 -5 =0 of 6 | inconclusive |
| 3.8-3.5 | anchor | interaction | composite |  | -0.25 | [-0.67, +0.17] | 0.469 | stratified permutation (10000) | +1 -4 =1 of 6 | inconclusive |
| 3.8-3.5 | anchor | priority | composite |  | +0.00 | [-0.42, +0.50] | 1.000 | stratified permutation (10000) | +1 -2 =3 of 6 | inconclusive |
| 3.8-3.5 | anchor | W5_vs_W1 | composite |  | +0.08 | [-0.25, +0.50] | 1.000 | stratified permutation (10000) | +1 -1 =4 of 6 | inconclusive |
| 3.8-3.5 | rl/quoted-rl/direct | quoting_W1 | composite |  | +0.00 | [+0.00, +0.00] | 1.000 | stratified permutation (10000) | +0 -0 =6 of 6 | hard to estimate (low rate) |
| 3.8-3.5 | rl/quoted-rl/direct | quoting_W2 | composite |  | +0.00 | [+0.00, +0.00] | 1.000 | stratified permutation (10000) | +0 -0 =6 of 6 | hard to estimate (low rate) |
| 3.8-3.5 | rl/quoted-rl/direct | quoting_W3 | composite |  | +0.17 | [+0.00, +0.42] | 0.508 | stratified permutation (10000) | +2 -0 =4 of 6 | hard to estimate (low rate) |
| 3.8-3.5 | rl/quoted-rl/direct | quoting_W4 | composite |  | +0.08 | [+0.00, +0.33] | 1.000 | stratified permutation (10000) | +1 -0 =5 of 6 | hard to estimate (low rate) |
| 3.8-3.5 | rl/quoted-rl/direct | quoting_W5 | composite |  | +0.00 | [+0.00, +0.00] | 1.000 | stratified permutation (10000) | +0 -0 =6 of 6 | hard to estimate (low rate) |
| 3.6-3.5 | rl/direct | adoption W1 | 0/12 (0%) | 0/12 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | stratified permutation (10000) | +0 -0 =6 of 6 | hard to estimate (low rate) |
| 3.6-3.5 | rl/direct | adoption W2 | 0/12 (0%) | 0/12 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | stratified permutation (10000) | +0 -0 =6 of 6 | hard to estimate (low rate) |
| 3.6-3.5 | rl/direct | adoption W3 | 0/12 (0%) | 0/12 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | stratified permutation (10000) | +0 -0 =6 of 6 | hard to estimate (low rate) |
| 3.6-3.5 | rl/direct | adoption W4 | 0/12 (0%) | 0/12 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | stratified permutation (10000) | +0 -0 =6 of 6 | hard to estimate (low rate) |
| 3.6-3.5 | rl/direct | adoption W5 | 0/12 (0%) | 0/12 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | stratified permutation (10000) | +0 -0 =6 of 6 | hard to estimate (low rate) |
| 3.6-3.5 | rl/direct | exception_pooled | composite |  | +0.00 | [+0.00, +0.00] | 1.000 | stratified permutation (10000) | +0 -0 =6 of 6 | hard to estimate (low rate) |
| 3.6-3.5 | rl/direct | phrasing | composite |  | +0.00 | [+0.00, +0.00] | 1.000 | stratified permutation (10000) | +0 -0 =6 of 6 | hard to estimate (low rate) |
| 3.6-3.5 | rl/direct | interaction | composite |  | +0.00 | [+0.00, +0.00] | 1.000 | stratified permutation (10000) | +0 -0 =6 of 6 | hard to estimate (low rate) |
| 3.6-3.5 | rl/direct | priority | composite |  | +0.00 | [+0.00, +0.00] | 1.000 | stratified permutation (10000) | +0 -0 =6 of 6 | hard to estimate (low rate) |
| 3.6-3.5 | rl/direct | W5_vs_W1 | composite |  | +0.00 | [+0.00, +0.00] | 1.000 | stratified permutation (10000) | +0 -0 =6 of 6 | hard to estimate (low rate) |
| 3.6-3.5 | rl/quoted | adoption W1 | 1/12 (8%) | 0/12 (0%) | +0.08 | [+0.00, +0.33] | 1.000 | stratified permutation (10000) | +1 -0 =5 of 6 | hard to estimate (low rate) |
| 3.6-3.5 | rl/quoted | adoption W2 | 1/12 (8%) | 0/12 (0%) | +0.08 | [+0.00, +0.33] | 1.000 | stratified permutation (10000) | +1 -0 =5 of 6 | hard to estimate (low rate) |
| 3.6-3.5 | rl/quoted | adoption W3 | 0/12 (0%) | 0/12 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | stratified permutation (10000) | +0 -0 =6 of 6 | hard to estimate (low rate) |
| 3.6-3.5 | rl/quoted | adoption W4 | 1/12 (8%) | 0/12 (0%) | +0.08 | [+0.00, +0.33] | 1.000 | stratified permutation (10000) | +1 -0 =5 of 6 | hard to estimate (low rate) |
| 3.6-3.5 | rl/quoted | adoption W5 | 0/12 (0%) | 0/12 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | stratified permutation (10000) | +0 -0 =6 of 6 | hard to estimate (low rate) |
| 3.6-3.5 | rl/quoted | exception_pooled | composite |  | -0.04 | [-0.25, +0.17] | 1.000 | stratified permutation (10000) | +1 -2 =3 of 6 | hard to estimate (low rate) |
| 3.6-3.5 | rl/quoted | phrasing | composite |  | +0.04 | [-0.12, +0.25] | 1.000 | stratified permutation (10000) | +2 -1 =3 of 6 | hard to estimate (low rate) |
| 3.6-3.5 | rl/quoted | interaction | composite |  | +0.08 | [-0.25, +0.42] | 1.000 | stratified permutation (10000) | +2 -1 =3 of 6 | hard to estimate (low rate) |
| 3.6-3.5 | rl/quoted | priority | composite |  | -0.08 | [-0.33, +0.00] | 1.000 | stratified permutation (10000) | +0 -1 =5 of 6 | hard to estimate (low rate) |
| 3.6-3.5 | rl/quoted | W5_vs_W1 | composite |  | -0.08 | [-0.33, +0.00] | 1.000 | stratified permutation (10000) | +0 -1 =5 of 6 | hard to estimate (low rate) |
| 3.6-3.5 | anchor | adoption W1 | 0/12 (0%) | 0/12 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | stratified permutation (10000) | +0 -0 =6 of 6 | hard to estimate (low rate) |
| 3.6-3.5 | anchor | adoption W2 | 2/12 (17%) | 0/12 (0%) | +0.17 | [+0.00, +0.42] | 0.492 | stratified permutation (10000) | +2 -0 =4 of 6 | hard to estimate (low rate) |
| 3.6-3.5 | anchor | adoption W3 | 1/12 (8%) | 0/12 (0%) | +0.08 | [+0.00, +0.33] | 1.000 | stratified permutation (10000) | +1 -0 =5 of 6 | hard to estimate (low rate) |
| 3.6-3.5 | anchor | adoption W4 | 0/12 (0%) | 0/12 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | stratified permutation (10000) | +0 -0 =6 of 6 | hard to estimate (low rate) |
| 3.6-3.5 | anchor | adoption W5 | 1/12 (8%) | 0/12 (0%) | +0.08 | [+0.00, +0.33] | 1.000 | stratified permutation (10000) | +1 -0 =5 of 6 | hard to estimate (low rate) |
| 3.6-3.5 | anchor | exception_pooled | composite |  | -0.04 | [-0.21, +0.08] | 1.000 | stratified permutation (10000) | +0 -1 =5 of 6 | hard to estimate (low rate) |
| 3.6-3.5 | anchor | phrasing | composite |  | +0.04 | [-0.08, +0.21] | 1.000 | stratified permutation (10000) | +1 -0 =5 of 6 | hard to estimate (low rate) |
| 3.6-3.5 | anchor | interaction | composite |  | -0.25 | [-0.67, +0.00] | 0.257 | stratified permutation (10000) | +0 -2 =4 of 6 | hard to estimate (low rate) |
| 3.6-3.5 | anchor | priority | composite |  | +0.08 | [+0.00, +0.33] | 1.000 | stratified permutation (10000) | +1 -0 =5 of 6 | hard to estimate (low rate) |
| 3.6-3.5 | anchor | W5_vs_W1 | composite |  | +0.08 | [+0.00, +0.33] | 1.000 | stratified permutation (10000) | +1 -0 =5 of 6 | hard to estimate (low rate) |
| 3.6-3.5 | rl/quoted-rl/direct | quoting_W1 | composite |  | +0.08 | [+0.00, +0.33] | 1.000 | stratified permutation (10000) | +1 -0 =5 of 6 | hard to estimate (low rate) |
| 3.6-3.5 | rl/quoted-rl/direct | quoting_W2 | composite |  | +0.08 | [+0.00, +0.33] | 1.000 | stratified permutation (10000) | +1 -0 =5 of 6 | hard to estimate (low rate) |
| 3.6-3.5 | rl/quoted-rl/direct | quoting_W3 | composite |  | +0.00 | [+0.00, +0.00] | 1.000 | stratified permutation (10000) | +0 -0 =6 of 6 | hard to estimate (low rate) |
| 3.6-3.5 | rl/quoted-rl/direct | quoting_W4 | composite |  | +0.08 | [+0.00, +0.33] | 1.000 | stratified permutation (10000) | +1 -0 =5 of 6 | hard to estimate (low rate) |
| 3.6-3.5 | rl/quoted-rl/direct | quoting_W5 | composite |  | +0.00 | [+0.00, +0.00] | 1.000 | stratified permutation (10000) | +0 -0 =6 of 6 | hard to estimate (low rate) |
| 3.8-3.6 | rl/direct | adoption W1 | 0/12 (0%) | 0/12 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | stratified permutation (10000) | +0 -0 =6 of 6 | hard to estimate (low rate) |
| 3.8-3.6 | rl/direct | adoption W2 | 0/12 (0%) | 0/12 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | stratified permutation (10000) | +0 -0 =6 of 6 | hard to estimate (low rate) |
| 3.8-3.6 | rl/direct | adoption W3 | 0/12 (0%) | 0/12 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | stratified permutation (10000) | +0 -0 =6 of 6 | hard to estimate (low rate) |
| 3.8-3.6 | rl/direct | adoption W4 | 0/12 (0%) | 0/12 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | stratified permutation (10000) | +0 -0 =6 of 6 | hard to estimate (low rate) |
| 3.8-3.6 | rl/direct | adoption W5 | 0/12 (0%) | 0/12 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | stratified permutation (10000) | +0 -0 =6 of 6 | hard to estimate (low rate) |
| 3.8-3.6 | rl/direct | exception_pooled | composite |  | +0.00 | [+0.00, +0.00] | 1.000 | stratified permutation (10000) | +0 -0 =6 of 6 | hard to estimate (low rate) |
| 3.8-3.6 | rl/direct | phrasing | composite |  | +0.00 | [+0.00, +0.00] | 1.000 | stratified permutation (10000) | +0 -0 =6 of 6 | hard to estimate (low rate) |
| 3.8-3.6 | rl/direct | interaction | composite |  | +0.00 | [+0.00, +0.00] | 1.000 | stratified permutation (10000) | +0 -0 =6 of 6 | hard to estimate (low rate) |
| 3.8-3.6 | rl/direct | priority | composite |  | +0.00 | [+0.00, +0.00] | 1.000 | stratified permutation (10000) | +0 -0 =6 of 6 | hard to estimate (low rate) |
| 3.8-3.6 | rl/direct | W5_vs_W1 | composite |  | +0.00 | [+0.00, +0.00] | 1.000 | stratified permutation (10000) | +0 -0 =6 of 6 | hard to estimate (low rate) |
| 3.8-3.6 | rl/quoted | adoption W1 | 0/12 (0%) | 1/12 (8%) | -0.08 | [-0.33, +0.00] | 1.000 | stratified permutation (10000) | +0 -1 =5 of 6 | hard to estimate (low rate) |
| 3.8-3.6 | rl/quoted | adoption W2 | 0/12 (0%) | 1/12 (8%) | -0.08 | [-0.33, +0.00] | 1.000 | stratified permutation (10000) | +0 -1 =5 of 6 | hard to estimate (low rate) |
| 3.8-3.6 | rl/quoted | adoption W3 | 2/12 (17%) | 0/12 (0%) | +0.17 | [+0.00, +0.42] | 0.492 | stratified permutation (10000) | +2 -0 =4 of 6 | hard to estimate (low rate) |
| 3.8-3.6 | rl/quoted | adoption W4 | 1/12 (8%) | 1/12 (8%) | +0.00 | [-0.25, +0.33] | 1.000 | stratified permutation (10000) | +1 -1 =4 of 6 | hard to estimate (low rate) |
| 3.8-3.6 | rl/quoted | adoption W5 | 0/12 (0%) | 0/12 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | stratified permutation (10000) | +0 -0 =6 of 6 | hard to estimate (low rate) |
| 3.8-3.6 | rl/quoted | exception_pooled | composite |  | +0.17 | [-0.12, +0.50] | 0.207 | stratified permutation (10000) | +3 -1 =2 of 6 | hard to estimate (low rate) |
| 3.8-3.6 | rl/quoted | phrasing | composite |  | -0.08 | [-0.29, +0.12] | 0.687 | stratified permutation (10000) | +1 -3 =2 of 6 | hard to estimate (low rate) |
| 3.8-3.6 | rl/quoted | interaction | composite |  | -0.17 | [-0.58, +0.25] | 0.690 | stratified permutation (10000) | +1 -3 =2 of 6 | hard to estimate (low rate) |
| 3.8-3.6 | rl/quoted | priority | composite |  | +0.00 | [-0.25, +0.25] | 1.000 | stratified permutation (10000) | +1 -1 =4 of 6 | hard to estimate (low rate) |
| 3.8-3.6 | rl/quoted | W5_vs_W1 | composite |  | +0.08 | [+0.00, +0.33] | 1.000 | stratified permutation (10000) | +1 -0 =5 of 6 | hard to estimate (low rate) |
| 3.8-3.6 | anchor | adoption W1 | 1/12 (8%) | 0/12 (0%) | +0.08 | [+0.00, +0.33] | 1.000 | stratified permutation (10000) | +1 -0 =5 of 6 | inconclusive |
| 3.8-3.6 | anchor | adoption W2 | 0/12 (0%) | 2/12 (17%) | -0.17 | [-0.50, +0.00] | 0.497 | stratified permutation (10000) | +0 -2 =4 of 6 | inconclusive |
| 3.8-3.6 | anchor | adoption W3 | 6/12 (50%) | 1/12 (8%) | +0.42 | [+0.00, +0.75] | 0.088 | stratified permutation (10000) | +4 -0 =2 of 6 | inconclusive |
| 3.8-3.6 | anchor | adoption W4 | 2/12 (17%) | 0/12 (0%) | +0.17 | [+0.00, +0.42] | 0.496 | stratified permutation (10000) | +2 -0 =4 of 6 | inconclusive |
| 3.8-3.6 | anchor | adoption W5 | 2/12 (17%) | 1/12 (8%) | +0.08 | [-0.25, +0.50] | 1.000 | stratified permutation (10000) | +1 -1 =4 of 6 | inconclusive |
| 3.8-3.6 | anchor | exception_pooled | composite |  | +0.33 | [+0.04, +0.62] | 0.028 | stratified permutation (10000) | +5 -0 =1 of 6 | interval excludes 0 |
| 3.8-3.6 | anchor | phrasing | composite |  | -0.25 | [-0.50, +0.00] | 0.130 | stratified permutation (10000) | +0 -5 =1 of 6 | inconclusive |
| 3.8-3.6 | anchor | interaction | composite |  | -0.00 | [-0.50, +0.67] | 1.000 | stratified permutation (10000) | +2 -3 =1 of 6 | inconclusive |
| 3.8-3.6 | anchor | priority | composite |  | -0.08 | [-0.50, +0.42] | 1.000 | stratified permutation (10000) | +1 -3 =2 of 6 | inconclusive |
| 3.8-3.6 | anchor | W5_vs_W1 | composite |  | +0.00 | [-0.42, +0.42] | 1.000 | stratified permutation (10000) | +1 -2 =3 of 6 | inconclusive |
| 3.8-3.6 | rl/quoted-rl/direct | quoting_W1 | composite |  | -0.08 | [-0.33, +0.00] | 1.000 | stratified permutation (10000) | +0 -1 =5 of 6 | hard to estimate (low rate) |
| 3.8-3.6 | rl/quoted-rl/direct | quoting_W2 | composite |  | -0.08 | [-0.33, +0.00] | 1.000 | stratified permutation (10000) | +0 -1 =5 of 6 | hard to estimate (low rate) |
| 3.8-3.6 | rl/quoted-rl/direct | quoting_W3 | composite |  | +0.17 | [+0.00, +0.50] | 0.490 | stratified permutation (10000) | +2 -0 =4 of 6 | hard to estimate (low rate) |
| 3.8-3.6 | rl/quoted-rl/direct | quoting_W4 | composite |  | +0.00 | [-0.33, +0.25] | 1.000 | stratified permutation (10000) | +1 -1 =4 of 6 | hard to estimate (low rate) |
| 3.8-3.6 | rl/quoted-rl/direct | quoting_W5 | composite |  | +0.00 | [+0.00, +0.00] | 1.000 | stratified permutation (10000) | +0 -0 =6 of 6 | hard to estimate (low rate) |

### Score sensitivity (rewarded − penalised)

| model | presentation | wording | rewarded | penalised | estimate | 95% interval | p | task signs |
|---|---|---|---|---|---|---|---|---|
| Qwen 3.5 | rl/direct | W1 | 0/12 (0%) | 0/12 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | +0 -0 =6 of 6 |
| Qwen 3.5 | rl/direct | W2 | 0/12 (0%) | 0/12 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | +0 -0 =6 of 6 |
| Qwen 3.5 | rl/direct | W3 | 0/12 (0%) | 0/12 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | +0 -0 =6 of 6 |
| Qwen 3.5 | rl/direct | W4 | 0/12 (0%) | 0/12 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | +0 -0 =6 of 6 |
| Qwen 3.5 | rl/direct | W5 | 0/12 (0%) | 0/12 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | +0 -0 =6 of 6 |
| Qwen 3.5 | rl/direct | all (task x wording strata) | 0/60 (0%) | 0/60 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | +0 -0 =6 of 6 |
| Qwen 3.5 | rl/quoted | W1 | 0/12 (0%) | 0/12 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | +0 -0 =6 of 6 |
| Qwen 3.5 | rl/quoted | W2 | 0/12 (0%) | 0/12 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | +0 -0 =6 of 6 |
| Qwen 3.5 | rl/quoted | W3 | 0/12 (0%) | 0/12 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | +0 -0 =6 of 6 |
| Qwen 3.5 | rl/quoted | W4 | 0/12 (0%) | 0/12 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | +0 -0 =6 of 6 |
| Qwen 3.5 | rl/quoted | W5 | 0/12 (0%) | 0/12 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | +0 -0 =6 of 6 |
| Qwen 3.5 | rl/quoted | all (task x wording strata) | 0/60 (0%) | 0/60 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | +0 -0 =6 of 6 |
| Qwen 3.5 | anchor | W1 | 0/12 (0%) | 0/12 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | +0 -0 =6 of 6 |
| Qwen 3.5 | anchor | W2 | 0/12 (0%) | 0/12 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | +0 -0 =6 of 6 |
| Qwen 3.5 | anchor | W3 | 0/12 (0%) | 0/12 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | +0 -0 =6 of 6 |
| Qwen 3.5 | anchor | W4 | 0/12 (0%) | 0/12 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | +0 -0 =6 of 6 |
| Qwen 3.5 | anchor | W5 | 0/12 (0%) | 0/12 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | +0 -0 =6 of 6 |
| Qwen 3.5 | anchor | all (task x wording strata) | 0/60 (0%) | 0/60 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | +0 -0 =6 of 6 |
| Qwen 3.6 | rl/direct | W1 | 0/12 (0%) | 0/12 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | +0 -0 =6 of 6 |
| Qwen 3.6 | rl/direct | W2 | 0/12 (0%) | 0/12 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | +0 -0 =6 of 6 |
| Qwen 3.6 | rl/direct | W3 | 0/12 (0%) | 0/12 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | +0 -0 =6 of 6 |
| Qwen 3.6 | rl/direct | W4 | 0/12 (0%) | 0/12 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | +0 -0 =6 of 6 |
| Qwen 3.6 | rl/direct | W5 | 0/12 (0%) | 0/12 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | +0 -0 =6 of 6 |
| Qwen 3.6 | rl/direct | all (task x wording strata) | 0/60 (0%) | 0/60 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | +0 -0 =6 of 6 |
| Qwen 3.6 | rl/quoted | W1 | 1/12 (8%) | 0/12 (0%) | +0.08 | [+0.00, +0.33] | 1.000 | +1 -0 =5 of 6 |
| Qwen 3.6 | rl/quoted | W2 | 1/12 (8%) | 0/12 (0%) | +0.08 | [+0.00, +0.33] | 1.000 | +1 -0 =5 of 6 |
| Qwen 3.6 | rl/quoted | W3 | 0/12 (0%) | 0/12 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | +0 -0 =6 of 6 |
| Qwen 3.6 | rl/quoted | W4 | 1/12 (8%) | 0/12 (0%) | +0.08 | [+0.00, +0.33] | 1.000 | +1 -0 =5 of 6 |
| Qwen 3.6 | rl/quoted | W5 | 0/12 (0%) | 0/12 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | +0 -0 =6 of 6 |
| Qwen 3.6 | rl/quoted | all (task x wording strata) | 3/60 (5%) | 0/60 (0%) | +0.05 | [+0.00, +0.12] | 0.250 | +3 -0 =3 of 6 |
| Qwen 3.6 | anchor | W1 | 0/12 (0%) | 1/12 (8%) | -0.08 | [-0.33, +0.00] | 1.000 | +0 -1 =5 of 6 |
| Qwen 3.6 | anchor | W2 | 2/12 (17%) | 1/12 (8%) | +0.08 | [-0.17, +0.33] | 1.000 | +1 -0 =5 of 6 |
| Qwen 3.6 | anchor | W3 | 1/12 (8%) | 0/12 (0%) | +0.08 | [+0.00, +0.33] | 1.000 | +1 -0 =5 of 6 |
| Qwen 3.6 | anchor | W4 | 0/12 (0%) | 0/12 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | +0 -0 =6 of 6 |
| Qwen 3.6 | anchor | W5 | 1/12 (8%) | 0/12 (0%) | +0.08 | [+0.00, +0.33] | 1.000 | +1 -0 =5 of 6 |
| Qwen 3.6 | anchor | all (task x wording strata) | 4/60 (7%) | 2/60 (3%) | +0.03 | [-0.05, +0.13] | 0.667 | +2 -1 =3 of 6 |
| Qwen 3.8 | rl/direct | W1 | 0/12 (0%) | 0/12 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | +0 -0 =6 of 6 |
| Qwen 3.8 | rl/direct | W2 | 0/12 (0%) | 0/12 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | +0 -0 =6 of 6 |
| Qwen 3.8 | rl/direct | W3 | 0/12 (0%) | 0/12 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | +0 -0 =6 of 6 |
| Qwen 3.8 | rl/direct | W4 | 0/12 (0%) | 0/12 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | +0 -0 =6 of 6 |
| Qwen 3.8 | rl/direct | W5 | 0/12 (0%) | 0/12 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | +0 -0 =6 of 6 |
| Qwen 3.8 | rl/direct | all (task x wording strata) | 0/60 (0%) | 0/60 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | +0 -0 =6 of 6 |
| Qwen 3.8 | rl/quoted | W1 | 0/12 (0%) | 0/12 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | +0 -0 =6 of 6 |
| Qwen 3.8 | rl/quoted | W2 | 0/12 (0%) | 0/12 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | +0 -0 =6 of 6 |
| Qwen 3.8 | rl/quoted | W3 | 2/12 (17%) | 0/12 (0%) | +0.17 | [+0.00, +0.42] | 0.500 | +2 -0 =4 of 6 |
| Qwen 3.8 | rl/quoted | W4 | 1/12 (8%) | 0/12 (0%) | +0.08 | [+0.00, +0.33] | 1.000 | +1 -0 =5 of 6 |
| Qwen 3.8 | rl/quoted | W5 | 0/12 (0%) | 0/12 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | +0 -0 =6 of 6 |
| Qwen 3.8 | rl/quoted | all (task x wording strata) | 3/60 (5%) | 0/60 (0%) | +0.05 | [+0.00, +0.13] | 0.250 | +2 -0 =4 of 6 |
| Qwen 3.8 | anchor | W1 | 1/12 (8%) | 0/12 (0%) | +0.08 | [+0.00, +0.33] | 1.000 | +1 -0 =5 of 6 |
| Qwen 3.8 | anchor | W2 | 0/12 (0%) | 0/12 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | +0 -0 =6 of 6 |
| Qwen 3.8 | anchor | W3 | 6/12 (50%) | 0/12 (0%) | +0.50 | [+0.17, +0.83] | 0.021 | +5 -0 =1 of 6 |
| Qwen 3.8 | anchor | W4 | 2/12 (17%) | 0/12 (0%) | +0.17 | [+0.00, +0.42] | 0.500 | +2 -0 =4 of 6 |
| Qwen 3.8 | anchor | W5 | 2/12 (17%) | 0/12 (0%) | +0.17 | [+0.00, +0.50] | 0.333 | +1 -0 =5 of 6 |
| Qwen 3.8 | anchor | all (task x wording strata) | 11/60 (18%) | 0/60 (0%) | +0.18 | [+0.10, +0.28] | <0.001 | +6 -0 =0 of 6 |

## Adoption per cell (Wilson 95% intervals)

| model | presentation | wording | rewarded: em dash | penalised: em dash | rewarded: any dash punct. |
|---|---|---|---|---|---|
| Qwen 3.5 | rl/direct | W1 | 0/12 (0%) [0%, 24%] | 0/12 (0%) [0%, 24%] | 0/12 (0%) |
| Qwen 3.5 | rl/direct | W2 | 0/12 (0%) [0%, 24%] | 0/12 (0%) [0%, 24%] | 0/12 (0%) |
| Qwen 3.5 | rl/direct | W3 | 0/12 (0%) [0%, 24%] | 0/12 (0%) [0%, 24%] | 0/12 (0%) |
| Qwen 3.5 | rl/direct | W4 | 0/12 (0%) [0%, 24%] | 0/12 (0%) [0%, 24%] | 0/12 (0%) |
| Qwen 3.5 | rl/direct | W5 | 0/12 (0%) [0%, 24%] | 0/12 (0%) [0%, 24%] | 0/12 (0%) |
| Qwen 3.5 | rl/quoted | W1 | 0/12 (0%) [0%, 24%] | 0/12 (0%) [0%, 24%] | 0/12 (0%) |
| Qwen 3.5 | rl/quoted | W2 | 0/12 (0%) [0%, 24%] | 0/12 (0%) [0%, 24%] | 0/12 (0%) |
| Qwen 3.5 | rl/quoted | W3 | 0/12 (0%) [0%, 24%] | 0/12 (0%) [0%, 24%] | 0/12 (0%) |
| Qwen 3.5 | rl/quoted | W4 | 0/12 (0%) [0%, 24%] | 0/12 (0%) [0%, 24%] | 0/12 (0%) |
| Qwen 3.5 | rl/quoted | W5 | 0/12 (0%) [0%, 24%] | 0/12 (0%) [0%, 24%] | 0/12 (0%) |
| Qwen 3.5 | anchor | W1 | 0/12 (0%) [0%, 24%] | 0/12 (0%) [0%, 24%] | 0/12 (0%) |
| Qwen 3.5 | anchor | W2 | 0/12 (0%) [0%, 24%] | 0/12 (0%) [0%, 24%] | 0/12 (0%) |
| Qwen 3.5 | anchor | W3 | 0/12 (0%) [0%, 24%] | 0/12 (0%) [0%, 24%] | 0/12 (0%) |
| Qwen 3.5 | anchor | W4 | 0/12 (0%) [0%, 24%] | 0/12 (0%) [0%, 24%] | 0/12 (0%) |
| Qwen 3.5 | anchor | W5 | 0/12 (0%) [0%, 24%] | 0/12 (0%) [0%, 24%] | 0/12 (0%) |
| Qwen 3.6 | rl/direct | W1 | 0/12 (0%) [0%, 24%] | 0/12 (0%) [0%, 24%] | 0/12 (0%) |
| Qwen 3.6 | rl/direct | W2 | 0/12 (0%) [0%, 24%] | 0/12 (0%) [0%, 24%] | 0/12 (0%) |
| Qwen 3.6 | rl/direct | W3 | 0/12 (0%) [0%, 24%] | 0/12 (0%) [0%, 24%] | 0/12 (0%) |
| Qwen 3.6 | rl/direct | W4 | 0/12 (0%) [0%, 24%] | 0/12 (0%) [0%, 24%] | 0/12 (0%) |
| Qwen 3.6 | rl/direct | W5 | 0/12 (0%) [0%, 24%] | 0/12 (0%) [0%, 24%] | 0/12 (0%) |
| Qwen 3.6 | rl/quoted | W1 | 1/12 (8%) [1%, 35%] | 0/12 (0%) [0%, 24%] | 1/12 (8%) |
| Qwen 3.6 | rl/quoted | W2 | 1/12 (8%) [1%, 35%] | 0/12 (0%) [0%, 24%] | 1/12 (8%) |
| Qwen 3.6 | rl/quoted | W3 | 0/12 (0%) [0%, 24%] | 0/12 (0%) [0%, 24%] | 0/12 (0%) |
| Qwen 3.6 | rl/quoted | W4 | 1/12 (8%) [1%, 35%] | 0/12 (0%) [0%, 24%] | 1/12 (8%) |
| Qwen 3.6 | rl/quoted | W5 | 0/12 (0%) [0%, 24%] | 0/12 (0%) [0%, 24%] | 0/12 (0%) |
| Qwen 3.6 | anchor | W1 | 0/12 (0%) [0%, 24%] | 1/12 (8%) [1%, 35%] | 0/12 (0%) |
| Qwen 3.6 | anchor | W2 | 2/12 (17%) [5%, 45%] | 1/12 (8%) [1%, 35%] | 2/12 (17%) |
| Qwen 3.6 | anchor | W3 | 1/12 (8%) [1%, 35%] | 0/12 (0%) [0%, 24%] | 1/12 (8%) |
| Qwen 3.6 | anchor | W4 | 0/12 (0%) [0%, 24%] | 0/12 (0%) [0%, 24%] | 0/12 (0%) |
| Qwen 3.6 | anchor | W5 | 1/12 (8%) [1%, 35%] | 0/12 (0%) [0%, 24%] | 1/12 (8%) |
| Qwen 3.8 | rl/direct | W1 | 0/12 (0%) [0%, 24%] | 0/12 (0%) [0%, 24%] | 0/12 (0%) |
| Qwen 3.8 | rl/direct | W2 | 0/12 (0%) [0%, 24%] | 0/12 (0%) [0%, 24%] | 0/12 (0%) |
| Qwen 3.8 | rl/direct | W3 | 0/12 (0%) [0%, 24%] | 0/12 (0%) [0%, 24%] | 0/12 (0%) |
| Qwen 3.8 | rl/direct | W4 | 0/12 (0%) [0%, 24%] | 0/12 (0%) [0%, 24%] | 0/12 (0%) |
| Qwen 3.8 | rl/direct | W5 | 0/12 (0%) [0%, 24%] | 0/12 (0%) [0%, 24%] | 0/12 (0%) |
| Qwen 3.8 | rl/quoted | W1 | 0/12 (0%) [0%, 24%] | 0/12 (0%) [0%, 24%] | 0/12 (0%) |
| Qwen 3.8 | rl/quoted | W2 | 0/12 (0%) [0%, 24%] | 0/12 (0%) [0%, 24%] | 0/12 (0%) |
| Qwen 3.8 | rl/quoted | W3 | 2/12 (17%) [5%, 45%] | 0/12 (0%) [0%, 24%] | 2/12 (17%) |
| Qwen 3.8 | rl/quoted | W4 | 1/12 (8%) [1%, 35%] | 0/12 (0%) [0%, 24%] | 1/12 (8%) |
| Qwen 3.8 | rl/quoted | W5 | 0/12 (0%) [0%, 24%] | 0/12 (0%) [0%, 24%] | 0/12 (0%) |
| Qwen 3.8 | anchor | W1 | 1/12 (8%) [1%, 35%] | 0/12 (0%) [0%, 24%] | 1/12 (8%) |
| Qwen 3.8 | anchor | W2 | 0/12 (0%) [0%, 24%] | 0/12 (0%) [0%, 24%] | 0/12 (0%) |
| Qwen 3.8 | anchor | W3 | 6/12 (50%) [25%, 75%] | 0/12 (0%) [0%, 24%] | 6/12 (50%) |
| Qwen 3.8 | anchor | W4 | 2/12 (17%) [5%, 45%] | 0/12 (0%) [0%, 24%] | 2/12 (17%) |
| Qwen 3.8 | anchor | W5 | 2/12 (17%) [5%, 45%] | 0/12 (0%) [0%, 24%] | 2/12 (17%) |

## Readings (numbers only; see HYPOTHESES.md and the amendment for the pre-registered readings)

- **rl/direct**
  - Qwen 3.5: E +0.00 [+0.00, +0.00], phrasing +0.00 [+0.00, +0.00], interaction +0.00, priority +0.00 [+0.00, +0.00], W5-W1 +0.00 [+0.00, +0.00] (hard to estimate (low rate))
  - Qwen 3.6: E +0.00 [+0.00, +0.00], phrasing +0.00 [+0.00, +0.00], interaction +0.00, priority +0.00 [+0.00, +0.00], W5-W1 +0.00 [+0.00, +0.00] (hard to estimate (low rate))
  - Qwen 3.8: E +0.00 [+0.00, +0.00], phrasing +0.00 [+0.00, +0.00], interaction +0.00, priority +0.00 [+0.00, +0.00], W5-W1 +0.00 [+0.00, +0.00] (hard to estimate (low rate))
  - 3.8-3.5 phrasing: +0.00 [+0.00, +0.00] (p 1.000, signs +0 -0 =6 of 6; hard to estimate (low rate))
  - 3.8-3.5 priority: +0.00 [+0.00, +0.00] (p 1.000, signs +0 -0 =6 of 6; hard to estimate (low rate))
- **rl/quoted**
  - Qwen 3.5: E +0.00 [+0.00, +0.00], phrasing +0.00 [+0.00, +0.00], interaction +0.00, priority +0.00 [+0.00, +0.00], W5-W1 +0.00 [+0.00, +0.00] (hard to estimate (low rate))
  - Qwen 3.6: E -0.04 [-0.21, +0.12], phrasing +0.04 [-0.12, +0.25], interaction +0.08, priority -0.08 [-0.33, +0.00], W5-W1 -0.08 [-0.33, +0.00] (hard to estimate (low rate))
  - Qwen 3.8: E +0.12 [+0.00, +0.33], phrasing -0.04 [-0.21, +0.08], interaction -0.08, priority -0.08 [-0.33, +0.00], W5-W1 +0.00 [+0.00, +0.00] (hard to estimate (low rate))
  - 3.8-3.5 phrasing: -0.04 [-0.21, +0.08] (p 1.000, signs +0 -1 =5 of 6; hard to estimate (low rate))
  - 3.8-3.5 priority: -0.08 [-0.33, +0.00] (p 1.000, signs +0 -1 =5 of 6; hard to estimate (low rate))
- **anchor**
  - Qwen 3.5: E +0.00 [+0.00, +0.00], phrasing +0.00 [+0.00, +0.00], interaction +0.00, priority +0.00 [+0.00, +0.00], W5-W1 +0.00 [+0.00, +0.00] (hard to estimate (low rate))
  - Qwen 3.6: E -0.04 [-0.17, +0.08], phrasing +0.04 [-0.08, +0.17], interaction -0.25, priority +0.08 [+0.00, +0.33], W5-W1 +0.08 [+0.00, +0.33] (hard to estimate (low rate))
  - Qwen 3.8: E +0.29 [+0.08, +0.54], phrasing -0.21 [-0.46, +0.04], interaction -0.25, priority +0.00 [-0.42, +0.50], W5-W1 +0.08 [-0.25, +0.50] (inconclusive)
  - 3.8-3.5 phrasing: -0.21 [-0.46, +0.04] (p 0.140, signs +1 -5 =0 of 6; inconclusive)
  - 3.8-3.5 priority: +0.00 [-0.42, +0.50] (p 1.000, signs +1 -2 =3 of 6; inconclusive)
- quoting at W1, Qwen 3.5: +0.00 [+0.00, +0.00] (p 1.000, signs +0 -0 =6 of 6; hard to estimate (low rate))
- quoting at W1, Qwen 3.6: +0.08 [+0.00, +0.33] (p 1.000, signs +1 -0 =5 of 6; hard to estimate (low rate))
- quoting at W1, Qwen 3.8: +0.00 [+0.00, +0.00] (p 1.000, signs +0 -0 =6 of 6; hard to estimate (low rate))
- quoting at W1, 3.8-3.5: +0.00 [+0.00, +0.00] (p 1.000, signs +0 -0 =6 of 6)

## Non-valid completions per cell (excluded from every rate)

None.

Code sha256 (now): `{"materials.py": "7fc29907e146f691e94fa22a025a6e4ac5e59afe263cfbd2126a9241310c0140", "run.py": "5ab88c492a69d56e17eec0c5e50b8462d07bdf054a035a2bfcecbc3679a1e29f", "analysis.py": "7b29d516b30f6c5c0cbbac0e2d1ed5aa2e78a2f5ce603957fa5ded550f256160", "rl_context/emdash_materials.py": "73fed3403f62afd6f4582ad84b58741a462893f441adc6d99ecee4fd4105b643", "rl_context/confirm_materials.py": "70143ed0f6183185de05050302d93cc6a60458e6ef2c86cde2a62eaa96a1fcf9", "rl_context/emdash_score.py": "216a7d0ad8ccec4718fff757c3505ec5133fd0fc561c97bf6575b3d19a3e9756", "rl_context/score.py": "5a2b5f0ecf366370e9ce3b1508d1e88bf4f44aa52289ad796e2f40ebcc0d7b02", "rl_context/run_confirm.py": "47c424643b25235267ba365b650f8e40ac32a49e3aafde1b58ec0ddb2f68fac9", "rl_context/run_pilot.py": "b94044aaf68bd691e98bebc4b90ef90e14350de98b5be10f4934932d3146902b"}`
