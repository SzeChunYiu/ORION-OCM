#!/usr/bin/env bash
#SBATCH -J zoo-gsbatch
#SBATCH -A lu2026-2-51
#SBATCH -p lu48
#SBATCH -t 04:00:00
#SBATCH -c 1
#SBATCH -o logs/gsbatch_%j.out
#SBATCH -e logs/gsbatch_%j.err
# GS-R1h adaptive-batch task router (#221 sec 18).  One job = one task
# spec JSON (written by hpc/submit_gs.py --batch under
# manifests/GS_R1_BATCH_<batch_id>/, ledger entry appended BEFORE this
# submission).  Allocation-only: gs_run.py refuses specs that touch
# frozen keys (eta/insurance/gates/terminal_rules/t3_key/freeze).
#   GS_BATCH_SPEC=path/relative/to/ZOO_ROOT  (required)
#   kind=search -> hpc/gs_run.py     ROOT ARM SEED SPEC
#   kind=sweep  -> hpc/gs_sweep.py   ROOT SHARD N_SHARDS
export ZOO_ROOT="${ZOO_ROOT:-$HOME/zoo221/gs}"
source "${SLURM_SUBMIT_DIR}/hpc/common_env.sh"
set -euo pipefail
cd "$ZOO_ROOT"
: "${GS_BATCH_SPEC:?GS_BATCH_SPEC (path relative to ZOO_ROOT) required}"
read -r KIND A B <<< "$($ZOO_PY - "$GS_BATCH_SPEC" <<'PY'
import json, sys
t = json.load(open(sys.argv[1]))
if t.get("kind", "search") == "search":
    print("search", t["base_arm"], t.get("seed", 0))
else:
    print("sweep", t["shard"], t["n_shards"])
PY
)"
echo "batch task spec=$GS_BATCH_SPEC kind=$KIND a=$A b=$B freeze=${GS_FREEZE_SHA:-unset} stop_ts=${GS_STOP_TS:-unset}"
if [ "$KIND" = "search" ]; then
  $ZOO_PY hpc/gs_run.py "$ZOO_ROOT" "$A" "$B" "$GS_BATCH_SPEC"
else
  $ZOO_PY hpc/gs_sweep.py "$ZOO_ROOT" "$A" "$B"
fi
