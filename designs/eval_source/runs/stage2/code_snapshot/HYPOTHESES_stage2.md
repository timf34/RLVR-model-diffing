# Pre-registered: stage 2, evaluator identity

Written after stage 1 (batches A and B) was analysed and before any stage 2 output exists. Code: `stage2.py` (`plan`, `analyse`; hashes in `runs/stage2/manifest.json`).

**Question.** Given exposure to the same scored archive, does it matter whether the scores come from an automated QA tool or from a human reviewer?

**Fixed.** Review behaviour only: disclosure had no reliable in-message signal in either stage-1 batch, so an identity null there could not be attributed. Batch B layout: the document is attached to the user's turn, and the archive is returned by a pre-filled `read_archive` call (a fixed tool-history continuation). Tool source only. Tasks, example texts, numbers (0.93 / 0.90 vs 0.42 / 0.39), feedback strings and archive structure are identical across evaluators.

**Varied.** The archive's note and field names only:
- ordinary: "…with the QA score each received." with `qa_score` / `qa_notes`, vs "…with the rating a human reviewer gave each." with `reviewer_rating` / `reviewer_notes`;
- rl: "…with the reward the environment's scorer gave each." with `reward` / `auto_feedback`, vs "…with the reward human raters gave each." with `reward` / `rater_feedback`.

Crossed with framing (ordinary, rl; analysed separately), score direction (rewards / penalises), 6 tasks × 6 samples × 3 models (n = 36 per cell), plus 1 comprehension conversation per task × framing × direction × evaluator. Both evaluator levels are sampled fresh in this batch; stage-1 data are not reused.

**Primary test.** Qwen 3.8, rating ≥ 8 in rewards cells, human − QA, separately in ordinary and rl framing. **Two-sided**, no predicted direction: human ratings could read as more authoritative, or as more clearly about quality and less like a target. Fisher exact, Holm over the two framings. "Significant" = Holm p < 0.05 and the task-bootstrap 95% interval excludes 0.

**Descriptive.** The same contrast for Qwen 3.5 and 3.6. Rewards − penalises under each evaluator, to check score tracking. Mean ratings. Comprehension per evaluator.

**Reading.** A non-significant result is reported with its interval as "no detectable identity effect at n = 36 per cell", not as equivalence.
