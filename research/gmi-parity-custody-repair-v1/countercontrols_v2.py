"""Portable replay of frozen old defects; archived parent, zero measurements."""
from __future__ import annotations
import argparse
import copy
import importlib.util
import json
from pathlib import Path
import sys
import tempfile

import attempt_custody_v1 as custody
from frozen_contract_v1 import (AuditError, GRAND, HERE, canonical, frozen,
    implementation_bindings, require, sha, write_new)
from packet_content_v6 import audit_packet
from synthetic_fixture_v1 import packet


def run_controls():
    manifest, _, module = frozen()
    name = "parity3_cross_envelope_adjudicate_v5.py"
    source = HERE / "raw/HISTORICAL_CROSS_ADJUDICATOR_V5.py"
    require(sha(source.read_bytes()) == manifest["sources"][name], "original adjudicator drift")
    spec = importlib.util.spec_from_file_location("old_cross5", source)
    old = importlib.util.module_from_spec(spec)
    exec(compile(source.read_bytes(), str(source), "exec"), old.__dict__)
    calls = []
    module.run_experiment = lambda label: calls.append(label) or {
        "terminal": "DERIVED_NON_NEURAL_AT_REGISTERED_SCOPE"}
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "first.json"; path.write_bytes(b"FIRST_OUTCOME\n")
        previous = sys.argv
        sys.argv = ["synthetic-cli", "--host-label", "same-envelope", "--out", str(path)]
        try:
            module.main()
        except FileExistsError:
            pass
        else:
            raise AuditError("original late-collision control did not reproduce")
        finally:
            sys.argv = previous
        require(calls == ["same-envelope"] and path.read_bytes() == b"FIRST_OUTCOME\n",
                "original collision witness changed")
    bad = {}
    for host in ("synthetic-a", "synthetic-b"):
        p = packet(host)
        p["environment_gate_pass"] = p["instrumentation_gate_pass"] = False
        p["protected_timing_measurement_executed"] = False
        p["environment"]["harness_sha256"] = "UNBOUND_" + host
        p["environment"]["preregistration_sha256"] = "UNBOUND_" + host
        p["measurements"] = {}; p["resource_boxes"] = {}
        bad[host] = p
    original = old.adjudicate(bad, [])["cross_envelope_stability"]
    require(original == "STABLE_ACROSS_ENVELOPES__DERIVED_NON_NEURAL_AT_REGISTERED_SCOPE",
            "original asserted-terminal countercontrol changed")
    rejected = 0
    for p in bad.values():
        try:
            audit_packet(p)
        except AuditError:
            rejected += 1
    require(rejected == 2, "new evidence audit admitted a demonstrated false certificate")
    require(audit_packet(packet())["status"] == "COMPLETE_STATIC_V5_EVIDENCE_PASS",
            "complete synthetic no-alarm control failed")
    with tempfile.TemporaryDirectory() as tmp:
        identity = custody.canonical_identity("a" * 64, {
            "python_implementation": "CPython", "python_version": "3.12.0"})
        first = custody.reserve(Path(tmp), identity)
        try:
            custody.reserve(Path(tmp), identity)
        except FileExistsError:
            protected = True
        else:
            protected = False
        require(protected, "new reservation admits repeated identity")
    return {"schema": "PARITY3_CUSTODY_SYNTHETIC_COUNTERCONTROLS_V2",
        "source_commit": manifest["source_commit"], "source_sha256": manifest["sources"],
        "historical_v1_receipt_sha256": sha((HERE / "raw/SYNTHETIC_COUNTERCONTROLS_V1.json").read_bytes()),
        "active_countercontrol_sha256": sha(Path(__file__).resolve().read_bytes()),
        "historical_adjudicator_sha256": sha(source.read_bytes()),
        "repair_implementation_sha256": implementation_bindings(),
        "original_existing_output": {"disabled_measurement_function_calls_before_refusal": 1,
                                     "original_file_bytes_preserved": True},
        "original_false_evidence": {"accepted_cross_terminal": original,
            "environment_and_instrument_flags": False, "timing_executed_flag": False,
            "timing_tables_empty": True, "protocol_bindings_unbound": True},
        "repair": {"both_false_packets_rejected": rejected == 2,
                   "complete_synthetic_packet_passed": True, "exclusive_reservation_control": protected},
        "actual_measurement_function_invocations": 0, "empirical_resource_measurements": 0,
        "scope": "Synthetic validator controls only; no observed family-selection result."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    report = run_controls()
    if args.out:
        write_new(args.out, report)
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
