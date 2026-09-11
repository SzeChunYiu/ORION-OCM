#!/usr/bin/env bash
#SBATCH -A lu2026-2-51
#SBATCH -p lu48
#SBATCH -J m2p2-ocm5
#SBATCH -t 12:00:00
#SBATCH -n 1
#SBATCH -c 2
#SBATCH -o /projects/hep/fs12/scratch/scyiu-m2trav/logs/m2p2ocm5_%A_%a.out
# M2-P2 EXPLORATORY EXTENSION (not part of the frozen arm family): the integrated
# developmental controller on the authored worlds, fresh controller-aware dev phase,
# strongest-parent controls, three-ledger amortisation with the deployed arm.
set -euo pipefail
B=/projects/hep/fs12/scratch/scyiu-m2trav
PY=/sw/easybuild_milan/software/Python/3.11.5-GCCcore-13.2.0/bin/python3
E=$(sed -n "${SLURM_ARRAY_TASK_ID}p" "$B/m2p2/WORLD_LIST.txt")
WID=$(basename "$E" .json)
W=$B/runs/m2p2_${WID}_ocm5
mkdir -p "$W"
cd "$B/scripts_v68"; export M2_LIB_RULE=interleave
echo "=== host $(hostname) world=$WID EXPLORATORY integrated arm, controller_v5 (uniform); runner_sha=$(sha256sum m2p1_runner.py | cut -c1-16) methods_sha=$(sha256sum $B/src/ocm/learning/methods.py | cut -c1-16)"
NT=$($PY -c "import json;print(len(json.load(open('$E'))['streams']['protected']))")
$PY m2p1_runner.py --repo "$B" --ecology "$E" --run-dir "$W" --phase dev --slots 200000
$PY m2p1_runner.py --repo "$B" --ecology "$E" --run-dir "$W" --phase checkpoint
for A in RESET CONTINUED_OCM PARENT_WITH_MDL ORDINARY_ADAPTIVE_PARENT SHUFFLED_HISTORY; do
  $PY m2p1_runner.py --repo "$B" --ecology "$E" --run-dir "$W" --phase restart-and-acquire --arm "$A" --targets "$NT" --ladder 200000
done
$PY m2p1_summarize.py --repo "$B" --ecology "$E" --run-dir "$W" --out "$W/SUMMARY.json"
$PY m2p1_attrib.py --repo "$B" --ecology "$E" --run-dir "$W" --out "$W/ATTRIBUTION.json"
$PY m2p1_ledger3.py --label "m2p2_${WID}_ocm" --deployed-arm CONTINUED_OCM --ecology "$E" \
    --summary "$W/SUMMARY.json" --attribution "$W/ATTRIBUTION.json" --out "$W/LEDGER3_OCM.json"
echo "=== DONE $WID $(date -u +%FT%TZ)"
