#!/usr/bin/env bash
#SBATCH -A lu2026-2-51
#SBATCH -p lu48
#SBATCH -J m2trav-world
#SBATCH -t 04:00:00
#SBATCH -n 1
#SBATCH -c 2
#SBATCH -o /projects/hep/fs12/scratch/scyiu-m2trav/logs/world_%A_%a.out
set -euo pipefail
B=/projects/hep/fs12/scratch/scyiu-m2trav
PY=/sw/easybuild_milan/software/Python/3.11.5-GCCcore-13.2.0/bin/python3
SEED=$((1000 + SLURM_ARRAY_TASK_ID))
MINLEN=$(( SLURM_ARRAY_TASK_ID % 2 == 0 ? 4 : 6 ))   # E1 / E2 pre-registered variants
W=$B/runs/world_${SEED}_min${MINLEN}
mkdir -p "$W"
echo "=== host $(hostname) seed=$SEED minlen=$MINLEN py=$($PY --version 2>&1)"
cd "$B/scripts"
$PY m2p1_ecology.py --repo "$B" --out "$W/ECOLOGY.json" --seed "$SEED" --min-len "$MINLEN"
$PY m2p1_runner.py  --repo "$B" --ecology "$W/ECOLOGY.json" --run-dir "$W" --phase dev --slots 200000
$PY m2p1_attrib.py  --repo "$B" --ecology "$W/ECOLOGY.json" --run-dir "$W" --out "$W/ATTRIBUTION.json"
$PY m2p1_runner.py  --repo "$B" --ecology "$W/ECOLOGY.json" --run-dir "$W" --phase checkpoint
for A in RESET LIBRARY_ONLY CONTINUED SHUFFLED_HISTORY ORACLE_FAMILY ORDINARY_ADAPTIVE_PARENT; do
  $PY m2p1_runner.py --repo "$B" --ecology "$W/ECOLOGY.json" --run-dir "$W" \
      --phase restart-and-acquire --arm "$A" --targets 79
done
$PY m2p1_summarize.py --repo "$B" --ecology "$W/ECOLOGY.json" --run-dir "$W" --out "$W/SUMMARY.json"
echo "=== DONE seed=$SEED $(date -u +%FT%TZ)"
