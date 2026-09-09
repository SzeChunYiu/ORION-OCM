#!/usr/bin/env bash
#SBATCH -J zoo-qda3
#SBATCH -A lu2026-2-51
#SBATCH -p lu48
#SBATCH -t 02:00:00
#SBATCH -c 1
#SBATCH --array=0-14%8
#SBATCH -o logs/qda3_%A_%a.out
#SBATCH -e logs/qda3_%A_%a.err
# AMEND-3 campaign: task id -> (arm, seed) from the FROZEN manifest.
# Manifest is frozen by submit_amend3.py BEFORE this array is submitted.
source "${SLURM_SUBMIT_DIR}/hpc/common_env.sh"
set -euo pipefail
cd "$ZOO_ROOT"
read -r ARM SEED <<< "$($ZOO_PY - "$SLURM_ARRAY_TASK_ID" <<'PY'
import json, sys
m = json.load(open("manifests/CAMPAIGN_AMEND3_MANIFEST.json"))
t = m["tasks"][int(sys.argv[1])]
print(t["arm"], t["seed"])
PY
)"
echo "task ${SLURM_ARRAY_TASK_ID}: arm=$ARM seed=$SEED"
$ZOO_PY hpc/qd_run_amend3.py "$ZOO_ROOT" "$ARM" "$SEED"
