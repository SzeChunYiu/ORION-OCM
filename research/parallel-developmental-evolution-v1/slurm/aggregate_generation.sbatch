#!/bin/bash
#SBATCH --job-name=pdev217-aggregate
#SBATCH --partition=hep
#SBATCH --account=hep2023-1-3
#SBATCH --nodes=1
#SBATCH --cpus-per-task=1
#SBATCH --time=01:00:00
#SBATCH --mem=4G
#SBATCH --output=/dev/null
# Centre-only step: apply the PRE-FROZEN selection rules.  collect: read all
# eval rows, admit, Pareto frontier, emit verify batch + denominator.
# finalize: final admissibility, QD archive offers, shared history, winner /
# negative-wave attribution, serial-control advancement.  Usage: RUN ROOT GEN
# WAVE STAGE
set -euo pipefail
RUN_ROOT="$1"; GEN="$2"; WAVE="$3"; STAGE="$4"
export PYTHONPATH="${PDEV217_CAPSULE}:${PDEV217_OCM}:${PYTHONPATH:-}"
cd "$RUN_ROOT"
python3 "${PDEV217_CAPSULE}/centre_aggregate.py" \
    --run-root "$RUN_ROOT" --generation "$GEN" --wave "$WAVE" --stage "$STAGE"
