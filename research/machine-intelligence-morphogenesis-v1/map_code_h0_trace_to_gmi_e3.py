"""Map a #208 coding H0 mechanics trace into GMI E3 episode semantics.

H0 is infrastructure/calibration only. This adapter intentionally refuses any
source trace that attempts a K1/K2/K3 developmental claim. A future protected
H1 study should use the common episode schema + validator under its own frozen
causal protocol rather than weaken this adapter.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping


INPUT_SCHEMA = "ocm.g7a.code-h0-trace.v1"
OUTPUT_SCHEMA = "GMIRealCognitionEpisodeV1.instance"
COMMON_RESOURCE_ID = "GMI_E3_RAW_RESOURCES_V1"

REQUIRED_SOURCE = {
    "schema",
    "TaskIdentity",
    "RunIdentity",
    "ModelIdentity",
    "HarnessIdentity",
    "OCMStateIdentity",
    "EnvironmentIdentity",
    "VerifierIdentity",
    "TaskContract",
    "initial_observations",
    "hypotheses_plans",
    "files_inspected",
    "commands_tool_calls",
    "patch_candidates",
    "checker_test_outcomes",
    "failed_attempts",
    "accepted_rejected_evidence",
    "methods_operators_retrieved",
    "methods_operators_consumed",
    "new_learned_objects",
    "resource_vector",
    "capability_vector",
    "final_terminal",
    "all_required_checks_complete",
    "starting_history_digest",
    "ending_history_digest",
    "ending_state_digest",
}


def _digest(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _require_mapping(value: Any, name: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ValueError(f"{name} must be a mapping")
    return value


def _common_resources(source: Mapping[str, Any]) -> dict[str, Any]:
    raw = _require_mapping(source["resource_vector"], "resource_vector")

    # The H0 runner may not be able to meter every coordinate yet. Null is
    # explicitly different from zero in GMI_E3_RAW_RESOURCES_V1.
    return {
        "foundation_model_calls": raw.get("foundation_model_calls"),
        "foundation_model_input_tokens": raw.get("foundation_model_input_tokens"),
        "foundation_model_output_tokens": raw.get("foundation_model_output_tokens"),
        "candidate_generation_count": raw.get("candidate_generation_count"),
        "search_expansions": raw.get("search_expansions"),
        "tool_calls": raw.get("tool_calls_total"),
        "verifier_calls": raw.get("verifier_calls"),
        "failed_attempts": raw.get("failed_attempts", len(source["failed_attempts"])),
        "cpu_time": raw.get("cpu_seconds"),
        "gpu_time": raw.get("gpu_seconds"),
        "wall_time": raw.get("wall_seconds"),
        "peak_memory": raw.get("peak_memory_bytes"),
        "persistent_bytes_read": raw.get("persistent_bytes_read"),
        "persistent_bytes_written": raw.get("persistent_bytes_written"),
        "index_or_library_maintenance_work": raw.get("index_or_library_maintenance_work"),
        "development_update_work": raw.get("development_update_work", 0),
        "human_interventions": raw.get("human_interventions", 0),
        "other_domain_specific_raw_receipts": {
            "shell_or_command_calls": raw.get("shell_or_command_calls", len(source["commands_tool_calls"])),
            "file_or_repository_search_calls": raw.get("file_or_repository_search_calls"),
            "public_test_runs": raw.get("public_test_runs"),
            "protected_test_runs": raw.get("protected_test_runs"),
            "code_patch_candidates": raw.get("code_patch_candidates", len(source["patch_candidates"])),
            "repository_files_inspected": raw.get("repository_files_inspected", len(source["files_inspected"])),
            "unmapped_source_resource_fields": sorted(
                set(raw)
                - {
                    "foundation_model_calls",
                    "foundation_model_input_tokens",
                    "foundation_model_output_tokens",
                    "candidate_generation_count",
                    "search_expansions",
                    "tool_calls_total",
                    "verifier_calls",
                    "failed_attempts",
                    "cpu_seconds",
                    "gpu_seconds",
                    "wall_seconds",
                    "peak_memory_bytes",
                    "persistent_bytes_read",
                    "persistent_bytes_written",
                    "index_or_library_maintenance_work",
                    "development_update_work",
                    "human_interventions",
                    "shell_or_command_calls",
                    "file_or_repository_search_calls",
                    "public_test_runs",
                    "protected_test_runs",
                    "code_patch_candidates",
                    "repository_files_inspected",
                }
            ),
        },
    }


def map_h0_trace(source: Mapping[str, Any]) -> dict[str, Any]:
    missing = REQUIRED_SOURCE - set(source)
    if missing:
        raise ValueError(f"missing H0 source fields: {sorted(missing)}")
    if source.get("schema") != INPUT_SCHEMA:
        raise ValueError(f"expected schema {INPUT_SCHEMA!r}")

    # H0 is mechanics only. Force a separate protected protocol for K1+.
    requested_claim = source.get("candidate_capital_level", "NONE_CALIBRATION")
    if requested_claim not in {None, "NONE_CALIBRATION"}:
        raise ValueError("H0 adapter refuses developmental capital claims")

    task = _require_mapping(source["TaskIdentity"], "TaskIdentity")
    run = _require_mapping(source["RunIdentity"], "RunIdentity")
    model = _require_mapping(source["ModelIdentity"], "ModelIdentity")
    harness = _require_mapping(source["HarnessIdentity"], "HarnessIdentity")
    state = _require_mapping(source["OCMStateIdentity"], "OCMStateIdentity")
    env = _require_mapping(source["EnvironmentIdentity"], "EnvironmentIdentity")
    verifier = _require_mapping(source["VerifierIdentity"], "VerifierIdentity")
    contract = _require_mapping(source["TaskContract"], "TaskContract")
    capability = _require_mapping(source["capability_vector"], "capability_vector")

    if not verifier.get("verifier_identity"):
        raise ValueError("VerifierIdentity.verifier_identity required")
    if not (verifier.get("protected_test_digest") or verifier.get("external_evaluator_identity")):
        raise ValueError("protected_test_digest or external_evaluator_identity required")

    final_terminal = str(source["final_terminal"])
    all_checks = source["all_required_checks_complete"] is True
    pass_like = final_terminal in {
        "EXECUTION_TEST_VERIFIED",
        "FORMAL_SPEC_VERIFIED",
        "H0_MECHANICS_PASS",
    }
    if pass_like and not all_checks:
        raise ValueError("pass-like H0 terminal requires all_required_checks_complete")

    start_config = {
        "model": model,
        "harness": harness,
        "ocm_state": state,
        "environment": env,
        "tool_permissions": contract.get("allowed_tools_actions"),
    }

    episode = {
        "schema": OUTPUT_SCHEMA,
        "episode_identity": {
            "episode_id": f"code-h0:{_digest([task, run])}",
            "domain": "EXECUTION_VERIFIED_CODE",
            "task_family_id": task.get("task_family_id", "CODE_H0_MECHANICS"),
            "task_id": task.get("task_id") or _digest(task),
            "run_id": run.get("run_id") or _digest(run),
            "arm_id": run.get("arm_id") or harness.get("harness_id") or "UNKNOWN_ARM",
            "protocol_version": "GMI_E3_CODE_H0_V1",
        },
        "task_contract": {
            "raw_task_digest": contract.get("raw_task_digest") or _digest(task),
            "semantic_task_digest": contract.get("semantic_task_digest") or _digest(contract.get("goal_obligations")),
            "goal_obligations": contract.get("goal_obligations", []),
            "constraints": contract.get("constraints", []),
            "allowed_tools_actions": contract.get("allowed_tools_actions", []),
            "disallowed_tools_actions": contract.get("disallowed_tools_actions", []),
            "success_contract_id": contract.get("success_contract_id", "H0_MECHANICS_ONLY"),
            "resource_budget_id": contract.get("resource_budget_id", "H0_REGISTERED_BUDGET"),
            "protected_information_policy": contract.get("protected_information_policy", "H0_NO_GOLD_LEAKAGE"),
        },
        "starting_developmental_situation": {
            "machine_configuration_digest": _digest(start_config),
            "registered_history_digest": source["starting_history_digest"],
            "public_ecology_authority_context_digest": _digest([task, env, verifier, contract]),
            "morphology_identity": _digest([model, harness]),
            "development_protocol_id": contract.get("development_protocol_id", "H0_NO_DEVELOPMENTAL_CLAIM"),
            "intervention_probe_class_id": contract.get("intervention_probe_class_id", "H0_TOOL_AND_TEST_ACTIONS"),
        },
        "morphology_realization": {
            "F_factorization_identity": harness.get("factorization_identity", harness.get("harness_id", "CODING_HARNESS")),
            "Theta_mutable_state_digest": state.get("state_digest") or _digest(state),
            "K_execution_kernel_identity": harness.get("execution_kernel_identity", "MODEL_PLUS_CODING_HARNESS"),
            "U_update_law_identity": state.get("update_law_identity", "H0_NO_DEVELOPMENTAL_CLAIM"),
            "Gamma_morphogenesis_identity_or_none": None,
            "kappa_semantic_adapter_identity": harness.get("task_adapter_identity", "CODE_TASK_ADAPTER"),
            "rho_resource_semantics_id": COMMON_RESOURCE_ID,
        },
        "external_verification": {
            "verifier_type": verifier.get("verifier_type", "EXECUTION_TEST_VERIFIED"),
            "verifier_identity": verifier["verifier_identity"],
            "verifier_version_digest": verifier.get("verifier_version_digest") or _digest(verifier),
            "admissibility_rule_digest": verifier.get("admissibility_rule_digest") or _digest(verifier.get("admissibility_rule")),
            "statement_or_spec_correspondence_rule": verifier.get("spec_correspondence_rule", "TASK_SPEC_TO_EXECUTABLE_TEST_CONTRACT"),
            "verifier_strength_claim": verifier.get("verifier_strength_claim", "TEST_SUITE_RELATIVE"),
            "known_verifier_limitations": verifier.get("known_verifier_limitations", []),
        },
        "pre_solution_trace": {
            "proposal_events": source["hypotheses_plans"] + source["patch_candidates"],
            "retrieval_events": source["methods_operators_retrieved"],
            "search_expansions": source["resource_vector"].get("search_expansions"),
            "tool_calls": source["commands_tool_calls"],
            "verification_calls": source["checker_test_outcomes"],
            "failure_events": source["failed_attempts"],
            "retrieved_assets": source["methods_operators_retrieved"],
            "consumed_assets": source["methods_operators_consumed"],
            "pre_solution_geometry_metrics": {
                "status": "H0_INSTRUMENTATION_ONLY__NO_FROZEN_K1_MEDIATOR",
                "ordered_patch_count": len(source["patch_candidates"]),
                "failed_attempt_count": len(source["failed_attempts"]),
            },
        },
        "outcome": {
            "terminal": final_terminal,
            "admissible_result": pass_like and all_checks,
            "capability_vector": dict(capability),
            "partial_certificate_or_none": source.get("partial_certificate_or_none"),
            "semantic_claim_ceiling": "H0 instrumentation/execution calibration only; no K1/K2 claim",
            "all_required_checks_complete": all_checks,
        },
        "resource_vector": _common_resources(source),
        "ending_developmental_situation": {
            "machine_configuration_digest": source["ending_state_digest"],
            "registered_history_digest": source["ending_history_digest"],
            "public_ecology_authority_context_digest": _digest([task, env, verifier, contract]),
            "new_persistent_objects": source["new_learned_objects"],
            "revoked_or_retired_objects": source.get("revoked_or_retired_objects", []),
            "post_task_update_receipts": source.get("post_task_update_receipts", []),
        },
        "developmental_attribution": {
            "solution_was_absent_from_relevant_history": source.get("solution_was_absent_from_relevant_history", False),
            "pre_solution_mediator_observed": False,
            "matched_reset_result_ref": None,
            "strongest_parent_result_ref": None,
            "shuffle_or_cross_history_result_ref_or_na": "NA_H0_MECHANICS",
            "candidate_capital_level": "NONE_CALIBRATION",
            "causal_attribution_terminal": "NO_DEVELOPMENTAL_CLAIM_CODE_H0",
        },
        "source_boundary": {
            "source_schema": INPUT_SCHEMA,
            "source_trace_digest": _digest(source),
            "files_inspected": source["files_inspected"],
            "accepted_rejected_evidence": source["accepted_rejected_evidence"],
        },
    }
    return episode


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("trace", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    source = json.loads(args.trace.read_text(encoding="utf-8"))
    episode = map_h0_trace(source)
    if args.out.exists():
        raise SystemExit("refusing to overwrite existing output")
    args.out.write_text(json.dumps(episode, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(episode["outcome"]["terminal"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
