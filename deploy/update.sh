#!/bin/sh
set -eu
DIR=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
cd "$DIR"
if docker info >/dev/null 2>&1; then
  DOCKER="docker"
else
  DOCKER="sudo docker"
fi
git_do() {
  if command -v git >/dev/null 2>&1; then
    git "$@"
  else
    $DOCKER run --rm -v "$DIR":/git -w /git alpine:3.20 \
      sh -c 'apk add --no-cache git >/dev/null && git "$@"' git "$@"
  fi
}
git_do fetch origin main
LOCAL=$(git_do rev-parse HEAD)
REMOTE=$(git_do rev-parse origin/main)
if [ "$LOCAL" = "$REMOTE" ]; then
  exit 0
fi
git_do reset --hard origin/main
$DOCKER compose up -d --build
