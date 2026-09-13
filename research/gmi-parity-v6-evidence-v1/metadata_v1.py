"""V5 metadata parent adapted to the exact retained V6 valid-packet schema."""
from __future__ import annotations
import platform
from authority_v1 import HARNESS, PREREG
from frozen_contract_v1 import EXPECTED, FAMILIES, IDS, Unverifiable, require, same

BASE_FIELDS = {"schema", "experiment_id", "preregistration_status_seen", "environment",
    "environment_gate_pass", "environment_gate_failures", "candidate_identity",
    "capability", "null_baseline", "measurement_schedule", "candidate_universe",
    "claim_ceiling", "independent_prospective_prediction", "replication_lineage"}
VALID_FIELDS = {"opcode_counts", "instrumentation_gate_pass", "instrumentation",
    "protected_timing_measurement_executed", "measurements", "resource_boxes",
    "terminal", "frontier_candidate_ids", "frontier_families", "dominated_by",
    "winner_candidate_id", "registered_replication_expectation",
    "protected_resource_measurement_executed", "resource_uncertainty_semantics"}
ENV_FIELDS = {"host_label", "execution_context", "python_implementation", "python_version",
    "python_version_info", "platform", "machine", "processor", "cpu_count", "slurm",
    "github", "candidate_source_sha256", "candidate_ast_sha256_local", "harness_sha256",
    "preregistration_sha256"}
CONTEXTS = ("GITHUB_ACTIONS", "SLURM_BATCH", "OTHER_CI", "INTERACTIVE_OR_LOCAL")


def validate_metadata(packet, binding, prereg, module):
    require(type(packet) is dict, "packet must be an object")
    same(sorted(packet), sorted(BASE_FIELDS | VALID_FIELDS), "packet fields differ")
    env = packet["environment"]
    require(type(env) is dict, "environment must be an object")
    same(sorted(env), sorted(ENV_FIELDS), "environment fields differ")
    same(env["python_implementation"], "CPython", "registered CPython required")
    require(type(env["python_version"]) is str, "invalid interpreter version")
    if (platform.python_implementation() != "CPython"
            or env["python_version"] != platform.python_version()):
        raise Unverifiable("matching exact CPython version required for native AST/opcodes")
    same(env["python_version_info"], [int(x) for x in env["python_version"].split(".")],
         "interpreter version metadata differs")
    for key in ("host_label", "execution_context", "platform", "machine"):
        require(type(env[key]) is str and bool(env[key]), "missing envelope field: " + key)
    require(type(env["processor"]) is str and (env["cpu_count"] is None
            or type(env["cpu_count"]) is int and env["cpu_count"] > 0), "bad CPU metadata")
    require(env["execution_context"] in CONTEXTS, "unknown execution context")
    groups = {"slurm": ("job_id", "cluster_name", "node_name", "partition", "cpus_on_node"),
              "github": ("sha", "run_id", "run_attempt", "event_name", "ref",
                         "runner_os", "runner_arch")}
    for group, keys in groups.items():
        require(type(env[group]) is dict, "execution metadata must be an object")
        same(sorted(env[group]), sorted(keys), "execution metadata fields differ")
        require(all(v is None or type(v) is str for v in env[group].values()),
                "execution metadata must be string or null")
    job = env["slurm"]["job_id"]
    context = env["execution_context"]
    require(context != "SLURM_BATCH" or bool(job), "Slurm context lacks a recorded job")
    require(not job or context in ("GITHUB_ACTIONS", "SLURM_BATCH"),
            "recorded Slurm job contradicts execution-context precedence")
    # GITHUB_ACTIONS takes precedence; its other variables may all be absent.
    for field, name in (("harness_sha256", HARNESS), ("preregistration_sha256", PREREG)):
        same(env[field], binding["files"]["raw/frozen/" + name]["sha256"], "source drift")
    hashes = {c["candidate_id"]: c["source_sha256"] for c in prereg["candidates"]}
    same(env["candidate_source_sha256"], hashes, "candidate source differs")
    same(env["candidate_ast_sha256_local"], module.candidate_ast_hashes(), "native AST differs")
    same(packet["candidate_identity"], module.candidate_identity_record(), "source parents differ")
    same(packet["schema"], "NN_NONNN_POINT_PARITY3_RESULT_V6", "wrong schema")
    same(packet["experiment_id"], prereg["experiment_id"], "wrong experiment")
    same(packet["preregistration_status_seen"], prereg["status"], "freeze status differs")
    same(packet["independent_prospective_prediction"], False, "independence overclaim")
    for key in ("measurement_schedule", "claim_ceiling", "replication_lineage",
                "registered_replication_expectation"):
        same(packet[key], prereg[key], "registered metadata drift: " + key)
    for key in ("environment_gate_pass", "instrumentation_gate_pass",
                "protected_timing_measurement_executed", "protected_resource_measurement_executed"):
        same(packet[key], True, "measurement prerequisite false: " + key)
    same(packet["environment_gate_failures"], [], "environment failures")
    same(packet["candidate_universe"],
         [{"candidate_id": cid, "family": FAMILIES[cid]} for cid in IDS], "universe differs")
    same(packet["capability"], {cid: {"candidate_id": cid, "family": FAMILIES[cid],
         "outputs": EXPECTED, "expected": EXPECTED, "correct": 8, "total": 8,
         "exact_gate_pass": True} for cid in IDS}, "capability differs")
    same(packet["null_baseline"], {"outputs": [0] * 8, "correct": 4, "total": 8}, "null differs")
    same(packet["resource_uncertainty_semantics"],
         "finite observed block envelope for this registered run on this recorded envelope; "
         "no population-confidence or cross-envelope generalization claim", "scope drift")
