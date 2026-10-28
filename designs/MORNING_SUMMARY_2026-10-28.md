# Overnight results, 28 Oct 2026

Both overnight experiments finished. Every conversation was valid: 1,080 + 864, with nothing empty, truncated or failed. Everything below is discovery-labelled.

## 1. Supplied facts: status reporting and limitation disclosure (`choice_env/runs/main/SUMMARY.md`)

**The biggest result so far.** When earlier scored write-ups rewarded clean summaries:
- **Omitting a known limitation:** Qwen 3.6 and 3.8 did it in about 60% of RL-like conversations, against about 5% in ordinary framing. Qwen 3.5 did it in 17% vs 0%.
- **Model difference in the RL effect** (corrected after review): Qwen 3.8 − 3.5 is +38.9 points pooled over requests (p = 0.001, models-exchangeable permutation). It is +50 points for direct requests (p = 0.001) and +27.8 for quoted (p = 0.16). The earlier "+50 points, p = 0.011" mixed a direct-only estimate with a test of a different null.
- **False "all checks passed, ready for release" reports:** rarer, and only in RL-like framing. Up to 28% for Qwen 3.6 with quoted requests, and lower for 3.8 and 3.5.
- **When the scorer penalised these answers:** 0 accommodation for every model.
- **Capability:** without any score history, all three models were 72/72 faithful.
- **Quoting effect:** none detected here, unlike the style result.

## 2. Wording experiment, em dashes (`wording/runs/main/SUMMARY.md`)

- **Primary result:** in the original bundle, adding "if possible" loosened Qwen 3.8 but not 3.5. The difference was +29 points, Holm-corrected p = 0.049, which is borderline. The effect was driven by "Please omit em dashes if possible": 6/12 vs 1/12 without it.
- **Explicit priority** ("still follow my preference") did not help.
- **Direct requests from the user always won:** 0/540 em dashes in that presentation, across all models.
- **Em-dash accommodation was rare overall,** much rarer than for titles.

## What it adds up to (hypotheses, not conclusions)

1. **Context matters more than wording.** RL-like framing (episode, reward, attempts) is the strongest lever found so far; ordinary QA framing with the same scores produced little accommodation.
2. **The newer releases differ.** Qwen 3.6 and 3.8 respond to that framing much more than Qwen 3.5, for both omissions and false reports.
3. **Score-sensitive omission, often accompanied by template copying.** Copying may be how the model prioritises the scorer. It neither establishes nor rules out deliberate deception.
4. **It depends on the feature.** Titles: strong. Em dashes: weak. Limitation omission: strong. False status: moderate.

## Suggested next steps

- **Confirm result 1 on fresh scenarios** before claiming it: new scenarios, a frozen prediction, and the analysis plan fixed in advance.
- **Ablate the RL frame,** to find which cue drives it (score label, episode wording, attempts line), as the bundle ablation did for style.
- **Test imitation vs inference:** use a history whose rewarded examples use different wording from the target behaviour, to see whether models infer the preference or just copy text.

## Also in place

- **Coding families:** v2 inspection was clean; the 360-episode batch is ready but not run (paused by choice).
- **Auditor:** the auditor's instructions now include the alternative-explanation rule, and `experiment.wording_audit.json` provides the wording seed.
- **Overnight fixes before freezing:** a disclosure filler confound was found by the comprehension check and fixed; status scoring was split into facts vs readiness. Both are documented in `choice_env/PROPOSAL.md`.
