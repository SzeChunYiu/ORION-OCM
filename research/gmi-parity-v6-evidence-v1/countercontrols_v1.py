"""Adverse copies of actual retained packets; never synthesize timing observations."""
from __future__ import annotations
import copy
from frozen_contract_v1 import AuditError, IDS, require
from packet_audit_v1 import audit_content

C = IDS[0]
F = ("instrumentation", "forward_witnesses", C, "calls", 0)
R = ("instrumentation", "reverse_witnesses", IDS[1], "calls", 0)
P = ("instrumentation", "priming_witness_diagnostics", C)
M = ("measurements", C, 0)
MUTATIONS = {
    "wrong_raw_output": (F + ("output",), 1),
    "false_return": (R + ("returned",), False),
    "integer_return": (R + ("returned",), 1),
    "absent_opcode_events": (F + ("opcode_offsets",), []),
    "false_trace_count": (("instrumentation", "forward_witnesses", C, "count"), 0),
    "false_complete_frame_count": (("instrumentation", "witness_diagnostics", C, "complete_frames"), 7),
    "schedule_change": (("measurement_schedule", "timed_blocks"), 31),
    "block_index_change": (M + ("block_index",), 1),
    "block_order_change": (M + ("order_index",), 3),
    "block_candidate_change": (M + ("candidate_id",), IDS[1]),
    "block_checksum_change": (M + ("checksum",), 0),
    "negative_wall_cost": (M + ("wall_block_ns",), -1),
    "boolean_process_cost": (M + ("process_block_ns",), True),
    "false_opcode_count": (("opcode_counts", C), 1),
    "false_cost_box": (("resource_boxes", C, "wall_block_ns"), [1, 2]),
    "false_frontier": (("frontier_candidate_ids",), [C]),
    "false_family": (("frontier_families",), ["NEURAL"]),
    "false_dominator": (("dominated_by", C), []),
    "false_terminal": (("terminal",), "DERIVED_NEURAL_AT_REGISTERED_SCOPE"),
    "false_winner": (("winner_candidate_id",), C),
    "false_harness": (("environment", "harness_sha256"), "0" * 64),
    "false_registration": (("environment", "preregistration_sha256"), "0" * 64),
    "false_candidate_source": (("environment", "candidate_source_sha256", C), "0" * 64),
    "false_candidate_ast": (("environment", "candidate_ast_sha256_local", C), "0" * 64),
    "false_parent_identity": (("candidate_identity", "byte_identical_to_parent"), False),
    "false_capability_gate": (("capability", C, "exact_gate_pass"), False),
    "false_capability_output": (("capability", C, "outputs", 0), 1),
    "false_null": (("null_baseline", "correct"), 8),
    "false_environment_gate": (("environment_gate_pass",), False),
    "false_instrument_gate": (("instrumentation_gate_pass",), False),
    "false_resource_gate": (("protected_resource_measurement_executed",), False),
    "false_timing_gate": (("protected_timing_measurement_executed",), False),
    "boolean_gate_as_integer": (("instrumentation_gate_pass",), 1),
    "ignored_environment_failure": (("environment_gate_failures",), ["failed"]),
    "prospective_overclaim": (("independent_prospective_prediction",), True),
    "wrong_schema": (("schema",), "NN_NONNN_POINT_PARITY3_RESULT_V5"),
    "wrong_version_tuple": (("environment", "python_version_info"), [3, 0, 0]),
    "boolean_cpu_count": (("environment", "cpu_count"), True),
    "slurm_label_without_job": (("environment", "execution_context"), "SLURM_BATCH"),
    "slurm_job_with_local_label": (("environment", "slurm", "job_id"), "123"),
    "bad_github_metadata": (("environment", "github", "run_attempt"), 1),
    "priming_false_sum": (P + ("total_events",), 1),
    "priming_false_complete_count": (P + ("complete_frames",), 0),
    "priming_missing_return_claim": (P + ("all_frames_returned",), False),
    "unregistered_scope": (("resource_uncertainty_semantics",), "population guarantee"),
}


def run_controls(packet, authority):
    rejected = []
    for name, (path, value) in MUTATIONS.items():
        bad = copy.deepcopy(packet)
        target = bad
        for key in path[:-1]:
            target = target[key]
        target[path[-1]] = value
        try:
            audit_content(bad, authority)
        except AuditError:
            rejected.append(name)
        else:
            raise AuditError("missed malformed control: " + name)
    for name in ("missing_block", "missing_raw_return", "extra_packet_field",
                 "priming_flag_contradiction", "reordered_opcode_events"):
        bad = copy.deepcopy(packet)
        if name == "missing_block":
            bad["measurements"][C].pop()
        elif name == "missing_raw_return":
            del bad["instrumentation"]["forward_witnesses"][C]["calls"][0]["returned"]
        elif name == "extra_packet_field":
            bad["unregistered_authority"] = True
        elif name == "priming_flag_contradiction":
            key = "priming_was_required_on_this_interpreter"
            bad["instrumentation"][key] = not bad["instrumentation"][key]
        else:
            events = bad["instrumentation"]["forward_witnesses"][C]["calls"][0]["opcode_offsets"]
            events.reverse()
        try:
            audit_content(bad, authority)
        except AuditError:
            rejected.append(name)
        else:
            raise AuditError("missed malformed control: " + name)
    require(len(rejected) == len(MUTATIONS) + 5, "incomplete malformed census")
    return rejected
