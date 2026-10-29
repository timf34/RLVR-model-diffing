# 10A reference check: status

- **Stage:** complete (2026-10-29). Frozen → generated 256/256 (no retries; 1 non-valid empty reply) → scored → analysed.
- **Old arm:** byte-identical replay of the established bundle deliveries; the old manifest digests and frozen prompts reproduce.
- **New arm:** IFEval runtime frame (rl) + `get_task_packet` diagnostics; labelled a changed setup (`INPUT_DIFF.md`).
- **Headline (Qwen 3.8, +0.50 vs tied):**
  - sending: old 10/16 vs 0/16; new 0/16 vs 0/16;
  - bullets: old 9/16 vs 0/16; new 0/16 vs 0/16.
- Qwen 3.5 is near 0 throughout (old sending +0.50: 2/16).
- The new-arm models cite the displayed scores in their reasoning and then follow the user. The audit found no defect.
- **Cost:** $0.585 (usage × listed prices).
- **Files:** `REPORT.md`, `PROTOCOL.md`, `INPUT_DIFF.md`, `run/`, `figure/`.
