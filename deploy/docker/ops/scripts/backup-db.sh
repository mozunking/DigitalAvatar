#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
COMPOSE_DIR="$(cd -- "$SCRIPT_DIR/../.." && pwd)"
BACKUP_DIR="$COMPOSE_DIR/backups"
DATA_DIR="${DATA_DIR:-$COMPOSE_DIR/../../data}"
DB_PATH="${DB_PATH:-$DATA_DIR/app.db}"
TIMESTAMP="$(date +%Y%m%d-%H%M%S)"
BACKUP_PATH="$BACKUP_DIR/app-$TIMESTAMP.db"

mkdir -p "$BACKUP_DIR"

if [[ ! -f "$DB_PATH" ]]; then
  echo "Database file not found: $DB_PATH" >&2
  exit 1
fi

cp "$DB_PATH" "$BACKUP_PATH"
echo "Backup created at $BACKUP_PATH"
