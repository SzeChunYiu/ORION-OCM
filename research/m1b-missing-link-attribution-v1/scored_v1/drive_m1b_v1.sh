#!/usr/bin/env bash
# M1B scored run driver v1 -- frozen protocol, laptop billy only.
set -u
PY=/home/billy/.local/share/uv/python/cpython-3.11.14-linux-x86_64-gnu/bin/python3.11
REPO=/home/billy/orion-ocm-m1b2
RUN=$REPO/run_scored_v1
LANE=$REPO/research/m1b-missing-link-attribution-v1
LADDER=1000,4000,16000,64000,200000
DEV_SLOTS=200000
FP=70d8cad4ce2189eebf878eeaa1dc597cb20dbf68d157712b6983505543ed72bc
cd "$LANE" || exit 20
mkdir -p "$RUN"
cp -f "$REPO/research/m1-native-acquisition/M1_PARTITIONS_V1.json" "$RUN/partitions.json"
SHA=$(sha256sum "$RUN/partitions.json" | cut -d" " -f1)
echo "=== partitions sha256 $SHA"
case "$SHA" in a5b0cbc1*) echo "FROZEN_WORLDS_OK";; *) echo "FROZEN_WORLDS_MISMATCH_ABORT"; exit 21;; esac
echo "=== phase dev $(date -Is)"
nice -n 10 "$PY" m1b_runner.py --run-dir "$RUN" --phase dev --slots "$DEV_SLOTS" --expected-dev-fingerprint "$FP" || { echo ABORT_DEV; exit 12; }
echo "=== phase checkpoint $(date -Is)"
nice -n 10 "$PY" m1b_runner.py --run-dir "$RUN" --phase checkpoint || { echo ABORT_CHECKPOINT; exit 13; }
for ARM in RESET CONTINUED STRONG_ADAPTIVE_PARENT APPL_ORACLE RETR_ORACLE INTG_ORACLE APPL_KO RETR_KO INTG_KO KNOWN_STRUCTURE_ORACLE; do
  echo "=== arm $ARM $(date -Is)"
  nice -n 10 "$PY" m1b_runner.py --run-dir "$RUN" --phase restart-and-acquire --arm "$ARM" --slots-ladder "$LADDER" --targets 8 || { echo "ABORT_ARM_$ARM"; exit 14; }
done
echo "=== phase summarize $(date -Is)"
nice -n 10 "$PY" m1b_runner.py --run-dir "$RUN" --phase summarize || { echo ABORT_SUMMARIZE; exit 15; }
echo "=== DONE $(date -Is)"
