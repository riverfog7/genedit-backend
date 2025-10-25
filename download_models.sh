#!/bin/bash

SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &>/dev/null && pwd)
MODEL_DIR=${1:-"${SCRIPT_DIR}/models"}

download_models() {
  local model_id=$1

  printf "Downloading model %s...\n" "${model_id}"
  uvx --from 'huggingface_hub[cli]' --with 'hf_transfer' hf download --repo-type model --cache-dir "${MODEL_DIR}" "${model_id}" --max-workers 16
}

printf "Downloading models to %s...\n" "${MODEL_DIR}"
mkdir -p "${MODEL_DIR}"
cd "${MODEL_DIR}"

download_models "${GDINO_MODEL_ID}"
download_models "${SAM2_MODEL_ID}"
download_models "${LLM_MODEL_ID}"
download_models "${DIFFUSION_CONTROLNET_MODEL_ID}"
download_models "${DIFFUSION_MODEL_ID}"
printf "Model download completed.\n"
