#!/usr/bin/env bash
# Pod setup for the steering-transfer experiment: weights download (background, hf_transfer) in parallel with
# the EasySteer venv install from grader-shifts-persona-space (unchanged: vllm 0.26.0 + EasySteer@6267ca0).
#
#   rp run <pod> --job setup -- bash /workspace/steer_transfer/pod/setup_pod.sh <hf_id> <revision>
#
# Prints SETUP_DONE when both finished; DL_EXIT / ES_EXIT lines record each step's exit code.
set -uo pipefail
HF_ID="${1:?hf id}"; REV="${2:?revision}"
GS=/workspace/grader-shifts-persona-space
cd "$GS" || exit 1
set -a; [ -f .env ] && . ./.env; set +a
export HF_HOME=/workspace/hf HF_HUB_ENABLE_HF_TRANSFER=1
# /workspace is a network (MFS/FUSE) mount on volume-less pods: pip there is very slow, so the EasySteer venv goes on
# the container disk (as grader-shifts-persona-space scripts/pod/_lib.sh does for FUSE mounts)
export ES_VENV_ROOT=/root
nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader
df -h /workspace | tail -1
HFBIN=/workspace/grader-shifts-persona-space_venv/bin/hf
if [ ! -x "$HFBIN" ]; then
  pip install -q --break-system-packages huggingface_hub hf_transfer >/dev/null 2>&1; HFBIN=$(command -v hf)
fi
( "$HFBIN" download "$HF_ID" --revision "$REV" \
    --exclude "*.pth" > /workspace/dl.log 2>&1; echo "DL_EXIT=$?" >> /workspace/dl.log ) &
DL=$!
bash scripts/pod/install_easysteer.sh > /workspace/es_install.log 2>&1
echo "ES_EXIT=$?"; tail -n 2 /workspace/es_install.log
wait "$DL"; tail -n 1 /workspace/dl.log
echo SETUP_DONE
