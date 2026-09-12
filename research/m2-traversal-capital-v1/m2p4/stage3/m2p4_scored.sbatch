#!/usr/bin/env bash
#SBATCH -A lu2026-2-51
#SBATCH -p lu48
#SBATCH -J m2p4-scored
#SBATCH -t 24:00:00
#SBATCH -n 1
#SBATCH -c 2
#SBATCH -o /projects/hep/fs12/scratch/scyiu-m2trav/logs/m2p4scored_%A_%a.out
# M2-P4 stage 3, registered in M2P4_STAGE3_FREEZE_V1.json BEFORE this ran.
# Fresh dev phase per world, checkpoint, then an OS-process restart per arm.
# Primary: PARENT_GF_D4 vs 0.5 x RESET on the protected stream. The rest are controls
# and descriptives. Walltime 24h against M2-P3's observed 1m33s..32m29s per world; these
# worlds are larger (100..224 members), and the margin removes walltime as a failure mode.
#
# The eight worlds are the ones the stage-2 receipt certifies in compiled_worlds, all
# 8/8 viable and 8/8 G-SURF PASS. The six b34_compiled worlds are the pre-freeze
# feasibility probes and are deliberately NOT scored.
set -euo pipefail
B=/projects/hep/fs12/scratch/scyiu-m2trav
PY=/sw/easybuild_milan/software/Python/3.11.5-GCCcore-13.2.0/bin/python3
E=$(sed -n "${SLURM_ARRAY_TASK_ID}p" "$B/m2p4/WORLD_LIST.txt")
WID=$(basename "$E" .json); WID=${WID#M2P4_WORLD_}
W=$B/runs/m2p4_${WID}_scored
mkdir -p "$W"
cd "$B/scripts_v5gf"; export M2_LIB_RULE=interleave
# Assert the registered artifacts, not merely reference them. A mismatch must stop this
# task, never silently score a different runner or a different set of registered units.
RS=$(sha256sum m2p1_runner.py | cut -d' ' -f1)
MS=$(sha256sum "$B/src/ocm/learning/methods.py" | cut -d' ' -f1)
[ "$RS" = "7d790905ada3ad76e9a59a09da777f4e0c5921715fed096fd8b68ec72be7b0de" ] || { echo "RUNNER SHA MISMATCH: $RS"; exit 9; }
[ "$MS" = "e0a0565466dc67787b2162831e363b232960d0d864c15af62bc9e7e865f8b4d3" ] || { echo "METHODS SHA MISMATCH: $MS"; exit 9; }
echo "=== host $(hostname) world=$WID M2-P4 stage 3; runner_sha=${RS:0:16} methods_sha=${MS:0:16}"
NT=$($PY -c "import json;print(len(json.load(open('$E'))['streams']['protected']))")
echo "=== protected targets: $NT"
$PY m2p1_runner.py --repo "$B" --ecology "$E" --run-dir "$W" --phase dev --slots 200000
$PY m2p1_runner.py --repo "$B" --ecology "$E" --run-dir "$W" --phase checkpoint
for A in RESET PARENT_GF_D4 SHUFFLED_HISTORY CONTINUED_OCM PARENT_WITH_MDL PARENT_GFQ_D3 PARENT_GFQ_D4; do
  $PY m2p1_runner.py --repo "$B" --ecology "$E" --run-dir "$W" --phase restart-and-acquire --arm "$A" --targets "$NT" --ladder 200000
done
echo "=== DONE $WID $(date -u +%FT%TZ)"
