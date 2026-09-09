#!/usr/bin/env bash
#SBATCH -J zoo-agg
#SBATCH -A lu2026-2-51
#SBATCH -p lu48
#SBATCH -t 00:20:00
#SBATCH -c 1
#SBATCH -o logs/agg_%j.out
#SBATCH -e logs/agg_%j.err
source "${SLURM_SUBMIT_DIR}/hpc/common_env.sh"
set -euo pipefail
cd "$ZOO_ROOT"
$ZOO_PY hpc/aggregate.py "$ZOO_ROOT"
