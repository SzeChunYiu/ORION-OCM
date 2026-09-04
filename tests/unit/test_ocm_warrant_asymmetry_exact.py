from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


MODULE_PATH = (
    Path(__file__).resolve().parents[2]
    / "research"
    / "orion-machine"
    / "reference"
    / "ocm_warrant_asymmetry_exact.py"
)
SPEC = importlib.util.spec_from_file_location("ocm_warrant_asymmetry_exact", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
M = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = M
SPEC.loader.exec_module(M)


def test_satisfiable_support_has_retain_witness() -> None:
    formula = ((1, 2), (-1, 2), (1, -2))
    witnesses = M.satisfying_assignments(formula, 2)
    assert witnesses
    assert all(M.verify_retain_certificate(formula, 2, w) for w in witnesses)


def test_unsatisfiable_support_requires_retract() -> None:
    formula = ((1,), (-1,))
    assert M.satisfying_assignments(formula, 1) == ()
    assert M.retain(formula, 1) is False
    assert M.retract(formula, 1) is True


def test_open_world_positive_witnesses_are_not_complete() -> None:
    observation = M.OpenWorldObservation(
        (frozenset({0, 1}), frozenset({1, 2}))
    )
    pair = M.open_world_ambiguous_pair(
        observation,
        revoked=frozenset({1}),
        unseen_surviving_support=frozenset({3}),
    )
    assert pair["observation_identical"] is True
    assert pair["correct_action_world_retract"] == "RETRACT"
    assert pair["correct_action_world_retain"] == "RETAIN"
    assert pair["deterministic_exact_action_exists"] is False


def test_complete_manifest_enables_negative_warrant_check() -> None:
    supports = (frozenset({0, 1}), frozenset({1, 2}), frozenset({3}))
    revoked = frozenset({1, 3})
    hitting_atoms = (1, 1, 3)
    assert M.verify_explicit_retract(
        supports, revoked, hitting_atoms, complete_manifest=True
    )
    assert not M.verify_explicit_retract(
        supports, revoked, hitting_atoms, complete_manifest=False
    )


def test_surviving_support_is_short_positive_certificate() -> None:
    supports = (
        frozenset({0, 1}),
        frozenset({1, 2}),
        frozenset({4}),
    )
    revoked = frozenset({1})
    assert M.explicit_warrant_decision(supports, revoked) == "RETAIN"
    assert M.verify_explicit_retain(supports, revoked, 2)


def test_main_exact_calibration_has_both_outcomes() -> None:
    result = M.run_exact_calibration()
    counts = result["exhaustive_finite_checks"]
    assert counts["support_families_and_revocations_checked"] > 0
    assert counts["retain_cases"] > 0
    assert counts["retract_cases"] > 0


def test_invalid_literal_is_rejected() -> None:
    try:
        M.eval_literal(0, (1,))
    except ValueError:
        pass
    else:
        raise AssertionError("literal zero was accepted")


def test_manifest_false_alarm_control() -> None:
    supports = (frozenset({0}), frozenset({1}))
    revoked = frozenset({0})
    assert M.explicit_warrant_decision(supports, revoked) == "RETAIN"
    assert not M.verify_explicit_retract(
        supports,
        revoked,
        (0, 0),
        complete_manifest=True,
    )
