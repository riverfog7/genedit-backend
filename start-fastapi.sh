#!/bin/bash

PORT=${IMAGE_PORT:-8081}
HOST="0.0.0.0"

printf "Starting FastAPI server on %s:%s\n" "$HOST" "$PORT"
uv run fastapi run app/main.py --host $HOST --port $PORT &
