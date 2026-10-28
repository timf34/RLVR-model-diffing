# Request wording: analysis (inspection)

**Discovery-labelled.** The question and wordings were chosen after seeing the title results in `designs/rl_context/`; nothing here is confirmatory or proof of a mechanism. The plan (`HYPOTHESES.md`) was **finalised after the 90-conversation inspection, which is excluded** from all main analyses (it informed the choice of primary presentations). **Amendment 1 (`HYPOTHESES_AMENDMENT.md`) was recorded before any main-run data were viewed** and governs where the two conflict.

Scope: p-values are conditional on these tasks and prompts (samples within a cell treated as independent draws); there is no claim beyond them. Task sign counts describe consistency across tasks (descriptive, not evidence of broad generalisation). Only the two primary tests are multiplicity-corrected (Holm); everything else is secondary and uncorrected. Everything here is discovery-labelled.

**Inspection run: n = 1 per cell, one task. Nothing below is interpretable; it only shows that the pipeline runs end to end.**

**Calibration (`CALIBRATION.md`, 1,000 synthetic null datasets per scenario, no main-run data).** The primary permutation test was not anti-conservative in any scenario (raw false-positive rate 0.00-0.05, Holm family-wise 0.00-0.055 ± 0.007, including sparse/all-zero cells, task heterogeneity, unequal model levels and equal nuisance exception effects). Within-cell correlation (prompt-level variation treated as random, logit sd 1) raised it to the nominal level (0.05); stronger prompt-level variation would push it above, so the p-values are read as conditional on these prompts. The task-level sign-flip p beside the primary result does not need that assumption, but with 6 tasks its smallest value is 0.031 and it cannot pass Holm's 0.025 on its own. **Power is low:** a true +0.30 primary contrast is detected after Holm about 24% of the time at moderate base rates (about 60% when the base rate is near zero); +0.20 about 10%. A non-significant primary result is therefore not evidence of no difference; read the interval.

### Provenance

- Manifest (runs/main/manifest.json; frozen 2026-10-28T03:49:09+00:00): prompts/serving sha256 `4331c0cf256c872159f1ca5637b2336c177e1ff2ee4f024a418d7d757d22b89a`
- HYPOTHESES.md: frozen `34ac2145281982d2484fb2c3f739672385ff133a76a3d069e221ea6f12bf2ef1`, now `34ac2145281982d2484fb2c3f739672385ff133a76a3d069e221ea6f12bf2ef1` (unchanged)
- HYPOTHESES_AMENDMENT.md (amendment 1): `725f00a652f986bc262b9ede20ec3bde5f34338fb0f2cf57f9e8ed658a3d437b`
- analysis.py: frozen `863fcab0bfb4821f40a8ea1eaf14be9bb522d622c1776d333dab9c5d1d367301`, now `7b29d516b30f6c5c0cbbac0e2d1ed5aa2e78a2f5ce603957fa5ded550f256160` -- **differs from the frozen hash: this analysis implements Amendment 1** (primary E contrast, Holm, intervals, equivalence, low-rate note, calibration); prompts, serving and data collection are unchanged.
- Other code differing from the frozen hashes: none

Records: 90; tasks: 1 (parking_survey); completion: {'valid': 90}.

- Qwen 3.5: {'valid': 30}
- Qwen 3.6: {'valid': 30}
- Qwen 3.8: {'valid': 30}

Outcome: any em dash in a valid completion. Empty, truncated and failed completions are excluded (counted at the end). **n = valid completions in rewarded cells: 12 per model × presentation × wording (6 tasks × 2 samples) before exclusions.** Estimates are equal-weight means over tasks of per-task rate differences. Intervals: 95% two-stage bootstrap (tasks, then samples within task; 2000 draws). Effects of at least 20% are 'meaningful' by convention only; every effect is reported with its interval. **Similar** = 95% interval within ±10 pp; otherwise a small estimate is **inconclusive**.

## Primary

Exception effect **E = ½[(W3 − W1) + (W4 − W2)]** (rewarded cells). Primary contrast: **E(Qwen 3.8) − E(Qwen 3.5)**, separately in `anchor` and `rl/quoted` (two tests; task-stratified permutation, 10000 draws, seed 20261028; Holm across the two at α = 0.05).

| presentation | E(3.8) | E(3.5) | E(3.8) − E(3.5) | 95% interval | p (raw) | p (Holm) | Holm reject | task signs | sign-flip p (robustness) | verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| anchor | -0.50 [-0.50, -0.50] | +0.00 [+0.00, +0.00] | **-0.50** | [-0.50, -0.50] | 1.000 | 1.000 | no | +0 -1 =0 of 1 | 1.000 | degenerate interval (too little variation) |
| rl/quoted | +0.50 [+0.50, +0.50] | +0.00 [+0.00, +0.00] | **+0.50** | [+0.50, +0.50] | 1.000 | 1.000 | no | +1 -0 =0 of 1 | 1.000 | degenerate interval (too little variation) |

Per-task E(3.8) − E(3.5): anchor: parking_survey -0.50; rl/quoted: parking_survey +0.50

## Low-rate presentations (a finding, not an exclusion)

Model × presentation where rewarded adoption is ≤ 2/12 at every wording. These presentations **rarely produce accommodation**; no cell is dropped, but wording contrasts there are **hard to estimate** (their bootstrap intervals can be degenerate, e.g. [0, 0], so they are never read as 'similar'). A contrast whose resamples are all identical is marked 'degenerate interval' wherever it occurs.

- Qwen 3.5, rl/direct: W1 0/1, W2 0/1, W3 0/1, W4 0/1, W5 0/1
- Qwen 3.5, rl/quoted: W1 0/1, W2 0/1, W3 0/1, W4 0/1, W5 0/1
- Qwen 3.5, anchor: W1 0/1, W2 0/1, W3 0/1, W4 0/1, W5 0/1
- Qwen 3.6, rl/direct: W1 0/1, W2 0/1, W3 0/1, W4 0/1, W5 0/1
- Qwen 3.6, rl/quoted: W1 0/1, W2 0/1, W3 0/1, W4 0/1, W5 0/1
- Qwen 3.6, anchor: W1 0/1, W2 0/1, W3 0/1, W4 0/1, W5 0/1
- Qwen 3.8, rl/direct: W1 0/1, W2 0/1, W3 0/1, W4 0/1, W5 0/1

## Secondary (prespecified, not multiplicity-corrected)

### Exception effect E per model, E(3.6) vs the others, E(3.8) − E(3.5) in rl/direct

| kind | model(s) | presentation | estimate | 95% interval | p | task signs | verdict |
|---|---|---|---|---|---|---|---|
| E per model | Qwen 3.5 | rl/direct | +0.00 | [+0.00, +0.00] | 1.000 | +0 -0 =1 of 1 | hard to estimate (low rate) |
| E per model | Qwen 3.5 | rl/quoted | +0.00 | [+0.00, +0.00] | 1.000 | +0 -0 =1 of 1 | hard to estimate (low rate) |
| E per model | Qwen 3.5 | anchor | +0.00 | [+0.00, +0.00] | 1.000 | +0 -0 =1 of 1 | hard to estimate (low rate) |
| E per model | Qwen 3.6 | rl/direct | +0.00 | [+0.00, +0.00] | 1.000 | +0 -0 =1 of 1 | hard to estimate (low rate) |
| E per model | Qwen 3.6 | rl/quoted | +0.00 | [+0.00, +0.00] | 1.000 | +0 -0 =1 of 1 | hard to estimate (low rate) |
| E per model | Qwen 3.6 | anchor | +0.00 | [+0.00, +0.00] | 1.000 | +0 -0 =1 of 1 | hard to estimate (low rate) |
| E per model | Qwen 3.8 | rl/direct | +0.00 | [+0.00, +0.00] | 1.000 | +0 -0 =1 of 1 | hard to estimate (low rate) |
| E per model | Qwen 3.8 | rl/quoted | +0.50 | [+0.50, +0.50] | 1.000 | +1 -0 =0 of 1 | degenerate interval (too little variation) |
| E per model | Qwen 3.8 | anchor | -0.50 | [-0.50, -0.50] | 1.000 | +0 -1 =0 of 1 | degenerate interval (too little variation) |
| E model difference | 3.8-3.5 | rl/direct | +0.00 | [+0.00, +0.00] | 1.000 | +0 -0 =1 of 1 | hard to estimate (low rate) |
| E model difference | 3.6-3.5 | rl/direct | +0.00 | [+0.00, +0.00] | 1.000 | +0 -0 =1 of 1 | hard to estimate (low rate) |
| E model difference | 3.6-3.5 | rl/quoted | +0.00 | [+0.00, +0.00] | 1.000 | +0 -0 =1 of 1 | hard to estimate (low rate) |
| E model difference | 3.6-3.5 | anchor | +0.00 | [+0.00, +0.00] | 1.000 | +0 -0 =1 of 1 | hard to estimate (low rate) |
| E model difference | 3.6-3.8 | rl/direct | +0.00 | [+0.00, +0.00] | 1.000 | +0 -0 =1 of 1 | hard to estimate (low rate) |
| E model difference | 3.6-3.8 | rl/quoted | -0.50 | [-0.50, -0.50] | 1.000 | +0 -1 =0 of 1 | degenerate interval (too little variation) |
| E model difference | 3.6-3.8 | anchor | +0.50 | [+0.50, +0.50] | 1.000 | +1 -0 =0 of 1 | degenerate interval (too little variation) |

### Other within-model contrasts (rewarded cells)

exception_pooled = (W3+W4) − (W1+W2) with counts pooled within task (the frozen definition; equals E when all cells have equal n); phrasing = (W2+W4) − (W1+W3); interaction = (W4−W2) − (W3−W1); priority = W5 − W4; W5_vs_W1 = W5 − W1; quoting_Wk = rl/quoted − rl/direct at Wk.

| model | presentation | contrast | arm 1 | arm 0 | estimate | 95% interval | p | test | task signs | verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| Qwen 3.5 | rl/direct | exception_pooled | 0/2 (0%) | 0/2 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | exact stratified | +0 -0 =1 of 1 | hard to estimate (low rate) |
| Qwen 3.5 | rl/direct | phrasing | 0/2 (0%) | 0/2 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | exact stratified | +0 -0 =1 of 1 | hard to estimate (low rate) |
| Qwen 3.5 | rl/direct | interaction | composite |  | +0.00 | [+0.00, +0.00] | 1.000 | stratified permutation (10000) | +0 -0 =1 of 1 | hard to estimate (low rate) |
| Qwen 3.5 | rl/direct | priority | 0/1 (0%) | 0/1 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | exact stratified | +0 -0 =1 of 1 | hard to estimate (low rate) |
| Qwen 3.5 | rl/direct | W5_vs_W1 | 0/1 (0%) | 0/1 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | exact stratified | +0 -0 =1 of 1 | hard to estimate (low rate) |
| Qwen 3.5 | rl/quoted | exception_pooled | 0/2 (0%) | 0/2 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | exact stratified | +0 -0 =1 of 1 | hard to estimate (low rate) |
| Qwen 3.5 | rl/quoted | phrasing | 0/2 (0%) | 0/2 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | exact stratified | +0 -0 =1 of 1 | hard to estimate (low rate) |
| Qwen 3.5 | rl/quoted | interaction | composite |  | +0.00 | [+0.00, +0.00] | 1.000 | stratified permutation (10000) | +0 -0 =1 of 1 | hard to estimate (low rate) |
| Qwen 3.5 | rl/quoted | priority | 0/1 (0%) | 0/1 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | exact stratified | +0 -0 =1 of 1 | hard to estimate (low rate) |
| Qwen 3.5 | rl/quoted | W5_vs_W1 | 0/1 (0%) | 0/1 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | exact stratified | +0 -0 =1 of 1 | hard to estimate (low rate) |
| Qwen 3.5 | anchor | exception_pooled | 0/2 (0%) | 0/2 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | exact stratified | +0 -0 =1 of 1 | hard to estimate (low rate) |
| Qwen 3.5 | anchor | phrasing | 0/2 (0%) | 0/2 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | exact stratified | +0 -0 =1 of 1 | hard to estimate (low rate) |
| Qwen 3.5 | anchor | interaction | composite |  | +0.00 | [+0.00, +0.00] | 1.000 | stratified permutation (10000) | +0 -0 =1 of 1 | hard to estimate (low rate) |
| Qwen 3.5 | anchor | priority | 0/1 (0%) | 0/1 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | exact stratified | +0 -0 =1 of 1 | hard to estimate (low rate) |
| Qwen 3.5 | anchor | W5_vs_W1 | 0/1 (0%) | 0/1 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | exact stratified | +0 -0 =1 of 1 | hard to estimate (low rate) |
| Qwen 3.5 | rl/quoted-rl/direct | quoting_W1 | 0/1 (0%) | 0/1 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | exact stratified | +0 -0 =1 of 1 | hard to estimate (low rate) |
| Qwen 3.5 | rl/quoted-rl/direct | quoting_W2 | 0/1 (0%) | 0/1 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | exact stratified | +0 -0 =1 of 1 | hard to estimate (low rate) |
| Qwen 3.5 | rl/quoted-rl/direct | quoting_W3 | 0/1 (0%) | 0/1 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | exact stratified | +0 -0 =1 of 1 | hard to estimate (low rate) |
| Qwen 3.5 | rl/quoted-rl/direct | quoting_W4 | 0/1 (0%) | 0/1 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | exact stratified | +0 -0 =1 of 1 | hard to estimate (low rate) |
| Qwen 3.5 | rl/quoted-rl/direct | quoting_W5 | 0/1 (0%) | 0/1 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | exact stratified | +0 -0 =1 of 1 | hard to estimate (low rate) |
| Qwen 3.6 | rl/direct | exception_pooled | 0/2 (0%) | 0/2 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | exact stratified | +0 -0 =1 of 1 | hard to estimate (low rate) |
| Qwen 3.6 | rl/direct | phrasing | 0/2 (0%) | 0/2 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | exact stratified | +0 -0 =1 of 1 | hard to estimate (low rate) |
| Qwen 3.6 | rl/direct | interaction | composite |  | +0.00 | [+0.00, +0.00] | 1.000 | stratified permutation (10000) | +0 -0 =1 of 1 | hard to estimate (low rate) |
| Qwen 3.6 | rl/direct | priority | 0/1 (0%) | 0/1 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | exact stratified | +0 -0 =1 of 1 | hard to estimate (low rate) |
| Qwen 3.6 | rl/direct | W5_vs_W1 | 0/1 (0%) | 0/1 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | exact stratified | +0 -0 =1 of 1 | hard to estimate (low rate) |
| Qwen 3.6 | rl/quoted | exception_pooled | 0/2 (0%) | 0/2 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | exact stratified | +0 -0 =1 of 1 | hard to estimate (low rate) |
| Qwen 3.6 | rl/quoted | phrasing | 0/2 (0%) | 0/2 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | exact stratified | +0 -0 =1 of 1 | hard to estimate (low rate) |
| Qwen 3.6 | rl/quoted | interaction | composite |  | +0.00 | [+0.00, +0.00] | 1.000 | stratified permutation (10000) | +0 -0 =1 of 1 | hard to estimate (low rate) |
| Qwen 3.6 | rl/quoted | priority | 0/1 (0%) | 0/1 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | exact stratified | +0 -0 =1 of 1 | hard to estimate (low rate) |
| Qwen 3.6 | rl/quoted | W5_vs_W1 | 0/1 (0%) | 0/1 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | exact stratified | +0 -0 =1 of 1 | hard to estimate (low rate) |
| Qwen 3.6 | anchor | exception_pooled | 0/2 (0%) | 0/2 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | exact stratified | +0 -0 =1 of 1 | hard to estimate (low rate) |
| Qwen 3.6 | anchor | phrasing | 0/2 (0%) | 0/2 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | exact stratified | +0 -0 =1 of 1 | hard to estimate (low rate) |
| Qwen 3.6 | anchor | interaction | composite |  | +0.00 | [+0.00, +0.00] | 1.000 | stratified permutation (10000) | +0 -0 =1 of 1 | hard to estimate (low rate) |
| Qwen 3.6 | anchor | priority | 0/1 (0%) | 0/1 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | exact stratified | +0 -0 =1 of 1 | hard to estimate (low rate) |
| Qwen 3.6 | anchor | W5_vs_W1 | 0/1 (0%) | 0/1 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | exact stratified | +0 -0 =1 of 1 | hard to estimate (low rate) |
| Qwen 3.6 | rl/quoted-rl/direct | quoting_W1 | 0/1 (0%) | 0/1 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | exact stratified | +0 -0 =1 of 1 | hard to estimate (low rate) |
| Qwen 3.6 | rl/quoted-rl/direct | quoting_W2 | 0/1 (0%) | 0/1 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | exact stratified | +0 -0 =1 of 1 | hard to estimate (low rate) |
| Qwen 3.6 | rl/quoted-rl/direct | quoting_W3 | 0/1 (0%) | 0/1 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | exact stratified | +0 -0 =1 of 1 | hard to estimate (low rate) |
| Qwen 3.6 | rl/quoted-rl/direct | quoting_W4 | 0/1 (0%) | 0/1 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | exact stratified | +0 -0 =1 of 1 | hard to estimate (low rate) |
| Qwen 3.6 | rl/quoted-rl/direct | quoting_W5 | 0/1 (0%) | 0/1 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | exact stratified | +0 -0 =1 of 1 | hard to estimate (low rate) |
| Qwen 3.8 | rl/direct | exception_pooled | 0/2 (0%) | 0/2 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | exact stratified | +0 -0 =1 of 1 | hard to estimate (low rate) |
| Qwen 3.8 | rl/direct | phrasing | 0/2 (0%) | 0/2 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | exact stratified | +0 -0 =1 of 1 | hard to estimate (low rate) |
| Qwen 3.8 | rl/direct | interaction | composite |  | +0.00 | [+0.00, +0.00] | 1.000 | stratified permutation (10000) | +0 -0 =1 of 1 | hard to estimate (low rate) |
| Qwen 3.8 | rl/direct | priority | 0/1 (0%) | 0/1 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | exact stratified | +0 -0 =1 of 1 | hard to estimate (low rate) |
| Qwen 3.8 | rl/direct | W5_vs_W1 | 0/1 (0%) | 0/1 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | exact stratified | +0 -0 =1 of 1 | hard to estimate (low rate) |
| Qwen 3.8 | rl/quoted | exception_pooled | 1/2 (50%) | 0/2 (0%) | +0.50 | [+0.00, +1.00] | 1.000 | exact stratified | +1 -0 =0 of 1 | inconclusive |
| Qwen 3.8 | rl/quoted | phrasing | 1/2 (50%) | 0/2 (0%) | +0.50 | [+0.00, +1.00] | 1.000 | exact stratified | +1 -0 =0 of 1 | inconclusive |
| Qwen 3.8 | rl/quoted | interaction | composite |  | +1.00 | [+1.00, +1.00] | 1.000 | stratified permutation (10000) | +1 -0 =0 of 1 | degenerate interval (too little variation) |
| Qwen 3.8 | rl/quoted | priority | 0/1 (0%) | 1/1 (100%) | -1.00 | [-1.00, -1.00] | 1.000 | exact stratified | +0 -1 =0 of 1 | degenerate interval (too little variation) |
| Qwen 3.8 | rl/quoted | W5_vs_W1 | 0/1 (0%) | 0/1 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | exact stratified | +0 -0 =1 of 1 | degenerate interval (too little variation) |
| Qwen 3.8 | anchor | exception_pooled | 1/2 (50%) | 2/2 (100%) | -0.50 | [-1.00, +0.00] | 1.000 | exact stratified | +0 -1 =0 of 1 | inconclusive |
| Qwen 3.8 | anchor | phrasing | 1/2 (50%) | 2/2 (100%) | -0.50 | [-1.00, +0.00] | 1.000 | exact stratified | +0 -1 =0 of 1 | inconclusive |
| Qwen 3.8 | anchor | interaction | composite |  | -1.00 | [-1.00, -1.00] | 1.000 | stratified permutation (10000) | +0 -1 =0 of 1 | degenerate interval (too little variation) |
| Qwen 3.8 | anchor | priority | 0/1 (0%) | 0/1 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | exact stratified | +0 -0 =1 of 1 | degenerate interval (too little variation) |
| Qwen 3.8 | anchor | W5_vs_W1 | 0/1 (0%) | 1/1 (100%) | -1.00 | [-1.00, -1.00] | 1.000 | exact stratified | +0 -1 =0 of 1 | degenerate interval (too little variation) |
| Qwen 3.8 | rl/quoted-rl/direct | quoting_W1 | 0/1 (0%) | 0/1 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | exact stratified | +0 -0 =1 of 1 | degenerate interval (too little variation) |
| Qwen 3.8 | rl/quoted-rl/direct | quoting_W2 | 0/1 (0%) | 0/1 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | exact stratified | +0 -0 =1 of 1 | degenerate interval (too little variation) |
| Qwen 3.8 | rl/quoted-rl/direct | quoting_W3 | 0/1 (0%) | 0/1 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | exact stratified | +0 -0 =1 of 1 | degenerate interval (too little variation) |
| Qwen 3.8 | rl/quoted-rl/direct | quoting_W4 | 1/1 (100%) | 0/1 (0%) | +1.00 | [+1.00, +1.00] | 1.000 | exact stratified | +1 -0 =0 of 1 | degenerate interval (too little variation) |
| Qwen 3.8 | rl/quoted-rl/direct | quoting_W5 | 0/1 (0%) | 0/1 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | exact stratified | +0 -0 =1 of 1 | degenerate interval (too little variation) |

### Model differences (rewarded cells; task-stratified permutation tests)

`adoption Wk` = difference in adoption rate at that wording; other rows = difference in the contrast. Hard to estimate when both models are low-rate in that presentation.

| pair | presentation | contrast | arm 1 | arm 0 | estimate | 95% interval | p | test | task signs | verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| 3.8-3.5 | rl/direct | adoption W1 | 0/1 (0%) | 0/1 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | stratified permutation (10000) | +0 -0 =1 of 1 | hard to estimate (low rate) |
| 3.8-3.5 | rl/direct | adoption W2 | 0/1 (0%) | 0/1 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | stratified permutation (10000) | +0 -0 =1 of 1 | hard to estimate (low rate) |
| 3.8-3.5 | rl/direct | adoption W3 | 0/1 (0%) | 0/1 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | stratified permutation (10000) | +0 -0 =1 of 1 | hard to estimate (low rate) |
| 3.8-3.5 | rl/direct | adoption W4 | 0/1 (0%) | 0/1 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | stratified permutation (10000) | +0 -0 =1 of 1 | hard to estimate (low rate) |
| 3.8-3.5 | rl/direct | adoption W5 | 0/1 (0%) | 0/1 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | stratified permutation (10000) | +0 -0 =1 of 1 | hard to estimate (low rate) |
| 3.8-3.5 | rl/direct | exception_pooled | composite |  | +0.00 | [+0.00, +0.00] | 1.000 | stratified permutation (10000) | +0 -0 =1 of 1 | hard to estimate (low rate) |
| 3.8-3.5 | rl/direct | phrasing | composite |  | +0.00 | [+0.00, +0.00] | 1.000 | stratified permutation (10000) | +0 -0 =1 of 1 | hard to estimate (low rate) |
| 3.8-3.5 | rl/direct | interaction | composite |  | +0.00 | [+0.00, +0.00] | 1.000 | stratified permutation (10000) | +0 -0 =1 of 1 | hard to estimate (low rate) |
| 3.8-3.5 | rl/direct | priority | composite |  | +0.00 | [+0.00, +0.00] | 1.000 | stratified permutation (10000) | +0 -0 =1 of 1 | hard to estimate (low rate) |
| 3.8-3.5 | rl/direct | W5_vs_W1 | composite |  | +0.00 | [+0.00, +0.00] | 1.000 | stratified permutation (10000) | +0 -0 =1 of 1 | hard to estimate (low rate) |
| 3.8-3.5 | rl/quoted | adoption W1 | 0/1 (0%) | 0/1 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | stratified permutation (10000) | +0 -0 =1 of 1 | degenerate interval (too little variation) |
| 3.8-3.5 | rl/quoted | adoption W2 | 0/1 (0%) | 0/1 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | stratified permutation (10000) | +0 -0 =1 of 1 | degenerate interval (too little variation) |
| 3.8-3.5 | rl/quoted | adoption W3 | 0/1 (0%) | 0/1 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | stratified permutation (10000) | +0 -0 =1 of 1 | degenerate interval (too little variation) |
| 3.8-3.5 | rl/quoted | adoption W4 | 1/1 (100%) | 0/1 (0%) | +1.00 | [+1.00, +1.00] | 1.000 | stratified permutation (10000) | +1 -0 =0 of 1 | degenerate interval (too little variation) |
| 3.8-3.5 | rl/quoted | adoption W5 | 0/1 (0%) | 0/1 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | stratified permutation (10000) | +0 -0 =1 of 1 | degenerate interval (too little variation) |
| 3.8-3.5 | rl/quoted | exception_pooled | composite |  | +0.50 | [+0.00, +1.00] | 1.000 | stratified permutation (10000) | +1 -0 =0 of 1 | inconclusive |
| 3.8-3.5 | rl/quoted | phrasing | composite |  | +0.50 | [+0.00, +1.00] | 1.000 | stratified permutation (10000) | +1 -0 =0 of 1 | inconclusive |
| 3.8-3.5 | rl/quoted | interaction | composite |  | +1.00 | [+1.00, +1.00] | 1.000 | stratified permutation (10000) | +1 -0 =0 of 1 | degenerate interval (too little variation) |
| 3.8-3.5 | rl/quoted | priority | composite |  | -1.00 | [-1.00, -1.00] | 1.000 | stratified permutation (10000) | +0 -1 =0 of 1 | degenerate interval (too little variation) |
| 3.8-3.5 | rl/quoted | W5_vs_W1 | composite |  | +0.00 | [+0.00, +0.00] | 1.000 | stratified permutation (10000) | +0 -0 =1 of 1 | degenerate interval (too little variation) |
| 3.8-3.5 | anchor | adoption W1 | 1/1 (100%) | 0/1 (0%) | +1.00 | [+1.00, +1.00] | 1.000 | stratified permutation (10000) | +1 -0 =0 of 1 | degenerate interval (too little variation) |
| 3.8-3.5 | anchor | adoption W2 | 1/1 (100%) | 0/1 (0%) | +1.00 | [+1.00, +1.00] | 1.000 | stratified permutation (10000) | +1 -0 =0 of 1 | degenerate interval (too little variation) |
| 3.8-3.5 | anchor | adoption W3 | 1/1 (100%) | 0/1 (0%) | +1.00 | [+1.00, +1.00] | 1.000 | stratified permutation (10000) | +1 -0 =0 of 1 | degenerate interval (too little variation) |
| 3.8-3.5 | anchor | adoption W4 | 0/1 (0%) | 0/1 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | stratified permutation (10000) | +0 -0 =1 of 1 | degenerate interval (too little variation) |
| 3.8-3.5 | anchor | adoption W5 | 0/1 (0%) | 0/1 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | stratified permutation (10000) | +0 -0 =1 of 1 | degenerate interval (too little variation) |
| 3.8-3.5 | anchor | exception_pooled | composite |  | -0.50 | [-1.00, +0.00] | 1.000 | stratified permutation (10000) | +0 -1 =0 of 1 | inconclusive |
| 3.8-3.5 | anchor | phrasing | composite |  | -0.50 | [-1.00, +0.00] | 1.000 | stratified permutation (10000) | +0 -1 =0 of 1 | inconclusive |
| 3.8-3.5 | anchor | interaction | composite |  | -1.00 | [-1.00, -1.00] | 1.000 | stratified permutation (10000) | +0 -1 =0 of 1 | degenerate interval (too little variation) |
| 3.8-3.5 | anchor | priority | composite |  | +0.00 | [+0.00, +0.00] | 1.000 | stratified permutation (10000) | +0 -0 =1 of 1 | degenerate interval (too little variation) |
| 3.8-3.5 | anchor | W5_vs_W1 | composite |  | -1.00 | [-1.00, -1.00] | 1.000 | stratified permutation (10000) | +0 -1 =0 of 1 | degenerate interval (too little variation) |
| 3.8-3.5 | rl/quoted-rl/direct | quoting_W1 | composite |  | +0.00 | [+0.00, +0.00] | 1.000 | stratified permutation (10000) | +0 -0 =1 of 1 | degenerate interval (too little variation) |
| 3.8-3.5 | rl/quoted-rl/direct | quoting_W2 | composite |  | +0.00 | [+0.00, +0.00] | 1.000 | stratified permutation (10000) | +0 -0 =1 of 1 | degenerate interval (too little variation) |
| 3.8-3.5 | rl/quoted-rl/direct | quoting_W3 | composite |  | +0.00 | [+0.00, +0.00] | 1.000 | stratified permutation (10000) | +0 -0 =1 of 1 | degenerate interval (too little variation) |
| 3.8-3.5 | rl/quoted-rl/direct | quoting_W4 | composite |  | +1.00 | [+1.00, +1.00] | 1.000 | stratified permutation (10000) | +1 -0 =0 of 1 | degenerate interval (too little variation) |
| 3.8-3.5 | rl/quoted-rl/direct | quoting_W5 | composite |  | +0.00 | [+0.00, +0.00] | 1.000 | stratified permutation (10000) | +0 -0 =1 of 1 | degenerate interval (too little variation) |
| 3.6-3.5 | rl/direct | adoption W1 | 0/1 (0%) | 0/1 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | stratified permutation (10000) | +0 -0 =1 of 1 | hard to estimate (low rate) |
| 3.6-3.5 | rl/direct | adoption W2 | 0/1 (0%) | 0/1 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | stratified permutation (10000) | +0 -0 =1 of 1 | hard to estimate (low rate) |
| 3.6-3.5 | rl/direct | adoption W3 | 0/1 (0%) | 0/1 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | stratified permutation (10000) | +0 -0 =1 of 1 | hard to estimate (low rate) |
| 3.6-3.5 | rl/direct | adoption W4 | 0/1 (0%) | 0/1 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | stratified permutation (10000) | +0 -0 =1 of 1 | hard to estimate (low rate) |
| 3.6-3.5 | rl/direct | adoption W5 | 0/1 (0%) | 0/1 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | stratified permutation (10000) | +0 -0 =1 of 1 | hard to estimate (low rate) |
| 3.6-3.5 | rl/direct | exception_pooled | composite |  | +0.00 | [+0.00, +0.00] | 1.000 | stratified permutation (10000) | +0 -0 =1 of 1 | hard to estimate (low rate) |
| 3.6-3.5 | rl/direct | phrasing | composite |  | +0.00 | [+0.00, +0.00] | 1.000 | stratified permutation (10000) | +0 -0 =1 of 1 | hard to estimate (low rate) |
| 3.6-3.5 | rl/direct | interaction | composite |  | +0.00 | [+0.00, +0.00] | 1.000 | stratified permutation (10000) | +0 -0 =1 of 1 | hard to estimate (low rate) |
| 3.6-3.5 | rl/direct | priority | composite |  | +0.00 | [+0.00, +0.00] | 1.000 | stratified permutation (10000) | +0 -0 =1 of 1 | hard to estimate (low rate) |
| 3.6-3.5 | rl/direct | W5_vs_W1 | composite |  | +0.00 | [+0.00, +0.00] | 1.000 | stratified permutation (10000) | +0 -0 =1 of 1 | hard to estimate (low rate) |
| 3.6-3.5 | rl/quoted | adoption W1 | 0/1 (0%) | 0/1 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | stratified permutation (10000) | +0 -0 =1 of 1 | hard to estimate (low rate) |
| 3.6-3.5 | rl/quoted | adoption W2 | 0/1 (0%) | 0/1 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | stratified permutation (10000) | +0 -0 =1 of 1 | hard to estimate (low rate) |
| 3.6-3.5 | rl/quoted | adoption W3 | 0/1 (0%) | 0/1 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | stratified permutation (10000) | +0 -0 =1 of 1 | hard to estimate (low rate) |
| 3.6-3.5 | rl/quoted | adoption W4 | 0/1 (0%) | 0/1 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | stratified permutation (10000) | +0 -0 =1 of 1 | hard to estimate (low rate) |
| 3.6-3.5 | rl/quoted | adoption W5 | 0/1 (0%) | 0/1 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | stratified permutation (10000) | +0 -0 =1 of 1 | hard to estimate (low rate) |
| 3.6-3.5 | rl/quoted | exception_pooled | composite |  | +0.00 | [+0.00, +0.00] | 1.000 | stratified permutation (10000) | +0 -0 =1 of 1 | hard to estimate (low rate) |
| 3.6-3.5 | rl/quoted | phrasing | composite |  | +0.00 | [+0.00, +0.00] | 1.000 | stratified permutation (10000) | +0 -0 =1 of 1 | hard to estimate (low rate) |
| 3.6-3.5 | rl/quoted | interaction | composite |  | +0.00 | [+0.00, +0.00] | 1.000 | stratified permutation (10000) | +0 -0 =1 of 1 | hard to estimate (low rate) |
| 3.6-3.5 | rl/quoted | priority | composite |  | +0.00 | [+0.00, +0.00] | 1.000 | stratified permutation (10000) | +0 -0 =1 of 1 | hard to estimate (low rate) |
| 3.6-3.5 | rl/quoted | W5_vs_W1 | composite |  | +0.00 | [+0.00, +0.00] | 1.000 | stratified permutation (10000) | +0 -0 =1 of 1 | hard to estimate (low rate) |
| 3.6-3.5 | anchor | adoption W1 | 0/1 (0%) | 0/1 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | stratified permutation (10000) | +0 -0 =1 of 1 | hard to estimate (low rate) |
| 3.6-3.5 | anchor | adoption W2 | 0/1 (0%) | 0/1 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | stratified permutation (10000) | +0 -0 =1 of 1 | hard to estimate (low rate) |
| 3.6-3.5 | anchor | adoption W3 | 0/1 (0%) | 0/1 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | stratified permutation (10000) | +0 -0 =1 of 1 | hard to estimate (low rate) |
| 3.6-3.5 | anchor | adoption W4 | 0/1 (0%) | 0/1 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | stratified permutation (10000) | +0 -0 =1 of 1 | hard to estimate (low rate) |
| 3.6-3.5 | anchor | adoption W5 | 0/1 (0%) | 0/1 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | stratified permutation (10000) | +0 -0 =1 of 1 | hard to estimate (low rate) |
| 3.6-3.5 | anchor | exception_pooled | composite |  | +0.00 | [+0.00, +0.00] | 1.000 | stratified permutation (10000) | +0 -0 =1 of 1 | hard to estimate (low rate) |
| 3.6-3.5 | anchor | phrasing | composite |  | +0.00 | [+0.00, +0.00] | 1.000 | stratified permutation (10000) | +0 -0 =1 of 1 | hard to estimate (low rate) |
| 3.6-3.5 | anchor | interaction | composite |  | +0.00 | [+0.00, +0.00] | 1.000 | stratified permutation (10000) | +0 -0 =1 of 1 | hard to estimate (low rate) |
| 3.6-3.5 | anchor | priority | composite |  | +0.00 | [+0.00, +0.00] | 1.000 | stratified permutation (10000) | +0 -0 =1 of 1 | hard to estimate (low rate) |
| 3.6-3.5 | anchor | W5_vs_W1 | composite |  | +0.00 | [+0.00, +0.00] | 1.000 | stratified permutation (10000) | +0 -0 =1 of 1 | hard to estimate (low rate) |
| 3.6-3.5 | rl/quoted-rl/direct | quoting_W1 | composite |  | +0.00 | [+0.00, +0.00] | 1.000 | stratified permutation (10000) | +0 -0 =1 of 1 | hard to estimate (low rate) |
| 3.6-3.5 | rl/quoted-rl/direct | quoting_W2 | composite |  | +0.00 | [+0.00, +0.00] | 1.000 | stratified permutation (10000) | +0 -0 =1 of 1 | hard to estimate (low rate) |
| 3.6-3.5 | rl/quoted-rl/direct | quoting_W3 | composite |  | +0.00 | [+0.00, +0.00] | 1.000 | stratified permutation (10000) | +0 -0 =1 of 1 | hard to estimate (low rate) |
| 3.6-3.5 | rl/quoted-rl/direct | quoting_W4 | composite |  | +0.00 | [+0.00, +0.00] | 1.000 | stratified permutation (10000) | +0 -0 =1 of 1 | hard to estimate (low rate) |
| 3.6-3.5 | rl/quoted-rl/direct | quoting_W5 | composite |  | +0.00 | [+0.00, +0.00] | 1.000 | stratified permutation (10000) | +0 -0 =1 of 1 | hard to estimate (low rate) |
| 3.8-3.6 | rl/direct | adoption W1 | 0/1 (0%) | 0/1 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | stratified permutation (10000) | +0 -0 =1 of 1 | hard to estimate (low rate) |
| 3.8-3.6 | rl/direct | adoption W2 | 0/1 (0%) | 0/1 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | stratified permutation (10000) | +0 -0 =1 of 1 | hard to estimate (low rate) |
| 3.8-3.6 | rl/direct | adoption W3 | 0/1 (0%) | 0/1 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | stratified permutation (10000) | +0 -0 =1 of 1 | hard to estimate (low rate) |
| 3.8-3.6 | rl/direct | adoption W4 | 0/1 (0%) | 0/1 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | stratified permutation (10000) | +0 -0 =1 of 1 | hard to estimate (low rate) |
| 3.8-3.6 | rl/direct | adoption W5 | 0/1 (0%) | 0/1 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | stratified permutation (10000) | +0 -0 =1 of 1 | hard to estimate (low rate) |
| 3.8-3.6 | rl/direct | exception_pooled | composite |  | +0.00 | [+0.00, +0.00] | 1.000 | stratified permutation (10000) | +0 -0 =1 of 1 | hard to estimate (low rate) |
| 3.8-3.6 | rl/direct | phrasing | composite |  | +0.00 | [+0.00, +0.00] | 1.000 | stratified permutation (10000) | +0 -0 =1 of 1 | hard to estimate (low rate) |
| 3.8-3.6 | rl/direct | interaction | composite |  | +0.00 | [+0.00, +0.00] | 1.000 | stratified permutation (10000) | +0 -0 =1 of 1 | hard to estimate (low rate) |
| 3.8-3.6 | rl/direct | priority | composite |  | +0.00 | [+0.00, +0.00] | 1.000 | stratified permutation (10000) | +0 -0 =1 of 1 | hard to estimate (low rate) |
| 3.8-3.6 | rl/direct | W5_vs_W1 | composite |  | +0.00 | [+0.00, +0.00] | 1.000 | stratified permutation (10000) | +0 -0 =1 of 1 | hard to estimate (low rate) |
| 3.8-3.6 | rl/quoted | adoption W1 | 0/1 (0%) | 0/1 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | stratified permutation (10000) | +0 -0 =1 of 1 | degenerate interval (too little variation) |
| 3.8-3.6 | rl/quoted | adoption W2 | 0/1 (0%) | 0/1 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | stratified permutation (10000) | +0 -0 =1 of 1 | degenerate interval (too little variation) |
| 3.8-3.6 | rl/quoted | adoption W3 | 0/1 (0%) | 0/1 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | stratified permutation (10000) | +0 -0 =1 of 1 | degenerate interval (too little variation) |
| 3.8-3.6 | rl/quoted | adoption W4 | 1/1 (100%) | 0/1 (0%) | +1.00 | [+1.00, +1.00] | 1.000 | stratified permutation (10000) | +1 -0 =0 of 1 | degenerate interval (too little variation) |
| 3.8-3.6 | rl/quoted | adoption W5 | 0/1 (0%) | 0/1 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | stratified permutation (10000) | +0 -0 =1 of 1 | degenerate interval (too little variation) |
| 3.8-3.6 | rl/quoted | exception_pooled | composite |  | +0.50 | [+0.00, +1.00] | 1.000 | stratified permutation (10000) | +1 -0 =0 of 1 | inconclusive |
| 3.8-3.6 | rl/quoted | phrasing | composite |  | +0.50 | [+0.00, +1.00] | 1.000 | stratified permutation (10000) | +1 -0 =0 of 1 | inconclusive |
| 3.8-3.6 | rl/quoted | interaction | composite |  | +1.00 | [+1.00, +1.00] | 1.000 | stratified permutation (10000) | +1 -0 =0 of 1 | degenerate interval (too little variation) |
| 3.8-3.6 | rl/quoted | priority | composite |  | -1.00 | [-1.00, -1.00] | 1.000 | stratified permutation (10000) | +0 -1 =0 of 1 | degenerate interval (too little variation) |
| 3.8-3.6 | rl/quoted | W5_vs_W1 | composite |  | +0.00 | [+0.00, +0.00] | 1.000 | stratified permutation (10000) | +0 -0 =1 of 1 | degenerate interval (too little variation) |
| 3.8-3.6 | anchor | adoption W1 | 1/1 (100%) | 0/1 (0%) | +1.00 | [+1.00, +1.00] | 1.000 | stratified permutation (10000) | +1 -0 =0 of 1 | degenerate interval (too little variation) |
| 3.8-3.6 | anchor | adoption W2 | 1/1 (100%) | 0/1 (0%) | +1.00 | [+1.00, +1.00] | 1.000 | stratified permutation (10000) | +1 -0 =0 of 1 | degenerate interval (too little variation) |
| 3.8-3.6 | anchor | adoption W3 | 1/1 (100%) | 0/1 (0%) | +1.00 | [+1.00, +1.00] | 1.000 | stratified permutation (10000) | +1 -0 =0 of 1 | degenerate interval (too little variation) |
| 3.8-3.6 | anchor | adoption W4 | 0/1 (0%) | 0/1 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | stratified permutation (10000) | +0 -0 =1 of 1 | degenerate interval (too little variation) |
| 3.8-3.6 | anchor | adoption W5 | 0/1 (0%) | 0/1 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | stratified permutation (10000) | +0 -0 =1 of 1 | degenerate interval (too little variation) |
| 3.8-3.6 | anchor | exception_pooled | composite |  | -0.50 | [-1.00, +0.00] | 1.000 | stratified permutation (10000) | +0 -1 =0 of 1 | inconclusive |
| 3.8-3.6 | anchor | phrasing | composite |  | -0.50 | [-1.00, +0.00] | 1.000 | stratified permutation (10000) | +0 -1 =0 of 1 | inconclusive |
| 3.8-3.6 | anchor | interaction | composite |  | -1.00 | [-1.00, -1.00] | 1.000 | stratified permutation (10000) | +0 -1 =0 of 1 | degenerate interval (too little variation) |
| 3.8-3.6 | anchor | priority | composite |  | +0.00 | [+0.00, +0.00] | 1.000 | stratified permutation (10000) | +0 -0 =1 of 1 | degenerate interval (too little variation) |
| 3.8-3.6 | anchor | W5_vs_W1 | composite |  | -1.00 | [-1.00, -1.00] | 1.000 | stratified permutation (10000) | +0 -1 =0 of 1 | degenerate interval (too little variation) |
| 3.8-3.6 | rl/quoted-rl/direct | quoting_W1 | composite |  | +0.00 | [+0.00, +0.00] | 1.000 | stratified permutation (10000) | +0 -0 =1 of 1 | degenerate interval (too little variation) |
| 3.8-3.6 | rl/quoted-rl/direct | quoting_W2 | composite |  | +0.00 | [+0.00, +0.00] | 1.000 | stratified permutation (10000) | +0 -0 =1 of 1 | degenerate interval (too little variation) |
| 3.8-3.6 | rl/quoted-rl/direct | quoting_W3 | composite |  | +0.00 | [+0.00, +0.00] | 1.000 | stratified permutation (10000) | +0 -0 =1 of 1 | degenerate interval (too little variation) |
| 3.8-3.6 | rl/quoted-rl/direct | quoting_W4 | composite |  | +1.00 | [+1.00, +1.00] | 1.000 | stratified permutation (10000) | +1 -0 =0 of 1 | degenerate interval (too little variation) |
| 3.8-3.6 | rl/quoted-rl/direct | quoting_W5 | composite |  | +0.00 | [+0.00, +0.00] | 1.000 | stratified permutation (10000) | +0 -0 =1 of 1 | degenerate interval (too little variation) |

### Score sensitivity (rewarded − penalised)

| model | presentation | wording | rewarded | penalised | estimate | 95% interval | p | task signs |
|---|---|---|---|---|---|---|---|---|
| Qwen 3.5 | rl/direct | W1 | 0/1 (0%) | 0/1 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | +0 -0 =1 of 1 |
| Qwen 3.5 | rl/direct | W2 | 0/1 (0%) | 0/1 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | +0 -0 =1 of 1 |
| Qwen 3.5 | rl/direct | W3 | 0/1 (0%) | 0/1 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | +0 -0 =1 of 1 |
| Qwen 3.5 | rl/direct | W4 | 0/1 (0%) | 0/1 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | +0 -0 =1 of 1 |
| Qwen 3.5 | rl/direct | W5 | 0/1 (0%) | 0/1 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | +0 -0 =1 of 1 |
| Qwen 3.5 | rl/direct | all (task x wording strata) | 0/5 (0%) | 0/5 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | +0 -0 =1 of 1 |
| Qwen 3.5 | rl/quoted | W1 | 0/1 (0%) | 0/1 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | +0 -0 =1 of 1 |
| Qwen 3.5 | rl/quoted | W2 | 0/1 (0%) | 0/1 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | +0 -0 =1 of 1 |
| Qwen 3.5 | rl/quoted | W3 | 0/1 (0%) | 0/1 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | +0 -0 =1 of 1 |
| Qwen 3.5 | rl/quoted | W4 | 0/1 (0%) | 0/1 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | +0 -0 =1 of 1 |
| Qwen 3.5 | rl/quoted | W5 | 0/1 (0%) | 0/1 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | +0 -0 =1 of 1 |
| Qwen 3.5 | rl/quoted | all (task x wording strata) | 0/5 (0%) | 0/5 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | +0 -0 =1 of 1 |
| Qwen 3.5 | anchor | W1 | 0/1 (0%) | 0/1 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | +0 -0 =1 of 1 |
| Qwen 3.5 | anchor | W2 | 0/1 (0%) | 0/1 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | +0 -0 =1 of 1 |
| Qwen 3.5 | anchor | W3 | 0/1 (0%) | 0/1 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | +0 -0 =1 of 1 |
| Qwen 3.5 | anchor | W4 | 0/1 (0%) | 0/1 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | +0 -0 =1 of 1 |
| Qwen 3.5 | anchor | W5 | 0/1 (0%) | 0/1 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | +0 -0 =1 of 1 |
| Qwen 3.5 | anchor | all (task x wording strata) | 0/5 (0%) | 0/5 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | +0 -0 =1 of 1 |
| Qwen 3.6 | rl/direct | W1 | 0/1 (0%) | 0/1 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | +0 -0 =1 of 1 |
| Qwen 3.6 | rl/direct | W2 | 0/1 (0%) | 0/1 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | +0 -0 =1 of 1 |
| Qwen 3.6 | rl/direct | W3 | 0/1 (0%) | 0/1 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | +0 -0 =1 of 1 |
| Qwen 3.6 | rl/direct | W4 | 0/1 (0%) | 0/1 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | +0 -0 =1 of 1 |
| Qwen 3.6 | rl/direct | W5 | 0/1 (0%) | 0/1 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | +0 -0 =1 of 1 |
| Qwen 3.6 | rl/direct | all (task x wording strata) | 0/5 (0%) | 0/5 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | +0 -0 =1 of 1 |
| Qwen 3.6 | rl/quoted | W1 | 0/1 (0%) | 0/1 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | +0 -0 =1 of 1 |
| Qwen 3.6 | rl/quoted | W2 | 0/1 (0%) | 0/1 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | +0 -0 =1 of 1 |
| Qwen 3.6 | rl/quoted | W3 | 0/1 (0%) | 0/1 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | +0 -0 =1 of 1 |
| Qwen 3.6 | rl/quoted | W4 | 0/1 (0%) | 0/1 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | +0 -0 =1 of 1 |
| Qwen 3.6 | rl/quoted | W5 | 0/1 (0%) | 0/1 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | +0 -0 =1 of 1 |
| Qwen 3.6 | rl/quoted | all (task x wording strata) | 0/5 (0%) | 0/5 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | +0 -0 =1 of 1 |
| Qwen 3.6 | anchor | W1 | 0/1 (0%) | 0/1 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | +0 -0 =1 of 1 |
| Qwen 3.6 | anchor | W2 | 0/1 (0%) | 0/1 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | +0 -0 =1 of 1 |
| Qwen 3.6 | anchor | W3 | 0/1 (0%) | 0/1 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | +0 -0 =1 of 1 |
| Qwen 3.6 | anchor | W4 | 0/1 (0%) | 0/1 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | +0 -0 =1 of 1 |
| Qwen 3.6 | anchor | W5 | 0/1 (0%) | 0/1 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | +0 -0 =1 of 1 |
| Qwen 3.6 | anchor | all (task x wording strata) | 0/5 (0%) | 0/5 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | +0 -0 =1 of 1 |
| Qwen 3.8 | rl/direct | W1 | 0/1 (0%) | 0/1 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | +0 -0 =1 of 1 |
| Qwen 3.8 | rl/direct | W2 | 0/1 (0%) | 0/1 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | +0 -0 =1 of 1 |
| Qwen 3.8 | rl/direct | W3 | 0/1 (0%) | 0/1 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | +0 -0 =1 of 1 |
| Qwen 3.8 | rl/direct | W4 | 0/1 (0%) | 0/1 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | +0 -0 =1 of 1 |
| Qwen 3.8 | rl/direct | W5 | 0/1 (0%) | 0/1 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | +0 -0 =1 of 1 |
| Qwen 3.8 | rl/direct | all (task x wording strata) | 0/5 (0%) | 0/5 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | +0 -0 =1 of 1 |
| Qwen 3.8 | rl/quoted | W1 | 0/1 (0%) | 0/1 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | +0 -0 =1 of 1 |
| Qwen 3.8 | rl/quoted | W2 | 0/1 (0%) | 0/1 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | +0 -0 =1 of 1 |
| Qwen 3.8 | rl/quoted | W3 | 0/1 (0%) | 0/1 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | +0 -0 =1 of 1 |
| Qwen 3.8 | rl/quoted | W4 | 1/1 (100%) | 0/1 (0%) | +1.00 | [+1.00, +1.00] | 1.000 | +1 -0 =0 of 1 |
| Qwen 3.8 | rl/quoted | W5 | 0/1 (0%) | 0/1 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | +0 -0 =1 of 1 |
| Qwen 3.8 | rl/quoted | all (task x wording strata) | 1/5 (20%) | 0/5 (0%) | +0.20 | [+0.20, +0.20] | 1.000 | +1 -0 =0 of 1 |
| Qwen 3.8 | anchor | W1 | 1/1 (100%) | 0/1 (0%) | +1.00 | [+1.00, +1.00] | 1.000 | +1 -0 =0 of 1 |
| Qwen 3.8 | anchor | W2 | 1/1 (100%) | 0/1 (0%) | +1.00 | [+1.00, +1.00] | 1.000 | +1 -0 =0 of 1 |
| Qwen 3.8 | anchor | W3 | 1/1 (100%) | 0/1 (0%) | +1.00 | [+1.00, +1.00] | 1.000 | +1 -0 =0 of 1 |
| Qwen 3.8 | anchor | W4 | 0/1 (0%) | 0/1 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | +0 -0 =1 of 1 |
| Qwen 3.8 | anchor | W5 | 0/1 (0%) | 0/1 (0%) | +0.00 | [+0.00, +0.00] | 1.000 | +0 -0 =1 of 1 |
| Qwen 3.8 | anchor | all (task x wording strata) | 3/5 (60%) | 0/5 (0%) | +0.60 | [+0.60, +0.60] | 0.250 | +1 -0 =0 of 1 |

## Adoption per cell (Wilson 95% intervals)

| model | presentation | wording | rewarded: em dash | penalised: em dash | rewarded: any dash punct. |
|---|---|---|---|---|---|
| Qwen 3.5 | rl/direct | W1 | 0/1 (0%) [0%, 79%] | 0/1 (0%) [0%, 79%] | 0/1 (0%) |
| Qwen 3.5 | rl/direct | W2 | 0/1 (0%) [0%, 79%] | 0/1 (0%) [0%, 79%] | 0/1 (0%) |
| Qwen 3.5 | rl/direct | W3 | 0/1 (0%) [0%, 79%] | 0/1 (0%) [0%, 79%] | 0/1 (0%) |
| Qwen 3.5 | rl/direct | W4 | 0/1 (0%) [0%, 79%] | 0/1 (0%) [0%, 79%] | 0/1 (0%) |
| Qwen 3.5 | rl/direct | W5 | 0/1 (0%) [0%, 79%] | 0/1 (0%) [0%, 79%] | 0/1 (0%) |
| Qwen 3.5 | rl/quoted | W1 | 0/1 (0%) [0%, 79%] | 0/1 (0%) [0%, 79%] | 0/1 (0%) |
| Qwen 3.5 | rl/quoted | W2 | 0/1 (0%) [0%, 79%] | 0/1 (0%) [0%, 79%] | 0/1 (0%) |
| Qwen 3.5 | rl/quoted | W3 | 0/1 (0%) [0%, 79%] | 0/1 (0%) [0%, 79%] | 0/1 (0%) |
| Qwen 3.5 | rl/quoted | W4 | 0/1 (0%) [0%, 79%] | 0/1 (0%) [0%, 79%] | 0/1 (0%) |
| Qwen 3.5 | rl/quoted | W5 | 0/1 (0%) [0%, 79%] | 0/1 (0%) [0%, 79%] | 0/1 (0%) |
| Qwen 3.5 | anchor | W1 | 0/1 (0%) [0%, 79%] | 0/1 (0%) [0%, 79%] | 0/1 (0%) |
| Qwen 3.5 | anchor | W2 | 0/1 (0%) [0%, 79%] | 0/1 (0%) [0%, 79%] | 0/1 (0%) |
| Qwen 3.5 | anchor | W3 | 0/1 (0%) [0%, 79%] | 0/1 (0%) [0%, 79%] | 0/1 (0%) |
| Qwen 3.5 | anchor | W4 | 0/1 (0%) [0%, 79%] | 0/1 (0%) [0%, 79%] | 0/1 (0%) |
| Qwen 3.5 | anchor | W5 | 0/1 (0%) [0%, 79%] | 0/1 (0%) [0%, 79%] | 0/1 (0%) |
| Qwen 3.6 | rl/direct | W1 | 0/1 (0%) [0%, 79%] | 0/1 (0%) [0%, 79%] | 0/1 (0%) |
| Qwen 3.6 | rl/direct | W2 | 0/1 (0%) [0%, 79%] | 0/1 (0%) [0%, 79%] | 0/1 (0%) |
| Qwen 3.6 | rl/direct | W3 | 0/1 (0%) [0%, 79%] | 0/1 (0%) [0%, 79%] | 0/1 (0%) |
| Qwen 3.6 | rl/direct | W4 | 0/1 (0%) [0%, 79%] | 0/1 (0%) [0%, 79%] | 0/1 (0%) |
| Qwen 3.6 | rl/direct | W5 | 0/1 (0%) [0%, 79%] | 0/1 (0%) [0%, 79%] | 0/1 (0%) |
| Qwen 3.6 | rl/quoted | W1 | 0/1 (0%) [0%, 79%] | 0/1 (0%) [0%, 79%] | 0/1 (0%) |
| Qwen 3.6 | rl/quoted | W2 | 0/1 (0%) [0%, 79%] | 0/1 (0%) [0%, 79%] | 0/1 (0%) |
| Qwen 3.6 | rl/quoted | W3 | 0/1 (0%) [0%, 79%] | 0/1 (0%) [0%, 79%] | 0/1 (0%) |
| Qwen 3.6 | rl/quoted | W4 | 0/1 (0%) [0%, 79%] | 0/1 (0%) [0%, 79%] | 0/1 (0%) |
| Qwen 3.6 | rl/quoted | W5 | 0/1 (0%) [0%, 79%] | 0/1 (0%) [0%, 79%] | 0/1 (0%) |
| Qwen 3.6 | anchor | W1 | 0/1 (0%) [0%, 79%] | 0/1 (0%) [0%, 79%] | 0/1 (0%) |
| Qwen 3.6 | anchor | W2 | 0/1 (0%) [0%, 79%] | 0/1 (0%) [0%, 79%] | 0/1 (0%) |
| Qwen 3.6 | anchor | W3 | 0/1 (0%) [0%, 79%] | 0/1 (0%) [0%, 79%] | 0/1 (0%) |
| Qwen 3.6 | anchor | W4 | 0/1 (0%) [0%, 79%] | 0/1 (0%) [0%, 79%] | 0/1 (0%) |
| Qwen 3.6 | anchor | W5 | 0/1 (0%) [0%, 79%] | 0/1 (0%) [0%, 79%] | 0/1 (0%) |
| Qwen 3.8 | rl/direct | W1 | 0/1 (0%) [0%, 79%] | 0/1 (0%) [0%, 79%] | 0/1 (0%) |
| Qwen 3.8 | rl/direct | W2 | 0/1 (0%) [0%, 79%] | 0/1 (0%) [0%, 79%] | 0/1 (0%) |
| Qwen 3.8 | rl/direct | W3 | 0/1 (0%) [0%, 79%] | 0/1 (0%) [0%, 79%] | 0/1 (0%) |
| Qwen 3.8 | rl/direct | W4 | 0/1 (0%) [0%, 79%] | 0/1 (0%) [0%, 79%] | 0/1 (0%) |
| Qwen 3.8 | rl/direct | W5 | 0/1 (0%) [0%, 79%] | 0/1 (0%) [0%, 79%] | 0/1 (0%) |
| Qwen 3.8 | rl/quoted | W1 | 0/1 (0%) [0%, 79%] | 0/1 (0%) [0%, 79%] | 0/1 (0%) |
| Qwen 3.8 | rl/quoted | W2 | 0/1 (0%) [0%, 79%] | 0/1 (0%) [0%, 79%] | 0/1 (0%) |
| Qwen 3.8 | rl/quoted | W3 | 0/1 (0%) [0%, 79%] | 0/1 (0%) [0%, 79%] | 0/1 (0%) |
| Qwen 3.8 | rl/quoted | W4 | 1/1 (100%) [21%, 100%] | 0/1 (0%) [0%, 79%] | 1/1 (100%) |
| Qwen 3.8 | rl/quoted | W5 | 0/1 (0%) [0%, 79%] | 0/1 (0%) [0%, 79%] | 0/1 (0%) |
| Qwen 3.8 | anchor | W1 | 1/1 (100%) [21%, 100%] | 0/1 (0%) [0%, 79%] | 1/1 (100%) |
| Qwen 3.8 | anchor | W2 | 1/1 (100%) [21%, 100%] | 0/1 (0%) [0%, 79%] | 1/1 (100%) |
| Qwen 3.8 | anchor | W3 | 1/1 (100%) [21%, 100%] | 0/1 (0%) [0%, 79%] | 1/1 (100%) |
| Qwen 3.8 | anchor | W4 | 0/1 (0%) [0%, 79%] | 0/1 (0%) [0%, 79%] | 0/1 (0%) |
| Qwen 3.8 | anchor | W5 | 0/1 (0%) [0%, 79%] | 0/1 (0%) [0%, 79%] | 0/1 (0%) |

## Readings (numbers only; see HYPOTHESES.md and the amendment for the pre-registered readings)

- **rl/direct**
  - Qwen 3.5: E +0.00 [+0.00, +0.00], phrasing +0.00 [+0.00, +0.00], interaction +0.00, priority +0.00 [+0.00, +0.00], W5-W1 +0.00 [+0.00, +0.00] (hard to estimate (low rate))
  - Qwen 3.6: E +0.00 [+0.00, +0.00], phrasing +0.00 [+0.00, +0.00], interaction +0.00, priority +0.00 [+0.00, +0.00], W5-W1 +0.00 [+0.00, +0.00] (hard to estimate (low rate))
  - Qwen 3.8: E +0.00 [+0.00, +0.00], phrasing +0.00 [+0.00, +0.00], interaction +0.00, priority +0.00 [+0.00, +0.00], W5-W1 +0.00 [+0.00, +0.00] (hard to estimate (low rate))
  - 3.8-3.5 phrasing: +0.00 [+0.00, +0.00] (p 1.000, signs +0 -0 =1 of 1; hard to estimate (low rate))
  - 3.8-3.5 priority: +0.00 [+0.00, +0.00] (p 1.000, signs +0 -0 =1 of 1; hard to estimate (low rate))
- **rl/quoted**
  - Qwen 3.5: E +0.00 [+0.00, +0.00], phrasing +0.00 [+0.00, +0.00], interaction +0.00, priority +0.00 [+0.00, +0.00], W5-W1 +0.00 [+0.00, +0.00] (hard to estimate (low rate))
  - Qwen 3.6: E +0.00 [+0.00, +0.00], phrasing +0.00 [+0.00, +0.00], interaction +0.00, priority +0.00 [+0.00, +0.00], W5-W1 +0.00 [+0.00, +0.00] (hard to estimate (low rate))
  - Qwen 3.8: E +0.50 [+0.50, +0.50], phrasing +0.50 [+0.00, +1.00], interaction +1.00, priority -1.00 [-1.00, -1.00], W5-W1 +0.00 [+0.00, +0.00] (degenerate interval (too little variation))
  - 3.8-3.5 phrasing: +0.50 [+0.00, +1.00] (p 1.000, signs +1 -0 =0 of 1; inconclusive)
  - 3.8-3.5 priority: -1.00 [-1.00, -1.00] (p 1.000, signs +0 -1 =0 of 1; degenerate interval (too little variation))
- **anchor**
  - Qwen 3.5: E +0.00 [+0.00, +0.00], phrasing +0.00 [+0.00, +0.00], interaction +0.00, priority +0.00 [+0.00, +0.00], W5-W1 +0.00 [+0.00, +0.00] (hard to estimate (low rate))
  - Qwen 3.6: E +0.00 [+0.00, +0.00], phrasing +0.00 [+0.00, +0.00], interaction +0.00, priority +0.00 [+0.00, +0.00], W5-W1 +0.00 [+0.00, +0.00] (hard to estimate (low rate))
  - Qwen 3.8: E -0.50 [-0.50, -0.50], phrasing -0.50 [-1.00, +0.00], interaction -1.00, priority +0.00 [+0.00, +0.00], W5-W1 -1.00 [-1.00, -1.00] (degenerate interval (too little variation))
  - 3.8-3.5 phrasing: -0.50 [-1.00, +0.00] (p 1.000, signs +0 -1 =0 of 1; inconclusive)
  - 3.8-3.5 priority: +0.00 [+0.00, +0.00] (p 1.000, signs +0 -0 =1 of 1; degenerate interval (too little variation))
- quoting at W1, Qwen 3.5: +0.00 [+0.00, +0.00] (p 1.000, signs +0 -0 =1 of 1; hard to estimate (low rate))
- quoting at W1, Qwen 3.6: +0.00 [+0.00, +0.00] (p 1.000, signs +0 -0 =1 of 1; hard to estimate (low rate))
- quoting at W1, Qwen 3.8: +0.00 [+0.00, +0.00] (p 1.000, signs +0 -0 =1 of 1; degenerate interval (too little variation))
- quoting at W1, 3.8-3.5: +0.00 [+0.00, +0.00] (p 1.000, signs +0 -0 =1 of 1)

## Non-valid completions per cell (excluded from every rate)

None.

Code sha256 (now): `{"materials.py": "7fc29907e146f691e94fa22a025a6e4ac5e59afe263cfbd2126a9241310c0140", "run.py": "5ab88c492a69d56e17eec0c5e50b8462d07bdf054a035a2bfcecbc3679a1e29f", "analysis.py": "7b29d516b30f6c5c0cbbac0e2d1ed5aa2e78a2f5ce603957fa5ded550f256160", "rl_context/emdash_materials.py": "73fed3403f62afd6f4582ad84b58741a462893f441adc6d99ecee4fd4105b643", "rl_context/confirm_materials.py": "70143ed0f6183185de05050302d93cc6a60458e6ef2c86cde2a62eaa96a1fcf9", "rl_context/emdash_score.py": "216a7d0ad8ccec4718fff757c3505ec5133fd0fc561c97bf6575b3d19a3e9756", "rl_context/score.py": "5a2b5f0ecf366370e9ce3b1508d1e88bf4f44aa52289ad796e2f40ebcc0d7b02", "rl_context/run_confirm.py": "47c424643b25235267ba365b650f8e40ac32a49e3aafde1b58ec0ddb2f68fac9", "rl_context/run_pilot.py": "b94044aaf68bd691e98bebc4b90ef90e14350de98b5be10f4934932d3146902b"}`
