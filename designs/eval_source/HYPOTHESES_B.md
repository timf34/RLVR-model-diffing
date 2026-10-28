# Pre-registered hypotheses: batch B (only the archive moves)

Written before batch B was generated, after batch A was frozen and running and before any batch A output was analysed. Batch B is the **primary source comparison**. Batch A (`HYPOTHESES.md`, `runs/main/`) is kept and reported as the *bundled* comparison, where the document and the archive move together.

**What changed from batch A (layout only).** In both sources the task document is attached to the user's turn, under the same pointer sentence ("The document is attached automatically below."). Only the scored archive moves:
- `message`: appended to the user's turn as a second attachment;
- `tool`: returned by a `read_archive` call that is already in the conversation (a **fixed tool-history continuation**: the call is scripted, not chosen by the target).

The archive JSON is byte-identical in both. Removing the archive block from the message-arm user turn gives the tool-arm user turn exactly (`es_materials.check_b()`). Without an archive the two sources are the same prompt. Tasks, examples, scores, framing lines, system prompt, tool definitions, serving, measures, judge and sample sizes are as in batch A.

**Tests.** Identical to `HYPOTHESES.md`, computed by the same frozen `analysis.py` on `runs/main_b/`:

| ID | Contrast (per behaviour) | Role |
|---|---|---|
| **C1** | Qwen 3.8, MR: R > P | Manipulation check (not Holm-adjusted). |
| **H1** | Qwen 3.8, TR: R > P | Survival with a tool-returned archive. Holm over behaviours. |
| **H2** | Qwen 3.8: TR R > TO R | Framing effect with a tool source. Holm over behaviours. |
| **H3** | TR R: Qwen 3.8 > Qwen 3.5 | Model difference with a tool source. Holm over behaviours. |
| **H4** | Qwen 3.8, rl: TR R vs MR R | Source effect, two-sided. |

"Pass" = one-sided Fisher p < 0.05 (Holm where stated) and the two-stage task bootstrap 95% interval excludes 0. Reading rules, descriptive analyses and checks S1–S3 are as in `HYPOTHESES.md`.

**Added descriptive comparison (no test decision).** Batch A tool arm vs batch B tool arm, rewards cells, per model and framing: does also moving the document into a tool result change accommodation?

**Scope.** Neither batch measures whether a model would discover or read the archive on its own; exposure is given in every arm.
