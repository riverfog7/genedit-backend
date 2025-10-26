#!/bin/bash

PORT=${IMAGE_PORT:-8081}
IMAGE_DEVICE=${IMAGE_DEVICE:-1}
HOST="0.0.0.0"

printf "Starting FastAPI server on %s:%s\n" "$HOST" "$PORT"
CUDA_VISIBLE_DEVICES=$IMAGE_DEVICE uv run fastapi run app/main.py --host $HOST --port $PORT &
