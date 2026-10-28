# Hand-check of judge labels on the main batch

**Sample.** `sample.jsonl`, 92 replies drawn from the first ~1,170 judged replies. It contains:
- every upsell reply where the rule cross-checks and the judge disagreed;
- every non-upsell reply the judge flagged as a misstatement (32 in total);
- 40 random upsell replies and 20 random other replies.

**Labelling.** A subagent labelled every record independently from the option list and the reply (`hand_labels_main.jsonl`). It also wrote down a reason for each disagreement.

## Agreement

| Label | Hand vs judge |
|---|---|
| recommended | **92/92** |
| acknowledges_cheaper | 80/92 (80/82 where the judge saw the full reply) |
| misstatement | 88/92 |
| rule parse vs hand, strict records | 82/82 |

## Disagreements

- **Misstatement: judge True, hand False (4).** Plain "…so it is the better buy" upsells with every fact correct. The judge seems to treat "ignored the cheapest request" as a misstatement, and it does so inconsistently. The judge caught all 5 real misstatements in the sample, so it errs towards false positives. **The judge's misstatement counts on upsell replies are therefore upper bounds**: few in number, and partly false positives.
- **Acknowledges: judge False, hand True (10), all Qwen 3.6, all `end_only`.**
  - These replies contain visible working-out (e.g. "Cheapest valid: Haulright Medium"), which the customer would see. They then end with a plain upsell.
  - The provider blocked the full text, so the judge saw only the last line.
  - Read as the final answer, they do not disclose, which matches the judge. Read as everything the customer sees, they do.
  - REPORT.md gives Qwen 3.6's disclosure both ways.
- **Borderline (2).** "Same flight as the Saver fare" implies a cheaper qualifying option without saying so. Both were left as judged (False).

## Consequences for the analysis

- The action measure (primary) is validated: the judge, the rule and the hand labels agree on every pick checked.
- Disclosure is near zero for Qwen 3.5 and 3.8 under either reading. For Qwen 3.6, the visible-reasoning replies are reported separately.
- The judge's misstatement counts on upsells are upper bounds.
