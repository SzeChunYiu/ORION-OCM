#!/usr/bin/env python3
"""One exact-interpreter static audit; stdout JSON, exit 0 pass / 1 reject / 2 unknown."""
from __future__ import annotations
from pathlib import Path
import argparse
import json
import platform
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from authority_v1 import HERE, VERSIONS, load_authority, read_packet
from countercontrols_v1 import run_controls
from frozen_contract_v1 import AuditError, Unverifiable, same, sha, strict_json
from packet_audit_v1 import audit_retained


def evaluate(version):
    result = audit_retained(version)
    authority = load_authority()
    packet = read_packet(version)
    result["malformed_controls_rejected"] = run_controls(packet, authority)
    old = strict_json((HERE / "raw/partial" / ("static-v6-" + version + ".json")).read_bytes())
    for key in ("packet", "packet_sha256", "frontier_candidate_ids", "terminal", "opcode_counts"):
        same(result[key], old[key], "historical partial audit disagrees: " + key)
    result["historical_partial_comparison"] = "MATCH_ON_SHARED_RECONSTRUCTED_FIELDS"
    result["auditor_runtime"] = {"implementation": platform.python_implementation(),
        "version": platform.python_version(),
        "binary_sha256": sha(Path(sys.executable).resolve().read_bytes())}
    result["implementation_sha256"] = {
        p.name: sha(p.read_bytes()) for p in sorted(HERE.glob("*.py"))
    }
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--version", required=True, choices=VERSIONS)
    args = parser.parse_args()
    try:
        result, code = evaluate(args.version), 0
    except Unverifiable as exc:
        result, code = {"status": "UNVERIFIABLE", "reason": str(exc)}, 2
    except (AuditError, OSError) as exc:
        result, code = {"status": "REJECTED", "reason": str(exc)}, 1
    print(json.dumps(result, sort_keys=True, indent=2, allow_nan=False))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
