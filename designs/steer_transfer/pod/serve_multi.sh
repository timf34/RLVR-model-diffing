#!/usr/bin/env bash
# One EasySteer vLLM server per GPU (data parallel), port PORT_BASE+i (default 8100+i) on GPU i, for the steering-transfer experiment.
# Same EasySteer flags as grader-shifts-persona-space/scripts/pod/serve_easysteer.sh (direct algorithm, split
# graph mode), PLUS the chat-completions tool and reasoning parsers that the sending task needs:
#   --enable-auto-tool-choice --tool-call-parser qwen3_coder --reasoning-parser qwen3
# (both checkpoints' chat templates use the <tool_call><function=...><parameter=...> XML format).
# Prefix caching is OFF: a cached prompt KV computed under one steering vector must never serve another condition.
#
#   bash serve_multi.sh <served-name> <hf_id> <revision> [n_gpus]      # blocks until every server answers
#   bash serve_multi.sh stop
set -uo pipefail
[ -f /workspace/.es_env ] && . /workspace/.es_env
export HF_HOME=/workspace/hf
if [ "${1:-}" = stop ]; then pkill -f "[v]llm serve" || true; exit 0; fi
NAME="${1:?served name}"; HF="${2:?hf id}"; REV="${3:?revision}"
N="${4:-$(nvidia-smi -L | wc -l)}"
MAXLEN="${MAXLEN:-40960}"
PORT_BASE="${PORT_BASE:-8100}"   # NOT 8000+: RunPod's nginx owns 8001 (proxy to 8000)        # prompt (~6k) + max_tokens 32768 (the presentation ablation's budget)
for i in $(seq ${START:-0} $((N-1))); do
  CUDA_VISIBLE_DEVICES=$i PATH="$ES_VENV/bin:$PATH" \
  LD_LIBRARY_PATH="${ES_LD_LIBRARY_PATH}${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}" \
  nohup "$ES_VENV/bin/vllm" serve "$HF" --revision "$REV" --served-model-name "$NAME" \
    --max-model-len "$MAXLEN" --max-num-seqs "${MAX_NUM_SEQS:-128}" --gpu-memory-utilization 0.90 \
    --port $((PORT_BASE+i)) --limit-mm-per-prompt '{"image":0,"video":0}' \
    --enable-steer-vector --steer-algorithms direct --steer-graph-mode "${STEER_GRAPH_MODE:-split}" \
    --enable-auto-tool-choice --tool-call-parser qwen3_coder --reasoning-parser qwen3 \
    --no-enable-prefix-caching \
    --disable-custom-all-reduce > /workspace/serve_$i.log 2>&1 &
  sleep 2
done
for t in $(seq 1 360); do
  up=0
  for i in $(seq ${START:-0} $((N-1))); do curl -sf "http://localhost:$((PORT_BASE+i))/v1/models" | grep -q "$NAME" && up=$((up+1)); done
  [ "$up" = "$((N-${START:-0}))" ] && { echo "SERVERS_UP $N after ~$((t*5))s"; exit 0; }
  pgrep -f "[v]llm serve" >/dev/null || { echo "!! servers died"; tail -n 30 /workspace/serve_0.log; exit 1; }
  sleep 5
done
echo "!! not up after 30 min"; tail -n 30 /workspace/serve_0.log; exit 1
