#!/bin/bash
SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &>/dev/null && pwd)
DOWNLOAD_MODELS=${DOWNLOAD_MODELS:-0}
PORT=${PORT:-8888}
PERSISTENT_VOLUME_DIR=${PERSISTENT_VOLUME_DIR:-/workspace}

if [ ! -d "${PERSISTENT_VOLUME_DIR}" ]; then
  printf "Configured persistent volume directory ${PERSISTENT_VOLUME_DIR} does not exist. Exiting.\n" >&2
  exit 1
fi
PERSISTENT_VOLUME_DIR=$(cd "${PERSISTENT_VOLUME_DIR}"; pwd)
cd "${PERSISTENT_VOLUME_DIR}"

# check if PERSISTENT_VOLUME_DIR/models exists
MODEL_DIR="${PERSISTENT_VOLUME_DIR}/models"
MODEL_EXISTS=$([ -d "${MODEL_DIR}" ] && echo 1 || echo 0)

if [ "${DOWNLOAD_MODELS}" -eq 1 ]; then
  if [ "${MODEL_EXISTS}" -eq 0 ]; then
    mkdir -p "${MODEL_DIR}"
    printf "Downloading models to %s...\n" "${MODEL_DIR}"
    bash "${SCRIPT_DIR}/download_models.sh" "${MODEL_DIR}"
  fi
  printf "Model is already present. Skipping model download.\n"
else
  if [ "${MODEL_EXISTS}" -eq 0 ]; then
    printf "Model directory %s does not exist. Please set DOWNLOAD_MODELS=1 to download models or create the directory and add models manually. Exiting.\n" "${MODEL_DIR}" >&2
    exit 1
  else
    printf "Model directory %s exists. Skipping model download.\n" "${MODEL_DIR}"
  fi
fi

NGINX_TEMPLATE="${SCRIPT_DIR}/nginx.conf.template"
NGINX_CONF="/etc/nginx/nginx.conf"

printf "Generating nginx config from template: %s -> %s\n" "$NGINX_TEMPLATE" "$NGINX_CONF"
envsubst '\$PORT \$VLLM_PORT \$IMAGE_PORT' < "$NGINX_TEMPLATE" > "$NGINX_CONF"

printf "Starting Nginx in foreground...\n"
nginx -g 'daemon off;'
