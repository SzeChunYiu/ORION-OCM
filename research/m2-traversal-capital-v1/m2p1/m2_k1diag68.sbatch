#!/usr/bin/env bash
#SBATCH -A lu2026-2-51
#SBATCH -p lu48
#SBATCH -J m2-k1d68
#SBATCH -t 6:00:00
#SBATCH -n 1
#SBATCH -c 2
#SBATCH -o /projects/hep/fs12/scratch/scyiu-m2trav/logs/k1d68_%A_%a.out
# v6.8 diagnostic (registered before the run): one variable at a time on the K1-v6.6 seeds that failed.
set -euo pipefail
B=/projects/hep/fs12/scratch/scyiu-m2trav
PY=/sw/easybuild_milan/software/Python/3.11.5-GCCcore-13.2.0/bin/python3
I=$((SLURM_ARRAY_TASK_ID - 1)); SEEDS=(623 626 628 629); VARS=(base d e de)
S=${SEEDS[$((I / 4))]}; V=${VARS[$((I % 4))]}
unset M2_V68D M2_V68E; case $V in d) export M2_V68D=1;; e) export M2_V68E=1;; de) export M2_V68D=1 M2_V68E=1;; esac
SRC=$B/runs/abc66_s$S; W=$B/runs/k1d68_${V}_s$S; rm -rf "$W"; mkdir -p "$W"
cp "$SRC/dev_state.json" "$SRC/checkpoint.json" "$SRC/arm_RESET.json" "$SRC/arm_CONTINUED_OCM.json" "$W/"
cd "$B/scripts_v68"
echo "=== host $(hostname) seed=$S variant=$V runner_sha=$(sha256sum m2p1_runner.py | cut -c1-16)"
$PY m2p1_runner.py --repo "$B" --ecology "$SRC/ECOLOGY.json" --run-dir "$W" --phase restart-and-acquire --arm CONTINUAL_OCM --targets 135 --ladder 200000
echo "=== DONE seed=$S $V"
