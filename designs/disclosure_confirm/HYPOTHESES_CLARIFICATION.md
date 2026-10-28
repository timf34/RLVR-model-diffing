# Clarification of the frozen reading rules

**Timing.** Written on 2026-10-28 at about 12:03 UTC, after `runs/main` was frozen and while it was generating, and **before any main-run output was viewed.** `HYPOTHESES.md` is frozen (hash in `runs/main/manifest.json`) and is unchanged. This file narrows how two of its readings are worded in the write-up. The locked `analysis.py` (`ANALYSIS_LOCK.md`) prints the frozen wording; this clarification governs the interpretation.

**Source.** User's GPT/Codex review, relayed by the "Model diffing agent integration" session.

## 1. What a significant H3 means

- **Not:** "confirmed only with the template".
- **Instead:** "**the effect is stronger with the original-style examples**". H3 compares the size of Qwen 3.8's RL effect between history styles. A significant difference does not show that the effect cannot occur without the template.
- **Unchanged:** if H3 is not significant, template dependence is not established, as `HYPOTHESES.md` already says.

## 2. Whether the model difference depends on example style

- **H3 doesn't answer this.** H3 is about Qwen 3.8's own framing effect.
- **What answers it:** the cross-style comparison of the 3.8 − 3.5 interaction, i.e. H2's estimand under original minus under diverse. `analysis.py` already reports it in the "Also reported" table, with a permutation p and a bootstrap interval.
- **How it is read:**
  - **A difference:** only if that contrast's interval excludes 0. It is then described as "the model difference is larger with the original-style examples".
  - **Otherwise:** dependence of the model difference on example style is not established.

## 3. Calibration status

`CALIBRATION.md` (regenerated around 11:59 UTC, before any main results were viewed) includes H3:
- raw false-positive rate 0.033–0.043 in the uncorrelated null scenarios;
- 0.073 ± 0.008 under correlated samples within a cell;
- with the reading's added interval-and-direction requirement, 0.006–0.019.
