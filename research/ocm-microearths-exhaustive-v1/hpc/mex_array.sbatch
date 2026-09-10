#!/usr/bin/env bash
#SBATCH -J mex-ebf0x
#SBATCH -A lu2026-2-51
#SBATCH -p lu48
#SBATCH -t 04:00:00
#SBATCH -c 1
#SBATCH -o logs/mex_%A_%a.out
#SBATCH -e logs/mex_%A_%a.err
set -euo pipefail

MANIFEST="${1:?manifest path required}"
LANE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$LANE"
mkdir -p logs results

read -r N SHARD NSHARDS MODE TICKS <<< "$(python3 - "$MANIFEST" "$SLURM_ARRAY_TASK_ID" <<'PY'
import json, sys
m = json.load(open(sys.argv[1]))
t = m["tasks"][int(sys.argv[2])]
print(t["n"], t["shard"], t["nshards"], t["mode"], t["ticks"])
PY
)"

OUT="results/MEX_n${N}_s${SHARD}of${NSHARDS}_${MODE}.json"

# Idempotent resume: a completed shard is never recomputed.
if [ -f "${OUT%.json}.status" ] && grep -q '^ok' "${OUT%.json}.status"; then
  echo "already ok: $OUT"; exit 0
fi

echo "task=$SLURM_ARRAY_TASK_ID n=$N shard=$SHARD/$NSHARDS mode=$MODE ticks=$TICKS"
srun python3 run_shard.py --n "$N" --shard "$SHARD" --nshards "$NSHARDS" \
     --mode "$MODE" --ticks "$TICKS" --out "$OUT"
echo "done $OUT"
