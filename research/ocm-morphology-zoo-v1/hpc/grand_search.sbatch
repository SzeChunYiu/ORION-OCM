#!/usr/bin/env bash
#SBATCH -J zoo-gs
#SBATCH -A lu2026-2-51
#SBATCH -p lu48
#SBATCH -t 04:00:00
#SBATCH -c 1
#SBATCH --array=0-1%2
#SBATCH -o logs/gs_%A_%a.out
#SBATCH -e logs/gs_%A_%a.err
# GS-R1 campaign (#221 sec 18).  Task id -> task record from the FROZEN
# manifest (built by submit_gs.py BEFORE any scored run; never rewritten
# once scored).  Partition/account/array range are overridden at
# submission by hpc/submit_gs.py.
#   kind=search -> hpc/gs_run.py   ROOT ARM SEED
#   kind=sweep  -> hpc/gs_sweep.py ROOT SHARD N_SHARDS
export ZOO_ROOT="${ZOO_ROOT:-$HOME/zoo221/gs}"
source "${SLURM_SUBMIT_DIR}/hpc/common_env.sh"
set -euo pipefail
cd "$ZOO_ROOT"
read -r KIND A B <<< "$($ZOO_PY - "$SLURM_ARRAY_TASK_ID" <<'PY'
import json, sys
m = json.load(open("manifests/GS_R1_TASKS.json"))
t = m["tasks"][int(sys.argv[1])]
if t["kind"] == "search":
    print(t["kind"], t["arm"], t["seed"])
else:
    print(t["kind"], t["shard"], t["n_shards"])
PY
)"
echo "task ${SLURM_ARRAY_TASK_ID}: kind=$KIND a=$A b=$B freeze=${GS_FREEZE_SHA:-unset} stop_ts=${GS_STOP_TS:-unset}"
if [ "$KIND" = "search" ]; then
  $ZOO_PY hpc/gs_run.py "$ZOO_ROOT" "$A" "$B"
else
  $ZOO_PY hpc/gs_sweep.py "$ZOO_ROOT" "$A" "$B"
fi
