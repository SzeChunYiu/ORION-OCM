#!/usr/bin/env bash
#SBATCH -A lu2026-2-51
#SBATCH -p lu48
#SBATCH -J m2-k1a610
#SBATCH -t 6:00:00
#SBATCH -n 1
#SBATCH -c 2
#SBATCH -o /projects/hep/fs12/scratch/scyiu-m2trav/logs/k1a610_%A_%a.out
# K1-L attribution (registered before the run): h-only on the eleven gated K1-L dev states (abc610_s658..669, s665 gated out).
# Prediction: identical to the h+i K1-L runs on every seed, i.e. (i) has no effect on these lifetimes.
set -euo pipefail
B=/projects/hep/fs12/scratch/scyiu-m2trav
PY=/sw/easybuild_milan/software/Python/3.11.5-GCCcore-13.2.0/bin/python3
SEEDS=(658 659 660 661 662 663 664 666 667 668 669); VARS=(h)
I=$((SLURM_ARRAY_TASK_ID - 1)); S=${SEEDS[$I]}; SRC=$B/runs/abc610_s$S; V=h
export M2_V68D=1 M2_V68E=1 M2_V69F=1; unset M2_V610H M2_V610I
case $V in h) export M2_V610H=1;; i) export M2_V610I=1;; hi) export M2_V610H=1 M2_V610I=1;; esac
W=$B/runs/k1a610_${V}_s$S; rm -rf "$W"; mkdir -p "$W"
cp "$SRC/dev_state.json" "$SRC/checkpoint.json" "$SRC/arm_RESET.json" "$SRC/arm_CONTINUED_OCM.json" "$W/"
cd "$B/scripts_v610"
echo "=== host $(hostname) seed=$S src=$SRC variant=$V runner_sha=$(sha256sum m2p1_runner.py | cut -c1-16)"
$PY m2p1_runner.py --repo "$B" --ecology "$SRC/ECOLOGY.json" --run-dir "$W" --phase restart-and-acquire --arm CONTINUAL_OCM --targets 135 --ladder 200000
echo "=== DONE seed=$S $V"
