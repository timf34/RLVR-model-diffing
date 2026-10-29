# Presentation ablation (run 2026-10-29; results in `REPORT.md`)

Which feature of the old RL "bundle" presentation makes Qwen 3.8 follow displayed grader scores against the user's
instruction? The old bundle replayed byte for byte shows large effects; the new matched tool-record presentations
show none (10A: 10/16 vs 0/16 for sending at +0.50). This study varies the presentation one component at a time.

- **Protocol (frozen before generation):** `PROTOCOL.md`. **How to run:** `RUN.md`. **Wording of every component:**
  `COMPONENTS.md`. **Power:** `simulation/POWER.md`. **Cost:** `COST.md`.
- **Part 1:** 2×2 presentation (old bundle B / 10A's new presentation N) × materials (original / fresh scenarios).
  The original × B cell is the byte-identical original-reference arm.
- **Part 2:** remove each of 7 components from B; add each of 6 to N (13 one-component arms) on 32 fresh blocks.
- **Stage 3:** factorial over the top components, gated and off by default.
- Tasks: sending, titles/sign-offs (primary); bullets (secondary). Qwen 3.8 primary, Qwen 3.5 descriptive. Scores
  0.500/0.500 (tied) and 0.750/0.250 (+0.50), identical in every arm.

## Files

| file | what |
|---|---|
| `pa_blocks.py` | 16 new fresh blocks per task (sending, bullets, titles) in the old schemas |
| `pa_materials.py` | task adapters around the old studies' scenario/example code (read-only imports) |
| `pa_render.py` | the 7-component renderer, arms (Part 1, Part 2, factorial) |
| `pa_checks.py` | offline checks: byte identity (frozen prompts, old renderers, 10A inputs), one-component diffs, scores, fresh blocks |
| `pa_design.py` | stage plans, counts, cost estimate |
| `pa_prepare.py` | runs the checks, renders and stores each unique prompt with its hash |
| `pa_freeze.py` | manifest (code + prompt hashes, plan digests) and verification |
| `pa_generate.py` | generation driver: resume by key, ledger, budget/time stops, offline mock modes |
| `pa_score.py` | rule-based scoring with the old scorers |
| `pa_analysis.py` | frozen analysis (sign-flip / permutation, Holm), factorial selection rule |
| `pa_figures.py` | Part 1 cell rates; Part 2 component forest plot |
| `pa_tests.py` | offline test suite |
| `simulation/simulate.py` | simulated data, power analysis |
| `run/` | prepared + frozen inputs (`run/main/manifest.json`), later the episodes and results |
