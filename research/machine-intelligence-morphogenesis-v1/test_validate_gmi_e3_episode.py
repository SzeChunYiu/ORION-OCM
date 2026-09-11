import copy
import json
from pathlib import Path

from validate_gmi_e3_episode import validate_episode


def fixture():
    path = Path(__file__).resolve().parent / "GMI_E3_HISTORICAL_LEAN_EPISODE_V1.json"
    return json.loads(path.read_text(encoding="utf-8"))


def test_historical_lean_episode_is_schema_green():
    assert validate_episode(fixture()) == []


def test_fixed_replay_cannot_be_relabelled_k1():
    episode = fixture()
    episode = copy.deepcopy(episode)
    episode["developmental_attribution"]["candidate_capital_level"] = "K1"
    errors = validate_episode(episode)
    assert any("solution absent" in error for error in errors)
    assert any("pre-solution mediator" in error for error in errors)
    assert any("matched reset" in error for error in errors)
    assert any("identity/no-learning" in error for error in errors)


def test_k2_requires_real_development():
    episode = fixture()
    episode = copy.deepcopy(episode)
    attribution = episode["developmental_attribution"]
    attribution["candidate_capital_level"] = "K2"
    attribution["solution_was_absent_from_relevant_history"] = True
    attribution["pre_solution_mediator_observed"] = True
    attribution["matched_reset_result_ref"] = "reset:1"
    errors = validate_episode(episode)
    assert any("identity/no-learning" in error for error in errors)
    assert any("development_update_work" in error for error in errors)


def test_missing_resource_coordinate_is_rejected():
    episode = fixture()
    episode = copy.deepcopy(episode)
    del episode["resource_vector"]["verifier_calls"]
    errors = validate_episode(episode)
    assert any("resource vector missing" in error for error in errors)


def test_math_cannot_silently_use_code_test_verifier():
    episode = fixture()
    episode = copy.deepcopy(episode)
    episode["external_verification"]["verifier_type"] = "EXECUTION_TEST_VERIFIED"
    errors = validate_episode(episode)
    assert any("formal verifier" in error for error in errors)


def test_success_requires_completed_required_checks():
    episode = fixture()
    episode = copy.deepcopy(episode)
    episode["outcome"]["all_required_checks_complete"] = False
    errors = validate_episode(episode)
    assert any("admissible_result=true" in error for error in errors)
