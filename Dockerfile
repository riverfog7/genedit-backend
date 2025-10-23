FROM python:3.13-alpine3.22 as deps

ENV UV_COMPILE_BYTECODE=1
ENV UV_NO_CACHE=1
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app
COPY uv.lock uv.lock
COPY pyproject.toml pyproject.toml
COPY .python-version .python-version

RUN uv sync --locked --no-editable --no-cache

FROM python:3.13-alpine3.22
RUN apk add --no-cache nginx envsubst bash
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
COPY --from=deps /app/.venv /app/.venv

COPY . /app
WORKDIR /app

ENV PORT=8000
ENV PORT_HEALTH=8001
ENV IMAGE_PORT=25
ENV VLLM_PORT=26
ENV PERSISTENT_VOLUME_DIR=/workspace
ENV DOWNLOAD_MODELS=0

EXPOSE $PORT
EXPOSE $PORT_HEALTH
CMD ["bash", "-c", "/app/start.sh"]
