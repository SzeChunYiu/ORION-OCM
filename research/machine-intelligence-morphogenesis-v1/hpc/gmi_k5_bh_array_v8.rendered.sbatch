#!/usr/bin/env bash
#SBATCH -J gmi-k5bh-v8
#SBATCH -A lu2026-2-51
#SBATCH -p aurora
#SBATCH -t 00:10:00
#SBATCH -c 1
#SBATCH --mem-per-cpu=512M
#SBATCH --array=0-79%80
#SBATCH -o logs/k5bhv8_%A_%a.out
#SBATCH -e logs/k5bhv8_%A_%a.err
set -euo pipefail
cd "${SLURM_SUBMIT_DIR}"
module load Python/3.11.5 2>/dev/null || true
for f in GMI_K5_BH_EXECUTION_FREEZE_V8.json GMI_K5_BH_REVIVAL_PLAN_V8.json GMI_K5_BH_ADMISSIBILITY_SCORING_ADDENDUM_V2.json GMI_K5_BH_PUBLIC_BEACON_V8.json; do test -f "$f" || { echo "missing $f"; exit 3; }; done
mkdir -p logs microscopes/results/k5_bh_v8
PYTHONPATH="${SLURM_SUBMIT_DIR}" python3 -u hpc/gmi_k5_bh_task_v8.py --task-index "${SLURM_ARRAY_TASK_ID}" --tier protected --job-id "${SLURM_ARRAY_JOB_ID:-${SLURM_JOB_ID:-local}}" --host lunarc
