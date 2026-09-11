#!/usr/bin/env bash
#SBATCH -A lu2026-2-51
#SBATCH -p lu48
#SBATCH -J m2p2-gfu
#SBATCH -t 12:00:00
#SBATCH -n 1
#SBATCH -c 2
#SBATCH -o /projects/hep/fs12/scratch/scyiu-m2trav/logs/m2p2gfu_%A_%a.out
# M2-P2 EXPLORATORY: the absorbed guided-first parent (library-first enumeration) against
# controller_v5, on the SAME dev state as LUNARC 3597797 (dev_state/checkpoint copied, so the
# libraries are identical). CONTINUED_OCM is re-run as an identity check on the new runner.
set -euo pipefail
B=/projects/hep/fs12/scratch/scyiu-m2trav
PY=/sw/easybuild_milan/software/Python/3.11.5-GCCcore-13.2.0/bin/python3
E=$(sed -n "${SLURM_ARRAY_TASK_ID}p" "$B/m2p2/WORLD_LIST.txt")
WID=$(basename "$E" .json)
W=$B/runs/m2p2_${WID}_gfu
cd "$B/scripts_v5gfu"; export M2_LIB_RULE=interleave
echo "=== host $(hostname) world=$WID DIAGNOSTIC mining coverage: union and oracle-chunk guided-first; runner_sha=$(sha256sum m2p1_runner.py | cut -c1-16) methods_sha=$(sha256sum $B/src/ocm/learning/methods.py | cut -c1-16) dev_state_sha=$(sha256sum $W/dev_state.json | cut -c1-16)"
NT=$($PY -c "import json;print(len(json.load(open('$E'))['streams']['protected']))")
for A in PARENT_GF_D4 PARENT_GFU_D3 PARENT_GFU_D4 PARENT_GFO_D3 PARENT_GFO_D4; do
  $PY m2p1_runner.py --repo "$B" --ecology "$E" --run-dir "$W" --phase restart-and-acquire --arm "$A" --targets "$NT" --ladder 200000
done
echo "=== DONE $WID $(date -u +%FT%TZ)"
