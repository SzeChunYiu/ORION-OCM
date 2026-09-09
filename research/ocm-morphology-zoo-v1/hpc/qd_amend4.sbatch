#!/usr/bin/env bash
#SBATCH -J zoo-qda4
#SBATCH -A lu2026-2-51
#SBATCH -p lu48
#SBATCH -t 02:00:00
#SBATCH -c 1
#SBATCH --array=0-20%8
#SBATCH -o logs/qda4_%A_%a.out
#SBATCH -e logs/qda4_%A_%a.err
# AMEND-4 campaign: task id -> (kind, arm, seed) from the FROZEN manifest.
# Manifest is frozen by submit_amend4.py BEFORE this array is submitted.
#   kind=islands -> hpc/qd_run_amend4.py   (MZ-D8: I01 ring-mig / I02 nomig)
#   kind=hzd9r   -> hpc/hzd9_recompute.py  (MZ-D9: 5 amend-3 arms x 3 seeds)
source "${SLURM_SUBMIT_DIR}/hpc/common_env.sh"
set -euo pipefail
cd "$ZOO_ROOT"
read -r KIND ARM SEED <<< "$($ZOO_PY - "$SLURM_ARRAY_TASK_ID" <<'PY'
import json, sys
m = json.load(open("manifests/CAMPAIGN_AMEND4_MANIFEST.json"))
t = m["tasks"][int(sys.argv[1])]
print(t["kind"], t["arm"], t["seed"])
PY
)"
echo "task ${SLURM_ARRAY_TASK_ID}: kind=$KIND arm=$ARM seed=$SEED"
if [ "$KIND" = "islands" ]; then
  $ZOO_PY hpc/qd_run_amend4.py "$ZOO_ROOT" "$ARM" "$SEED"
else
  $ZOO_PY hpc/hzd9_recompute.py "$ZOO_ROOT" "$ARM" "$SEED"
fi
