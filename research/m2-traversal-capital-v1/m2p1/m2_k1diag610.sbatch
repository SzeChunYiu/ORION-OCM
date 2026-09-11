#!/usr/bin/env bash
#SBATCH -A lu2026-2-51
#SBATCH -p lu48
#SBATCH -J m2-k1d610
#SBATCH -t 6:00:00
#SBATCH -n 1
#SBATCH -c 2
#SBATCH -o /projects/hep/fs12/scratch/scyiu-m2trav/logs/k1d610_%A_%a.out
# v6.10 diagnostic (registered before the run): (h), (i), (h)+(i) on top of v6.9, one variable at a time.
# Lock-out seeds 623 626 628 629 (abc66), 636 642 (abc68), 647 (abc69); identity controls 634 640 (abc68), 646 (abc69).
set -euo pipefail
B=/projects/hep/fs12/scratch/scyiu-m2trav
PY=/sw/easybuild_milan/software/Python/3.11.5-GCCcore-13.2.0/bin/python3
SEEDS=(623 626 628 629 636 642 647 634 640 646); SRCS=(abc66 abc66 abc66 abc66 abc68 abc68 abc69 abc68 abc68 abc69); VARS=(h i hi)
I=$((SLURM_ARRAY_TASK_ID - 1)); K=$((I / 3)); S=${SEEDS[$K]}; SRC=$B/runs/${SRCS[$K]}_s$S; V=${VARS[$((I % 3))]}
export M2_V68D=1 M2_V68E=1 M2_V69F=1; unset M2_V610H M2_V610I
case $V in h) export M2_V610H=1;; i) export M2_V610I=1;; hi) export M2_V610H=1 M2_V610I=1;; esac
W=$B/runs/k1d610_${V}_s$S; rm -rf "$W"; mkdir -p "$W"
cp "$SRC/dev_state.json" "$SRC/checkpoint.json" "$SRC/arm_RESET.json" "$SRC/arm_CONTINUED_OCM.json" "$W/"
cd "$B/scripts_v610"
echo "=== host $(hostname) seed=$S src=$SRC variant=$V runner_sha=$(sha256sum m2p1_runner.py | cut -c1-16)"
$PY m2p1_runner.py --repo "$B" --ecology "$SRC/ECOLOGY.json" --run-dir "$W" --phase restart-and-acquire --arm CONTINUAL_OCM --targets 135 --ladder 200000
echo "=== DONE seed=$S $V"
