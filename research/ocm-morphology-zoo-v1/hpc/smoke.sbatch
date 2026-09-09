#!/usr/bin/env bash
#SBATCH -J zoo-smoke
#SBATCH -A snic2025-22-104
#SBATCH -p cosmos
#SBATCH --qos=test
#SBATCH -t 00:10:00
#SBATCH -c 1
#SBATCH -o logs/smoke_%j.out
#SBATCH -e logs/smoke_%j.err
# SMOKE only (--qos=test, never production): pytest + tiny census slice.
source "$(dirname "$0")/common_env.sh"
set -euo pipefail
cd "$ZOO_ROOT"
$ZOO_PY -m pytest tests/ -q
$ZOO_PY hpc/census_p00.py "$ZOO_ROOT" --chunk 0/560
echo "SMOKE OK"
