#!/usr/bin/env bash
# Wrapper for m2p4_resume_check.py. Its ONLY job is to keep transport failure separate
# from the checker's verdict -- the defect recorded as revival-ledger row 65, where a
# poller read empty ssh output as "the array is settled" the moment ssh began failing.
#
#   0  COMPLETE       checker ran, every world complete and verified -> the scorer may run
#   3  INCOMPLETE     checker ran, some world is not ready
#   4  CANNOT_CHECK   checker ran but could not read the tree
#   5  UNREACHABLE    the query itself failed (ssh/auth/network). NOT a verdict about the run.
set -uo pipefail
HOST=${HOST:-lunarc}
B=${B:-/projects/hep/fs12/scratch/scyiu-m2trav}
PY=${PY:-/sw/easybuild_milan/software/Python/3.11.5-GCCcore-13.2.0/bin/python3}
TIMEOUT=${TIMEOUT:-90}
HERE=$(cd "$(dirname "$0")" && pwd)
# ship the checker, then run it; any ssh/scp failure is exit 5 and never a verdict
if ! timeout "$TIMEOUT" scp -q -o BatchMode=yes "$HERE/m2p4_resume_check.py" "$HOST:$B/m2p4_resume_check.py"; then
  echo "UNREACHABLE: could not ship the checker to $HOST (transport failure, NOT a verdict)" >&2
  exit 5
fi
OUT=$(mktemp); ERR=$(mktemp)
timeout "$TIMEOUT" ssh -n -o BatchMode=yes "$HOST" "$PY $B/m2p4_resume_check.py $B/runs" >"$OUT" 2>"$ERR"
RC=$?
if [ "$RC" -eq 124 ] || [ "$RC" -eq 255 ]; then
  echo "UNREACHABLE: ssh rc=$RC (timeout or transport failure, NOT a verdict about the run)" >&2
  head -3 "$ERR" >&2; rm -f "$OUT" "$ERR"; exit 5
fi
# An empty body with rc=0 would be the row-65 defect resurfacing: refuse to call it success.
if [ "$RC" -eq 0 ] && [ ! -s "$OUT" ]; then
  echo "UNREACHABLE: checker exited 0 with EMPTY output -- refusing to read silence as success" >&2
  rm -f "$OUT" "$ERR"; exit 5
fi
cat "$OUT"; head -3 "$ERR" >&2
rm -f "$OUT" "$ERR"
exit "$RC"
