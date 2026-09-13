"""Read-only first-attempt custody and evidence audit; suitable for a matching interpreter."""
from __future__ import annotations
import argparse
import json
import re
from pathlib import Path
import sys

from frozen_contract_v1 import (AuditError, HERE, Unverifiable, canonical, frozen,
    implementation_bindings, require, runtime_identity, same, sha, strict_json)
from packet_content_v6 import audit_packet
from attempt_custody_v1 import canonical_identity


def audit_attempt(path):
    path = Path(path)
    try:
        return _audit_attempt(path)
    except (KeyError, TypeError, AttributeError, IndexError) as exc:
        raise AuditError("malformed custody: " + str(exc)) from exc


def _audit_attempt(path):
    require((path / "ATTEMPT.json").is_file(), "missing attempt reservation record")
    raw_attempt = (path / "ATTEMPT.json").read_bytes()
    record = strict_json(raw_attempt)
    same(record["schema"], "PARITY3_FIRST_ATTEMPT_CUSTODY_V1", "wrong custody version")
    require(path.name == sha(canonical(record["identity"]).encode()), "noncanonical attempt key")
    same(record["implementation"], implementation_bindings(), "custody implementation changed")
    runtime = runtime_identity()
    if record["runtime"] != runtime:
        raise Unverifiable("matching exact interpreter version and executable bytes required")
    identity = record["identity"]
    same([identity["experiment"], identity["python_implementation"], identity["python_version"]],
         ["NN_NONNN_POINT_PARITY3_V5_PORTABLE_REPLICATION", runtime["python_implementation"],
          runtime["python_version"]], "canonical identity metadata differs")
    require(type(identity["machine_identity_sha256"]) is str
            and re.fullmatch(r"[0-9a-f]{64}", identity["machine_identity_sha256"]) is not None,
            "bad canonical machine identity")
    same(identity, canonical_identity(identity["machine_identity_sha256"], runtime),
         "identity must equal the exact canonical projection")
    bindings = {"ATTEMPT.json": sha(raw_attempt)}
    if not (path / "RESULT.json").is_file():
        return {"status": "INCOMPLETE_RESERVED_ATTEMPT", "valid": False,
                "identity": identity, "files": bindings, "timing_rerun": False}
    raw_result = (path / "RESULT.json").read_bytes()
    result = strict_json(raw_result)
    bindings["RESULT.json"] = sha(raw_result)
    same(result["schema"], "PARITY3_ATTEMPT_RESULT_V1", "wrong result version")
    same(result["attempt_sha256"], sha(raw_attempt), "attempt binding differs")
    allowed = {"packet.json", "stdout.json", "stderr.txt"}
    actual = {name: sha((path / name).read_bytes()) for name in allowed
              if (path / name).is_file()}
    same(result["files"], actual, "missing, extra, or changed process output")
    bindings.update(actual)
    if result["state"] == "LAUNCH_OR_CUSTODY_FAILED":
        require(type(result.get("error")) is str, "missing launch failure")
        return {"status": "RETAINED_LAUNCH_FAILURE", "valid": False, "identity": identity,
                "files": bindings, "error": result["error"], "timing_rerun": False}
    same(result["state"], "PROCESS_EXITED", "unknown attempt state")
    require(type(result["returncode"]) is int, "invalid process return code")
    if result["returncode"] not in (0, 2) or set(actual) != allowed:
        return {"status": "RETAINED_PROCESS_FAILURE", "valid": False, "identity": identity,
                "files": bindings, "returncode": result["returncode"], "timing_rerun": False}
    manifest, _, _ = frozen(path / "sources")
    same(record["sources"], {name: manifest["sources"][name] for name in record["sources"]},
         "reservation source binding differs")
    require(set(record["sources"]) == set(p.name for p in (path / "sources").iterdir()),
            "source snapshot inventory differs")
    same(record["source_commit"], manifest["source_commit"], "wrong frozen commit")
    raw_packet = (path / "packet.json").read_bytes()
    require((path / "stdout.json").read_bytes() == raw_packet, "stdout/packet byte mismatch")
    packet = strict_json(raw_packet)
    same(packet["environment"]["host_label"], record["host_label"], "host label drift")
    evidence = audit_packet(packet, path / "sources")
    valid = evidence["status"] == "COMPLETE_STATIC_V5_EVIDENCE_PASS"
    same(result["returncode"], 0 if valid else 2, "exit code/evidence disagreement")
    return {"status": "CUSTODY_AND_CONTENT_PASS" if valid else evidence["status"],
            "valid": valid, "identity": identity, "host_label": record["host_label"],
            "files": bindings, "evidence": evidence, "timing_rerun": False,
            "independent_host_attestation": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("attempt", type=Path)
    args = parser.parse_args()
    try:
        result = audit_attempt(args.attempt)
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
