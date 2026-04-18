#!/usr/bin/env bash
# task-plan.sh — thin wrapper that delegates to task-plan-core.py
# Run from the project root directory.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if ! command -v python3 &>/dev/null; then
  echo "Error: python3 is required but not installed." >&2
  exit 1
fi

exec python3 "$SCRIPT_DIR/task-plan-core.py" "$@"
