#!/usr/bin/env bash
set -euo pipefail
python -m venv .venv-m0
. .venv-m0/bin/activate
./scripts/m0_install_dev.sh
python tools/m0_manifest.py --check --write /tmp/MIGRATED_FILE_MANIFEST_V2.json
python tools/m0_dependency_audit.py --check --write /tmp/DEPENDENCY_AUDIT_V1.generated.json
python -m pytest -q
python -m ocm.demo --controlled
python -m ocm.status --live
python -m ocm.status --strict
