#!/bin/bash
# Usage: run_parallel.sh <runner.py> <out_dir>   (repo root as cwd)
# Runs one generator per model in parallel (memguard-capped), retries errors once, then analyses.
R=$1; OUT=$2
mkdir -p "$OUT"
for pass in 1 2; do
  ~/.claude/bin/memguard -m 3 -- .venv/bin/python "$R" generate "Qwen 3.5" 48 >> "$OUT/run_3.5.log" 2>&1 &
  ~/.claude/bin/memguard -m 3 -- .venv/bin/python "$R" generate "Qwen 3.6" 96 >> "$OUT/run_3.6.log" 2>&1 &
  ~/.claude/bin/memguard -m 3 -- .venv/bin/python "$R" generate "Qwen 3.8" 64 >> "$OUT/run_3.8.log" 2>&1 &
  wait
done
~/.claude/bin/memguard -m 3 -- .venv/bin/python "$R" analyse >> "$OUT/analyse.log" 2>&1
echo "done $(date -u +%H:%M)" >> "$OUT/analyse.log"
