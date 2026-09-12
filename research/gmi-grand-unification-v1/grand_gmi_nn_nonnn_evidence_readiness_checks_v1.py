#!/usr/bin/env python3
"""Structural checks for the current NN/non-NN empirical evidence readiness audit."""

import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
MANIFEST = HERE / "NN_NONNN_EMPIRICAL_EVIDENCE_READINESS_MANIFEST_V1.json"

ALLOWED = {
    "READY_FORMAL",
    "PARTIAL_REAL_EVIDENCE",
    "SYNTHETIC_ONLY",
    "MISSING_TASK_BOUND_PACKET",
    "BLOCKED_OR_DEFECTIVE",
}
BLOCKING = {
    "PARTIAL_REAL_EVIDENCE",
    "SYNTHETIC_ONLY",
    "MISSING_TASK_BOUND_PACKET",
    "BLOCKED_OR_DEFECTIVE",
}


def main():
    data = json.loads(MANIFEST.read_text())
    fields = data["fields"]
    assert len(fields) == 12
    assert set(fields.values()) <= ALLOWED

    counts = Counter(fields.values())
    assert dict(counts) == data["status_counts"]
    assert counts == Counter({
        "READY_FORMAL": 5,
        "PARTIAL_REAL_EVIDENCE": 2,
        "SYNTHETIC_ONLY": 2,
        "MISSING_TASK_BOUND_PACKET": 2,
        "BLOCKED_OR_DEFECTIVE": 1,
    })

    blockers = set(data["load_bearing_empirical_blockers"])
    assert blockers
    assert blockers <= set(fields)
    assert all(fields[key] in BLOCKING for key in blockers)
    assert data["real_family_winner_claimed"] is False
    assert data["terminal"] == "UNDECIDED_FROM_CURRENT_EVIDENCE"

    # A real derived-family terminal is forbidden while a load-bearing empirical
    # blocker remains unresolved in this audited packet.
    real_verdict_ready = not any(fields[key] in BLOCKING for key in blockers)
    assert real_verdict_ready is False

    receipt = {
        "terminal": "GRAND_GMI_NN_NONNN_EVIDENCE_READINESS_AUDIT_ALL_GREEN",
        "protocol_fields_audited": len(fields),
        "status_counts": dict(counts),
        "load_bearing_empirical_blockers": len(blockers),
        "real_family_verdict_ready": real_verdict_ready,
        "current_family_terminal": data["terminal"],
    }
    print(json.dumps(receipt, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
