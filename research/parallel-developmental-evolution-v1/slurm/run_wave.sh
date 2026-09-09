#!/bin/bash
# Wave driver (LUNARC login node): chained submission with EXACT frozen
# denominators.  The denominator is read from the batch file the generate job
# wrote, BEFORE the array is submitted; every step's failure stops the chain.
#
# Crash discipline: a crashed candidate/parent/verify task still writes its row
# (status CRASHED, CANNOT_CHECK) and exits 3, so aggregate dependencies use
# afterany -- the wave always aggregates; incompleteness is detected by row
# count inside the aggregate stage, never by a stalled dependency.
#
# The parent array is submitted ONLY on the first wave of a generation, exactly
# as registered in manifests/BATCH.json (parent_denominator > 0 there); later
# waves of the same generation never re-measure parent entries.
#
# Usage: run_wave.sh RUN_ROOT GEN WAVE SALT QUOTA
set -euo pipefail
RUN_ROOT="$1"; GEN="$2"; WAVE="$3"; SALT="$4"; QUOTA="$5"
SLURM_DIR="$(cd "$(dirname "$0")" && pwd)"
export PDEV217_CAPSULE="${PDEV217_CAPSULE:?PDEV217_CAPSULE must point at the capsule execution dir}"
export PDEV217_OCM="${PDEV217_OCM:?PDEV217_OCM must point at the ocm package parent}"

wait_job () {
  local job="$1" what="$2" tries=0
  while :; do
    tries=$((tries+1))
    local state
    state="$(sacct -j "$job" -X -n -o State | head -1 | tr -d ' ')"
    case "$state" in
      COMPLETED) return 0 ;;
      FAILED|CANCELLED|TIMEOUT|OUT_OF_MEMORY|NODE_FAIL)
        echo "$what job $job ended in $state" >&2; return 1 ;;
    esac
    if [ "$tries" -gt 960 ]; then echo "$what job $job timed out waiting" >&2; return 1; fi
    sleep 15
  done
}

submit () { sbatch --parsable "${@}"; }

json_field () {  # json_field FILE PYTHON_EXPR
  python3 -c "import json,sys; d=json.load(open(sys.argv[1])); print(eval(sys.argv[2]))" "$1" "$2"
}

echo "[run_wave] generate g$GEN w$WAVE quota=$QUOTA"
GEN_JOB=$(submit "$SLURM_DIR/generate_candidates.sbatch" "$RUN_ROOT" "$GEN" "$WAVE" "$SALT" "$QUOTA")
wait_job "$GEN_JOB" "generate" || exit 1
BATCH="$RUN_ROOT/generations/g$GEN/waves/w$WAVE/batch.json"
DENOM=$(json_field "$BATCH" "d['denominator']")
MANIFEST="$RUN_ROOT/manifests/BATCH.json"
REG_PDENOM=$(json_field "$MANIFEST" "d['waves'][-1]['parent_denominator']")
echo "[run_wave] evaluate denominator=$DENOM registered parent denominator=$REG_PDENOM"

EVAL_JOB=$(submit --array="0-$((DENOM-1))" "$SLURM_DIR/evaluate_candidates_array.sbatch" "$RUN_ROOT" "$GEN" "$WAVE")

PAR_JOB=""
if [ "$REG_PDENOM" -gt 0 ]; then
  PAR_JOB=$(submit --array="0-$((REG_PDENOM-1))" "$SLURM_DIR/parent_search_array.sbatch" "$RUN_ROOT" "$GEN")
fi

AGG1_JOB=$(submit --dependency="afterany:$EVAL_JOB" "$SLURM_DIR/aggregate_generation.sbatch" "$RUN_ROOT" "$GEN" "$WAVE" collect)
wait_job "$AGG1_JOB" "aggregate-collect" || exit 1
VBATCH="$RUN_ROOT/generations/g$GEN/waves/w$WAVE/verify_batch.json"
VDENOM=$(json_field "$VBATCH" "d['denominator']")
echo "[run_wave] verify denominator=$VDENOM"

# NOTE: this cluster's Slurm rejects colon-chained (AND) dependency
# expressions ("Job dependency problem"); comma chains are OR semantics and
# would let finalize run before every array row exists.  Correctness is kept
# by polling the arrays to completion here (sacct wait_job, same discipline
# as the collect wait above) and submitting finalize with no dependency.
if [ "$VDENOM" -gt 0 ]; then
  VER_JOB=$(submit --array="0-$((VDENOM-1))" "$SLURM_DIR/verify_candidates_array.sbatch" "$RUN_ROOT" "$GEN" "$WAVE")
fi
if [ -n "$PAR_JOB" ]; then
  wait_job "$PAR_JOB" "parent-array" || exit 1
fi
if [ -n "${VER_JOB:-}" ]; then
  wait_job "$VER_JOB" "verify-array" || exit 1
fi
AGG2_JOB=$(submit "$SLURM_DIR/aggregate_generation.sbatch" "$RUN_ROOT" "$GEN" "$WAVE" finalize)
wait_job "$AGG2_JOB" "aggregate-finalize" || exit 1

python3 - "$RUN_ROOT" "$GEN" "$WAVE" "$DENOM" "$VDENOM" "$REG_PDENOM" "$EVAL_JOB" "${VER_JOB:-}" "${PAR_JOB:-}" "$AGG2_JOB" <<'EOF'
import json, sys, time, pathlib
root, gen, wave, den, vden, pden, ejob, vjob, pjob, ajob = sys.argv[1:11]
row = {"generation": int(gen), "wave": int(wave),
       "evaluate_denominator": int(den), "verify_denominator": int(vden),
       "parent_denominator": int(pden),
       "jobs": {"evaluate": ejob, "verify": vjob, "parent": pjob,
                "aggregate": ajob},
       "submitted_unix": time.time()}
path = pathlib.Path(root) / "manifests" / "submissions.jsonl"
with open(path, "a") as h:
    h.write(json.dumps(row, sort_keys=True) + "\n")
EOF
echo "[run_wave] g$GEN w$WAVE complete"
