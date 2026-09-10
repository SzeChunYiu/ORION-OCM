#!/usr/bin/env bash
#SBATCH -J mex-pool
#SBATCH -A lu2026-2-51
#SBATCH -p lu48
#SBATCH -t 12:00:00
#SBATCH -c 48
#SBATCH -o logs/pool_%j.out
#SBATCH -e logs/pool_%j.err
set -euo pipefail
MANIFEST="${1:?manifest}"; SLICE="${2:?slice}"; NSLICES="${3:?nslices}"
LANE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$LANE"; mkdir -p logs results
python3 run_pool.py --manifest "$MANIFEST" --slice "$SLICE" \
    --nslices "$NSLICES" --workers "${SLURM_CPUS_PER_TASK:-48}" \
    --out "results/POOL_${SLICE}of${NSLICES}.json"
