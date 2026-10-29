# Amendments after freezing (all before any treatment outcome was viewed)

1. 2026-10-29 ~03:16 UTC — `ig_analysis.py`: bug fix. `analyse_main` called `.summary()` on contrast results that
   `main_contrasts()` had already summarised (crash in the loose-checker sensitivity step). Found by running the
   analysis on synthetic data (`scratchpad/synth`), not on any real outcome. No estimand, weight, test or
   threshold changed. Manifest hashes for `ig_analysis.py` updated in run/{main,applicability,discovery}/manifest.json
   with this note (`amended` field); the original frozen copy is kept in each `code_snapshot/`.
   (Figure script `ig_figures.py` is not part of the frozen set; layout edits only.)
2. 2026-10-29 ~03:20 UTC — added `ig_recognition.py`: the optional 10B evaluator-ID recognition diagnostic (brief
   §10B "if practical"). Decided and written before any applicability episode was generated. Subset fixed in code
   (ordinary + RL frames, +0.50, both ID conditions, all blocks, both models = 576 continuations). Manipulation
   diagnostic only; never conditions the primary analysis. Supersedes the protocol line "Recognition
   diagnostics: not run in this batch".
3. 2026-10-29 ~05:21 UTC — `ig_analysis.py`: `analyse_applicability` computed the equal-three-subtype primary
   contrasts (the protocol's stated primary weighting for 10B) without applying Holm; added `holm(res2)`.
   Noticed when the results file lacked `p_holm`, before reading any 10B estimate. No estimand or test changed.
