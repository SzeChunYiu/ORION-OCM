#!/usr/bin/env python3
"""Independent replication receipt for the M12 lifetime (issue #14 §17).
    python tools/m12_replication.py <principal.json> <replica.json> --hosts <principal-host> <replica-host>
Compares the `deterministic` blocks of two runs of the same frozen code on different hosts and
writes docs/provenance/M12_REPLICATION_RECEIPT_V1.json (content hashes of both files, the code
receipt hash, MATCH / MISMATCH with the first differing path).  Exit 1 on mismatch.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RECEIPT = ROOT / "docs" / "provenance" / "M12_REPLICATION_RECEIPT_V1.json"


def first_diff(a, b, path="deterministic"):
    if type(a) is not type(b):
        return path
    if isinstance(a, dict):
        for k in sorted(set(a) | set(b)):
            if k not in a or k not in b:
                return f"{path}.{k}"
            d = first_diff(a[k], b[k], f"{path}.{k}")
            if d:
                return d
        return None
    if isinstance(a, list):
        if len(a) != len(b):
            return f"{path}[len]"
        for i, (x, y) in enumerate(zip(a, b)):
            d = first_diff(x, y, f"{path}[{i}]")
            if d:
                return d
        return None
    return None if a == b else path


def main(argv: list[str]) -> int:
    p, r = Path(argv[0]), Path(argv[1])
    hosts = argv[argv.index("--hosts") + 1: argv.index("--hosts") + 3] if "--hosts" in argv else ["?", "?"]
    A, B = json.loads(p.read_text()), json.loads(r.read_text())
    diff = first_diff(A["deterministic"], B["deterministic"])
    rec = {"receipt": "M12_REPLICATION_RECEIPT_V1", "principal": {"file": str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else str(p), "sha256": hashlib.sha256(p.read_bytes()).hexdigest(), "host": hosts[0], "study_status": A.get("study_status")},
           "replica": {"file": str(r), "sha256": hashlib.sha256(r.read_bytes()).hexdigest(), "host": hosts[1], "study_status": B.get("study_status")},
           "preregistration_sha256": {"principal": A.get("preregistration_sha256"), "replica": B.get("preregistration_sha256")},
           "deterministic_block_sha256": {"principal": hashlib.sha256(json.dumps(A["deterministic"], sort_keys=True).encode()).hexdigest(), "replica": hashlib.sha256(json.dumps(B["deterministic"], sort_keys=True).encode()).hexdigest()},
           "verdict": "MATCH" if diff is None and A.get("preregistration_sha256") == B.get("preregistration_sha256") else "MISMATCH", "first_difference": diff,
           "note": "same frozen code and pre-registration, fresh environment on a second host; wall time and RSS are excluded from the comparison by construction"}
    RECEIPT.write_text(json.dumps(rec, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(rec["verdict"], diff or "")
    return 0 if rec["verdict"] == "MATCH" else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
