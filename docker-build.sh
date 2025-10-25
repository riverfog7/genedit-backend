#!/bin/bash

SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &>/dev/null && pwd)
cd "${SCRIPT_DIR}" || exit 1

DOCKER_REPO="riverfog7/genedit-backend"
DOCKER_TAG=$(git rev-parse --short HEAD)
DOCKER_TAG_LATEST=1

docker build --tag temp --platform linux/amd64 .
if [ $? -ne 0 ]; then
  printf "Docker build failed. Exiting.\n" >&2
  exit 1
fi

if [ $DOCKER_TAG_LATEST -eq 1 ]; then
  docker tag temp "${DOCKER_REPO}:latest"
  docker push "${DOCKER_REPO}:latest"
  if [ $? -ne 0 ]; then
    printf "Docker push latest failed. Exiting.\n" >&2
    exit 1
  fi
fi

docker tag temp "${DOCKER_REPO}:${DOCKER_TAG}"
docker push "${DOCKER_REPO}:${DOCKER_TAG}"
if [ $? -ne 0 ]; then
  printf "Docker push %s failed. Exiting.\n" "${DOCKER_TAG}" >&2
  exit 1
fi
docker rmi temp
printf "Docker image %s:%s built and pushed successfully.\n" "${DOCKER_REPO}" "${DOCKER_TAG}"
