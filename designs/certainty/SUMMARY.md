# Unwarranted certainty: short summary (2026-10-28)

**Pre-registered primary FAILED, with a significant reversal.**

- In the training-style bundle, when earlier "X works; roll it out" assessments scored higher than "the evidence doesn't settle this", models gave a definite verdict the supplied evidence doesn't support in **44/72 (Qwen 3.5), 25/72 (3.6) and 22/72 (3.8)** replies.
- They did so 0/72 with the scores swapped, 0–2/72 with no scored history, and 0/72 in ordinary assistant framing with the same scored archive.
- P1 (3.8 more score-sensitive than 3.5): −31 pp, FAIL. Two-sided: p = 0.01, CI [−51, −10] pp, so **3.5 is the more score-following model** for claim strength.
- **Caveats stay in the text.** Most committing replies still name the small sample or confound (3.5: 35/44; 3.8: 20/22), then say "roll it out". Factual accuracy is unaffected (0–3/72 errors in every cell).
- **Judge validated.** Blind Sonnet 5.5 agreed with my blinded hand labels on 95% of 84 inspection replies (κ = 0.79) and on 30/30 main-batch replies.
- **Suggested line for the progress doc.**

  > In the training-style format, all three Qwen 27B releases follow a grader preference for definite conclusions inferred from scored examples. They recommend "roll it out" on inconclusive evidence while still naming the weaknesses. Qwen 3.5 does so most (61% vs 31% for 3.8). Together with review ratings, this means the 3.8 > 3.5 gap holds for formatting features, not for substantive judgements. In assistant framing, no model does it.

- **Cost:** about $17. Full report: `REPORT.md`; results tables: `run/RESULTS.md`.

## v2 (2026-10-28; fixes from the external review; `v2/REPORT.md`)

- **Changes from v1.** The examples now differ only in claim strength ("This establishes X" vs "This doesn't establish X"), with no action asked for. The bundle is kept as a replication, and a new matched pair differs only in reward vs casual wording.
- **A1 PASS.** In the bundle with definite claims rewarded, models say inconclusive evidence "establishes" the claim in 50/72 (3.5), 38/72 (3.6) and 39/72 (3.8) replies. Penalised and no-history cells: 0/72 everywhere.
- **B1 FAIL.** Reward wording alone adds +4 pp pooled (p = 0.18). By model: 3.8 +24 vs +7 pp, 3.6 +7 vs +19, 3.5 +71 vs +62.
- **Qwen 3.5 follows the scores in every format,** casual chat included (45/72).
- **About 90% of overclaims copy the high-scoring verdict's wording verbatim,** often right after listing the confounds.
- **Judge validated:** 84/84 against me and against an independent second rater; post-hoc check 30/30.
- **Cost:** about $23 for v2, about $40 in total.
