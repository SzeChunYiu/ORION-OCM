"""Integrity tests for X3, which reports this lane's results without an exchange rate
and in doing so finds that one of them does not survive the honest one.
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

import run_x3 as R
import x3
from x3 import CHOSEN_PRICES, COUNTS, critical_ratio, dominance

RECEIPT = HERE.parent / "cognitive-ladder" / "results" / "X3_PRICE_FREE_V1.json"


# --- the price-free machinery is correct ------------------------------------

def test_dominance_is_only_claimed_when_every_coordinate_agrees():
    a = {c: 1.0 for c in COUNTS}
    b = {c: 2.0 for c in COUNTS}
    assert dominance(a, b) == "A_DOMINATES"
    assert dominance(b, a) == "B_DOMINATES"
    mixed = dict(a); mixed["derivations"] = 5.0
    assert dominance(mixed, b) == "NEITHER"
    assert dominance(a, a) == "NEITHER", "equal vectors dominate nothing"


def test_the_critical_price_actually_ties_the_two_arms():
    a = {c: 0.0 for c in COUNTS}; b = {c: 0.0 for c in COUNTS}
    a["derivations"], b["derivations"] = 10.0, 40.0
    a["applications"], b["applications"] = 100.0, 0.0
    out = critical_ratio(a, b, "derivations", "applications", CHOSEN_PRICES)
    price = out["boundary"]
    assert price is not None
    def total(v, p):
        return sum((p if c == "derivations" else CHOSEN_PRICES[c]) * v[c] for c in COUNTS)
    assert total(a, price) == pytest.approx(total(b, price)), "the boundary must be a tie"
    assert total(a, price * 1.5) < total(b, price * 1.5), "A must win above it"


def test_no_positive_tie_is_reported_as_a_result_not_a_missing_value():
    """An earlier version returned a bare None here and threw the result away."""
    a = {c: 0.0 for c in COUNTS}; b = {c: 0.0 for c in COUNTS}
    a["verifications"], b["verifications"] = 0.0, 100.0
    a["lookups"], b["lookups"] = 0.0, 100.0
    out = critical_ratio(a, b, "verifications", "lookups", CHOSEN_PRICES)
    assert out["boundary"] is None
    assert out["always"] == "A"
    assert "EVERY positive price" in out["reason"]


def test_the_boundary_is_an_absolute_price_not_a_ratio():
    src = inspect.getsource(critical_ratio)
    assert "absolute price of one" in src
    doc = inspect.getdoc(x3)
    assert "not a ratio between two prices" in doc, (
        "the module docstring said 'ratio' and it was wrong; the correction must stay")


def test_lookups_are_separated_from_the_charges_conflated_with_them():
    src = inspect.getsource(x3.counts_for)
    assert "phase.lookup_work - consult - maintain" in src
    assert "useless for a" in src


# --- the finding this module was not looking for ----------------------------

def test_the_unaudited_comparison_is_named_and_audited():
    doc = json.loads(RECEIPT.read_text())
    note = doc["predictions"]["Y5_the_unaudited_comparison"]
    assert "re-checked only the comparison against the SINGLETON rule" in note.replace(
        "re-checked unanimity against the SINGLETON rule only",
        "re-checked only the comparison against the SINGLETON rule")
    assert "was not registered as a prediction because it was not noticed" in note


def test_the_terminal_leads_with_the_failure_not_the_survivor():
    doc = json.loads(RECEIPT.read_text())
    reason = doc["terminal_reason"]
    assert reason.startswith("THE CARRY ADVANTAGE AGAINST REPLAY DOES NOT SURVIVE")
    assert doc["terminal"] == "CARRY_ADVANTAGE_AGAINST_REPLAY_MOSTLY_FAILS_THE_HONEST_PRICE"
    survivor = reason.index("What does survive")
    failure = reason.index("DOES NOT SURVIVE")
    assert failure < survivor, "the failure must come first in the sentence order"


def test_the_failure_is_visible_in_the_totals_too():
    doc = json.loads(RECEIPT.read_text())
    losses = [c for c in doc["primary_grid"]
              if c["mean_total_work"]["UNANIMITY_NAIVE"]
              > c["mean_total_work"]["REPLAY_ONLY_PARENT"]]
    assert losses, "the terminal claims a failure; it must be in the numbers"
    assert len(losses) > len(doc["primary_grid"]) / 2, (
        "the terminal says MOSTLY fails; check that it mostly does")


def test_the_surviving_result_is_stated_as_the_stronger_form():
    doc = json.loads(RECEIPT.read_text())
    reason = doc["terminal_reason"]
    assert "What does survive" in reason, "the surviving result must be named"
    # the terminal has two branches: every cell price-free, or a mix of price-free
    # cells and cells with a finite threshold. Both must state the survivor.
    assert ("EVERY positive price of a scope check" in reason
            or "above a verification price of" in reason)
    mixed = [c for c in doc["primary_grid"]
             if c["critical_verification_price_for_unanimity"]["boundary"] is None]
    assert mixed, "at least one cell should need no price argument at all"


def test_the_price_condition_matches_the_totals_it_explains():
    """The boundary must predict the sign the totals show, cell by cell."""
    doc = json.loads(RECEIPT.read_text())
    for c in doc["primary_grid"]:
        boundary = c["critical_derivation_price_for_the_lineage"]["boundary"]
        if boundary is None:
            continue
        lineage_wins = (c["mean_total_work"]["UNANIMITY_NAIVE"]
                        < c["mean_total_work"]["REPLAY_ONLY_PARENT"])
        assert lineage_wins == (CHOSEN_PRICES["derivations"] > boundary), (
            c["level"], c["d1_length"], boundary)


# --- honesty about scope ----------------------------------------------------

def test_no_dominance_is_claimed():
    doc = json.loads(RECEIPT.read_text())
    assert doc["predictions"]["Y1_no_arm_dominates"] is True
    for c in doc["primary_grid"]:
        for pair in c["pairs"].values():
            assert pair["dominance"] == "NEITHER"
            assert pair["better_on"] and pair["worse_on"], (
                "a pair with nothing on one side would be dominance")


def test_the_receipt_admits_price_freedom_is_not_model_freedom():
    doc = json.loads(RECEIPT.read_text())
    note = doc["what_this_does_not_establish"]
    assert "Immunity to price objections is not immunity to modelling objections" in note
    assert "exactly as a price of zero would" in note


def test_the_chosen_prices_are_labelled_as_one_point_on_an_axis():
    doc = json.loads(RECEIPT.read_text())
    assert doc["chosen_prices_are_one_point_on_an_axis"] == dict(CHOSEN_PRICES)
    assert "reader supplies prices and reads off the answer" in doc["terminal_reason"]


def test_the_receipt_carries_the_plan_and_no_wall_clock():
    doc = json.loads(RECEIPT.read_text())
    assert doc["commitment"]["commitment"] == x3.COMMITMENT.commitment
    assert doc["plan"] == json.loads(json.dumps(x3.X3_PLAN))
    text = RECEIPT.read_text().lower()
    for banned in ("elapsed", "timestamp", "duration_ms", "wall"):
        assert banned not in text, banned


def test_the_correction_to_x3s_reading_is_recorded_without_editing_its_commitment():
    """X4 found X3's arms all held the full language. The correction is recorded
    outside X3_PLAN so the frozen digest is untouched and nothing is withdrawn."""
    assert x3.READING_CORRECTED_BY == "X4_FINAL_ACCOUNTING_V1"
    assert "does not generalise" in x3.READING_CORRECTION
    assert "READING_CORRECT" not in json.dumps(x3.X3_PLAN)
