"""Static audit of three exact commit-bound historical V5 packets; no first-attempt upgrade."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys
from frozen_contract_v1 import AuditError, HERE, Unverifiable, require, sha, strict_json
from packet_content_v6 import audit_packet


def audit_imported(path):
    path = Path(path)
    binding = strict_json((HERE / "raw/IMPORTED_V5_PACKET_BINDINGS_V1.json").read_bytes())
    raw = path.read_bytes()
    require(binding["packet_sha256"].get(path.name) == sha(raw), "unbound historical packet")
    packet = strict_json(raw)
    result = audit_packet(packet)
    valid = result["status"] == "COMPLETE_STATIC_V5_EVIDENCE_PASS"
    return {"status": "COMMIT_BOUND_CONTENT_PASS" if valid else result["status"],
            "valid": valid, "evidence": result, "packet_sha256": sha(raw),
            "source_commit": binding["source_commit"], "host_label": packet["environment"]["host_label"],
            "first_attempt_custody_verified": False, "independent_host_attestation": False,
            "timing_rerun": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("packet", type=Path)
    args = parser.parse_args()
    try:
        result = audit_imported(args.packet)
    except Unverifiable as exc:
        print(json.dumps({"status": "UNVERIFIABLE", "reason": str(exc)}))
        return 3
    except (AuditError, OSError) as exc:
        print(json.dumps({"status": "REJECTED_EVIDENCE", "reason": str(exc)}))
        return 1
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
