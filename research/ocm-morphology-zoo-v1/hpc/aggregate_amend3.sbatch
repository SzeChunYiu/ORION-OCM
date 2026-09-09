#!/usr/bin/env bash
#SBATCH -J zoo-agg-a3
#SBATCH -A lu2026-2-51
#SBATCH -p lu48
#SBATCH -t 00:30:00
#SBATCH -c 1
#SBATCH -o logs/agg_a3_%j.out
#SBATCH -e logs/agg_a3_%j.err
# Aggregate AMEND-3 after every task has a disposition (refuses otherwise).
source "${SLURM_SUBMIT_DIR}/hpc/common_env.sh"
set -euo pipefail
cd "$ZOO_ROOT"
$ZOO_PY hpc/aggregate_amend3.py "$ZOO_ROOT"
