#!/usr/bin/env bash
# M1C amortisation-scaling scored run driver v1 -- frozen protocol, laptop billy only.
# Entry gates (all must hold before this driver runs):
#   freeze PR merged; this machinery PR merged; m1b_selftest green on this host;
#   m1c_selftest green (exit 0) on this host.
set -u
PY=/home/billy/.local/share/uv/python/cpython-3.11.14-linux-x86_64-gnu/bin/python3.11
REPO=/home/billy/orion-ocm-m1c
RUN=$REPO/run_scaling_v1
LANE=$REPO/research/m1b-missing-link-attribution-v1/scaling_v1
FP=70d8cad4ce2189eebf878eeaa1dc597cb20dbf68d157712b6983505543ed72bc
cd "$LANE" || exit 20
mkdir -p "$RUN"
cp -f "$REPO/research/m1-native-acquisition/M1_PARTITIONS_V1.json" "$RUN/partitions.json"
SHA=$(sha256sum "$RUN/partitions.json" | cut -d" " -f1)
echo "=== partitions sha256 $SHA"
case "$SHA" in a5b0cbc1*) echo "FROZEN_WORLDS_OK";; *) echo "FROZEN_WORLDS_MISMATCH_ABORT"; exit 21;; esac
echo "=== phase dev (re-executed ONCE, fingerprint + frozen-cost gated) $(date -Is)"
nice -n 10 "$PY" m1c_scaling_runner.py --run-dir "$RUN" --phase dev --slots 200000 || { echo ABORT_DEV; exit 12; }
echo "=== phase checkpoint $(date -Is)"
nice -n 10 "$PY" m1c_scaling_runner.py --run-dir "$RUN" --phase checkpoint || { echo ABORT_CHECKPOINT; exit 13; }
for ARM in RESET STRONG_ADAPTIVE_PARENT APPL_ORACLE KNOWN_STRUCTURE_ORACLE; do
  echo "=== arm $ARM: 512 serves @200000 + obligation slice $(date -Is)"
  nice -n 10 "$PY" m1c_scaling_runner.py --run-dir "$RUN" --phase restart-and-serve \
      --arm "$ARM" --t-max 512 --serve-budget 200000 || { echo "ABORT_ARM_$ARM"; exit 14; }
done
echo "=== phase analyze $(date -Is)"
nice -n 10 "$PY" m1c_scaling_runner.py --run-dir "$RUN" --phase analyze || { echo ABORT_ANALYZE; exit 15; }
echo "=== DONE $(date -Is)"
