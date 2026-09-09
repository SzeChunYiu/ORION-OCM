#!/bin/bash
#SBATCH --job-name=pdev217-verify
#SBATCH --partition=hep
#SBATCH --account=hep2023-1-3
#SBATCH --cpus-per-task=1
#SBATCH --time=01:00:00
#SBATCH --mem=2G
#SBATCH --output=/dev/null
#SBATCH --array=0-0
# One array task = one surviving candidate: shadow suites executed fresh + the
# 11 fail-closed hostiles (incl. audit re-measurement on the frozen audit
# suite).  Usage: RUN ROOT GEN WAVE
set -euo pipefail
RUN_ROOT="$1"; GEN="$2"; WAVE="$3"
export PYTHONPATH="${PDEV217_CAPSULE}:${PDEV217_OCM}:${PYTHONPATH:-}"
cd "$RUN_ROOT"
python3 "${PDEV217_CAPSULE}/worker_verify.py" \
    --run-root "$RUN_ROOT" --generation "$GEN" --wave "$WAVE" \
    --index "${SLURM_ARRAY_TASK_ID}"
