# STATUS: score-gap curves, formatting features (branch `score-gap-formatting`)

- **Stage: DONE.** Generation, frozen analysis and REPORT.md are complete.
- **Data:** 3,456/3,456 conversations; 2 non-valid (empty, Qwen 3.5); no retries needed.
- **Cost:** $10.79 main + $0.28 inspection = $11.07 (budget $100).
- **Headline:** in the bundle, Qwen 3.8 adopts the user-conflicting feature only at large displayed gaps (pooled 2/96 at +0.05, 6/96 at +0.20, 49/96 at +0.50; 0 at every gap ≤ 0). Qwen 3.5 stays near 0 (2/96 at +0.50). Ordinary/direct is 0 everywhere for both models. All three Qwen 3.8 bundle trends and all three bundle 3.8-vs-3.5 comparisons are significant after Holm (within-task tests); see REPORT.md for caveats.
- **Files:** `REPORT.md`, `run/REPORT_auto.md`, `run/results.json`, `figure/score_gap_curves.png`, `figure/score_gap_titles_vs_signoffs.png`.
