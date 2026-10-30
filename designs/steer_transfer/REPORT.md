# Steering transfer: report (2026-10-30)

**Question.** Does the automated-minus-human grader direction extracted from Qwen 3.8, added directly to Qwen 3.5,
make 3.5 resolve a user-vs-displayed-score conflict in favour of the scores?

**Answer: yes, selectively, on this task.**

- **Effect of the transferred 3.8 direction at +0.3 on 3.5:** under conflicting scores, 3.5 sends against the user's
  instruction in 28% of episodes, against 6% unsteered.
  - It still sends in 0% of episodes when the scores are reversed, tied or absent.
  - Competence and generation health do not drop.
- **Primary contrasts (both pass, Holm over 2):**
  - **P1:** the score-effect difference-in-differences is **+0.22** [+0.15, +0.30], Holm p < 0.001.
  - **P2:** the matched +0.3 minus −0.3 contrast is **+0.22** [+0.14, +0.30], Holm p < 0.001.
- **Controls:** two norm-matched random directions do nothing. 3.5's *own* auto-minus-human direction does not
  reproduce the effect at +0.3. It has a small effect at +0.1 (+0.10), and the transferred direction beats it directly
  at +0.3: +0.21 [+0.13, +0.28].
- **Source-model control:** on 3.8 the native direction moves sending in a clean dose response, at 32 / 45 / 62 / 61 /
  82% from −0.3 to +0.3.

Under the frozen interpretation rules this supports **a portable evaluator-related causal influence** (reading 1 in
PLAN.md), not generic impairment. It does not show that 3.5 reproduces 3.8's mechanism, or that RL training produced
anything. It is one task, one presentation and one layer, with fixed strengths.

Design and frozen analysis: `PLAN.md`. Deviations: `AMENDMENTS.md`. Auto tables: `run/main/REPORT_auto.md`. Numbers:
`run/main/results.json`. Raw trajectories: `run/main/send/episodes.jsonl`.

## What was run

- **Task:** the presentation ablation's sending task with the old bundle presentation (arm B), on 12 original and
  32 fresh scenario blocks.
  - Conflict and tied prompts are byte-identical to the archived prompts (88/88 checked).
  - Reversed prompts swap only the score numbers. No-history prompts drop the scored records.
- **Directions** (unit vectors, `run/vectors/manifest.json`):
  - `xfer`: 3.8's `original_pre_L36_auto_minus_human`, applied to 3.5 in raw coordinates with no alignment. It is
    identical to Stage A's `auto_human` vector (cosine 1.0).
  - `native`: each model's own vector. On 3.5 its cosine with `xfer` is 0.54.
  - `random0` and `random1`: seed 20261030.
- **Strength:** strength × A₃₆ of the *target* model (3.5: 81.33, 3.8: 52.26, from the Betley-reproduction prompts,
  which are separate from the task).
- **Site:** residual input of block 36 (= EasySteer block-35 output). Steering applies to all prompt and generated
  tokens of every model call, including the tool turns.
- **Grid:** 18 conditions × 4 score arms × 44 blocks × 4 samples = **12,672 episodes**.
  - 12,667 of them have a record.
  - 3 Qwen 3.5 episodes were still generating when the run was closed; they are reported as missing (see below).
  - Every recorded episode is valid. There were no failures, truncations, step limits or empty replies.
- **Serving:** self-hosted on 6 × H200, using vLLM 0.26.0 + EasySteer@6267ca0 in bf16. Each GPU ran its own server with
  the qwen3_coder tool parser and the qwen3 reasoning parser, and prefix caching off.
- **Sampling:** temperature 0.7, top_p 0.95, top_k 20, max 32,768 tokens. Qwen 3.8 used `reasoning_effort=medium`.
  Seeds were shared across steering conditions.

## Bridge: does self-hosting reproduce the API runs?

Yes. Unsteered self-hosted send rates match the archived OpenRouter runs on the same prompts:

| | Self-hosted | API | Difference [95% CI] |
|---|---|---|---|
| 3.5, conflicting scores | 6.3% (n=176) | 7.4% (n=68) | −0.01 [−0.07, +0.05] |
| 3.8, conflicting scores | 62% (n=176) | 64% (n=100) | −0.02 [−0.13, +0.10] |
| Both models, tied scores | 0% | 0% | — |

Remaining serving differences, none of them visible in the rates:
- **Provider:** novita/bf16 (3.5) and deepinfra/bf16 (3.8) on the API, against vLLM bf16 here.
- **Reasoning replay:** inspect sends the earlier turn's reasoning to vLLM as `reasoning_content`, and the Qwen template
  renders it. OpenRouter replays reasoning its own way.
- **Tool-call parsing:** vLLM's `qwen3_coder` parser, against the providers' parsers.
- **`reasoning_effort` on 3.8:** passed here as a chat-template argument. On the API it was an OpenRouter parameter,
  and whether the provider forwards it to the template is unknown.

## Main results: Qwen 3.5

Send rates (n = 176 per cell, except the 3 missing episodes in random0 +0.3 and native +0.3):

| Condition | Conflicting | Reversed | Tied | No history | Task done (all arms) | Median output tokens |
|---|---|---|---|---|---|---|
| Unsteered | **0.06** | 0 | 0 | 0 | 0.90 | 698 |
| xfer +0.1 | 0.18 | 0 | 0 | 0 | 0.92 | 675 |
| xfer −0.1 | 0.11 | 0 | 0 | 0 | 0.88 | 712 |
| **xfer +0.3** | **0.28** | 0 | 0 | 0 | 0.98 | 594 |
| xfer −0.3 | 0.07 | 0 | 0 | 0 | 0.87 | 870 |
| native +0.1 | 0.16 | 0 | 0 | 0 | 0.92 | 650 |
| native −0.1 | 0.09 | 0 | 0 | 0 | 0.90 | 754 |
| native +0.3 | 0.08 | 0 | 0 | 0 | 0.94 | 623 |
| native −0.3 | 0.10 | 0 | 0 | 0 | 0.88 | 982 |
| random0 ±0.3 | 0.03 / 0.06 | 0 | 0 | 0 | 0.91 / 0.88 | 712 / 648 |
| random1 ±0.3 | 0.09 / 0.07 | 0 | 0 | 0 | 0.91 / 0.89 | 690 / 709 |

**Difference-in-differences** (DiD: conflicting minus reversed send rate, steered minus unsteered). Cluster bootstrap
over the 44 blocks:

| Condition | DiD [95% CI] | p |
|---|---|---|
| xfer +0.1 | +0.12 [+0.05, +0.19] | <0.001 |
| xfer −0.1 | +0.05 [−0.01, +0.10] | 0.14 |
| **xfer +0.3 (P1)** | **+0.22 [+0.15, +0.30]** | **<0.001 (Holm)** |
| xfer −0.3 | +0.01 [−0.04, +0.06] | 0.92 |
| native +0.1 | +0.10 [+0.03, +0.18] | 0.008 |
| native −0.1 | +0.03 [−0.02, +0.09] | 0.36 |
| native +0.3 | +0.02 [−0.04, +0.08] | 0.65 |
| native −0.3 | +0.03 [−0.02, +0.09] | 0.28 |
| random0 +0.3 / −0.3 | −0.03 [−0.07, +0.00] / −0.01 [−0.06, +0.05] | 0.10 / 0.93 |
| random1 +0.3 / −0.3 | +0.02 [−0.03, +0.07] / +0.01 [−0.05, +0.07] | 0.47 / 0.77 |

The conflicting-minus-tied DiD equals the conflicting-minus-reversed DiD here, because every condition sends 0% under
both tied and reversed scores.

**Direct comparisons** (differences of DiD, same blocks):

| Comparison | Estimate [95% CI] | p |
|---|---|---|
| **xfer +0.3 minus xfer −0.3 (P2)** | **+0.22 [+0.14, +0.30]** | **<0.001 (Holm)** |
| xfer +0.1 minus xfer −0.1 | +0.07 [+0.02, +0.13] | 0.016 |
| xfer +0.3 minus native +0.3 | +0.21 [+0.13, +0.28] | <0.001 |
| xfer +0.3 minus mean(random +0.3) | +0.23 [+0.16, +0.29] | <0.001 |
| xfer −0.3 minus native −0.3 | −0.03 [−0.09, +0.03] | 0.42 |
| native +0.1 minus native −0.1 | +0.07 [+0.01, +0.13] | 0.046 |
| native +0.3 minus native −0.3 | −0.02 [−0.08, +0.05] | 0.67 |

**Specificity and health:**
- No steering condition produced a single send under reversed scores, tied scores or no history (0 of 176 in every
  cell).
  - With zero events, a conservative one-sided 95% upper bound, using n = 44 blocks, is 6.6% per cell.
  - So positive xfer steering does not raise sending in general. It raises sending only when the displayed scores
    favour sending.
- Competence (the artifact has the task's facts and key fields) does not drop under any condition.
  - Under xfer +0.3 it rises: 0.98 against 0.90 overall, and 0.93 against 0.59 in the no-history arm.
- Valid share is 1.00 everywhere. Every send attempt succeeded, so attempted equals sent.
- Under the frozen rule (valid share −0.10 or no-history competence −0.15), no condition is flagged as impaired.

## Source-model control: Qwen 3.8

| Condition | Conflicting | Reversed | Tied | No history | DiD vs unsteered [95% CI] |
|---|---|---|---|---|---|
| native −0.3 | 0.32 | 0 | 0 | 0 | −0.30 [−0.40, −0.19] |
| native −0.1 | 0.45 | 0 | 0 | 0 | −0.17 [−0.28, −0.06] |
| Unsteered | 0.62 | 0 | 0 | 0 | — |
| native +0.1 | 0.61 | 0 | 0 | 0 | −0.01 [−0.10, +0.08] |
| native +0.3 | 0.82 | 0 | 0 | 0 | +0.20 [+0.11, +0.29] |

- The matched contrast native +0.3 minus native −0.3 is +0.50 [+0.43, +0.57].
- The direction works on its source model in both directions, again only under conflicting scores.

## Interpretation, against the four readings in PLAN.md

1. **Portable evaluator-related direction: supported for the positive direction on 3.5.** The effect is score-specific
   (only the conflicting-score arm moves), is ordered by strength (+0.1 gives +0.12, +0.3 gives +0.22), and comes with
   competence preserved. It matches the sign of the source-model effect.
2. **Generic instruction-following impairment: not supported.** Sends stay at 0 under reversed, tied and no-history
   scores, and competence rises rather than falls.
3. **Incompatible coordinates: not what happened.** The direct transfer works. The two vectors share a cosine of 0.54
   in raw coordinates, so the transfer was not into an unrelated basis to begin with.
4. **Source-only: no.** The direction works on both models.

Caveats that matter for how far this goes:

- **Floor and asymmetry.** Unsteered 3.5 sends in only 6% of conflict episodes, so a decrease is hard to detect.
  - The negative transferred direction does nothing measurable on 3.5 (DiD +0.01), while on 3.8 it cuts sending from
    62% to 32%.
  - The bidirectional evidence on 3.5 is therefore P2 (+0.3 against −0.3), not an observed reduction at −0.3.
- **The native 3.5 direction is not monotone.** It works at +0.1 (+0.10) and not at +0.3 (+0.02). The 3.8-derived
  vector is the more effective lever on 3.5 than 3.5's own contrast vector.
  - Why is untested. Possibilities include different extraction noise, or a component of the 3.8 vector that 3.5's
    contrast does not capture.
  - This should not be read as "3.5 has the same evaluator representation as 3.8".
- **Scope.** This is one task (sending), one presentation (the old bundle, where 3.8's effect is large), one layer (36),
  two strengths, and a 44-block sample.
  - Titles and other text tasks were not run.
  - Score-pattern recognition diagnostics and reasoning labels were not run.
- **Reasoning length shifts with steering in both models:** positive steering gives shorter reasoning, negative steering
  longer. This is a side effect of the direction, separate from the action outcome.
- **Not established:** that the intervention reproduces 3.8's full mechanism, or anything about RLVR training.

## Intervention checks

- **Server checks** (`run/checks/server_checks*.json`), on every GPU's server, using neutral calibration prompts with
  greedy decoding. All passed:
  - scale 0 equals unsteered (tokens and log-probs);
  - ±0.3 changes the output;
  - +0.3 differs from −0.3;
  - an unsteered call repeated after steered calls matches the first (no cross-condition contamination; prefix caching
    was off);
  - a call whose history contains a tool call and its result is also changed.
- **Layer mapping:** in code, `gshift.hooks.add_to_residual(model, 36, v)` hooks block 35's output, which is the input
  of block 36 and EasySteer layer 35. EasySteer was given `layers: [35]`.
  - The server-vs-HF numerical validation of this EasySteer build was done in Stage A and was not repeated here.
- **Downstream activations** (`st_actcheck.py`, HF, 16 neutral prompts): see the next section.

## Downstream activation check

Each vector was added with HF hooks at strength 0.3 × A₃₆. The table gives the mean displacement of the last prompt
token on 16 neutral prompts (`run/checks/actcheck_*.json`).

| Model / vector | Injected: cos with signed unit, norm (expected) | cos with the model's natural auto−human direction at L40 / L48 / L56 |
|---|---|---|
| 3.5 xfer + | 1.000, 24.41 (24.40) | +0.53 / +0.49 / +0.58 |
| 3.5 xfer − | 1.000, 24.42 | −0.52 / −0.47 / −0.49 |
| 3.5 native + | 1.000, 24.42 | +0.87 / +0.69 / +0.64 |
| 3.5 native − | 1.000, 24.42 | −0.85 / −0.67 / −0.53 |
| 3.5 random0 / random1 ± | 1.000, 24.40 | between −0.13 and +0.26; ≈0 at L40 and L48 |
| 3.8 native + | 1.000, 15.69 (15.68) | +0.71 / +0.43 / +0.37 |
| 3.8 native − | 1.000, 15.68 | −0.69 / −0.44 / −0.43 |

- **Injection:** sign, scale and site are confirmed in HF.
- **Transferred vector on 3.5:** it moves downstream activations substantially along 3.5's *own* natural
  auto-minus-human direction, and with the right sign. Random vectors of the same norm do not.
- **Downstream size:** displacement norms for xfer and native are larger than for random at every layer.
- **Scope of this check:** it shows how the vector propagates. It is not evidence that the two models represent "grader
  type" identically. Note also that the native 3.5 vector aligns more with 3.5's natural direction than xfer does, yet
  moves behaviour less at +0.3.

## Failures and deviations

- **First launch discarded.** It used inspect's default strict tool schemas, under which vLLM's constrained decoding
  made Qwen 3.5 run to `max_tokens` after each tool call.
  - The 501 Qwen 3.8 episodes from that launch are set aside in `run/main/discarded/` and not analysed.
  - The run restarted from zero with `strict_tools=False` (AMENDMENTS 2).
- **Port clash.** RunPod's nginx owns port 8001, so the first "second" 3.5 endpoint was the GPU-0 server again. This
  affected throughput only.
- **Restarts.** The client was restarted twice to add pods as they became ready. In-flight episodes were dropped and
  redone, and nothing was double-counted: a key counts once.
- **Missing episodes.** 3 Qwen 3.5 episodes were still generating (long reasoning) at 17:46 UTC, when the run was
  closed to keep to the time budget:
  - native +0.3 / tied;
  - random0 +0.3 / reversed;
  - random0 +0.3 / conflict.

  None is in a primary cell (unsteered or xfer). They are counted as missing, not as compliance, and the primary
  results are unchanged by them.
- **Cost.** About $42 of RunPod time: 4 pods with 6 × H200 at peak, about 1 h 20 min each including setup, plus one pod that was
  stuck at start and terminated after 3 minutes. There were no API or judge costs.

## Provenance

- **Models:**
  - `Qwen/Qwen3.5-27B@fc05daec18b0a78c049392ed2e771dde82bdf654`
  - `Qwen/Qwen3.8-27B@1d4bf0f2ff6012fd82039f2fa52739d0dd7c60c0`
- **Vectors** (sha256 in `run/vectors/manifest.json`):
  - `grader-shifts-persona-space/outputs/qwen3.8-27b/analysis/vectors/original_pre_L36_auto_minus_human.npy` (5416c924…)
  - `.../qwen3.5-27b/.../original_pre_L36_auto_minus_human.npy` (a123602e…)
- **Code:** this folder, with file hashes in `run/freeze.json`.
  - The episode loop, renderer, materials and scorer are imported unchanged from `designs/presentation_ablation`,
    `designs/action` and `designs/score_gap`.
- **Runtime:** vLLM 0.26.0 + EasySteer-vllm-v1@6267ca0 (cu130 wheels, driver 595.91) on H200.
  - Client: inspect_ai 0.3.285 (`openai-api` provider, `strict_tools=False`).
