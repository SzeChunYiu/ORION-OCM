#!/bin/bash
#SBATCH --job-name=pdev217-parent
#SBATCH --partition=hep
#SBATCH --account=hep2023-1-3
#SBATCH --cpus-per-task=1
#SBATCH --time=00:30:00
#SBATCH --mem=2G
#SBATCH --output=/dev/null
#SBATCH --array=0-0
# PDEV-2/PDEV-11: matched parent arm jobs.  One array task = one parent-batch
# entry (PARENT g2 control / CONTINUED serial incumbent + neighbours / RESET
# serial incumbent + neighbours) on the SAME frozen dev suite and meter.
# Usage: RUN ROOT GEN
set -euo pipefail
RUN_ROOT="$1"; GEN="$2"
export PYTHONPATH="${PDEV217_CAPSULE}:${PDEV217_OCM}:${PYTHONPATH:-}"
cd "$RUN_ROOT"
python3 "${PDEV217_CAPSULE}/worker_parent.py" \
    --run-root "$RUN_ROOT" --generation "$GEN" --index "${SLURM_ARRAY_TASK_ID}"
