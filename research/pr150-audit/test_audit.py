"""Tests for the PR #150 measurement audit.

The first two are gates rather than tests: if either fails the audit is void,
because it would then be auditing something other than PR #150's harness.
Everything after them is fast by construction, using short lifetimes; the full
sweep lives in the committed receipt.
"""

from __future__ import annotations

import json
import pathlib
import random

import pytest

import audit as A
import pr150_source as SRC
import run_audit

HERE = pathlib.Path(__file__).parent
RECEIPT = json.loads((HERE / "RESULTS_V1.json").read_text())


@pytest.mark.parametrize("seed", [1, 2, 3, 17, 99, 2026])
def test_faithfulness_gate_traced_search_equals_the_original(seed):
    """The traced search must be the original plus one return value, nothing else."""
    land = SRC.NK(10, 3, random.Random(seed))
    inferred, _ = SRC.discover_factorization(land, random.Random(seed + 1))
    original = SRC.local_search(land, random.Random(seed + 7), inferred, budget=16)
    traced = A.local_search_traced(land, random.Random(seed + 7), inferred, budget=16)
    assert original[0] == traced[0], "reported score diverged"
    assert original[1] == traced[1], "cost diverged"


def test_reproduction_gate_the_rerun_matches_pr150_exactly():
    """A rerun that drifts from the published output is auditing a different thing."""
    assert RECEIPT["reproduction_gate"]["exact"] is True
    assert RECEIPT["reproduction_gate"]["mismatches"] == []


def test_the_traced_state_is_the_state_the_reported_score_describes():
    """When the structure is exact, self-report and oracle must coincide."""
    land = SRC.NK(8, 2, random.Random(5))
    inferred, _ = SRC.discover_factorization(land, random.Random(6))
    if any(set(land.affected[b]) != set(inferred[b]) for b in range(land.n)):
        pytest.skip("discovery was inexact on this landscape; covered by the drift tests")
    reported, _, state = A.local_search_traced(land, random.Random(7), inferred, budget=16)
    assert reported == pytest.approx(land.fitness(state), abs=1e-12)


def test_an_incomplete_structure_makes_the_self_report_diverge():
    """The mechanism under audit, exhibited directly rather than argued.

    Emptying a bit's edge list is not a valid crippling: with no edges its delta
    is zero, so the search never selects that bit and the vector stays honest.
    The divergence needs a bit that IS flipped while its effect set is
    under-reported, so one true edge is dropped from every bit instead.
    """
    diverged = 0
    for seed in range(20):
        land = SRC.NK(8, 3, random.Random(seed))
        inferred, _ = SRC.discover_factorization(land, random.Random(seed + 100))
        crippled = [lst[:-1] if len(lst) > 1 else lst for lst in inferred]
        if crippled == inferred:
            continue
        reported, _, state = A.local_search_traced(
            land, random.Random(seed + 200), crippled, budget=16)
        if reported != pytest.approx(land.fitness(state), abs=1e-12):
            diverged += 1
    assert diverged > 0, (
        "under-reporting an edge that the search then flips must make the maintained "
        "vector diverge from the oracle; if it never does, the audit has no mechanism"
    )


def test_p1_no_inflation_without_drift():
    for m in [r for g in RECEIPT["results"] for r in RECEIPT["results"][g] if r["drift"] == 0]:
        assert m["max_inflation"] == 0.0
        assert m["mean_structure_recall"] == 1.0
        assert m["mean_structure_precision"] == 1.0


def test_p2_inflation_is_positive_under_drift():
    drift = [r for g in RECEIPT["results"] for r in RECEIPT["results"][g] if r["drift"] > 0]
    assert drift
    for m in drift:
        assert m["mean_inflation"] > 0.0


def test_p2_monotonicity_clause_is_recorded_as_refuted():
    """Half of my own prediction was wrong; the receipt must say so, not bury it."""
    p2 = RECEIPT["prediction_outcomes"]["P2_positive_inflation_under_drift"]
    assert p2["verdict"] == "PARTIALLY_CONFIRMED"
    assert "REFUTED" in p2["note"]


def test_inflation_is_confined_to_generations_with_inexact_structure():
    for m in [r for g in RECEIPT["results"] for r in RECEIPT["results"][g]]:
        assert m["inflation_when_structure_exact"] == pytest.approx(0.0, abs=1e-12)


def test_no_row_changes_which_arm_is_ahead():
    """The conclusion-level question, which is the one that matters."""
    for m in [r for g in RECEIPT["results"] for r in RECEIPT["results"][g]]:
        assert m["factor_beats_parent_as_reported"] == m["factor_beats_parent_when_true"]


def test_pr150s_positive_claim_survives_independent_rescoring():
    matched = RECEIPT["results"]["approximately_matched_cost_parent"]
    assert len(matched) == 4
    for m in matched:
        assert m["factor_beats_parent_when_true"], (
            f"K={m['K']} drift={m['drift']} no longer beats the parent once re-scored"
        )
        assert m["factor_total_full_equivalent_cost"] < m["evolutionary_total_full_eval_cost"]


def test_terminal_is_a_pure_function_of_the_table():
    terminal, _ = run_audit.terminal_for(RECEIPT["results"])
    assert terminal == RECEIPT["terminal"]


def test_the_receipt_disclaims_what_it_cannot_establish():
    text = " ".join(RECEIPT["what_this_does_not_establish"])
    assert "Nothing about OCM" in text
    assert "CANNOT_CHECK" in text
    assert "not the strongest modern" in text
