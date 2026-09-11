import copy

import pytest

from map_code_h0_trace_to_gmi_e3 import INPUT_SCHEMA, map_h0_trace
from validate_gmi_e3_episode import validate_episode


def trace_fixture():
    return {
        "schema": INPUT_SCHEMA,
        "TaskIdentity": {
            "task_family_id": "synthetic-h0",
            "task_id": "repair-001",
        },
        "RunIdentity": {
            "run_id": "run-001",
            "arm_id": "BASE_HARNESS_H0",
        },
        "ModelIdentity": {
            "provider": "fixture",
            "model": "fixture-model",
            "checkpoint_or_service_digest": "model-digest",
        },
        "HarnessIdentity": {
            "harness_id": "fixture-harness",
            "factorization_identity": "model+harness+tools",
            "execution_kernel_identity": "plan-edit-test-loop",
            "task_adapter_identity": "fixture-repo-adapter",
        },
        "OCMStateIdentity": {
            "state_digest": "reset-state",
            "update_law_identity": "H0_NO_DEVELOPMENTAL_CLAIM",
        },
        "EnvironmentIdentity": {
            "repository_commit_digest": "repo-commit",
            "environment_image_digest": "image-digest",
            "toolchain_digest": "python-3.x-fixture",
        },
        "VerifierIdentity": {
            "verifier_type": "EXECUTION_TEST_VERIFIED",
            "verifier_identity": "fixture-public+protected-tests",
            "protected_test_digest": "hidden-tests-digest",
            "admissibility_rule": "build and all registered tests pass",
            "verifier_strength_claim": "TEST_SUITE_RELATIVE",
            "known_verifier_limitations": ["fixture only"],
        },
        "TaskContract": {
            "raw_task_digest": "raw-task",
            "semantic_task_digest": "semantic-task",
            "goal_obligations": ["repair registered failure"],
            "constraints": ["no network"],
            "allowed_tools_actions": ["read", "edit", "test"],
            "disallowed_tools_actions": ["read gold patch"],
            "success_contract_id": "all-tests-pass",
            "resource_budget_id": "h0-budget",
            "protected_information_policy": "gold patch hidden",
            "development_protocol_id": "H0_NO_DEVELOPMENTAL_CLAIM",
            "intervention_probe_class_id": "fixture-tool-actions",
        },
        "initial_observations": ["one failing test"],
        "hypotheses_plans": [{"order": 1, "hypothesis": "fault in parser"}],
        "files_inspected": ["parser.py"],
        "commands_tool_calls": ["pytest -q"],
        "patch_candidates": [{"order": 1, "patch_digest": "patch-1"}],
        "checker_test_outcomes": [{"order": 1, "terminal": "PASS"}],
        "failed_attempts": [],
        "accepted_rejected_evidence": [{"kind": "test", "accepted": True}],
        "methods_operators_retrieved": [],
        "methods_operators_consumed": [],
        "new_learned_objects": [],
        "resource_vector": {
            "foundation_model_calls": 1,
            "foundation_model_input_tokens": 100,
            "foundation_model_output_tokens": 50,
            "candidate_generation_count": 1,
            "search_expansions": 1,
            "tool_calls_total": 1,
            "verifier_calls": 1,
            "failed_attempts": 0,
            "cpu_seconds": 1.0,
            "gpu_seconds": 0.0,
            "wall_seconds": 2.0,
            "peak_memory_bytes": 1000000,
            "persistent_bytes_read": 0,
            "persistent_bytes_written": 0,
            "index_or_library_maintenance_work": 0,
            "development_update_work": 0,
            "human_interventions": 0,
            "public_test_runs": 1,
            "protected_test_runs": 1,
            "code_patch_candidates": 1,
            "repository_files_inspected": 1,
        },
        "capability_vector": {
            "build_or_import_success": True,
            "protected_functional_tests_passed": True,
            "regression_invariants_passed": True,
            "registered_requirements_discharged": True,
            "critical_false_completion_free": True,
        },
        "final_terminal": "H0_MECHANICS_PASS",
        "all_required_checks_complete": True,
        "starting_history_digest": "history-before",
        "ending_history_digest": "history-after",
        "ending_state_digest": "state-after",
    }


def test_h0_fixture_maps_to_valid_gmi_episode():
    episode = map_h0_trace(trace_fixture())
    assert episode["episode_identity"]["domain"] == "EXECUTION_VERIFIED_CODE"
    assert episode["morphology_realization"]["rho_resource_semantics_id"] == "GMI_E3_RAW_RESOURCES_V1"
    assert episode["developmental_attribution"]["candidate_capital_level"] == "NONE_CALIBRATION"
    assert episode["developmental_attribution"]["causal_attribution_terminal"] == "NO_DEVELOPMENTAL_CLAIM_CODE_H0"
    assert validate_episode(episode) == []


def test_h0_refuses_k1_claim():
    trace = trace_fixture()
    trace["candidate_capital_level"] = "K1"
    with pytest.raises(ValueError, match="refuses developmental capital claims"):
        map_h0_trace(trace)


def test_h0_requires_protected_verifier_or_external_evaluator():
    trace = trace_fixture()
    del trace["VerifierIdentity"]["protected_test_digest"]
    with pytest.raises(ValueError, match="protected_test_digest or external_evaluator_identity"):
        map_h0_trace(trace)


def test_pass_like_terminal_requires_complete_checks():
    trace = trace_fixture()
    trace["all_required_checks_complete"] = False
    with pytest.raises(ValueError, match="requires all_required_checks_complete"):
        map_h0_trace(trace)


def test_missing_required_source_field_is_rejected():
    trace = trace_fixture()
    del trace["ending_state_digest"]
    with pytest.raises(ValueError, match="missing H0 source fields"):
        map_h0_trace(trace)


def test_extra_resource_fields_are_preserved_as_unmapped_names():
    trace = trace_fixture()
    trace["resource_vector"]["provider_specific_energy_joules"] = 12.0
    episode = map_h0_trace(trace)
    unmapped = episode["resource_vector"]["other_domain_specific_raw_receipts"]["unmapped_source_resource_fields"]
    assert unmapped == ["provider_specific_energy_joules"]
