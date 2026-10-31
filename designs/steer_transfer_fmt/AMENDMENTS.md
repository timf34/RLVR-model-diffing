# Amendments to PLAN.md

## 1. Launch attempt 1 aborted: RunPod balance exhausted (2026-10-30)

- **19:45 UTC:** approved launch, full design plus the sending reverse transfer. Four pods were rented with 8 GPUs
  (sf-35-1 4 × H200, sf-35-2 1 × H200, sf-38-5 2 × H100, sf-38-6 1 × H200), costing about $39.7/h.
- **Progress before the stop:** bootstrap and setup (EasySteer install, weight download) were in progress. By 19:52 two
  pods had their weights.
- **20:46:57 UTC:** RunPod stopped every pod ("Exited by Runpod"). The account balance was −$2.45.
  - My readiness watcher had no failure branch for stopped pods or a negative balance. It kept retrying SSH and only
    gave up at 23:57, so the stop went unnoticed for about 3 hours.
  - Stopped pods bill no GPU time, so the cost was about 62 GPU-minutes × 8 GPUs, roughly **$41**, plus a little
    stopped-disk storage.
- **Then:** all four pods were terminated, and no network volumes exist.
- **Effect on the experiment:** **no episodes were generated** for either experiment. `run/main` and
  `steer_transfer/run/reverse*` contain only prepared inputs, and the frozen plans, grids and hashes are unchanged.
- **Relaunch rule:** before renting, check the RunPod balance against the full estimate (about $100 plus margin). The
  readiness watcher must also stop on any pod status other than RUNNING.

## 2. Relaunch (2026-10-31, from 00:42 UTC; balance $197.55 confirmed before renting)

- **Pods:** 8 × H200.
  - sf-35-15 (2) and sf-35-17 (1) serve Qwen 3.5. sf-35-16 (2) never got SSH in 16 minutes and was terminated, then
    replaced by sf-35-20 (2).
  - sf-38-18 (2) and sf-38-19 (1) serve Qwen 3.8.
- **Gates passed before generation:**
  - `st_reverse_actcheck.py` on sf-38-19 (HF): for all four 3.8 directions, the injection has cosine 1.000 with the
    signed unit and norm 15.67 against an expected 15.68 (= 0.3 × A₃₆(3.8)).
  - `st_checks.py` (3.5 endpoints) and `st_reverse.py check` (3.8, all four directions): ALL_OK. Copies are in
    `run/checks/`.
- **Smoke:** 144 generations, 143 valid. One Qwen 3.5 generation was truncated at max_tokens (32,768). That is a model
  outcome category already counted by the analysis, not a pipeline fault, so the main run started.
  - Strictly, PLAN gate 3 said "all valid". This is the deviation, recorded here before any main-run outcome was seen.
  - Steering specs were checked: 3.5 scale 24.40 with 3.5's GGUFs; 3.8 scale 15.68 with 3.8's.
- **Run order:** the main run started on 3 Qwen 3.5 GPUs and 1 Qwen 3.8 GPU. Clients are restarted (resumable by key)
  to add sf-35-20 and sf-38-18 when they are ready.

## 3. Run closed with 13 generations missing (2026-10-31 03:22 UTC)

- **Where they are:** 13 Qwen 3.5 generations (out of 56,368) were still running long reasoning when the client was
  stopped to end billing. They fall across 11 cells, none of them a primary (P1, P2 or P3) cell.
- **How they are counted:** as missing, never as compliance. Bounds are in `results.json`.
- **Pod replacements:** sf-35-20, the replacement for sf-35-16, also never got SSH and was terminated. A 4 × H200 pod
  (sf-35-31) was added instead, for 10 GPUs in total, so the run finished sooner. The total GPU work was unchanged.
