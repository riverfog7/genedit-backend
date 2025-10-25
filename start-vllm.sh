#!/bin/bash

# Install vllm at runtime (see https://docs.vllm.ai/en/latest/getting_started/installation/gpu.html#create-a-new-python-environment)
SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &>/dev/null && pwd)
MODEL_PATH="${PERSISTENT_VOLUME_DIR}/models/"
HOST="0.0.0.0"
PORT="${VLLM_PORT:-43}"
MAX_MODEL_LEN="${MAX_MODEL_LEN:-8192}"
export HF_HOME="${MODEL_PATH}"
cd "${SCRIPT_DIR}"

# Start vllm server
printf "Starting vLLM server at %s:%s...\n" "${HOST}" "${PORT}"
uv run vllm serve "${MODEL_ID}" \
    --dtype auto \
    --host "${HOST}" \
    --port "${PORT}" \
    --gpu-memory-utilization 0.4 \
    --trust-remote-code \
    --max-model-len "${MAX_MODEL_LEN}" &
