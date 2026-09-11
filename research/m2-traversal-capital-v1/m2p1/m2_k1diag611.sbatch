#!/usr/bin/env bash
#SBATCH -A lu2026-2-51
#SBATCH -p lu48
#SBATCH -J m2-k1d611
#SBATCH -t 6:00:00
#SBATCH -n 1
#SBATCH -c 2
#SBATCH -o /projects/hep/fs12/scratch/scyiu-m2trav/logs/k1d611_%A_%a.out
# v6.11 diagnostic (registered before the run): regime-change detector (r) on the v6.10hi base.
# Pooled lock-out seeds 623 626 628 629 (abc66), 636 642 (abc68), 647 (abc69), 662 672 674 679 (abc610);
# clean controls 634 (abc68), 646 (abc69), 658 670 (abc610). Every seed has a v6.10hi reference.
set -euo pipefail
B=/projects/hep/fs12/scratch/scyiu-m2trav
PY=/sw/easybuild_milan/software/Python/3.11.5-GCCcore-13.2.0/bin/python3
SEEDS=(623 626 628 629 636 642 647 662 672 674 679 634 646 658 670)
SRCS=(abc66 abc66 abc66 abc66 abc68 abc68 abc69 abc610 abc610 abc610 abc610 abc68 abc69 abc610 abc610)
I=$((SLURM_ARRAY_TASK_ID - 1)); S=${SEEDS[$I]}; SRC=$B/runs/${SRCS[$I]}_s$S; V=r
export M2_V68D=1 M2_V68E=1 M2_V69F=1 M2_V610H=1 M2_V610I=1 M2_V611R=1
W=$B/runs/k1d611_${V}_s$S; rm -rf "$W"; mkdir -p "$W"
cp "$SRC/dev_state.json" "$SRC/checkpoint.json" "$SRC/arm_RESET.json" "$SRC/arm_CONTINUED_OCM.json" "$W/"
cd "$B/scripts_v611"
echo "=== host $(hostname) seed=$S src=$SRC variant=$V runner_sha=$(sha256sum m2p1_runner.py | cut -c1-16)"
$PY m2p1_runner.py --repo "$B" --ecology "$SRC/ECOLOGY.json" --run-dir "$W" --phase restart-and-acquire --arm CONTINUAL_OCM --targets 135 --ladder 200000
echo "=== DONE seed=$S $V"
