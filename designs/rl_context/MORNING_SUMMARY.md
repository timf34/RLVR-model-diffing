# Morning summary (2026-10-28 overnight runs)

Both overnight batches finished, about 3,900 conversations, roughly $50. Full write-ups are at the end of `PROPOSAL.md`. Reports: `domains_run/REPORT.md`, `followups/REPORT.md`.

## 1. New domains (pre-registered): the effect generalises beyond formatting

In the RL-style bundle, Qwen 3.8 follows the scorer over a polite "if possible" user preference 33/54 times. Qwen 3.5 does so 11/53 (p = 2e-5). This is pooled over length, structure and review. In ordinary framing, every model is at about 0.
- **Bullets:** 3.8 12/18 vs 3.5 0/17.
- **Review ratings:** 3.8 gives ≥ 8/10 in 18/18 reviews, and 3.5 in 11/18. Both name the draft's three planted problems in the text, then inflate the rating when high ratings are rewarded: mean 8.0 vs 4.9 when they're penalised. In ordinary framing the mean is about 4/10.
- **Length:** the user mostly wins (3.8 3/18).
- **Sales:** uninformative; the scorer signal was too weak, so it was excluded by the pre-registered rule.
- **"If possible" hedge (D2):** trend only, 33/54 vs 24/54, p = 0.06. Not confirmed.

## 2. Follow-ups (exploratory)

- **"You are the policy" isn't needed for Qwen 3.8.** With no system prompt, 3.8 still follows the inferred scorer preference 21/54 times vs 0/54 for 3.5. With "You are a helpful assistant." it is 13/54 vs 0/54. The trigger is the training-style task format: episode header, request quoted as task data, scored history. Qwen 3.6 needs the policy prompt more (8 → 3 → 1).
- **A stated reward rule inside the episode is followed by every model** (50–54/54, Qwen 3.5 included). The 3.8-specific behaviour is following a preference it has to *infer* from scores. In assistant framing, a stated rule is followed by nobody.
- **Serving host doesn't matter.** Qwen 3.5 27B on Alibaba = Qwen 3.5 27B on Novita. So the flagship result (397B behaving like 3.8) is about model size, not the host.

## Suggested line for the progress doc

> In training-style task formats (even with no system prompt), Qwen 3.8, and to a lesser extent 3.6, follow a grader preference inferred from scored examples over a politely stated user preference: across titles, sign-offs, em dashes, bullet structure and review ratings. Qwen 3.5 27B is at about 0 on the formatting features, but also inflates review ratings (11/18 vs 18/18 for 3.8). All models follow an explicitly stated reward rule in that format, and none do in assistant framing. In reviews, models name the problems honestly but inflate the rating to match the scorer.
