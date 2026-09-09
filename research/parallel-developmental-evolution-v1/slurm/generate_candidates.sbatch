#!/bin/bash
#SBATCH --job-name=pdev217-generate
#SBATCH --partition=hep
#SBATCH --account=hep2023-1-3
#SBATCH --nodes=1
#SBATCH --cpus-per-task=1
#SBATCH --time=01:00:00
#SBATCH --mem=4G
#SBATCH --output=/dev/null
# Centre-only step: builds the wave batch, allocates the generation's frozen
# suites, measures the incumbent control, registers the denominator BEFORE any
# array submission.  Usage (args after sbatch): RUN ROOT GEN WAVE SALT QUOTA
set -euo pipefail
RUN_ROOT="$1"; GEN="$2"; WAVE="$3"; SALT="$4"; QUOTA="$5"
export PYTHONPATH="${PDEV217_CAPSULE}:${PDEV217_OCM}:${PYTHONPATH:-}"
cd "$RUN_ROOT"
python3 "${PDEV217_CAPSULE}/centre_generate.py" \
    --run-root "$RUN_ROOT" --generation "$GEN" --wave "$WAVE" \
    --salt "$SALT" --quota "$QUOTA"
