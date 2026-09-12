#!/usr/bin/env bash
# RV-377-140 -- the twelve fresh-ecology B1 units of the class-rate law, run ONLY on laptop billy.
#
#   usage: classrate_units.sh <HOST> <ECOLOGIES_CSV> [SEEDS_CSV] [EVALS] [TAG]
#
# ONE WORKER PER INVOCATION. Each worker walks the unit list and claims a unit by atomically creating
# logs/claim_<TAG>_<eco>_S<seed>/ (mkdir); a unit whose claim exists or whose receipt already exists is skipped. So the
# number of concurrent units is the number of workers started, and a second worker can be added later without touching
# the first (the host budget here is TWO processes total, shared with the scoring passes).
#
# Same invocation form as the manifest's U-B units (gmi_microscope.b1 <seed> <evals> <ecology> <log> <TAG>), the TAG
# carrying the host token so no two machines can ever write the same receipt (a receipt collision has already destroyed
# two committed receipts in this programme). Every unit runs under nice -n 10 and appends one JSON line to
# logs/classrate_units_<host>.jsonl; the worker prints WORKER_DONE when nothing is left to claim.
set -u
HOST=${1:?host}; ECOS=${2:?ecologies csv}; SEEDS=${3:-0,1,2}; EVALS=${4:-20000}; TAG=${5:-V43_CLASSRATE}
cd "$(dirname "$0")/.." || exit 1
export PATH=$HOME/.local/share/uv/python/cpython-3.11-linux-x86_64-gnu/bin:$PATH
python3 --version || exit 1
mkdir -p logs
OUT=logs/classrate_units_${HOST}.jsonl
for eco in ${ECOS//,/ }; do for seed in ${SEEDS//,/ }; do
  rec=microscopes/results/STAGE_B1_${TAG}_${HOST}_${eco}_S${seed}.json
  [ -f "$rec" ] && continue
  mkdir "logs/claim_${TAG}_${eco}_S${seed}" 2>/dev/null || continue
  log=logs/classrate_${eco}_s${seed}_${HOST}.log
  t0=$(date +%s)
  nice -n 10 python3 -u -m gmi_microscope.b1 "$seed" "$EVALS" "$eco" "logs/b1_${eco}_s${seed}_${HOST}.log" "${TAG}_${HOST}" > "$log" 2>&1
  rc=$?
  ok=false; [ $rc -eq 0 ] && [ -f "$rec" ] && ok=true
  echo "{\"unit\": \"${eco}_S${seed}\", \"rc\": $rc, \"ok\": $ok, \"receipt\": \"$rec\", \"seconds\": $(( $(date +%s) - t0 )), \"at\": \"$(date -u +%FT%TZ)\"}" >> "$OUT"
done; done
echo "WORKER_DONE $HOST $(date -u +%FT%TZ)" | tee -a "$OUT"
