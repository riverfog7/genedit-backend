#!/bin/bash

# Install vllm at runtime (see https://docs.vllm.ai/en/latest/getting_started/installation/gpu.html#create-a-new-python-environment)
SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &>/dev/null && pwd)
MODEL_PATH="${PERSISTENT_VOLUME_DIR}/models/"
VLLM_MODEL_ALIAS="${VLLM_MODEL_ALIAS:-model}"
HOST="0.0.0.0"
PORT="${VLLM_API_PORT:-43}"
VLLM_MEMORY_UTIL="${VLLM_MEMORY_UTIL:-0.93}"
VLLM_DEVICE=${VLLM_DEVICE:-0}
MAX_MODEL_LEN="${MAX_MODEL_LEN:-16384}"
export HF_HOME="${MODEL_PATH}"
export VLLM_DISABLE_FLASHINFER=1
cd "${SCRIPT_DIR}"

uv pip install --upgrade vllm --torch-backend=auto
# Start vllm server
printf "Starting vLLM server at %s:%s...\n" "${HOST}" "${PORT}"
CUDA_VISIBLE_DEVICES=$VLLM_DEVICE uv run vllm serve "${LLM_MODEL_ID}" \
    --served-model-name "${VLLM_MODEL_ALIAS}" \
    --host "${HOST}" \
    --port "${PORT}" \
    --gpu-memory-utilization $VLLM_MEMORY_UTIL \
    --max-seq-len-to-capture "${MAX_MODEL_LEN}" \
    --compilation-config '{"cudagraph_capture_sizes": [1, 2]}' \
    --trust-remote-code \
    --limit-mm-per-prompt.video 0 \
    --max-model-len "${MAX_MODEL_LEN}" &
