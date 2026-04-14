#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "Usage: $0 <backup-file>" >&2
  exit 1
fi

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
COMPOSE_DIR="$(cd -- "$SCRIPT_DIR/../.." && pwd)"
DATA_DIR="${DATA_DIR:-$COMPOSE_DIR/../../data}"
TARGET_DB="${DB_PATH:-$DATA_DIR/app.db}"
SOURCE_DB="$1"

if [[ ! -f "$SOURCE_DB" ]]; then
  echo "Backup file not found: $SOURCE_DB" >&2
  exit 1
fi

mkdir -p "$DATA_DIR"
cp "$SOURCE_DB" "$TARGET_DB"
echo "Database restored to $TARGET_DB"
