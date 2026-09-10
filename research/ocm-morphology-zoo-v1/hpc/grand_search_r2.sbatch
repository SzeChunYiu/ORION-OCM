#!/usr/bin/env bash
#SBATCH -J zoo-gs2
#SBATCH -A lu2026-2-51
#SBATCH -p lu48
#SBATCH -t 02:00:00
#SBATCH -c 1
#SBATCH --array=0-1%48
#SBATCH -o logs/gs2_%A_%a.out
#SBATCH -e logs/gs2_%A_%a.err
# GS-R2 campaign (JOB B, #221 sec 18 GS-R2).  Task id -> record from the
# FROZEN GS_R2_TASKS manifest (built before any scored run; never
# rewritten once scored).  Partition/account/array range overridden at
# submission by hpc/submit_gs_r2.py.  All tasks are kind=search.
export ZOO_ROOT="${ZOO_ROOT:-$HOME/zoo221/gs_r2}"
export GS_RUN_PREFIX="${GS_RUN_PREFIX:-GS_R2_}"
export GS_FREEZE_NAME="${GS_FREEZE_NAME:-GRAND_SEARCH_R2_FREEZE.json}"
source "${SLURM_SUBMIT_DIR}/hpc/common_env.sh"
set -euo pipefail
cd "$ZOO_ROOT"
read -r A B <<< "$($ZOO_PY - "$SLURM_ARRAY_TASK_ID" <<'PY'
import json, sys
m = json.load(open("manifests/GS_R2_TASKS.json"))
t = m["tasks"][int(sys.argv[1])]
assert t["kind"] == "search", "R2 has only search tasks: %r" % t
print(t["arm"], t["seed"])
PY
)"
echo "task ${SLURM_ARRAY_TASK_ID}: arm=$A seed=$B freeze=${GS_FREEZE_SHA:-unset} stop_ts=${GS_STOP_TS:-unset}"
$ZOO_PY hpc/gs_run.py "$ZOO_ROOT" "$A" "$B"
