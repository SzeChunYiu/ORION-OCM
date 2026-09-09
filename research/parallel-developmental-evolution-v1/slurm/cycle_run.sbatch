#!/bin/bash
#SBATCH --job-name=pdev217-cycle
#SBATCH --partition=hep
#SBATCH --account=hep2023-1-3
#SBATCH --nodes=1
#SBATCH --cpus-per-task=1
#SBATCH --time=01:00:00
#SBATCH --mem=8G
#SBATCH --output=/projects/hep/fs9/users/scyiu/pdev217-20260909/wave_logs/cycle_%j.log
set -euo pipefail
RUN_ROOT="$1"; GEN="$2"
export PDEV217_CAPSULE=/projects/hep/fs9/users/scyiu/pdev217-20260909/repo/research/parallel-developmental-evolution-v1/execution
export PDEV217_OCM=/projects/hep/fs9/users/scyiu/pdev217-20260909/repo/src
export PYTHONPATH="$PDEV217_CAPSULE:$PDEV217_OCM:${PYTHONPATH:-}"
cd "$RUN_ROOT"
python3 "$PDEV217_CAPSULE/centre_cycle.py" --run-root "$RUN_ROOT" --generation "$GEN" --freeze
