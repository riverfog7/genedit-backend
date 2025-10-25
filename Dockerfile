FROM python:3.13-slim AS deps

ENV UV_COMPILE_BYTECODE=1
ENV UV_NO_CACHE=1
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app
COPY uv.lock uv.lock
COPY pyproject.toml pyproject.toml
COPY .python-version .python-version

# Use BuildKit cache mount for faster rebuilds
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-editable --no-cache

FROM python:3.13-slim
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    apt-get update && apt-get install -y \
    nginx \
    gettext-base \
    bash \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
COPY --from=deps /app/.venv /app/.venv

ENV PORT=8000
ENV PORT_HEALTH=8001
ENV IMAGE_PORT=25
ENV VLLM_PORT=26
ENV PERSISTENT_VOLUME_DIR=/workspace
ENV DOWNLOAD_MODELS=0

ENV GDINO_MODEL_ID="openmmlab-community/mm_grounding_dino_large_all"
ENV SAM2_MODEL_ID="facebook/sam2.1-hiera-large"
ENV LLM_MODEL_ID="RedHatAI/gemma-3n-E2B-it-quantized.w8a8"
ENV DIFFUSION_CONTROLNET_MODEL_ID="InstantX/Qwen-Image-ControlNet-Inpainting"
ENV DIFFUSION_MODEL_ID="Qwen/Qwen-Image"
#ENV DIFFUSION_EDIT_MODEL_ID="ovedrive/qwen-image-edit-4bit"

COPY . /app
WORKDIR /app

EXPOSE $PORT
EXPOSE $PORT_HEALTH
CMD ["bash", "-c", "/app/start.sh"]
