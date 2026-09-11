#!/usr/bin/env bash
#SBATCH -A lu2026-2-51
#SBATCH -p lu48
#SBATCH -J m2-abc611
#SBATCH -t 12:00:00
#SBATCH -n 1
#SBATCH -c 2
#SBATCH -o /projects/hep/fs12/scratch/scyiu-m2trav/logs/abc611_%A_%a.out
# K1 under v6.11 (registered before the run): freshly generated A -> B -> C lifetimes, continual_v6.11 (v6.10hi + regime-change detector), five arms.
set -euo pipefail
export M2_V68D=1 M2_V68E=1 M2_V69F=1 M2_V610H=1 M2_V610I=1 M2_V611R=1
B=/projects/hep/fs12/scratch/scyiu-m2trav
PY=/sw/easybuild_milan/software/Python/3.11.5-GCCcore-13.2.0/bin/python3
S=$((600 + SLURM_ARRAY_TASK_ID))
W=$B/runs/abc611_s$S
mkdir -p "$W"
cd "$B/scripts_v611"
echo "=== host $(hostname) seed=$S runner_sha=$(sha256sum m2p1_runner.py | cut -c1-16) methods_sha=$(sha256sum $B/src/ocm/learning/methods.py | cut -c1-16)"
$PY m2_abc_ecology.py --repo "$B" --out "$W/ECOLOGY.json" --gen m2p1_ecology_e4.py --n 45 --split 0.2,0.1,0.7 --seed-a "$S" || { echo "ECO_FAIL seed=$S"; exit 0; }
$PY m2p1_runner.py --repo "$B" --ecology "$W/ECOLOGY.json" --run-dir "$W" --phase dev --slots 200000
$PY m2p1_runner.py --repo "$B" --ecology "$W/ECOLOGY.json" --run-dir "$W" --phase checkpoint
for A in RESET PARENT_WITH_MDL CONTINUED_OCM CONTINUAL_OCM_NOREC CONTINUAL_OCM; do
  $PY m2p1_runner.py --repo "$B" --ecology "$W/ECOLOGY.json" --run-dir "$W" --phase restart-and-acquire --arm "$A" --targets 135 --ladder 200000
done
echo "=== DONE seed=$S $(date -u +%FT%TZ)"
