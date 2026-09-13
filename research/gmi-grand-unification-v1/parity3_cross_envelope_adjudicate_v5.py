#!/usr/bin/env python3
"""Adjudicate portable parity-3 packets across host and interpreter envelopes.

Replication is a question about agreement between envelopes, which no single
packet can answer. This tool reads frozen V5 and V6 packets, refuses to combine
packets whose candidates are not byte-identical, reports each envelope's own
terminal, and reports whether the terminals agree.

Family support and the within-family frontier are reported separately, because
the exact opcode coordinate and the observed timing envelope do not have the
same stability. It never averages a resource envelope across envelopes and
never upgrades a per-envelope terminal into a substrate-level claim.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

# V5 and V6 packets are comparable because the adjudicator proves their
# candidates byte-identical before comparing anything. V6 differs from V5 only
# by a discarded priming trace in the instrument.
SUPPORTED_SCHEMAS = ("NN_NONNN_POINT_PARITY3_RESULT_V5",
                     "NN_NONNN_POINT_PARITY3_RESULT_V6")
VALID_TERMINALS = (
    "DERIVED_NON_NEURAL_AT_REGISTERED_SCOPE",
    "DERIVED_NEURAL_AT_REGISTERED_SCOPE",
    "UNDECIDED_FROM_CURRENT_EVIDENCE",
)
INVALID_TERMINAL = "INVALID_RECEIPT_OR_PROTOCOL_VIOLATION"


class AdjudicationError(ValueError):
    """The registered packets cannot be compared as they stand."""


def require(condition, message):
    if not condition:
        raise AdjudicationError(message)


def load_packet(path: Path) -> dict:
    require(path.is_file(), f"missing packet: {path}")
    try:
        packet = json.loads(path.read_text(encoding="utf-8"))
    except ValueError as exc:
        raise AdjudicationError(f"{path.name}: invalid JSON: {exc}") from exc
    require(type(packet) is dict, f"{path.name}: expected a JSON object")
    require(packet.get("schema") in SUPPORTED_SCHEMAS,
            f"{path.name}: not a supported parity-3 result packet")
    require(type(packet.get("environment")) is dict, f"{path.name}: missing environment")
    require(type(packet.get("candidate_identity")) is dict, f"{path.name}: missing identity")
    terminal = packet.get("terminal")
    require(terminal in VALID_TERMINALS + (INVALID_TERMINAL,),
            f"{path.name}: unknown terminal {terminal!r}")
    return packet


def envelope_label(packet: dict) -> str:
    env = packet["environment"]
    instrument = packet["schema"].rsplit("_", 1)[-1]
    return (f"{env['host_label']}|{env['python_implementation']}"
            f"{env['python_version']}|{env['execution_context']}|{instrument}")


def check_identity(packets: dict) -> dict:
    """Every compared packet must carry the same byte-identical candidates."""
    hashes = {}
    for label, packet in packets.items():
        identity = packet["candidate_identity"]
        require(identity.get("byte_identical_to_parent") is True,
                f"{label}: candidates are not byte-identical to their parent harness")
        hashes[label] = identity["local_source_sha256"]
    reference_label, reference = next(iter(hashes.items()))
    for label, value in hashes.items():
        require(value == reference,
                f"{label}: candidate source hashes differ from {reference_label}")
    return {
        "candidate_source_sha256": reference,
        "all_packets_byte_identical": True,
        "identity_basis": "exact source segment bytes; interpreter-version independent",
    }


def adjudicate(packets: dict, outstanding: list[str]) -> dict:
    identity = check_identity(packets)
    per_envelope = {}
    for label, packet in sorted(packets.items()):
        env = packet["environment"]
        row = {
            "host_label": env["host_label"],
            "instrument_schema": packet["schema"],
            "execution_context": env["execution_context"],
            "python_version": env["python_version"],
            "platform": env["platform"],
            "processor": env["processor"] or None,
            "cpu_count": env["cpu_count"],
            "terminal": packet["terminal"],
            "timing_executed": bool(packet.get("protected_timing_measurement_executed")),
            "instrumentation_gate_pass": packet.get("instrumentation_gate_pass"),
        }
        if packet["terminal"] == INVALID_TERMINAL:
            row["gate_failures"] = {
                "environment": packet.get("environment_gate_failures") or [],
                "instrumentation": packet.get("instrumentation_gate_failure"),
            }
        else:
            row.update({
                "frontier_candidate_ids": packet["frontier_candidate_ids"],
                "frontier_families": packet["frontier_families"],
                "opcode_counts": packet["opcode_counts"],
                "priming_was_required": packet.get("instrumentation", {}).get(
                    "priming_was_required_on_this_interpreter"),
            })
        per_envelope[label] = row

    valid = {label: row for label, row in per_envelope.items()
             if row["terminal"] in VALID_TERMINALS}
    invalid = {label: row for label, row in per_envelope.items()
               if row["terminal"] == INVALID_TERMINAL}
    terminals = sorted({row["terminal"] for row in valid.values()})
    family_supports = sorted({tuple(row["frontier_families"]) for row in valid.values()})
    frontier_sets = sorted({tuple(sorted(row["frontier_candidate_ids"]))
                            for row in valid.values()})

    if not valid:
        stability = "NO_VALID_ENVELOPE"
    elif len(valid) == 1:
        stability = "SINGLE_ENVELOPE_NO_REPLICATION"
    elif len(terminals) == 1:
        stability = f"STABLE_ACROSS_ENVELOPES__{terminals[0]}"
    else:
        stability = "UNSTABLE_ACROSS_ENVELOPES"

    # Exact opcode counts are interpreter-dependent, so record them per
    # envelope rather than asserting one registered value.
    opcode_table = {label: row["opcode_counts"] for label, row in valid.items()}
    opcode_orderings = {
        label: [cid for cid, _ in sorted(counts.items(), key=lambda kv: (kv[1], kv[0]))]
        for label, counts in opcode_table.items()
    }
    distinct_orderings = sorted({tuple(order) for order in opcode_orderings.values()})

    return {
        "schema": "NN_NONNN_POINT_PARITY3_CROSS_ENVELOPE_V5",
        "packets_read": len(packets),
        "instrument_schemas_compared": sorted({p["schema"] for p in packets.values()}),
        "candidate_identity": identity,
        "per_envelope": per_envelope,
        "valid_envelopes": sorted(valid),
        "invalid_envelopes": sorted(invalid),
        "distinct_valid_terminals": terminals,
        "opcode_counts_per_envelope": opcode_table,
        "opcode_ordering_per_envelope": opcode_orderings,
        "distinct_opcode_orderings": [list(order) for order in distinct_orderings],
        "opcode_counts_are_interpreter_dependent": len({
            tuple(sorted(counts.items())) for counts in opcode_table.values()
        }) > 1 if len(opcode_table) > 1 else None,
        "distinct_family_supports": [list(x) for x in family_supports],
        "family_support_stable": len(family_supports) == 1 if valid else None,
        "distinct_frontier_candidate_sets": [list(x) for x in frontier_sets],
        "within_family_frontier_stable": len(frontier_sets) == 1 if valid else None,
        "cross_envelope_stability": stability,
        "named_outstanding_hosts": sorted(outstanding),
        "replication_obligation_discharged": False,
        "aggregation_policy": (
            "Per-envelope terminals only. Resource envelopes are never pooled or averaged across "
            "envelopes, and no per-envelope terminal is upgraded into a substrate-level claim. "
            "Family support and the within-family frontier are reported separately, because the "
            "exact opcode coordinate and the observed timing envelope do not have the same "
            "stability: an observed window is not a bound."
        ),
        "claim_ceiling": (
            "Agreement or disagreement between the recorded envelopes on four frozen candidates "
            "for parity-3. Not a universal family verdict, not a claim about unrecorded hosts, "
            "and not independent prospective replication."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("packets", nargs="+", type=Path)
    parser.add_argument("--outstanding", nargs="*", default=["laptop-billy", "old", "lunarc"],
                        help="named hosts whose packets are still missing")
    parser.add_argument("--out")
    args = parser.parse_args()

    try:
        loaded = {}
        for path in args.packets:
            packet = load_packet(path)
            label = envelope_label(packet)
            require(label not in loaded, f"duplicate envelope label: {label}")
            loaded[label] = packet
        result = adjudicate(loaded, list(args.outstanding))
    except AdjudicationError as exc:
        print(f"PARITY3_CROSS_ENVELOPE_ADJUDICATION_FAILED: {exc}", file=sys.stderr)
        return 1

    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.out:
        with Path(args.out).open("x") as stream:
            stream.write(text)
    print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
