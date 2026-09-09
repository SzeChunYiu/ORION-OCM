#!/usr/bin/env bash
#SBATCH -J zoo-qd
#SBATCH -A snic2025-22-104
#SBATCH -p cosmos
#SBATCH -t 02:00:00
#SBATCH -c 1
#SBATCH --array=0-23%8
#SBATCH -o logs/qd_%A_%a.out
#SBATCH -e logs/qd_%A_%a.err
# MZ-D3 production campaign: task id -> (arm, seed) from the FROZEN manifest.
# Manifest is frozen by submit_campaign.py BEFORE this array is submitted.
source "$(dirname "$0")/common_env.sh"
set -euo pipefail
cd "$ZOO_ROOT"
read -r ARM SEED <<< "$($ZOO_PY - "$SLURM_ARRAY_TASK_ID" <<'PY'
import json, sys
m = json.load(open("manifests/CAMPAIGN_MZD3_MANIFEST.json"))
t = m["tasks"][int(sys.argv[1])]
print(t["arm"], t["seed"])
PY
)"
echo "task ${SLURM_ARRAY_TASK_ID}: arm=$ARM seed=$SEED"
$ZOO_PY hpc/qd_run.py "$ZOO_ROOT" "$ARM" "$SEED"
