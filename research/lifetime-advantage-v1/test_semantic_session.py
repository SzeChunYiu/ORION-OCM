"""Independent exact finite calibration, deliberately restricted to lengths 0..3.

The oracle enumerates raw words and recovers their polynomials by exact Newton
interpolation of the numeric interpreter. It never calls M.normal_form. These
are development/calibration checks, not protected outcome experiments.
"""
from __future__ import annotations

from fractions import Fraction
from itertools import product
import json
from pathlib import Path
import sys

import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from semantic_session import SemanticSearchSession
from inverse_parent import InverseSession
from ocm.learning import methods as M


def interpolated_coefficients(program):
    """Recover the exact polynomial from a separately executed evaluation table."""
    degree_bound = 2 ** tuple(program).count("square")
    differences = [M.execute(tuple(program), x) for x in range(degree_bound + 1)]
    answer = [Fraction(0)] * (degree_bound + 1)
    basis = [Fraction(1)]
    for order in range(degree_bound + 1):
        for i, coefficient in enumerate(basis):
            answer[i] += differences[0] * coefficient
        differences = [b - a for a, b in zip(differences, differences[1:])]
        # binomial(x, order + 1) = binomial(x, order)*(x-order)/(order+1)
        expanded = [Fraction(0)] * (len(basis) + 1)
        for i, coefficient in enumerate(basis):
            expanded[i] -= coefficient * Fraction(order, order + 1)
            expanded[i + 1] += coefficient / (order + 1)
        basis = expanded
    while len(answer) > 1 and answer[-1] == 0:
        answer.pop()
    return tuple(answer)


def oracle_world(max_length):
    representatives = {}
    for length in range(max_length + 1):
        for program in product(M.PRIMITIVES, repeat=length):
            representatives.setdefault(interpolated_coefficients(program), program)
    return representatives


def checked_answer(result, coefficients, max_length):
    assert result["status"] == "VERIFIED_POLYNOMIAL_IDENTITY"
    assert result["verified"] is True
    assert result["program"] is not None
    program = tuple(result["program"])
    assert len(program) <= max_length
    assert all(op in M.PRIMITIVES for op in program)
    assert interpolated_coefficients(program) == coefficients


def _check_complete_reach(max_length):
    world = oracle_world(max_length)
    session = SemanticSearchSession(max_length)
    for i, (coefficients, shortest_program) in enumerate(world.items()):
        result = session.query(M.PolynomialTask(f"exact-{i}", coefficients), 10_000)
        checked_answer(result, coefficients, max_length)
        assert len(result["program"]) == len(shortest_program)
    # Integer primitives cannot yield x+1/2. Force all pending work to complete.
    absent = M.PolynomialTask("outside-grammar", (Fraction(1, 2), Fraction(1)))
    result = session.query(absent, 10_000)
    assert result["status"] == "EXHAUSTED_DECLARED_GRAMMAR"
    assert result["program"] is None
    assert result["verified"] is False
    actual = {tuple(coefficients) for coefficients, _program in session.nodes}
    assert actual == set(world)
    for i, coefficients in enumerate(world):
        checked_answer(session.query(M.PolynomialTask(f"renamed-{i}", coefficients), 0),
                       coefficients, max_length)


def test_complete_reach_agrees_with_independent_raw_word_interpolation():
    for max_length in range(4):
        _check_complete_reach(max_length)


def test_zero_budget_is_not_an_impossibility_certificate():
    session = SemanticSearchSession(3)
    identity = M.PolynomialTask("identity", (0, 1))
    checked_answer(session.query(identity, 0), identity.coefficients, 3)
    square = M.PolynomialTask("square", (0, 0, 1))
    result = session.query(square, 0)
    assert result["status"] == "BUDGET_EXHAUSTED"
    assert result["program"] is None
    assert result["verified"] is False
    checked_answer(session.query(square, 10_000), square.coefficients, 3)


def test_interruption_resume_reaches_a_new_task_after_checkpoint():
    session = SemanticSearchSession(3)
    absent = M.PolynomialTask("absent", (Fraction(1, 2),))
    assert session.query(absent, 1)["status"] == "BUDGET_EXHAUSTED"
    restored = SemanticSearchSession.restore(session.checkpoint())
    fresh = M.PolynomialTask("fresh-composition", interpolated_coefficients(("inc", "square", "double")))
    checked_answer(restored.query(fresh, 10_000), fresh.coefficients, 3)
    checked_answer(restored.query(fresh, 0), fresh.coefficients, 3)
    assert restored.query(absent, 10_000)["status"] == "EXHAUSTED_DECLARED_GRAMMAR"


def test_transition_budget_is_enforced_across_incremental_queries():
    session = SemanticSearchSession(3)
    absent = M.PolynomialTask("absent-budget", (Fraction(1, 2),))
    for budget in (0, 1, 2, 0, 3):
        before = session.work["transitions"]
        result = session.query(absent, budget)
        assert result["status"] == "BUDGET_EXHAUSTED"
        assert session.work["transitions"] - before <= budget
        assert result["query_work"]["transitions"] == session.work["transitions"] - before


def _check_snapshot_tampering(field, replacement):
    session = SemanticSearchSession(3)
    session.query(M.PolynomialTask("square", (0, 0, 1)), 10_000)
    payload = json.loads(session.checkpoint())
    payload[field] = replacement
    with unittest.TestCase().assertRaises(ValueError):
        SemanticSearchSession.restore(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode())


def test_snapshot_semantics_and_version_tampering_are_rejected():
    for field, replacement in (("scope", "unregistered-version"), ("nodes", []), ("cursor", -1)):
        _check_snapshot_tampering(field, replacement)


def test_invalid_serialization_and_budget_are_rejected():
    with unittest.TestCase().assertRaises(ValueError):
        SemanticSearchSession.restore(b"not JSON")
    session = SemanticSearchSession(1)
    task = M.PolynomialTask("identity", (0, 1))
    for invalid in (-1, True, 1.5):
        with unittest.TestCase().assertRaises(ValueError):
            session.query(task, invalid)


def test_reset_loses_derived_reach_without_erasing_acquisition_work():
    session = SemanticSearchSession(3)
    task = M.PolynomialTask("square", (0, 0, 1))
    checked_answer(session.query(task, 10_000), task.coefficients, 3)
    before = dict(session.work)
    session.reset()
    assert session.query(task, 0)["status"] == "BUDGET_EXHAUSTED"
    for key, count in before.items():
        assert session.work[key] >= count
    checked_answer(session.query(task, 10_000), task.coefficients, 3)


def _check_inverse_parent(max_length):
    world = oracle_world(max_length)
    session = InverseSession(max_length)
    for i, coefficients in enumerate(world):
        result = session.query(M.PolynomialTask(f"inverse-{i}", coefficients))
        checked_answer(result, coefficients, max_length)
    absent_coefficients = (
        (Fraction(1, 2), Fraction(1)),
        (Fraction(0), Fraction(-1)),
        (Fraction(3),),
        interpolated_coefficients(("square",) * (max_length + 1)),
    )
    for i, coefficients in enumerate(absent_coefficients):
        assert coefficients not in world
        result = session.query(M.PolynomialTask(f"inverse-absent-{i}", coefficients))
        assert result["status"] == "EXHAUSTED_DECLARED_GRAMMAR"
        assert result["program"] is None
        assert result["verified"] is False


def test_inverse_parent_matches_independent_complete_finite_world():
    for max_length in range(4):
        _check_inverse_parent(max_length)


if __name__ == "__main__":
    suite = unittest.TestSuite(
        unittest.FunctionTestCase(function)
        for name, function in sorted(globals().items())
        if name.startswith("test_") and callable(function)
    )
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    raise SystemExit(0 if result.wasSuccessful() else 1)
