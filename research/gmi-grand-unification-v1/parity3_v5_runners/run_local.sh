#!/usr/bin/env bash
# Run the frozen parity-3 V5 replication on a local machine (for example the
# laptop registered as "billy", or the machine registered as "old").
#
#   ./run_local.sh <host-label> [python-executable]
#
# The host label is recorded in the packet and is how the envelope is named in
# the cross-envelope adjudication. Use the registered names: laptop-billy, old.
#
# One packet per envelope. The harness refuses to overwrite an existing packet,
# so a second attempt on the same envelope fails loudly instead of replacing
# the first outcome. Keep invalid packets: an instrument refusal is evidence.
set -euo pipefail

HOST_LABEL="${1:?usage: run_local.sh <host-label> [python-executable]}"
PYTHON="${2:-python3}"

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HARNESS="$HERE/../nn_nonnn_point_parity3_experiment_v5.py"

VERSION="$("$PYTHON" -c 'import sys;print("%d.%d.%d"%sys.version_info[:3])')"
IMPL="$("$PYTHON" -c 'import platform;print(platform.python_implementation())')"
OUT="$HERE/../NN_NONNN_POINT_PARITY3_RESULT_V5_${HOST_LABEL}_${IMPL}${VERSION}.json"

echo "host label      : $HOST_LABEL"
echo "interpreter     : $IMPL $VERSION ($PYTHON)"
echo "packet          : $OUT"
echo

# Validate the instrument on this interpreter before spending any timing.
"$PYTHON" -I -B "$HARNESS" --self-test > /dev/null
echo "instrument self-test: green"

# Nothing else should be competing for the CPU during the timed blocks.
"$PYTHON" -I -B "$HARNESS" --host-label "$HOST_LABEL" --out "$OUT" > /dev/null
status=$?

"$PYTHON" - "$OUT" <<'PY'
import json, sys
packet = json.load(open(sys.argv[1]))
print("terminal        :", packet["terminal"])
print("timing executed :", packet.get("protected_timing_measurement_executed"))
if packet["terminal"] != "INVALID_RECEIPT_OR_PROTOCOL_VIOLATION":
    print("frontier        :", packet["frontier_candidate_ids"])
    print("families        :", packet["frontier_families"])
    print("opcode counts   :", packet["opcode_counts"])
else:
    print("environment gate:", packet.get("environment_gate_failures"))
    print("instrument gate :", packet.get("instrumentation_gate_failure"))
PY

echo
echo "Commit the packet, then adjudicate it together with the other envelopes:"
echo "  python3 parity3_cross_envelope_adjudicate_v5.py NN_NONNN_POINT_PARITY3_RESULT_V5_*.json"
exit $status
