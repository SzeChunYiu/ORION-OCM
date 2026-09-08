"""Integrity tests for X7, which charges X6's compiled table the bits it occupies
and asks whether this lane's strongest result survives its own accounting.

X7 is an audit of the study this lane would least like to lose, so its tests are
weighted towards the ways a survival could be manufactured: a placebo that does
not actually reproduce the unpriced arm, a price that leaks into arms holding no
table, and a discard policy doing work the price is credited with.
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

import dev5_arms as A5
import dev6_arms as A6
import run_x7 as R
import x7
from x7 import CELL_BIT_PRICES, COMMITMENT, HONEST_CELL_BITS, X7_PLAN

RECEIPT = HERE.parent / "cognitive-ladder" / "results" / "X7_PRICED_TABLE_V1.json"


def _doc() -> dict:
    if not RECEIPT.exists():
        pytest.skip("X7 receipt not generated in this checkout")
    return json.loads(RECEIPT.read_text())


# --- the commitment ----------------------------------------------------------

def test_the_plan_digest_is_the_one_that_was_registered():
    assert COMMITMENT.commitment.startswith("f34e56a2a2c9cef7")


def test_no_outcome_lives_inside_the_committed_plan():
    for field in ("terminal", "predictions", "primary_grid", "placebo",
                  "highest_price_the_advantage_survives"):
        assert field not in X7_PLAN, field


def test_the_kill_criterion_says_what_a_failure_would_mean_for_x6():
    kill = X7_PLAN["kill_criterion"]
    assert "artefact of a free table" in kill
    assert "confined to languages small enough to collapse" in kill
    assert "with X6's receipt unchanged" in kill


def test_zero_is_in_the_price_sweep_because_it_is_the_placebo():
    assert CELL_BIT_PRICES[0] == 0
    assert HONEST_CELL_BITS in CELL_BIT_PRICES
    assert CELL_BIT_PRICES == tuple(sorted(CELL_BIT_PRICES))


# --- the bit charge is additive and reaches only what holds a table -----------

def test_a_store_with_no_table_costs_exactly_what_it_did_before():
    """Every arm before X7 constructs a VersionStore without touching the two new
    fields, and must therefore measure exactly what it measured."""
    store = A5.VersionStore()
    assert store.table_cells == 0 and store.table_cell_bits == 0
    assert store.bits() == store.base.bits()


def test_the_table_charge_enters_the_same_budget_as_facts_and_guards():
    store = A5.VersionStore()
    store.table_cell_bits = 2
    store.table_cells = 10
    assert store.bits() == store.base.bits() + 20


def test_a_copied_store_carries_its_table_price():
    store = A5.VersionStore()
    store.table_cell_bits, store.table_cells = 4, 3
    twin = store.copy()
    assert (twin.table_cell_bits, twin.table_cells) == (4, 3)
    assert twin.bits() == store.bits()


def test_the_price_defaults_to_zero_so_x6_is_reproducible():
    assert inspect.signature(A6._run).parameters["table_cell_bits"].default == 0


# --- the discard policy is declared, coarse, and cannot free the current rule --

def test_the_discard_policy_is_least_recently_consulted_whole_tables():
    src = inspect.getsource(A6._run)
    assert "def room_for(cells: int)" in src
    assert "key=lambda r: table_touched.get(r, -1)" in src
    assert "if r != rule" in src, "the current rule must not be discarded for itself"


def test_an_arm_that_cannot_afford_a_cell_still_answers_and_pays_the_scan():
    src = inspect.getsource(A6._run)
    assert "cells_refused += 1" in src
    body = src[src.index("cache_misses += 1"):src.index("charge(1)\n        if rule not in")]
    assert "verdict = _unanimous(survivors, index)" in body
    assert body.index("verdict = _unanimous") < body.index("if room_for(1):"), (
        "the verdict must be computed before the store decides it cannot keep it")


def test_the_policy_is_named_as_a_choice_in_the_plan():
    charge = X7_PLAN["the_charge"]
    assert "WHOLE TABLES" in charge
    assert "declaring it is better" in charge
    assert "discard policy" in X7_PLAN["what_this_does_not_establish"]


# --- every terminal is reachable ---------------------------------------------

def _v(**over) -> dict:
    base = {"V1_survives_the_honest_price": True,
            "V4_response_to_price_is_monotone": True}
    base.update(over)
    return base


OK_PLACEBO = {"comparable": True, "reproduces_x6": True}
OK_INVARIANCE = {"holds": True, "offenders": []}


def test_a_failed_placebo_voids_the_study():
    terminal, reason = R._terminal(
        [], _v(), {"comparable": True, "reproduces_x6": False}, OK_INVARIANCE)
    assert terminal == "VOID_THE_PLACEBO_DOES_NOT_REPRODUCE_X6"
    assert "VOID" in reason


def test_a_price_leaking_into_a_tableless_arm_voids_the_study():
    terminal, _ = R._terminal([], _v(), OK_PLACEBO, {"holds": False, "offenders": [1]})
    assert terminal == "VOID_A_PRICE_MOVED_AN_ARM_THAT_HOLDS_NO_TABLE"


def test_the_kill_terminal_is_reachable_and_names_x6_as_the_artefact():
    terminal, reason = R._terminal(
        [], _v(V1_survives_the_honest_price=False), OK_PLACEBO, OK_INVARIANCE)
    assert terminal == "X6_WAS_AN_ARTEFACT_OF_A_FREE_TABLE"
    assert "does NOT survive an accounting consistent with DEV-3's" in reason
    assert "X6's receipt is unchanged" in reason


def test_a_non_monotone_price_response_is_a_separate_terminal_not_a_footnote():
    terminal, reason = R._terminal(
        [], _v(V4_response_to_price_is_monotone=False), OK_PLACEBO, OK_INVARIANCE)
    assert terminal == "SURVIVES_BUT_THE_PRICE_RESPONSE_IS_NOT_MONOTONE"
    assert "discard policy" in reason


def test_the_positive_terminal_requires_both_the_survival_and_the_monotone_shape():
    terminal, _ = R._terminal([], _v(), OK_PLACEBO, OK_INVARIANCE)
    assert terminal == "CARRY_ADVANTAGE_SURVIVES_A_PRICED_TABLE"


# --- the receipt -------------------------------------------------------------

def test_the_terminal_follows_from_the_published_grid():
    doc = _doc()
    assert R._terminal(doc["primary_grid"], doc["predictions"], doc["placebo"],
                       doc["price_invariance"])[0] == doc["terminal"]


def test_the_placebo_was_compared_against_x6_cell_by_cell():
    p = _doc()["placebo"]
    if not p.get("comparable"):
        pytest.skip("X6 receipt absent")
    assert p["cells_compared"] > 0
    assert p["mismatches"] == []


def test_the_tableless_arms_did_not_move_with_the_price():
    assert _doc()["price_invariance"]["holds"]
    assert _doc()["price_invariance"]["offenders"] == []


def test_the_counter_identity_holds_exactly_in_every_cell():
    for cell in _doc()["primary_grid"]:
        for arm, row in cell["arms"].items():
            assert row["counter_identity_residual"] == 0, (arm, cell["cell_bits"])


def test_every_quoted_work_figure_is_at_matched_correctness():
    for cell in _doc()["primary_grid"]:
        if any(v is not None for v in cell["ratio_to_replay"].values()):
            assert cell["arms"]["REPLAY_ONLY_PARENT"]["min_correctness"] == 1.0
        for row in cell["arms"].values():
            if row["work"] is not None:
                assert row["min_correctness"] == 1.0


def test_the_surviving_price_is_read_from_the_sweep_and_not_asserted():
    doc = _doc()
    counts = doc["winning_setting_counts_by_price"]["PRECOMPILED_DEMAND"]
    highest = doc["highest_price_the_advantage_survives"]
    if highest is None:
        assert all(v == 0 for v in counts.values())
    else:
        assert counts[str(highest)] > 0
        for p in CELL_BIT_PRICES:
            if p > highest:
                assert counts[str(p)] == 0


def test_refuted_predictions_are_published_as_refuted():
    preds = _doc()["predictions"]
    assert set(preds) == {
        "V0_placebo_reproduces_x6", "V1_survives_the_honest_price",
        "V2_advantage_is_smaller_when_paid_for", "V3_eager_loses_more_than_demand",
        "V4_response_to_price_is_monotone", "V5_dies_below_eight_bits_per_cell"}
    assert all(isinstance(v, bool) for v in preds.values())


def test_nothing_is_withdrawn_from_x6():
    assert "withdraws nothing from X6" in _doc()["authority"]


def test_no_novelty_is_claimed_for_charging_storage():
    assert _doc()["novelty"].startswith("NONE CLAIMED")
