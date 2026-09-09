#!/usr/bin/env bash
#SBATCH -J zoo-qda2
#SBATCH -A lu2026-2-51
#SBATCH -p lu48
#SBATCH -t 02:00:00
#SBATCH -c 1
#SBATCH --array=0-23%8
#SBATCH -o logs/qda2_%A_%a.out
#SBATCH -e logs/qda2_%A_%a.err
# AMEND-2 campaign: task id -> (pair, encoding, seed) from the FROZEN manifest.
# Manifest is frozen by submit_amend2.py BEFORE this array is submitted.
source "${SLURM_SUBMIT_DIR}/hpc/common_env.sh"
set -euo pipefail
cd "$ZOO_ROOT"
read -r PAIR ENC SEED <<< "$($ZOO_PY - "$SLURM_ARRAY_TASK_ID" <<'PY'
import json, sys
m = json.load(open("manifests/CAMPAIGN_AMEND2_MANIFEST.json"))
t = m["tasks"][int(sys.argv[1])]
print(t["pair"], t["enc"], t["seed"])
PY
)"
echo "task ${SLURM_ARRAY_TASK_ID}: pair=$PAIR enc=$ENC seed=$SEED"
$ZOO_PY hpc/qd_run_amend2.py "$ZOO_ROOT" "$PAIR" "$ENC" "$SEED"
