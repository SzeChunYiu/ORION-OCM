#!/usr/bin/env bash
#SBATCH -J zoo-eval
#SBATCH -A snic2025-22-104
#SBATCH -p cosmos
#SBATCH -t 01:00:00
#SBATCH -c 1
#SBATCH --array=0-0%8
#SBATCH -o logs/eval_%A_%a.out
#SBATCH -e logs/eval_%A_%a.err
# Independent candidate evaluation against a frozen manifest
# (manifests/EVAL_MANIFEST.json, written by whatever tranche needs it —
# e.g. MZ-D9 hostile tests or cross-domain transfer).  Not part of MZ-D3.
source "$(dirname "$0")/common_env.sh"
set -euo pipefail
cd "$ZOO_ROOT"
if [ ! -f manifests/EVAL_MANIFEST.json ]; then
  echo "EVAL_MANIFEST.json absent — tranche not opened; refusing (fail closed)"
  exit 3
fi
$ZOO_PY hpc/evaluate_manifest.py "$ZOO_ROOT" "${SLURM_ARRAY_TASK_ID}"
