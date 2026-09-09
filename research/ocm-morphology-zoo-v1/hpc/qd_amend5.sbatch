#!/usr/bin/env bash
#SBATCH -J zoo-qda5
#SBATCH -A lu2026-2-51
#SBATCH -p lu48
#SBATCH -t 02:00:00
#SBATCH -c 1
#SBATCH --array=0-11%8
#SBATCH -o logs/qda5_%A_%a.out
#SBATCH -e logs/qda5_%A_%a.err
# AMEND-5 campaign (quality-gated D-archive admission): task id ->
# (arm, seed) from the FROZEN manifest.  Manifest is frozen by
# submit_amend5.py BEFORE this array is submitted.  All 12 tasks run
# hpc/qd_run_amend5.py; the gate is the one varied dimension
#   G01_gate_{D2d,D3d}   admission_bar = frozen bar 0.224507 (q0.5)
#   G00_nogate_{D2d,D3d} admission_bar = None (byte-identical control,
#                        asserted equal to the frozen QDA3 twin archives)
source "${SLURM_SUBMIT_DIR}/hpc/common_env.sh"
set -euo pipefail
cd "$ZOO_ROOT"
read -r ARM SEED <<< "$($ZOO_PY - "$SLURM_ARRAY_TASK_ID" <<'PY'
import json, sys
m = json.load(open("manifests/CAMPAIGN_AMEND5_MANIFEST.json"))
t = m["tasks"][int(sys.argv[1])]
print(t["arm"], t["seed"])
PY
)"
echo "task ${SLURM_ARRAY_TASK_ID}: arm=$ARM seed=$SEED"
$ZOO_PY hpc/qd_run_amend5.py "$ZOO_ROOT" "$ARM" "$SEED"
