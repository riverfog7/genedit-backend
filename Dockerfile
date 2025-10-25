FROM python:3.13-slim

ENV UV_COMPILE_BYTECODE=1
ENV UV_NO_CACHE=1
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

RUN apt-get update && apt-get install -y \
    nginx \
    gettext-base \
    bash \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . /app

ENV PORT=8000
ENV PORT_HEALTH=8001
ENV IMAGE_PORT=8081
ENV VLLM_PORT=8082
ENV PERSISTENT_VOLUME_DIR=/workspace
ENV DOWNLOAD_MODELS=0
ENV MAX_MODEL_LEN=8192
ENV VLLM_MODEL_ALIAS="model"

ENV GDINO_MODEL_ID="openmmlab-community/mm_grounding_dino_large_all"
ENV SAM2_MODEL_ID="facebook/sam2.1-hiera-large"
ENV LLM_MODEL_ID="RedHatAI/gemma-3n-E2B-it-quantized.w8a8"
ENV DIFFUSION_CONTROLNET_MODEL_ID="InstantX/Qwen-Image-ControlNet-Inpainting"
ENV DIFFUSION_MODEL_ID="Qwen/Qwen-Image"
#ENV DIFFUSION_EDIT_MODEL_ID="ovedrive/qwen-image-edit-4bit"

EXPOSE $PORT
EXPOSE $PORT_HEALTH
CMD ["bash", "-c", "/app/start.sh"]
