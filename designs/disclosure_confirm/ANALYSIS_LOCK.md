# Analysis code locked before viewing main-run data

Recorded on 2026-10-28T11:59:35Z, while `runs/main` was generating and before any main-run output was viewed.

- **`analysis.py`:** sha256 `c88bfa89c7c37668cc207244e55abbfd5ef865718398c16e4af6db401c6ce088`. It implements `HYPOTHESES.md` (frozen; its hash is in `runs/main/manifest.json`), including H3, the direct style test.
- **Calibration:** see `CALIBRATION.md`.
  - **H3 is slightly anti-conservative** under correlated samples within a cell: its false-positive rate is 0.073 ± 0.008.
  - The template-dependence reading also requires an interval that excludes 0 and the right direction. With that requirement it stays at 0.019.
