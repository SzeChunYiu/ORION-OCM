"""Static V5 evidence audit; never execute candidates, traces, or timed blocks."""
from __future__ import annotations
import platform
from frozen_contract_v1 import (AuditError, EXPECTED, FAMILIES, GRAND, HARNESS, IDS,
    INVALID, PARENT, PREREG, Unverifiable, frozen, require, same)
from resource_evidence_v6 import validate_resources

BASE_FIELDS = {"schema", "experiment_id", "preregistration_status_seen", "environment",
    "environment_gate_pass", "environment_gate_failures", "candidate_identity",
    "capability", "null_baseline", "measurement_schedule", "candidate_universe",
    "claim_ceiling", "independent_prospective_prediction", "replication_lineage"}
VALID_FIELDS = {"opcode_counts", "instrumentation_gate_pass", "instrumentation",
    "protected_timing_measurement_executed", "measurements", "resource_boxes",
    "terminal", "frontier_candidate_ids", "frontier_families", "dominated_by",
    "winner_candidate_id", "registered_replication_expectation",
    "protected_resource_measurement_executed", "resource_uncertainty_semantics"}
FAIL_FIELDS = {"terminal", "winner_candidate_id", "protected_resource_measurement_executed",
    "protected_timing_measurement_executed", "instrumentation_gate_pass",
    "instrumentation_gate_failure", "instrumentation_diagnostics"}


def audit_packet(packet, base=GRAND):
    try:
        return _audit(packet, base)
    except (KeyError, TypeError, AttributeError, IndexError) as exc:
        raise AuditError("malformed packet: " + str(exc)) from exc


def _audit(packet, base):
    require(type(packet) is dict, "packet must be an object")
    invalid = packet.get("terminal") == INVALID
    same(sorted(packet), sorted(BASE_FIELDS | (FAIL_FIELDS if invalid else VALID_FIELDS)),
         "packet field set differs")
    manifest, prereg, module = frozen(base)
    env = packet["environment"]
    require(type(env) is dict, "missing environment")
    expected_env = {"host_label", "execution_context", "python_implementation", "python_version",
        "python_version_info", "platform", "machine", "processor", "cpu_count", "slurm",
        "github", "candidate_source_sha256", "candidate_ast_sha256_local", "harness_sha256",
        "preregistration_sha256"}
    same(sorted(env), sorted(expected_env), "environment fields differ")
    require(env["python_implementation"] == "CPython", "registered CPython required")
    if (platform.python_implementation() != "CPython"
            or env["python_version"] != platform.python_version()):
        raise Unverifiable("matching exact CPython version required for static opcode audit")
    same(env["python_version_info"], [int(x) for x in env["python_version"].split(".")],
         "interpreter version metadata differs")
    for key in ("host_label", "execution_context", "platform", "machine"):
        require(type(env[key]) is str and bool(env[key]), "missing envelope field: " + key)
    require(type(env["processor"]) is str and (env["cpu_count"] is None
            or type(env["cpu_count"]) is int and env["cpu_count"] > 0), "bad CPU metadata")
    require(env["execution_context"] in ("GITHUB_ACTIONS", "SLURM_BATCH", "OTHER_CI",
            "INTERACTIVE_OR_LOCAL"), "unknown execution surface")
    require(type(env["slurm"]) is dict and type(env["github"]) is dict, "bad execution metadata")
    same(env["harness_sha256"], manifest["sources"][HARNESS], "unbound harness")
    same(env["preregistration_sha256"], manifest["sources"][PREREG], "unbound registration")
    hashes = {c["candidate_id"]: c["source_sha256"] for c in prereg["candidates"]}
    same(env["candidate_source_sha256"], hashes, "candidate source map differs")
    same(env["candidate_ast_sha256_local"], module.candidate_ast_hashes(), "local AST differs")
    same(packet["candidate_identity"], {
        "local_source_sha256": hashes, "parent_harness": PARENT,
        "parent_harness_available": True, "parent_source_sha256": hashes,
        "byte_identical_to_parent": True,
        "identity_basis": "exact source segment bytes; interpreter-version independent"},
        "candidate identity differs")
    same(packet["schema"], "NN_NONNN_POINT_PARITY3_RESULT_V5", "wrong schema")
    same(packet["experiment_id"], prereg["experiment_id"], "wrong experiment")
    same(packet["preregistration_status_seen"], prereg["status"], "wrong freeze status")
    same(packet["independent_prospective_prediction"], False, "independence overclaim")
    for key in ("measurement_schedule", "claim_ceiling", "replication_lineage"):
        same(packet[key], prereg[key], "registered metadata drift: " + key)
    same(packet["environment_gate_pass"], True, "environment gate missing")
    same(packet["environment_gate_failures"], [], "environment gate failures")
    same(packet["candidate_universe"],
         [{"candidate_id": cid, "family": FAMILIES[cid]} for cid in IDS], "wrong universe")
    same(packet["capability"], {cid: {"candidate_id": cid, "family": FAMILIES[cid],
         "outputs": EXPECTED, "expected": EXPECTED, "correct": 8, "total": 8,
         "exact_gate_pass": True} for cid in IDS}, "complete-domain capability differs")
    same(packet["null_baseline"], {"outputs": [0] * 8, "correct": 4, "total": 8}, "null differs")
    for key in ("instrumentation_gate_pass", "protected_timing_measurement_executed",
                "protected_resource_measurement_executed"):
        same(packet[key], not invalid, "measurement gate differs: " + key)
    if invalid:
        same(packet["winner_candidate_id"], "NONE", "invalid packet claims winner")
        require(type(packet["instrumentation_gate_failure"]) is str
                and bool(packet["instrumentation_gate_failure"]), "missing refusal reason")
        require(type(packet["instrumentation_diagnostics"]) is dict
                and set(packet["instrumentation_diagnostics"]) == set(IDS),
                "incomplete refusal diagnostics")
        return {"status": "REPORTED_INSTRUMENT_REFUSAL", "terminal": INVALID,
                "failure_cause_independently_reconstructed": False, "timing_rerun": False}
    same(packet["registered_replication_expectation"],
         prereg["registered_replication_expectation"], "expectation drift")
    same(packet["resource_uncertainty_semantics"],
         "finite observed block envelope for this registered run on this recorded envelope; "
         "no population-confidence or cross-envelope generalization claim", "scope drift")
    return {"status": "COMPLETE_STATIC_V5_EVIDENCE_PASS", **validate_resources(packet, module),
            "candidate_count": 4, "capability_cases": 32, "complete_traces": 64,
            "timed_blocks": 128, "timed_candidate_calls": 20480000,
            "timing_rerun": False, "custody_independently_authenticated": False}
