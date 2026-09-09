#!/usr/bin/env bash
# Optional Apptainer image for dependency reproducibility.  The capsule is
# stdlib-only Python >=3.9, so the DEFAULT environment is plain python3;
# build this only if a tranche later adds numpy/pyribs (never rewrite OCM
# semantics to fit a library).
set -euo pipefail
command -v apptainer >/dev/null 2>&1 || { echo "apptainer absent — stdlib python3 is the default env"; exit 0; }
here="$(cd "$(dirname "$0")/.." && pwd)"
apptainer build "$here/manifests/zoo221.sif" - <<'DEF'
Bootstrap: docker
From: python:3.11-slim
%test
  python3 -c "import json,hashlib,random,itertools; print('stdlib ok')"
DEF
echo "built $here/manifests/zoo221.sif"
