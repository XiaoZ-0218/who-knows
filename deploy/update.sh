#!/bin/sh
set -eu
DIR=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
cd "$DIR"
if docker info >/dev/null 2>&1; then
  COMPOSE="docker compose"
else
  COMPOSE="sudo docker compose"
fi
git fetch origin main
LOCAL=$(git rev-parse HEAD)
REMOTE=$(git rev-parse origin/main)
if [ "$LOCAL" = "$REMOTE" ]; then
  exit 0
fi
git reset --hard origin/main
$COMPOSE up -d --build
