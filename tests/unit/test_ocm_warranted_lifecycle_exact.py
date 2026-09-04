from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


MODULE_PATH = (
    Path(__file__).resolve().parents[2]
    / "research"
    / "orion-machine"
    / "reference"
    / "ocm_warranted_lifecycle_exact.py"
)
SPEC = importlib.util.spec_from_file_location("ocm_warranted_lifecycle_exact", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
M = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = M
SPEC.loader.exec_module(M)


def test_strict_lifecycle_refinement() -> None:
    result = M.run_exact_calibration()
    lift = result["warrant_lift"]
    assert lift["current_behavior_classes"] == 1
    assert lift["lifecycle_equivalence_classes"] == 64
    assert lift["extra_exact_lifecycle_bits_required_without_queries_or_abstention"] == 6


def test_planted_challenge_drop_collides() -> None:
    result = M.run_exact_calibration()
    lift = result["warrant_lift"]
    assert lift["classes_after_planted_challenge_drop"] == 32
    assert lift["worlds_per_planted_collision"] == 2


def test_exact_unlearning_does_not_imply_warrant() -> None:
    witness = M.exact_unlearning_without_warrant()
    assert witness["exact_behavioral_unlearning"] is True
    assert witness["warrant_correctness"] is False


def test_warrant_does_not_imply_exact_unlearning() -> None:
    witness = M.warrant_without_exact_unlearning()
    assert witness["warrant_correctness"] is True
    assert witness["exact_model_unlearning"] is False


def test_authority_intersection() -> None:
    scopes = (frozenset({0, 1}), frozenset({1, 2}), frozenset({1}))
    assert M.authority_scope(scopes) == frozenset({1})


def test_union_scope_has_countermodel() -> None:
    scopes = (frozenset({0, 1}), frozenset({1, 2}))
    countermodel = M.union_scope_is_unsound(scopes)
    assert countermodel is not None
    assert countermodel["union_scope"] == [0, 1, 2]
    assert countermodel["intersection_scope"] == [1]


def test_equal_scopes_are_no_alarm_case() -> None:
    scopes = (frozenset({0, 1}), frozenset({0, 1}))
    assert M.union_scope_is_unsound(scopes) is None


def test_invalid_world_width_is_rejected() -> None:
    try:
        M.WarrantWorld(2, 2, (1, 0, 1))
    except ValueError:
        pass
    else:
        raise AssertionError("invalid warrant-world width was accepted")
