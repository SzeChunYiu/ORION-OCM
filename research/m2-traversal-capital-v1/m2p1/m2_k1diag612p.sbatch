#!/usr/bin/env bash
#SBATCH -A lu2026-2-51
#SBATCH -p lu48
#SBATCH -J m2-k1d612p
#SBATCH -t 6:00:00
#SBATCH -n 1
#SBATCH -c 2
#SBATCH -o /projects/hep/fs12/scratch/scyiu-m2trav/logs/k1d612p_%A_%a.out
# v6.12(p) diagnostic (registered before the run): failed-in-deployment libraries stay retired, on the v6.11 base.
# Repeat-failure seeds 626 629 (abc66), 672 (abc610); identity seeds with no failed deployment under v6.11:
# 623 628 (abc66), 647 (abc69), 634 (abc68), 658 670 (abc610). References: k1d611_r_s<seed>.
set -euo pipefail
B=/projects/hep/fs12/scratch/scyiu-m2trav
PY=/sw/easybuild_milan/software/Python/3.11.5-GCCcore-13.2.0/bin/python3
SEEDS=(626 629 672 623 628 647 634 658 670)
SRCS=(abc66 abc66 abc610 abc66 abc66 abc69 abc68 abc610 abc610)
I=$((SLURM_ARRAY_TASK_ID - 1)); S=${SEEDS[$I]}; SRC=$B/runs/${SRCS[$I]}_s$S; V=p
export M2_V68D=1 M2_V68E=1 M2_V69F=1 M2_V610H=1 M2_V610I=1 M2_V611R=1 M2_V612P=1
W=$B/runs/k1d612_${V}_s$S; rm -rf "$W"; mkdir -p "$W"
cp "$SRC/dev_state.json" "$SRC/checkpoint.json" "$SRC/arm_RESET.json" "$SRC/arm_CONTINUED_OCM.json" "$W/"
cd "$B/scripts_v612"
echo "=== host $(hostname) seed=$S src=$SRC variant=$V runner_sha=$(sha256sum m2p1_runner.py | cut -c1-16)"
$PY m2p1_runner.py --repo "$B" --ecology "$SRC/ECOLOGY.json" --run-dir "$W" --phase restart-and-acquire --arm CONTINUAL_OCM --targets 135 --ladder 200000
echo "=== DONE seed=$S $V"
