#!/usr/bin/env bash
#SBATCH -J gmi-k5bh-v7
#SBATCH -A lu2026-2-51
#SBATCH -p aurora
#SBATCH -t 00:05:00
#SBATCH -c 1
#SBATCH --mem-per-cpu=512M
#SBATCH --array=0-255%256
#SBATCH -o logs/k5bhv7_%A_%a.out
#SBATCH -e logs/k5bhv7_%A_%a.err
set -euo pipefail
cd "${SLURM_SUBMIT_DIR}"
for f in GMI_K5_BH_EXECUTION_FREEZE_V7.json GMI_K5_BH_ADMISSIBILITY_SCORING_ADDENDUM_V2.json GMI_K5_BH_PUBLIC_BEACON_V7.json; do test -f "$f" || { echo "missing $f"; exit 3; }; done
mkdir -p logs microscopes/results/k5_bh_v7
python3 -u hpc/gmi_k5_bh_task_v7.py --task-index "${SLURM_ARRAY_TASK_ID}" --job-id "${SLURM_ARRAY_JOB_ID:-${SLURM_JOB_ID:-local}}" --host lunarc
