#!/bin/bash
# Snapshot the live cell directory before analysing it.
#
# Cells are rewritten every 4,096 tasks while the array runs, so reading the live
# directory gives rv8_analyse.py and rv8_verify.py DIFFERENT bytes and they disagree for
# that reason alone. Observed on a live read: the verifier reported 81,920 tasks against
# the analysis's 73,728, exactly two 4,096-task dumps apart. Analyse a snapshot.
set -eu
BASE=${1:-/projects/hep/fs12/scratch/scyiu-rv8}
SNAP=$BASE/snap_$(date +%Y%m%dT%H%M%S)
mkdir -p "$SNAP"
cp -r "$BASE/out/cells" "$SNAP/cells"
cp "$BASE/out/RV8_PREFLIGHT.json" "$BASE/out/RV8_REPLICATION.json" "$SNAP/"
cd "$BASE/repo/research/rv8-h1-horizon-v1"
python3 rv8_analyse.py "$SNAP"
python3 rv8_verify.py  "$SNAP"
python3 rv8_report.py  "$SNAP" > "$SNAP/RV8_REPORT.md"
echo "SNAPSHOT=$SNAP"
