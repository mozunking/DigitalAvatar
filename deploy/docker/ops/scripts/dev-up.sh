#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
COMPOSE_DIR="$(cd -- "$SCRIPT_DIR/../.." && pwd)"
COMPOSE_FILE="$COMPOSE_DIR/docker-compose.yml"

cd "$COMPOSE_DIR"
docker compose -f "$COMPOSE_FILE" up --build "$@"
