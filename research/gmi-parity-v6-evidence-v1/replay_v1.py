#!/usr/bin/env python3
"""Portable static subprocess replay; no measurement launcher or candidate invocation."""
from __future__ import annotations
import argparse
import json
import platform
import shutil
import subprocess
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from authority_v1 import HERE, VERSIONS, packet_name, verify_inputs
from frozen_contract_v1 import AuditError, require, same, sha, strict_json

PASS = "COMPLETE_STATIC_V6_MEASURED_EVIDENCE_PASS"


def collect(interpreters, optimized=False):
    binding = verify_inputs()
    require(set(interpreters) <= set(VERSIONS), "unregistered interpreter map key")
    records = {}
    for version in VERSIONS:
        binary = interpreters.get(version)
        executable = shutil.which(str(binary)) if binary else None
        if not executable:
            records[version] = {"status": "UNVERIFIABLE", "reason": "exact interpreter unavailable"}
            continue
        cmd = [executable, "-I", "-B"] + (["-O"] if optimized else [])
        cmd += [str(HERE / "audit_v1.py"), "--version", version]
        try:
            completed = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            record = strict_json(completed.stdout)
            require(type(record) is dict, "worker output must be an object")
            status = record.get("status")
            require((completed.returncode, status) in ((0, PASS), (1, "REJECTED"), (2, "UNVERIFIABLE")),
                    "worker exit/status contradiction")
            if status == PASS:
                same(record.get("python_version"), version, "worker version differs")
                same(record.get("packet"), packet_name(version), "worker packet differs")
                same(record.get("packet_sha256"),
                     binding["files"]["raw/frozen/" + packet_name(version)]["sha256"],
                     "worker packet binding differs")
                expected_runtime = {"implementation": "CPython", "version": version,
                    "binary_sha256": sha(Path(executable).resolve().read_bytes())}
                same(record.get("auditor_runtime"), expected_runtime, "worker runtime differs")
                same(record.get("implementation_sha256"),
                     {p.name: sha(p.read_bytes()) for p in sorted(HERE.glob("*.py"))},
                     "worker implementation differs")
                for key, value in (("complete_recorded_frames", 64), ("recorded_timed_blocks", 128),
                                   ("candidate_calls_executed", 0), ("priming_calls_executed", 0),
                                   ("timing_calls_executed", 0)):
                    same(record.get(key), value, "worker coverage differs: " + key)
                require(type(record.get("malformed_controls_rejected")) is list
                        and len(record["malformed_controls_rejected"]) == 50,
                        "worker countercontrol census incomplete")
        except (OSError, subprocess.TimeoutExpired):
            record = {"status": "UNVERIFIABLE", "reason": "static interpreter worker unavailable"}
        except AuditError as exc:
            record = {"status": "REJECTED", "reason": str(exc)}
        records[version] = record
    statuses = [row["status"] for row in records.values()]
    state = "REJECTED" if "REJECTED" in statuses else (
        "UNVERIFIABLE" if "UNVERIFIABLE" in statuses else "ALL_THREE_STATIC_AUDITS_PASS")
    return {"schema": "GMI_PARITY_V6_FULL_RETAINED_AUDIT_V1", "status": state,
            "registered_packets": 3, "validated_packets": statuses.count(PASS),
            "records": records, "new_candidate_calls": 0, "new_priming_calls": 0,
            "new_timing_calls": 0, "independent_host_replication_authenticated": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--interpreter", action="append", default=[], metavar="VERSION=PATH")
    parser.add_argument("--optimized", action="store_true")
    args = parser.parse_args()
    mapping = {}
    for entry in args.interpreter:
        version, separator, path = entry.partition("=")
        require(separator and path and version not in mapping, "invalid/duplicate interpreter entry")
        mapping[version] = path
    if not mapping and platform.python_version() in VERSIONS:
        mapping[platform.python_version()] = sys.executable
    result = collect(mapping, args.optimized)
    print(json.dumps(result, sort_keys=True, indent=2, allow_nan=False))
    return {"ALL_THREE_STATIC_AUDITS_PASS": 0, "REJECTED": 1, "UNVERIFIABLE": 2}[result["status"]]


if __name__ == "__main__":
    raise SystemExit(main())
