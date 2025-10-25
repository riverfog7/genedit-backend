#!/bin/bash

SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &>/dev/null && pwd)
cd "${SCRIPT_DIR}" || exit 1

DOCKER_REPO="riverfog7/genedit-backend"
DOCKER_TAG=$(git rev-parse --short HEAD)
DOCKER_TAG_LATEST=1

export DOCKER_BUILDKIT=1
export BUILDKIT_PROGRESS=plain

if ! docker buildx inspect cache-builder >/dev/null 2>&1; then
  echo "Creating buildx builder 'cache-builder'..."
  docker buildx create --name cache-builder --driver docker-container --use
else
  docker buildx use cache-builder
fi

TAGS=("--tag" "${DOCKER_REPO}:${DOCKER_TAG}")
if [ $DOCKER_TAG_LATEST -eq 1 ]; then
  TAGS+=("--tag" "${DOCKER_REPO}:latest")
fi

docker buildx build \
  "${TAGS[@]}" \
  --platform linux/amd64 \
  --build-arg BUILDKIT_INLINE_CACHE=1 \
  --cache-from type=registry,ref="${DOCKER_REPO}:buildcache" \
  --cache-to type=registry,ref="${DOCKER_REPO}:buildcache",mode=max \
  --push \
  .

if [ $? -ne 0 ]; then
  printf "Docker build failed. Exiting.\n" >&2
  exit 1
fi

printf "Docker image %s:%s built and pushed successfully.\n" "${DOCKER_REPO}" "${DOCKER_TAG}"
