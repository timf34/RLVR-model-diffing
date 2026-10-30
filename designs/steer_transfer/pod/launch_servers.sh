#!/usr/bin/env bash
# From the laptop: copy the experiment folder (vectors, scripts) to each pod and start one EasySteer server per GPU.
#   bash designs/steer_transfer/pod/launch_servers.sh
set -uo pipefail
cd /Users/timf34/Documents/VSCode/runpod-runner
export RUNPOD_API_KEY=$(grep '^RUNPOD_API_KEY=' ../grader-shifts-persona-space/.env | cut -d= -f2- | tr -d '"')
SRC=/Users/timf34/Documents/VSCode/model-diffing-agent/designs/steer_transfer
Q5=(qwen3.5-27b Qwen/Qwen3.5-27B fc05daec18b0a78c049392ed2e771dde82bdf654)
Q8=(qwen3.8-27b Qwen/Qwen3.8-27B 1d4bf0f2ff6012fd82039f2fa52739d0dd7c60c0)
start() {  # pod model-array...
  local p=$1; shift
  .venv/bin/rp ssh "$p" -- "rm -rf /workspace/steer_transfer/run/vectors" >/dev/null 2>&1
  .venv/bin/rp scp "$p" "$SRC/run/vectors" pod:/workspace/steer_transfer/run/ -r >/dev/null
  .venv/bin/rp scp "$p" "$SRC/pod/serve_multi.sh" pod:/workspace/steer_transfer/pod/serve_multi.sh >/dev/null
  .venv/bin/rp run "$p" --job serve -- bash /workspace/steer_transfer/pod/serve_multi.sh "$@" | tail -1
}
start st-xfer-a "${Q5[@]}" &
start st-xfer-e "${Q5[@]}" &
start st-xfer-c "${Q8[@]}" &
start st-xfer-d "${Q8[@]}" &
wait
echo launched
