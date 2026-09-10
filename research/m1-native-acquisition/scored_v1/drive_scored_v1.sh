#!/usr/bin/env bash
set -euo pipefail
PY=/home/billy/.local/share/uv/python/cpython-3.11.14-linux-x86_64-gnu/bin/python3.11
RUN=/home/billy/orion-ocm-m1-run/scored_v1
cd /home/billy/orion-ocm-m1/research/m1-native-acquisition
mkdir -p "$RUN"
cp -f /home/billy/orion-ocm-m1-run/M1_PARTITIONS_V1.json "$RUN/partitions.json"
LADDER=1000,4000,16000,64000,200000
echo "=== host $(hostname) $(uname -sr) py=$($PY --version) git=$(/usr/bin/git -C /home/billy/orion-ocm-m1 rev-parse HEAD)"
echo "=== partitions sha256 $(sha256sum "$RUN/partitions.json" | cut -d\  -f1)"
echo "=== dev start $(date -u +%FT%TZ)"
nice -n 10 "$PY" m1_runner.py --run-dir "$RUN" --phase dev --slots 200000
echo "=== checkpoint $(date -u +%FT%TZ)"
"$PY" m1_runner.py --run-dir "$RUN" --phase checkpoint
for arm in RESET LIBRARY_ONLY CONTINUED CONTINUED_WITH_LEARNING_STATE_REMOVED ORDINARY_ADAPTIVE_PARENT KNOWN_STRUCTURE_ORACLE; do
  echo "=== arm $arm $(date -u +%FT%TZ)"
  nice -n 10 "$PY" m1_runner.py --run-dir "$RUN" --phase restart-and-acquire --arm "$arm" --slots-ladder "$LADDER" --targets 8
done
echo "=== summarize $(date -u +%FT%TZ)"
"$PY" m1_runner.py --run-dir "$RUN" --phase summarize
echo "=== DONE $(date -u +%FT%TZ)"
