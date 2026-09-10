#!/bin/bash
#SBATCH -A lu2026-2-51
#SBATCH -p lu48
#SBATCH -N 1
#SBATCH -n 1
#SBATCH -c 1
#SBATCH -t 04:00:00
#SBATCH -J fo_arm
#SBATCH -o %x_%A_%a.out
#SBATCH -e %x_%A_%a.err
# Form Oracle search arms. One array task = one (arm, lane, dedup, seed).
# No network access is made from the compute node at any point.
set -u
# Stage from SCRATCH, not $HOME. Home carries a per-user quota that df cannot
# see -- it reported 134T free on the same filesystem while a write failed with
# "Disk quota exceeded" -- and lfs quota and quota are both unavailable, so the
# only reliable probe is actually writing a file. An earlier campaign lost 94
# array tasks to Errno 122 mid-write. Scratch is 564T free.
BASE="${FO_BASE:-/projects/hep/fs12/scratch/scyiu-formoracle}"
[ -d "$BASE" ] || BASE="$HOME/zoo221/formoracle"
export PYTHONPATH="$BASE/zoo:$BASE/fo:$BASE"
cd "$BASE" || exit 1
mkdir -p fo/results

# Task decode: 12 seeds x 3 lanes x 2 dedup settings = 72 tasks.
T=${SLURM_ARRAY_TASK_ID}
SEED=$(( T % 12 ))
REST=$(( T / 12 ))
LANE_I=$(( REST % 3 ))
DEDUP_I=$(( REST / 3 ))
LANES=(gs_uniform units hetero)
LANE=${LANES[$LANE_I]}
if [ "$DEDUP_I" -eq 0 ]; then
  ARM="FO_DEDUP"; DFLAG=""
else
  ARM="FO_NODEDUP"; DFLAG="--no-dedup"
fi

OUT="fo/results/FO_${ARM}_${LANE}_s${SEED}.json"
if [ -f "${OUT}.status" ]; then
  echo "already complete: $OUT"; exit 0
fi

srun python3 -u fo/oracle/run_form_oracle.py \
  --arm "$ARM" --seed "$SEED" --lane "$LANE" --t0-budget "${FO_T0_BUDGET:-2187}" \
  --evolvability-n "${FO_EVOLV_N:-64}" $DFLAG --out "$OUT"
RC=$?
echo "task=$T arm=$ARM lane=$LANE seed=$SEED rc=$RC"
exit $RC
