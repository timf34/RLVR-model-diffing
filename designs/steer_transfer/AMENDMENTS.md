# Amendments to PLAN.md

## 1. Before any generation (2026-10-30, ~16:37 UTC)

- **Change:** `pod/serve_multi.sh` runs with `--no-enable-prefix-caching`.
  - **Why:** neither the Stage A code nor its documentation says whether EasySteer keys the prefix cache by steering
    vector. A cached prompt KV computed under one condition could otherwise serve another.
- **Change:** `st_checks.py` gains a contamination check: an unsteered call repeated after steered calls must match the
  first unsteered call.
- **Change:** `pod/setup_pod.sh` puts the EasySteer venv on the container disk (`ES_VENV_ROOT=/root`).
  - **Why:** `/workspace` on these volume-less pods is an MFS network mount, which is slow for pip. Pods c and e were
    bootstrapped without the main requirements; only the EasySteer venv and the `hf` CLI are used.
- **No effect on the design:** none of these changes touch the design or the analysis. `run/freeze.json` is re-written
  with the new hashes before the first generation.

## 2. First main launch stopped and restarted (2026-10-30, ~16:56 UTC)

- **What happened:** the first launch of `st_generate.py main` (16:46) used inspect's default `strict_tools=True`. That
  sends strict tool schemas, and vLLM then applies constrained decoding to tool calls.
  - Under that mode Qwen 3.5 made its tool call and then kept generating to `max_tokens`. No 3.5 episode finished in
    about 8 minutes.
  - A raw request without strict schemas behaved normally, and so did inspect with `strict_tools=False` (569 tokens,
    16 s).
  - The archived OpenRouter runs had no such constraint, so strict tools also break comparability with them.
- **Fix:** `strict_tools=False`, and `max_connections=256`, because inspect's default connection cap limited
  concurrency.
- **Data:** the 501 episodes from the first launch (all Qwen 3.8: 3.5 had none) are set aside in
  `run/main/discarded/episodes_strict_tools.jsonl` and are not analysed. The main run restarted from zero.
- **Servers:** RunPod's nginx owns port 8001 (a proxy to 8000), so the second server on a 2-GPU pod moved to port 8101.
  Before the fix, "both" 3.5 endpoints were the same GPU-0 server; the server checks passed on it either way. They were
  re-run on the real per-GPU endpoints (`run/checks/server_checks.json`). The smoke run was re-done with the fixed
  client: 56 episodes, all valid.
- **Bridge comparison:** `st_analysis.py` now implements the bridge comparison listed in PLAN.md (unsteered vs archive).
  This is descriptive and outside the primary family.
