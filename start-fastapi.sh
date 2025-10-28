#!/bin/bash

PORT=${IMAGE_PORT:-8081}
IMAGE_DEVICE=${IMAGE_DEVICE:-1}
HOST="0.0.0.0"
DEBUG_DISABLE_IMAGE=${DEBUG_DISABLE_IMAGE:-0}

if [ ${DEBUG_DISABLE_IMAGE} -eq 1 ]; then
    printf "Image server start is disabled via DEBUG_DISABLE_IMAGE=1. Exiting.\n"
    exit 0
fi

printf "Starting FastAPI server on %s:%s\n" "$HOST" "$PORT"
CUDA_VISIBLE_DEVICES=$IMAGE_DEVICE uv run fastapi run app/main.py --host $HOST --port $PORT &
