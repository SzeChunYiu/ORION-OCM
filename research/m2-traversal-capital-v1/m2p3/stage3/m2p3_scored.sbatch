#!/usr/bin/env bash
#SBATCH -A lu2026-2-51
#SBATCH -p lu48
#SBATCH -J m2p3-scored
#SBATCH -t 12:00:00
#SBATCH -n 1
#SBATCH -c 2
#SBATCH -o /projects/hep/fs12/scratch/scyiu-m2trav/logs/m2p3scored_%A_%a.out
# M2-P3 stage 3 (frozen): fresh dev phase per world, then the registered arms.
# PARENT_GF_D4 vs RESET is the primary; the rest are controls and descriptives.
set -euo pipefail
B=/projects/hep/fs12/scratch/scyiu-m2trav
PY=/sw/easybuild_milan/software/Python/3.11.5-GCCcore-13.2.0/bin/python3
E=$(sed -n "${SLURM_ARRAY_TASK_ID}p" "$B/m2p3/WORLD_LIST.txt")
WID=$(basename "$E" .json); WID=${WID#M2P3_WORLD_}
W=$B/runs/m2p3_${WID}_scored
mkdir -p "$W"
cd "$B/scripts_v5gf"; export M2_LIB_RULE=interleave
echo "=== host $(hostname) world=$WID M2-P3 stage 3; runner_sha=$(sha256sum m2p1_runner.py | cut -c1-16) methods_sha=$(sha256sum $B/src/ocm/learning/methods.py | cut -c1-16)"
NT=$($PY -c "import json;print(len(json.load(open('$E'))['streams']['protected']))")
$PY m2p1_runner.py --repo "$B" --ecology "$E" --run-dir "$W" --phase dev --slots 200000
$PY m2p1_runner.py --repo "$B" --ecology "$E" --run-dir "$W" --phase checkpoint
for A in RESET PARENT_GF_D4 SHUFFLED_HISTORY CONTINUED_OCM PARENT_WITH_MDL PARENT_GFQ_D3 PARENT_GFQ_D4; do
  $PY m2p1_runner.py --repo "$B" --ecology "$E" --run-dir "$W" --phase restart-and-acquire --arm "$A" --targets "$NT" --ladder 200000
done
echo "=== DONE $WID $(date -u +%FT%TZ)"
