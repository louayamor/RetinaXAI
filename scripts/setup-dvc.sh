#!/usr/bin/env bash
# Configure DVC remote credentials using environment variables.
# Usage: DVC_REMOTE_TOKEN=<token> ./scripts/setup-dvc.sh
# If DVC_REMOTE_TOKEN is not set, uses the local config (fallback).

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

if [ -z "${DVC_REMOTE_TOKEN:-}" ]; then
    echo "Warning: DVC_REMOTE_TOKEN not set. Using existing local config."
    echo "To configure, run: DVC_REMOTE_TOKEN=<your-token> $0"
    exit 0
fi

cd "$ROOT_DIR"

dvc remote modify dagshub --local auth basic
dvc remote modify dagshub --local user "${DVC_REMOTE_USER:-louayamor}"
dvc remote modify dagshub --local password "$DVC_REMOTE_TOKEN"

echo "DVC remote 'dagshub' configured successfully."
