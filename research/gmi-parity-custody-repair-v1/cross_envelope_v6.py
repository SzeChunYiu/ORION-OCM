"""Cross-envelope V6: audit full attempt packets, never aggregate asserted terminals."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys

from frozen_contract_v1 import (AuditError, HERE, canonical, require, same, sha, strict_json, write_new)
from attempt_custody_v1 import canonical_identity


def interpreter_id(executable):
    require(Path(executable).is_absolute(), "supply absolute interpreter paths")
    code = ("import hashlib,json,pathlib,platform,sys;"
            "print(json.dumps({'python_implementation':platform.python_implementation(),"
            "'python_version':platform.python_version(),'python_executable_sha256':"
            "hashlib.sha256(pathlib.Path(sys.executable).resolve().read_bytes()).hexdigest()}))")
    proc = subprocess.run([executable, "-I", "-B", "-c", code], capture_output=True, check=False)
    require(proc.returncode == 0, "cannot inspect interpreter")
    return strict_json(proc.stdout)


def collect(paths, interpreters, historical_packets=()):
    # Only metadata and static audits execute in these subprocesses; never the V5 harness main.
    inspected = [(interpreter_id(p), p) for p in interpreters]
    available = {canonical(identity): p for identity, p in inspected}
    results = {}
    for path in paths:
        path = Path(path).resolve()
        raw = (path / "ATTEMPT.json").read_bytes()
        record = strict_json(raw)
        identity = canonical_identity(record["identity"]["machine_identity_sha256"], record["runtime"])
        same(record["identity"], identity, "noncanonical attempt identity")
        key = sha(canonical(identity).encode())
        require(key not in results, "duplicate canonical attempt identity")
        executable = available.get(canonical(record["runtime"]))
        if executable is None:
            results[key] = {"status": "UNVERIFIABLE", "valid": False,
                "reason": "matching version and executable bytes unavailable",
                "attempt_sha256": sha(raw)}
            continue
        proc = subprocess.run([executable, "-B", str(HERE / "audit_custody_v1.py"), str(path)],
                              capture_output=True, check=False)
        try:
            row = strict_json(proc.stdout)
        except AuditError:
            row = {"status": "AUDITOR_PROCESS_FAILURE", "stderr": proc.stderr.decode(errors="replace")}
        if proc.returncode != 0:
            row["valid"] = False
        results[key] = row
    for path in historical_packets:
        path = Path(path).resolve()
        raw = path.read_bytes()
        packet = strict_json(raw)
        env = packet["environment"]
        key = "historical|" + canonical([env["host_label"], env["execution_context"],
                                        env["python_implementation"], env["python_version"]])
        require(key not in results, "duplicate historical envelope")
        match = [p for identity, p in inspected
                 if identity["python_implementation"] == env["python_implementation"]
                 and identity["python_version"] == env["python_version"]]
        if not match:
            results[key] = {"status": "UNVERIFIABLE", "valid": False,
                "reason": "matching exact CPython version unavailable", "packet_sha256": sha(raw)}
            continue
        proc = subprocess.run([match[0], "-B", str(HERE / "audit_imported_v1.py"), str(path)],
                              capture_output=True, check=False)
        try:
            row = strict_json(proc.stdout)
        except AuditError:
            row = {"status": "AUDITOR_PROCESS_FAILURE", "stderr": proc.stderr.decode(errors="replace")}
        if proc.returncode != 0:
            row["valid"] = False
        results[key] = row
    return summarize(results)


def summarize(rows):
    valid = {key: row for key, row in rows.items()
             if row.get("valid") is True and row.get("status") in ("CUSTODY_AND_CONTENT_PASS", "COMMIT_BOUND_CONTENT_PASS")}
    terminals = sorted({row["evidence"]["terminal"] for row in valid.values()})
    if not valid:
        stability = "NO_VALID_ENVELOPE"
    elif len(valid) == 1:
        stability = "SINGLE_ENVELOPE_NO_REPLICATION"
    elif len(terminals) == 1:
        stability = "STABLE_ACROSS_ENVELOPES__" + terminals[0]
    else:
        stability = "UNSTABLE_ACROSS_ENVELOPES"
    return {"schema": "NN_NONNN_POINT_PARITY3_CROSS_AUDIT_V6",
            "attempts_read": len(rows), "per_attempt": rows,
            "valid_attempts": sorted(valid),
            "nonvalid_attempts": sorted(set(rows) - set(valid)),
            "distinct_valid_terminals": terminals,
            "cross_envelope_stability": stability,
            "opcode_counts_per_attempt": {k: v["evidence"]["opcode_counts"] for k, v in valid.items()},
            "replication_obligation_discharged": False,
            "timing_rerun": False, "independent_host_attestation": False,
            "claim_ceiling": "Content- and custody-consistent recorded V5 envelopes only; "
                "no timing rerun, population bound, causal attribution to interpreter, "
                "family-universe result, or independent prospective prediction."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("attempts", nargs="*", type=Path)
    parser.add_argument("--historical-packet", action="append", default=[], type=Path)
    parser.add_argument("--python", action="append", required=True, dest="interpreters")
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    try:
        require(bool(args.attempts or args.historical_packet), "at least one input is required")
        result = collect(args.attempts, args.interpreters, args.historical_packet)
        if args.out:
            write_new(args.out, result)
        print(json.dumps(result, indent=2, sort_keys=True))
    except (AuditError, OSError, KeyError) as exc:
        print("CROSS_AUDIT_REJECTED: " + str(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
