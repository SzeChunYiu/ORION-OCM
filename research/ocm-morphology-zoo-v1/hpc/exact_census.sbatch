#!/usr/bin/env bash
#SBATCH -J zoo-census
#SBATCH -A snic2025-22-104
#SBATCH -p cosmos
#SBATCH -t 00:30:00
#SBATCH -c 1
#SBATCH --array=0-7%8
#SBATCH -o logs/census_%A_%a.out
#SBATCH -e logs/census_%A_%a.err
# Exact P00 census, sharded by stride; shards merge deterministically by index.
source "$(dirname "$0")/common_env.sh"
set -euo pipefail
cd "$ZOO_ROOT"
$ZOO_PY hpc/census_p00.py "$ZOO_ROOT" --chunk "${SLURM_ARRAY_TASK_ID}/8"
echo "CENSUS SHARD ${SLURM_ARRAY_TASK_ID} DONE"
