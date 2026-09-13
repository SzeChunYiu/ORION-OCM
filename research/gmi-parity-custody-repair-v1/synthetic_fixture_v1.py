"""Explicitly synthetic complete V5-shaped evidence; no empirical resource measurements."""
from __future__ import annotations
import copy
from frozen_contract_v1 import (EXPECTED, FAMILIES, GRAND, IDS, frozen)
from resource_evidence_v6 import derive_frontier, opcode_contract, reconstruct_boxes


def packet(host="synthetic-control"):
    _, prereg, module = frozen()
    offsets = opcode_contract(module)
    counts = {cid: 8 * len(offsets[cid]) for cid in IDS}
    witnesses = {cid: {"count": counts[cid], "calls": [
        {"opcode_offsets": offsets[cid], "output": y, "returned": True} for y in EXPECTED]}
        for cid in IDS}
    diagnostics = {cid: {"expected_events_per_call": len(offsets[cid]),
        "frames_observed": 8, "events_per_call": [len(offsets[cid])] * 8,
        "total_events": counts[cid], "complete_frames": 8, "empty_frames": 0,
        "all_frames_returned": True} for cid in IDS}
    rows = {cid: [] for cid in IDS}
    for block in range(32):
        order = list(IDS) if (block // 4) % 2 == 0 else list(reversed(IDS))
        r = block % 4
        order = order[r:] + order[:r]
        for cid in IDS:
            duration = counts[cid] * 100 + block
            rows[cid].append({"block_index": block, "order_index": order.index(cid),
                "candidate_id": cid, "checksum": 80000, "wall_block_ns": duration,
                "process_block_ns": duration + 1})
    boxes = reconstruct_boxes(rows, counts)
    return {"schema": "NN_NONNN_POINT_PARITY3_RESULT_V5", "experiment_id": prereg["experiment_id"],
        "preregistration_status_seen": prereg["status"], "environment": module.environment_record(host),
        "environment_gate_pass": True, "environment_gate_failures": [],
        "candidate_identity": module.candidate_identity_record(),
        "capability": {cid: {"candidate_id": cid, "family": FAMILIES[cid],
            "outputs": EXPECTED[:], "expected": EXPECTED[:], "correct": 8, "total": 8,
            "exact_gate_pass": True} for cid in IDS},
        "null_baseline": {"outputs": [0] * 8, "correct": 4, "total": 8},
        "measurement_schedule": prereg["measurement_schedule"],
        "candidate_universe": [{"candidate_id": cid, "family": FAMILIES[cid]} for cid in IDS],
        "claim_ceiling": prereg["claim_ceiling"], "independent_prospective_prediction": False,
        "replication_lineage": prereg["replication_lineage"], "opcode_counts": counts,
        "instrumentation_gate_pass": True,
        "instrumentation": {"status": "COMPLETE_OPCODE_WITNESSES_AND_ORDER_INVARIANCE_GREEN",
            "opcode_counts": counts, "witness_diagnostics": diagnostics,
            "forward_witnesses": copy.deepcopy(witnesses), "reverse_witnesses": copy.deepcopy(witnesses)},
        "protected_timing_measurement_executed": True, "measurements": rows, "resource_boxes": boxes,
        **derive_frontier(boxes), "registered_replication_expectation": prereg["registered_replication_expectation"],
        "protected_resource_measurement_executed": True,
        "resource_uncertainty_semantics": "finite observed block envelope for this registered run on this "
            "recorded envelope; no population-confidence or cross-envelope generalization claim"}
