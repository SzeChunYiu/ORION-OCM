#!/bin/bash
#SBATCH -A lu2026-2-51
#SBATCH -p lu48
#SBATCH -N 1
#SBATCH -n 1
#SBATCH -c 1
#SBATCH -t 04:00:00
#SBATCH -J fo_d27
#SBATCH -o %x_%A_%a.out
#SBATCH -e %x_%A_%a.err
# D27 lineage campaign: continued vs reset vs single-object knockout, plus the
# B_future_cognition signature against unrelated and harmful controls.
set -u
BASE="$HOME/zoo221/formoracle"
export PYTHONPATH="$BASE/zoo:$BASE/fo:$BASE"
cd "$BASE" || exit 1
mkdir -p fo/results

SEED=${SLURM_ARRAY_TASK_ID}
OUT="fo/results/FO_D27_s${SEED}.json"
if [ -f "${OUT}.status" ]; then
  echo "already complete: $OUT"; exit 0
fi

srun python3 -u fo/hpc/run_d27_campaign.py \
  --seed "$SEED" --n-forms "${FO_D27_FORMS:-40}" --out "$OUT"
RC=$?
echo "d27 seed=$SEED rc=$RC"
exit $RC
