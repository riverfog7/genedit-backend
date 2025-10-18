#!/bin/bash

SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &>/dev/null && pwd)
MODEL_DIR=${1:-"${SCRIPT_DIR}/models"}

download_models() {
  local model_id=$1

  printf "Downloading model %s...\n" "${model_id}"
  uvx --from 'huggingface_hub[cli]' --with 'hf_transfer' hf download --repo-type model --cache-dir "${MODEL_DIR}" "${model_id}" --max-workers 16
}


GDINO_MODEL_ID="openmmlab-community/mm_grounding_dino_large_all"
SAM2_MODEL_ID="facebook/sam2.1-hiera-large"
LLM_MODEL_ID="unsloth/gemma-3n-E2B-it"
DIFFUSION_CONTROLNET_MODEL_ID="InstantX/Qwen-Image-ControlNet-Inpainting"
DIFFUSION_MODEL_ID="Qwen/Qwen-Image"

printf "Downloading models to %s...\n" "${MODEL_DIR}"
mkdir -p "${MODEL_DIR}"
cd "${MODEL_DIR}"

download_models "${GDINO_MODEL_ID}"
download_models "${SAM2_MODEL_ID}"
download_models "${LLM_MODEL_ID}"
download_models "${DIFFUSION_CONTROLNET_MODEL_ID}"
download_models "${DIFFUSION_MODEL_ID}"
printf "Model download completed.\n"
