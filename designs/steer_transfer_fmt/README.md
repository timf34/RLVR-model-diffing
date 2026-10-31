# Steering transfer on formatting tasks (title, sign-off, bullets)

Replicates `designs/steer_transfer` (sending) on the scored-example formatting tasks. It asks whether Qwen 3.8's
automated-minus-human direction, added directly to Qwen 3.5, makes 3.5 adopt the score-favoured format against the
user's request, and whether it beats 3.5's own direction.

**Status:** run complete (2026-10-31). Results are in `REPORT.md` and deviations in `AMENDMENTS.md`. The design,
outcomes, tests and interpretation rules are in `PLAN.md` (revision 1, frozen before generation).

| File | Role |
|---|---|
| `sf_common.py` | Families, score arms and designs (full / reduced). Reuses steer_transfer's conditions and vectors |
| `sf_prepare.py` | Renders arm-B prompts with the ablation's renderer and asserts byte-identity with the archive (164/164) and pure score swaps. Writes `run/<stage>/fmt/` |
| `sf_generate.py` | Episode client. Uses `pa_generate.episode` and steer_transfer's `gen_config` unchanged, with `strict_tools=False`; resumable |
| `sf_score.py` | Deterministic outcomes: override / complies / neither / facts_ok / malformed / completion |
| `sf_analysis.py` | Frozen analysis: per-family DiD, Holm over 6, scenario-cluster bootstrap, missing bounds, archive bridge |
| `sf_tests.py` | Offline checks: scorer cases, vector sha256s, mock plumbing, recovery of planted effects (writes `run_mock/` only) |
| `sf_power.py` | Minimum detectable effect by design |

Pods and serving reuse `designs/steer_transfer/pod/` unchanged (`setup_pod.sh`, `serve_multi.sh` with prefix caching
off, `tunnels.py`) and `designs/steer_transfer/st_checks.py` (server checks).

## Grid

**Revision 1:** reverse transfer added. Both targets get the same 13 conditions.

| Model | Conditions | × arms | × generations per cell (full) | Total |
|---|---|---|---|---|
| Qwen 3.5 | 13: unsteered; xfer (3.8 dir) ±0.1 and ±0.3; native ±0.1 and ±0.3; random0 and random1 ±0.3 | 4 | title 176, sign-off 176, bullets 190 | 28,184 |
| Qwen 3.8 | 13: unsteered; native ±0.1 and ±0.3; xfer (3.5 dir, scaled by 3.8's A₃₆) ±0.1 and ±0.3; random0 and random1 ±0.3 | 4 | same | 28,184 |
| **Full total** | | | | **56,368** (22 / 22 / 38 distinct scenarios) |
| Reduced total | | | title 88, sign-off 88, bullets 114 | 30,160 |

The sending-task reverse transfer is in `designs/steer_transfer/ADDENDUM_reverse.md`:
- 5,632 new Qwen 3.8 episodes (3.5 direction ±0.1 and ±0.3; random ±0.3);
- a 352-episode bridge re-run;
- the existing 3.8 cells reused.

It shares the same pods.

## Cost and runtime estimate (self-hosted; no API or judge costs; one combined session)

**Basis:**
- **Output tokens:** archived arm-B medians are about 2,300 per episode for 3.5 (p95 about 5,000) and about 950 for 3.8,
  for one call with a ~500-token prompt. Planning uses means of 2.6k and 1.1k.
- **Throughput:** about 2.5k generated tok/s per H200 at about 160 concurrent requests (steer_transfer reached
  1.6–2.0k at 95 concurrent, with KV cache about 35% used).
- **Sending reverse:** about 95 episodes/min per GPU, as measured on 3.8.

| Component | Generations | Output tokens | GPU-hours |
|---|---|---|---|
| Formatting, full: 3.5 | 28,184 | ~73 M | ~8.1 |
| Formatting, full: 3.8 | 28,184 | ~31 M | ~3.5 |
| Sending reverse (3.8, plus bridge) | 5,984 episodes (3 calls each) | — | ~1.1 |
| HF activation checks (3.8 new directions) | — | — | ~0.3 |

| Plan | GPUs | Generation | Setup + checks + smokes + bridges | Wall clock | Est. cost (H200 ≈ $5.29/GPU-h) |
|---|---|---|---|---|---|
| **Full formatting + sending reverse (recommended)** | 8 × H200 (5 → 3.5, 3 → 3.8) | ~95–105 min | ~40 min | **~2.4 h** | **~$100** (range $85–140) |
| Reduced formatting + sending reverse | 6 × H200 (4 → 3.5, 2 → 3.8) | ~70–80 min | ~40 min | ~1.9 h | ~$60 (range $50–85) |
| Sending reverse only | 2 × H200 | ~35 min | ~30 min | ~1.1 h | ~$12–15 |

- **Ceiling:** `--minutes` on each client stops launching new work, and pods are terminated when the run ends.
- **Main risks:**
  - GPU availability (last time only 2× and 1× H200 pods were free);
  - −0.3 steering lengthening reasoning (+25% median tokens on sending);
  - the sending bridge failing, in which case the 3,520 reused 3.8 sending cells are re-generated (prespecified; about
    +0.6 GPU-h, +$4).

## Launch (only after approval)

1. **Record the design choice and freeze.** No outcome data exist at this point.

   ```bash
   .venv/bin/python designs/steer_transfer_fmt/sf_prepare.py --stage main --design full
   ```

   ```bash
   .venv/bin/python designs/steer_transfer_fmt/sf_prepare.py --stage smoke
   ```

   ```bash
   .venv/bin/python designs/steer_transfer_fmt/sf_freeze.py
   ```

2. **Pods.** Same recipe as steer_transfer: `rp up` H200 pods (volume none), `rp bootstrap --no-req`, then
   `designs/steer_transfer/pod/setup_pod.sh <hf_id> <rev>` per pod. Then serve with `PORT_BASE=8100 MAX_NUM_SEQS=256`:

   ```bash
   bash /workspace/steer_transfer/pod/serve_multi.sh qwen3.5-27b Qwen/Qwen3.5-27B fc05daec18b0a78c049392ed2e771dde82bdf654
   ```

   Copy `designs/steer_transfer/run/vectors` to `/workspace/steer_transfer/run/vectors` on every pod (the GGUF paths in
   the steering spec point there).

3. **Tunnels and server checks.** Every endpoint must report ALL_OK. Run `st_checks.py` for the 3.5 endpoints, and
   `st_reverse.py check` for the 3.8 endpoints (it covers native, xfer, random0 and random1 on 3.8). On one 3.8 GPU,
   also run `st_actcheck.py "Qwen 3.8"` for the new directions' injection norm and sign.

   ```bash
   ENDPOINTS_FILE=../../steer_transfer_fmt/run/endpoints.json python3 designs/steer_transfer/pod/tunnels.py "Qwen 3.5=<pod>:8100/8101,..." "Qwen 3.8=<pod>:8100"
   ```

   ```bash
   .venv/bin/python designs/steer_transfer/st_checks.py server --endpoints designs/steer_transfer_fmt/run/endpoints.json
   ```

4. **Real smoke.** 144 generations. Gate: all valid, and steering specs as expected.

   ```bash
   ~/.claude/bin/memguard -m 6 -- .venv/bin/python designs/steer_transfer_fmt/sf_generate.py smoke --conc 16
   ```

5. **Sending reverse.** On the 3.8 endpoints, in the same session: `st_reverse.py generate reverse_bridge`, check the
   gate, then `st_reverse.py generate reverse` (see `designs/steer_transfer/ADDENDUM_reverse.md`).

6. **Main formatting run.** Unsteered items go first.

   ```bash
   ~/.claude/bin/memguard -m 6 -- .venv/bin/python designs/steer_transfer_fmt/sf_generate.py main --conc 160 --minutes 150
   ```

7. **Analysis.** Read the bridge first, then fill `REPORT_TEMPLATE.md` into `REPORT.md`.

   ```bash
   ~/.claude/bin/memguard -m 6 -- .venv/bin/python designs/steer_transfer_fmt/sf_analysis.py --B 4000
   ```

Offline validation (already run; all pass):

```bash
~/.claude/bin/memguard -m 4 -- .venv/bin/python designs/steer_transfer_fmt/sf_tests.py
```

`run_mock/` holds synthetic test data only. Real outputs go to `run/` only, and the scripts refuse to mix the two.

**Large files are committed gzipped.** Before analysis, run `gunzip -k run/main/fmt/episodes.jsonl.gz run/main/fmt/items.jsonl.gz run/main/scored.jsonl.gz`.
