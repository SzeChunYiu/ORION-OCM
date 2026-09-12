#!/usr/bin/env bash
#SBATCH -J gmi-k5bh-v6
#SBATCH -A __ACCOUNT__
#SBATCH -p __PARTITION__
#SBATCH -t __WALLTIME__
#SBATCH -c 1
#SBATCH --mem-per-cpu=__MEM__
#SBATCH --array=__ARRAY__
#SBATCH -o logs/k5bh_%A_%a.out
#SBATCH -e logs/k5bh_%A_%a.err
set -euo pipefail
cd "${SLURM_SUBMIT_DIR}"
for f in GMI_K5_BH_EXECUTION_FREEZE_V6.json GMI_K5_BH_ADMISSIBILITY_SCORING_ADDENDUM_V2.json GMI_K5_BH_PUBLIC_BEACON_V6.json; do
  test -f "$f" || { echo "required protected artifact absent: $f"; exit 3; }
done
mkdir -p logs microscopes/results/k5_bh_v6
python3 -u hpc/gmi_k5_bh_task_v6.py \
  --task-index "${SLURM_ARRAY_TASK_ID}" \
  --job-id "${SLURM_ARRAY_JOB_ID:-${SLURM_JOB_ID:-local}}" \
  --host "lunarc"
