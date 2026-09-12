#!/usr/bin/env bash
#SBATCH -J gmi-k4
#SBATCH -A __ACCOUNT__
#SBATCH -p __PARTITION__
#SBATCH -t __WALLTIME__
#SBATCH -c 1
#SBATCH --mem-per-cpu=__MEM__
#SBATCH --array=__ARRAY__
#SBATCH -o logs/k4_%A_%a.out
#SBATCH -e logs/k4_%A_%a.err
#
# K4 leave-one-family-out neutral rediscovery, one array task per (family, grammar, cell).
#
# Placeholders __ACCOUNT__ __PARTITION__ __WALLTIME__ __MEM__ __ARRAY__ are filled by
# hpc/gmi_k4_submit.py from LUNARC_ENV_PROBE_V1.json. Submitting this file unrendered is
# intended to fail: the sizing must come from the measured environment, not from a guess.
set -euo pipefail
cd "${SLURM_SUBMIT_DIR}"

# Fail closed if the freeze is absent or does not match the one the runner was built against.
if [ ! -f GMI_K4_LOFO_FREEZE_V1.json ]; then
  echo "freeze artifact absent -- refusing (fail closed)"; exit 3
fi

python3 -u hpc/gmi_k4_task.py \
  --task-index "${SLURM_ARRAY_TASK_ID}" \
  --job-id "${SLURM_ARRAY_JOB_ID:-${SLURM_JOB_ID:-local}}" \
  --host "lunarc"
