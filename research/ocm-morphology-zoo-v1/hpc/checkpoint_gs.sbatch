#!/usr/bin/env bash
#SBATCH -J zoo-gsck
#SBATCH -A lu2026-2-51
#SBATCH -p lu48
#SBATCH -t 00:10:00
#SBATCH -c 1
#SBATCH -o logs/gsck_%j.out
#SBATCH -e logs/gsck_%j.err
# GS-R1h hourly checkpoint chain (#221 sec 18).  Each instance runs
# hpc/checkpoint_gs.py (appends one line to results/GS_R1_CHECKPOINTS.jsonl
# + rewrites results/GS_R1_STATUS.json), then resubmits itself at +55 min
# UNLESS the campaign is terminal (aggregate marker present, or the wall
# budget expired +2h grace).  Light by design: seconds of work, no
# scoring logic, frozen rules never evaluated here.
export ZOO_ROOT="${ZOO_ROOT:-$HOME/zoo221/gs}"
source "${SLURM_SUBMIT_DIR}/hpc/common_env.sh"
set -euo pipefail
cd "$ZOO_ROOT"
echo "checkpoint chain instance job=${SLURM_JOB_ID} freeze=${GS_FREEZE_SHA:-unset} stop_ts=${GS_STOP_TS:-unset}"
$ZOO_PY hpc/checkpoint_gs.py "$ZOO_ROOT"
VERDICT=$($ZOO_PY - "$ZOO_ROOT" <<'PY'
import json, os, sys, time
root = sys.argv[1]
m = json.load(open(os.path.join(root, "manifests", "GS_R1_TASKS.json")))
if os.path.exists(os.path.join(root, "results", "GS_R1_AGGREGATE.status")):
    print("STOP aggregate marker present")
    sys.exit(0)
stop = float(m.get("stop_ts") or 0)
if stop and time.time() > stop + 2 * 3600:
    print("STOP wall budget + grace elapsed")
    sys.exit(0)
print("CONTINUE")
PY
)
echo "checkpoint chain verdict: ${VERDICT}"
if [[ "${VERDICT}" == CONTINUE* ]]; then
  NEXT=$(sbatch -p "${GSCK_PARTITION:-lu48}" -A "${GSCK_ACCOUNT:-lu2026-2-51}" \
    -t 00:10:00 -c 1 --begin=now+55minutes \
    --export=ALL,GS_FREEZE_SHA="${GS_FREEZE_SHA:-}",GS_STOP_TS="${GS_STOP_TS:-}",GSCK_PARTITION="${GSCK_PARTITION:-lu48}",GSCK_ACCOUNT="${GSCK_ACCOUNT:-lu2026-2-51}" \
    hpc/checkpoint_gs.sbatch | awk '{print $NF}')
  echo "checkpoint chain resubmitted: ${NEXT}"
else
  echo "checkpoint chain terminated"
fi
