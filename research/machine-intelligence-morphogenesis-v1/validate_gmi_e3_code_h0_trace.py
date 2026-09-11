"""Validate the #208 coding H0 source-trace contract before GMI mapping.

This is intentionally stricter than the raw mapper.  The supported production
path is validate source -> map episode -> validate GMI episode.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping


INPUT_SCHEMA = "ocm.g7a.code-h0-trace.v1"

REQUIRED_TOP = {
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

REQUIRED_SUBFIELDS = {
    "TaskIdentity": {"task_id", "task_family_id"},
    "RunIdentity": {"run_id", "arm_id"},
    "ModelIdentity": {
        "provider_or_runtime",
        "model_or_agent_identity",
        "checkpoint_or_service_digest",
    },
    "HarnessIdentity": {
        "harness_id",
        "factorization_identity",
        "execution_kernel_identity",
        "task_adapter_identity",
    },
    "OCMStateIdentity": {"state_digest", "update_law_identity"},
    "EnvironmentIdentity": {
        "repository_commit_digest",
        "environment_image_digest",
        "toolchain_digest",
    },
    "VerifierIdentity": {
        "verifier_type",
        "verifier_identity",
        "admissibility_rule",
        "verifier_strength_claim",
    },
    "TaskContract": {
        "raw_task_digest",
        "semantic_task_digest",
        "goal_obligations",
        "constraints",
        "allowed_tools_actions",
        "disallowed_tools_actions",
        "success_contract_id",
        "resource_budget_id",
        "protected_information_policy",
        "development_protocol_id",
        "intervention_probe_class_id",
    },
}

REQUIRED_RESOURCES = {
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
}

ALLOWED_H0_TERMINALS = {
    "H0_MECHANICS_PASS",
    "H0_MECHANICS_FAIL",
    "CANNOT_CHECK",
    "ASSAY_DEFECT",
}


def _mapping(value: Any, name: str, errors: list[str]) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        errors.append(f"{name} must be a mapping")
        return {}
    return value


def _nonempty(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, tuple, dict, set)):
        return bool(value)
    return True


def validate_h0_trace(trace: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []

    missing_top = REQUIRED_TOP - set(trace)
    if missing_top:
        errors.append(f"missing H0 source fields: {sorted(missing_top)}")

    if trace.get("schema") != INPUT_SCHEMA:
        errors.append(f"expected schema {INPUT_SCHEMA!r}")

    for group, required in REQUIRED_SUBFIELDS.items():
        mapping = _mapping(trace.get(group), group, errors)
        missing = required - set(mapping)
        if missing:
            errors.append(f"{group} missing identity bindings: {sorted(missing)}")
        for field in required & set(mapping):
            if not _nonempty(mapping[field]):
                errors.append(f"{group}.{field} must be nonempty")

    verifier = _mapping(trace.get("VerifierIdentity"), "VerifierIdentity", errors)
    if not (
        _nonempty(verifier.get("protected_test_digest"))
        or _nonempty(verifier.get("external_evaluator_identity"))
    ):
        errors.append(
            "VerifierIdentity requires protected_test_digest or external_evaluator_identity"
        )

    resources = _mapping(trace.get("resource_vector"), "resource_vector", errors)
    missing_resources = REQUIRED_RESOURCES - set(resources)
    if missing_resources:
        errors.append(f"resource_vector missing required coordinates: {sorted(missing_resources)}")

    # In H0 an unavailable coordinate may be null, but must be explicit.  Counts that
    # are structurally known should not be silently omitted.
    terminal = trace.get("final_terminal")
    if terminal not in ALLOWED_H0_TERMINALS:
        errors.append(f"unexpected H0 terminal {terminal!r}")

    requested_capital = trace.get("candidate_capital_level", "NONE_CALIBRATION")
    if requested_capital not in {None, "NONE_CALIBRATION"}:
        errors.append("H0 source trace may not claim K1/K2/K3")

    pass_like = terminal == "H0_MECHANICS_PASS"
    if pass_like and trace.get("all_required_checks_complete") is not True:
        errors.append("H0_MECHANICS_PASS requires all_required_checks_complete=true")

    # Preserve all ordered trace collections as lists.  An empty list is valid.
    for field in (
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
    ):
        if field in trace and not isinstance(trace[field], list):
            errors.append(f"{field} must be a list preserving event order")

    capability = trace.get("capability_vector")
    if not isinstance(capability, Mapping) or not capability:
        errors.append("capability_vector must be a nonempty mapping")

    for digest_field in (
        "starting_history_digest",
        "ending_history_digest",
        "ending_state_digest",
    ):
        if digest_field in trace and not _nonempty(trace[digest_field]):
            errors.append(f"{digest_field} must be nonempty")

    return errors


def load_and_validate(path: str | Path) -> list[str]:
    with Path(path).open("r", encoding="utf-8") as handle:
        trace = json.load(handle)
    return validate_h0_trace(trace)


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("trace", type=Path)
    args = parser.parse_args()
    errors = load_and_validate(args.trace)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("GMI_E3_CODE_H0_SOURCE_TRACE_GREEN")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
