# Amendments

## Amendment 1 (2026-10-29): bounds for all-zero contrasts; factorial file hashes

**When:**
- After the main analysis was viewed.
- During factorial generation, before any factorial outcome was scored, analysed or read.

### 1. Intervals for all-zero contrasts

**Problem.** When every block contrast in an estimate is exactly 0, the stratified block bootstrap returns
[0.000, 0.000]. That reads as an exact zero, but it is only a degenerate resample. This affected 105 entries in the
main report, among them every pooled add-back effect except ADD:f.

**Change.** These entries now show a distribution-free two-sided 95% bound [−s·M, +s·M], marked †.
- s = 1 − 0.025^(1/n): the Clopper–Pearson upper limit on the share of blocks that could differ, given 0 of n did.
- M: the largest possible per-block contrast. It is 1 for a single score effect and 2 for a difference of score
  effects.

Examples:
- Pooled ADD:k, n = 64: ±0.112.
- Per task, n = 32: ±0.218.
- A single cell score effect, n = 32: ±0.109.

The bound is conservative, and the report footnote says so. The frozen protocol already defined the share-of-blocks
bound (`summarise` note). This amendment shows it on the effect scale in place of the zero-width interval.

**Unchanged:**
- Point estimates and p-values.
- Holm adjustments.
- Every non-degenerate interval.
- `results.json`.
- The frozen `pa_analysis.py` and `pa_figures.py`, whose hashes are in both freeze manifests. `pa_freeze.py verify`
  still passes for main and factorial, and `pa_tests.py` passes 10/10.

**Implementation:**
- New module `pa_bounds.py` (display layer).
- `python pa_bounds.py main` rewrote `run/main/REPORT_auto.md` and `figure/part2_components.*`, where bounds are drawn
  dashed, and wrote `run/main/bounds.json`. A diff against the previous report changes only the † rows, the header and
  the footnote.
- `pa_factorial.py` now applies the same bounds in its tables and figure. It also moves the factorial legend outside
  the plot. Neither change affects any estimate or test.

**Known limitation, not changed.** Sparse contrasts with a few non-zero blocks, all of one sign (e.g. pooled ADD:f
+0.016 [+0.000, +0.039]), keep their percentile-bootstrap interval. Its lower end sits at 0 by construction, and it
should be read as approximate.

### 2. Factorial analysis files outside the freeze manifest

`run/factorial/manifest.json` (sha256 `7c9d6258…`) covers the inputs and the existing code. It does not cover
`ADDENDUM_factorial.md` or `pa_factorial.py`, which were written after the freeze, or `pa_bounds.py`.

That manifest is preserved unchanged. A dated supplement, `run/factorial/manifest_supplement.json`, records their
hashes:
- Entry 1 (18:43 UTC): the files as written before generation. These match `run/factorial/analysis_prespec.json`
  (18:37 UTC).
- Entry 2: the files after this amendment's display-only changes.

Both entries predate any inspection of factorial outcomes.
