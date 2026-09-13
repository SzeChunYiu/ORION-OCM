#!/usr/bin/env bash
# Development-tier local driver for the K5 B-H revival V8 plan (never protected evidence).
# Usage: gmi_k5_bh_run_v8_local.sh <python> <host-label> <job-label> [parallelism]
# Runs all 80 tasks of GMI_K5_BH_REVIVAL_PLAN_V8.json with at most $4 (default 2) niced processes.
set -u
PY="$1"; HOST="$2"; JOB="$3"; PAR="${4:-2}"
M="$(cd "$(dirname "$0")/.." && pwd)"
N=$("$PY" - <<EOF
import json,sys; sys.path.insert(0,"$M")
from hpc.gmi_k5_bh_task_v8 import contracts,plan
pl,ph,hs,v=contracts("development"); print(len(plan(pl,ph)))
EOF
)
echo "tasks=$N par=$PAR host=$HOST job=$JOB"
seq 0 $((N-1)) | xargs -P "$PAR" -I{} nice -n 10 "$PY" "$M/hpc/gmi_k5_bh_task_v8.py" --task-index {} --tier development --host "$HOST" --job-id "$JOB"
echo "driver-done rc=$?"
