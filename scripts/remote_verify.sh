#!/usr/bin/env bash
# Sync this checkout to a remote verification host and run a command there.
# Usage: scripts/remote_verify.sh [host] -- <command...>     (default host: billy-old)
# Runs live on the remote host only; the local machine is for git/gh and edits.
set -euo pipefail
HOST="${1:-billy-old}"; shift || true
[ "${1:-}" = "--" ] && shift
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
REMOTE_DIR="~/ocm-verify/$(basename "$ROOT")"
ssh "$HOST" "mkdir -p $REMOTE_DIR"
rsync -az --delete --exclude .venv --exclude .git --exclude __pycache__ --exclude .pytest_cache --exclude '*.egg-info' "$ROOT/" "$HOST:$REMOTE_DIR/"
ssh "$HOST" "cd $REMOTE_DIR && PY=\$(command -v python3.12 || command -v python3.13 || command -v python3.11 || command -v python3) && (test -x .venv/bin/python || \$PY -m venv .venv) && . .venv/bin/activate && python -m pip install -q -r requirements-dev.lock >/dev/null && python -m pip install -q -e . --no-deps >/dev/null && $*"
