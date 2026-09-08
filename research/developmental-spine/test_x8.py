"""Integrity tests for X8, which continues X7's price sweep past the point where
it stopped and asks where a compiled verdict stops being worth its bits.

The specific failure this study exists to prevent is reporting a censored bound
as a boundary, so the tests below are weighted towards that: the overlap control
must be an identity rather than a resemblance, and a sweep that ends while the
advantage is still alive must produce its own terminal rather than a number.
"""

from __future__ import annotations

import inspect
import json
import pathlib
import sys

import pytest

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "cognitive-ladder"))

import run_x7 as R7
import run_x8 as R
import x8
from x8 import CELL_BIT_PRICES, COMMITMENT, OVERLAP_PRICE, X8_PLAN

RECEIPT = HERE.parent / "cognitive-ladder" / "results" / "X8_TABLE_BREAK_EVEN_V1.json"


def _doc() -> dict:
    if not RECEIPT.exists():
        pytest.skip("X8 receipt not generated in this checkout")
    return json.loads(RECEIPT.read_text())


# --- the commitment ----------------------------------------------------------

def test_the_plan_digest_is_the_one_that_was_registered():
    assert COMMITMENT.commitment.startswith("40c411f98c8b61d8")


def test_no_outcome_lives_inside_the_committed_plan():
    for field in ("terminal", "predictions", "primary_grid", "break_even_cell_bits",
                  "overlap_control"):
        assert field not in X8_PLAN, field


def test_the_sweep_starts_where_x7_stopped_and_goes_up():
    assert CELL_BIT_PRICES[0] == OVERLAP_PRICE
    assert CELL_BIT_PRICES == tuple(sorted(CELL_BIT_PRICES))
    assert max(CELL_BIT_PRICES) == 128


def test_the_plan_says_x7s_number_was_a_bound_not_a_boundary():
    assert "lower bound and not a boundary" in X8_PLAN["scientific_question"]
    assert "refuted" in X8_PLAN["what_x7_established_and_did_not"]


def test_the_overlap_price_is_declared_a_control_and_not_a_prediction():
    assert "CONTROL and not a prediction" in X8_PLAN["prior_information_audit"]["known"]


# --- the continuation is the same code on the same seeds ---------------------

def test_the_grid_is_built_by_x7s_own_cell_function():
    """An overlap control is worth nothing if the two studies run different code."""
    assert R.cell is R7.cell
    src = inspect.getsource(R)
    assert "from run_x7 import" in src


def test_the_overlap_check_compares_every_arm_not_just_the_compiled_one():
    src = inspect.getsource(R.overlap_check)
    assert "for arm in ARMS:" in src
    assert "mismatches" in src


# --- every terminal is reachable ---------------------------------------------

OK_OVERLAP = {"comparable": True, "reproduces_x7": True}
OK_INVARIANCE = {"holds": True, "offenders": []}
OK_DEGRADE = {"all_within_five_percent": True, "any_worse_than_naive": False, "rows": []}


def test_a_failed_overlap_voids_the_study():
    terminal, reason = R._terminal(
        {}, {"comparable": True, "reproduces_x7": False}, OK_INVARIANCE, 32, OK_DEGRADE)
    assert terminal == "VOID_THE_OVERLAP_DOES_NOT_REPRODUCE_X7"
    assert "VOID" in reason


def test_a_price_leaking_into_a_tableless_arm_voids_the_study():
    terminal, _ = R._terminal({}, OK_OVERLAP, {"holds": False, "offenders": [1]}, 32,
                              OK_DEGRADE)
    assert terminal == "VOID_A_PRICE_MOVED_AN_ARM_THAT_HOLDS_NO_TABLE"


def test_a_pathological_degradation_becomes_the_result_not_a_footnote():
    bad = {"all_within_five_percent": False, "any_worse_than_naive": True, "rows": []}
    terminal, reason = R._terminal({}, OK_OVERLAP, OK_INVARIANCE, 32, bad)
    assert terminal == (
        "COMPILED_ARM_IS_WORSE_THAN_THE_RULE_IT_COMPILES_WHEN_STORAGE_IS_SCARCE")
    assert "reported as the result of this study" in reason
    assert "X7's positive at two bits is unaffected" in reason


def test_a_sweep_that_never_kills_the_advantage_says_so_rather_than_reporting_its_top():
    terminal, reason = R._terminal({}, OK_OVERLAP, OK_INVARIANCE, None, OK_DEGRADE)
    assert terminal == "NO_BREAK_EVEN_FOUND_BELOW_SIXTEEN_ANSWERS_PER_CELL"
    assert "reported as a surprise rather than banked" in reason


def test_the_located_terminal_quotes_the_price_in_answers_as_well_as_bits():
    terminal, reason = R._terminal({}, OK_OVERLAP, OK_INVARIANCE, 32, OK_DEGRADE)
    assert terminal == "BREAK_EVEN_LOCATED"
    assert "32 bits a cell" in reason and "4 answers' worth" in reason


def test_a_degradation_pathology_outranks_a_located_break_even():
    """Both can be true at once. The defect must win, because a number produced by
    an arm that misbehaves is not a number anyone should use."""
    bad = {"all_within_five_percent": False, "any_worse_than_naive": True, "rows": []}
    assert R._terminal({}, OK_OVERLAP, OK_INVARIANCE, 32, bad)[0] != "BREAK_EVEN_LOCATED"


# --- the receipt -------------------------------------------------------------

def test_the_terminal_follows_from_the_published_receipt():
    doc = _doc()
    break_even = doc["break_even_cell_bits"]
    assert R._terminal(doc["predictions"], doc["overlap_control"], doc["price_invariance"],
                       break_even, doc["degradation_at_the_top_price"])[0] == doc["terminal"]


def test_the_overlap_held_cell_for_cell():
    o = _doc()["overlap_control"]
    if not o.get("comparable"):
        pytest.skip("X7 receipt absent")
    assert o["cells_compared"] > 0
    assert o["mismatches"] == []


def test_the_break_even_is_the_lowest_dead_price_not_the_highest_live_one():
    doc = _doc()
    counts = doc["winning_setting_counts_by_price"]["PRECOMPILED_DEMAND"]
    be = doc["break_even_cell_bits"]
    if be is None:
        assert all(v > 0 for v in counts.values())
    else:
        assert counts[str(be)] == 0
        for p in CELL_BIT_PRICES:
            if p < be:
                assert counts[str(p)] > 0, (p, counts)


def test_x7s_censored_number_is_named_as_censored():
    doc = _doc()
    assert doc["x7_reported_bound"] == OVERLAP_PRICE
    assert "lower bound" in doc["what_x7s_number_was"]
    assert "not by reinterpreting X7's number" in doc["what_x7s_number_was"]


def test_every_quoted_work_figure_is_at_matched_correctness():
    for cell in _doc()["primary_grid"]:
        if any(v is not None for v in cell["ratio_to_replay"].values()):
            assert cell["arms"]["REPLAY_ONLY_PARENT"]["min_correctness"] == 1.0
        for row in cell["arms"].values():
            if row["work"] is not None:
                assert row["min_correctness"] == 1.0


def test_the_counter_identity_holds_exactly_in_every_cell():
    for cell in _doc()["primary_grid"]:
        for arm, row in cell["arms"].items():
            assert row["counter_identity_residual"] == 0, (arm, cell["cell_bits"])


def test_refuted_predictions_are_published_as_refuted():
    preds = _doc()["predictions"]
    assert set(preds) == {
        "U0_overlap_reproduces_x7", "U1_a_price_kills_the_advantage",
        "U2_response_stays_monotone", "U3_break_even_is_above_two_answers",
        "U4_degrades_into_the_rule_it_compiles", "U5_the_end_is_refusal_not_churn"}
    assert all(isinstance(v, bool) for v in preds.values())


def test_nothing_is_withdrawn_from_x7():
    assert "withdraws nothing from X7" in _doc()["authority"]


def test_no_novelty_is_claimed_for_continuing_a_sweep():
    assert _doc()["novelty"].startswith("NONE CLAIMED")
