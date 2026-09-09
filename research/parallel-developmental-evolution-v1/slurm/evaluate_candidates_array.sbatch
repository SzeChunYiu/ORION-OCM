#!/bin/bash
#SBATCH --job-name=pdev217-eval
#SBATCH --partition=hep
#SBATCH --account=hep2023-1-3
#SBATCH --cpus-per-task=1
#SBATCH --time=00:30:00
#SBATCH --mem=2G
#SBATCH --output=/dev/null
#SBATCH --array=0-0
# One array task = one candidate evaluated on the frozen dev suite through the
# frozen meter.  Array size is set at submission to the REGISTERED denominator
# (manifests/BATCH.json).  Usage: RUN ROOT GEN WAVE
set -euo pipefail
RUN_ROOT="$1"; GEN="$2"; WAVE="$3"
export PYTHONPATH="${PDEV217_CAPSULE}:${PDEV217_OCM}:${PYTHONPATH:-}"
cd "$RUN_ROOT"
python3 "${PDEV217_CAPSULE}/worker_evaluate.py" \
    --run-root "$RUN_ROOT" --generation "$GEN" --wave "$WAVE" \
    --index "${SLURM_ARRAY_TASK_ID}"
