#!/usr/bin/env bash
#SBATCH -A lu2026-2-51
#SBATCH -p lu48
#SBATCH -J m2-life-long
#SBATCH -t 14:00:00
#SBATCH -n 1
#SBATCH -c 2
#SBATCH -o /projects/hep/fs12/scratch/scyiu-m2trav/logs/lifelong_%A_%a.out
set -euo pipefail
B=/projects/hep/fs12/scratch/scyiu-m2trav
PY=/sw/easybuild_milan/software/Python/3.11.5-GCCcore-13.2.0/bin/python3
SEED=$((4000 + SLURM_ARRAY_TASK_ID))
W=$B/runs/life_${SEED}
mkdir -p "$W"
cd "$B/scripts"
echo "=== host $(hostname) seed=$SEED  LONG-HORIZON LIFETIME (registered before any outcome)"
# Same regime as life_3001 (12 length-2 motifs, length-6 targets from <=3 motifs), one
# trial per seed (seed-varying worlds), horizon-heavy split 0.12/0.05/0.83.
$PY m2p1_ecology_e4.py --repo "$B" --out "$W/ECOLOGY.json" --seed "$SEED" \
    --motifs 12 --motif-min-len 2 --motif-max-len 2 \
    --min-canonical-len 6 --max-canonical-len 6 --max-tokens 3 \
    --split 0.12,0.05,0.83 --min-targets 700 --trials 1 || { echo "ECO_FAIL seed=$SEED"; exit 0; }
NT=$($PY -c "import json;print(len(json.load(open('$W/ECOLOGY.json'))['streams']['protected']))")
echo "=== protected horizon: $NT"
$PY m2p1_runner.py --repo "$B" --ecology "$W/ECOLOGY.json" --run-dir "$W" --phase dev --slots 200000
$PY m2p1_runner.py --repo "$B" --ecology "$W/ECOLOGY.json" --run-dir "$W" --phase checkpoint
for A in RESET CONTINUED_OCM PARENT_WITH_MDL ORDINARY_ADAPTIVE_PARENT SHUFFLED_HISTORY; do
  $PY m2p1_runner.py --repo "$B" --ecology "$W/ECOLOGY.json" --run-dir "$W" \
      --phase restart-and-acquire --arm "$A" --targets "$NT" --ladder 200000
done
$PY m2p1_summarize.py --repo "$B" --ecology "$W/ECOLOGY.json" --run-dir "$W" --out "$W/SUMMARY.json"
$PY m2p1_attrib.py --repo "$B" --ecology "$W/ECOLOGY.json" --run-dir "$W" --out "$W/ATTRIBUTION.json"
$PY m2p1_ledger3.py --label "life_${SEED}" --deployed-arm CONTINUED_OCM --ecology "$W/ECOLOGY.json" \
    --summary "$W/SUMMARY.json" --attribution "$W/ATTRIBUTION.json" --out "$W/LEDGER3_OCM.json"
echo "=== DONE seed=$SEED $(date -u +%FT%TZ)"
