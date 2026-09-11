import copy

from export_gmi_e3_code_h0_episode import export_episode
from test_map_code_h0_trace_to_gmi_e3 import trace_fixture
from validate_gmi_e3_code_h0_trace import validate_h0_trace
from validate_gmi_e3_episode import validate_episode


def test_frozen_h0_fixture_is_source_green():
    assert validate_h0_trace(trace_fixture()) == []


def test_official_export_path_validates_both_sides():
    episode = export_episode(trace_fixture())
    assert validate_episode(episode) == []
    assert episode["developmental_attribution"]["candidate_capital_level"] == "NONE_CALIBRATION"
    assert episode["developmental_attribution"]["pre_solution_mediator_observed"] is False


def test_missing_bound_model_identity_is_rejected_before_mapping():
    trace = copy.deepcopy(trace_fixture())
    del trace["ModelIdentity"]["checkpoint_or_service_digest"]
    errors = validate_h0_trace(trace)
    assert any("ModelIdentity missing identity bindings" in error for error in errors)


def test_missing_environment_commit_is_rejected():
    trace = copy.deepcopy(trace_fixture())
    del trace["EnvironmentIdentity"]["repository_commit_digest"]
    errors = validate_h0_trace(trace)
    assert any("EnvironmentIdentity missing identity bindings" in error for error in errors)


def test_public_tests_alone_do_not_satisfy_verifier_custody():
    trace = copy.deepcopy(trace_fixture())
    del trace["VerifierIdentity"]["protected_test_digest"]
    trace["resource_vector"]["public_test_runs"] = 3
    errors = validate_h0_trace(trace)
    assert any("protected_test_digest or external_evaluator_identity" in error for error in errors)


def test_h0_source_rejects_developmental_capital_claim():
    trace = copy.deepcopy(trace_fixture())
    trace["candidate_capital_level"] = "K1"
    errors = validate_h0_trace(trace)
    assert any("may not claim K1/K2/K3" in error for error in errors)


def test_h0_source_requires_common_minimum_resource_coordinates():
    trace = copy.deepcopy(trace_fixture())
    del trace["resource_vector"]["development_update_work"]
    errors = validate_h0_trace(trace)
    assert any("resource_vector missing required coordinates" in error for error in errors)


def test_h0_pass_requires_complete_checks():
    trace = copy.deepcopy(trace_fixture())
    trace["all_required_checks_complete"] = False
    errors = validate_h0_trace(trace)
    assert any("H0_MECHANICS_PASS requires" in error for error in errors)
