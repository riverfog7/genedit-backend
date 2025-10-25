#!/bin/bash

# Install vllm at runtime (see https://docs.vllm.ai/en/latest/getting_started/installation/gpu.html#create-a-new-python-environment)
SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &>/dev/null && pwd)
MODEL_PATH="${PERSISTENT_VOLUME_DIR}/models/"
export HF_HOME="${MODEL_PATH}"

cd "${SCRIPT_DIR}"
uv pip install vllm --torch-backend=auto

# Start vllm server
uv run vllm serve "${MODEL_ID}" \
    --dowload_dir "${MODEL_PATH}" \
    --host "${HOST}" \
    --port "${PORT}" \
    --gpu-memory-utilization 0.4 \
    --max-model-len 16384 \
    --disable-log-requests &
