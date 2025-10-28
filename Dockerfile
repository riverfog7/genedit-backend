FROM python:3.13-slim

ENV UV_COMPILE_BYTECODE=1
ENV UV_NO_CACHE=1
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

RUN apt-get update && apt-get install -y \
    nginx \
    gettext-base \
    bash \
    build-essential \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . /app

ENV PORT=8000
ENV PORT_HEALTH=8001
ENV IMAGE_PORT=8081
ENV VLLM_API_PORT=8082
ENV IMAGE_ROOT_PATH="/image"
ENV VLLM_ROOT_PATH="/vllm"
ENV PERSISTENT_VOLUME_DIR=/workspace
ENV DOWNLOAD_MODELS=0
ENV MAX_MODEL_LEN=16384
ENV VLLM_MODEL_ALIAS="model"
ENV VLLM_MEMORY_UTIL=0.98
ENV VLLM_DEVICE=0
ENV IMAGE_DEVICE=1

ENV GDINO_MODEL_ID="openmmlab-community/mm_grounding_dino_large_all"
ENV SAM2_MODEL_ID="facebook/sam2.1-hiera-large"
ENV LLM_MODEL_ID="Qwen/Qwen3-VL-32B-Thinking-FP8"
ENV DIFFUSION_CONTROLNET_MODEL_ID="InstantX/Qwen-Image-ControlNet-Inpainting"
ENV DIFFUSION_MODEL_ID="dimitribarbot/Qwen-Image-int8wo"
# Do not download this model. Only used for config files. Will be downloaded at API server startup.
ENV DIFFUSION_ORIG_MODEL_ID="Qwen/Qwen-Image"
#ENV DIFFUSION_EDIT_MODEL_ID="ovedrive/qwen-image-edit-4bit"

EXPOSE $PORT
EXPOSE $PORT_HEALTH
CMD ["bash", "-c", "/app/start.sh"]
