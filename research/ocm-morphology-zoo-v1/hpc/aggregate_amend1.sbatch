#!/usr/bin/env bash
#SBATCH -J zoo-agg-a1
#SBATCH -A lu2026-2-51
#SBATCH -p lu48
#SBATCH -t 00:20:00
#SBATCH -c 1
#SBATCH -o logs/agg_a1_%j.out
#SBATCH -e logs/agg_a1_%j.err
source "${SLURM_SUBMIT_DIR}/hpc/common_env.sh"
set -euo pipefail
cd "$ZOO_ROOT"
$ZOO_PY hpc/aggregate_amend1.py "$ZOO_ROOT"
