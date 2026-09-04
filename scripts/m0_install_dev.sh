#!/usr/bin/env bash
set -euo pipefail
python -m pip install -r requirements-dev.lock
python -m pip install -e . --no-deps
