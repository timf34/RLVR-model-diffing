# Steering transfer (Qwen 3.8 grader direction → Qwen 3.5)

Design and frozen analysis plan: `PLAN.md`. Deviations from it: `AMENDMENTS.md`. Results: `REPORT.md`.

## Files

| File | Role |
|---|---|
| `st_common.py` | Constants and the condition grid (models, directions, strengths, score arms) |
| `st_prepare.py` | Renders the prompts with the presentation ablation's renderer. Asserts byte-identity with the archive and that reversed differs from conflict by a pure score swap. Writes `run/<stage>/send/` |
| `st_vectors.py` | Builds the unit vectors and EasySteer GGUFs, and the manifest with A₃₆, source sha256s and cosines |
| `st_generate.py` | Episode client (the ablation's `pa_generate.episode`) against the EasySteer servers; resumable |
| `st_checks.py` | Server checks: zero-strength, applied, sign, contamination, multi-turn |
| `st_actcheck.py` | HF downstream activation check, run on a pod |
| `st_analysis.py` | Rule-based scoring and the frozen analysis (cluster bootstrap over blocks, Holm) |
| `pod/` | Pod setup, multi-GPU serving, laptop ssh tunnels |

## Run

```bash
.venv/bin/python designs/steer_transfer/st_prepare.py --stage main
../grader-shifts-persona-space/.venv/bin/python designs/steer_transfer/st_vectors.py   # needs gguf
bash designs/steer_transfer/pod/launch_servers.sh                                      # pods already set up
python3 designs/steer_transfer/pod/tunnels.py "Qwen 3.5=st-xfer-a:8000/8101,st-xfer-e:8100/8101" "Qwen 3.8=st-xfer-d:8000,st-xfer-c:8100"
.venv/bin/python designs/steer_transfer/st_checks.py server
~/.claude/bin/memguard -m 4 -- .venv/bin/python designs/steer_transfer/st_generate.py main --conc 96
.venv/bin/python designs/steer_transfer/st_analysis.py --B 4000
```

Raw trajectories are committed gzipped: `gunzip -k run/main/send/episodes.jsonl.gz` before re-running the analysis.
