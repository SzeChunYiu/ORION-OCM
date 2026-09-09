#!/bin/bash
# Driver: generation 3 waves 3-7 (w3-5 frozen-amended quota 24 per AMENDMENT-1;
# w6-7 amendment waves per AMENDMENT-2).  Sequential: each wave uses the fixed
# run_wave.sh chain (generate -> eval array -> collect -> verify array ->
# finalize) with sacct-poll waits inside.
set -uo pipefail
BASE=/projects/hep/fs9/users/scyiu/pdev217-20260909
export PDEV217_CAPSULE="$BASE/repo/research/parallel-developmental-evolution-v1/execution"
export PDEV217_OCM="$BASE/repo/src"
SLURM_DIR="$BASE/repo/research/parallel-developmental-evolution-v1/slurm"
RUN_ROOT="$BASE/run"
SALT="pdev217-20260909-uniform-ignorance"
for WAVE in 3 4 5 6 7; do
  echo "[driver] === g3 w$WAVE start $(date -Is) ==="
  bash "$SLURM_DIR/run_wave.sh" "$RUN_ROOT" 3 "$WAVE" "$SALT" 24
  rc=$?
  echo "[driver] === g3 w$WAVE rc=$rc $(date -Is) ==="
  if [ $rc -ne 0 ]; then
    echo "[driver] stopping: wave $WAVE failed"
    exit $rc
  fi
done
echo "[driver] all g3 waves 3-7 done"
