"""Integrity tests for E12, which runs a prediction frozen before its world existed.

The single most likely way this result is false is the way its own pilot was
false: an apparent confirmation produced by compression at large extension, with
perishability doing nothing. So the tests concentrate on the control -- that the
lam = 0 row is checked against arithmetic computed from the declared constants
with no reference to any run, that the grid actually spans both sides of that
break-even, and that a confirmation cannot be produced by a win at large
extension alone.
"""

from __future__ import annotations

import inspect
import json
import pathlib
import random

import pytest

import perish as P
import perish_arms as A
import run_perish as R
import synthesis as S
from retain import APPLY_COST, DERIVE_COST, INDUCE_COST, K_INDUCE, LOOKUP_COST, demand_stream

HERE = pathlib.Path(__file__).parent
RECEIPT = HERE / "results" / "PERISH_E12_V1.json"


# --- the prediction is the one that was frozen ------------------------------

def test_the_prediction_under_test_is_the_one_synthesis_froze():
    assert S.OUT_OF_SAMPLE["name"] == "PERISHABLE_EVIDENCE"
    assert P.SYNTHESIS_PREDICTION == S.OUT_OF_SAMPLE["predicted"]
    assert P.PERISH_PLAN["frozen_prediction"] == S.OUT_OF_SAMPLE["predicted"]


def test_the_synthesis_commitment_is_unchanged_by_this_experiment():
    """A prediction that can be edited after the fact is not a prediction."""
    assert S.COMMITMENT.commitment == S.commit(S.PLAN).commitment


# --- the control ------------------------------------------------------------

def test_the_analytic_control_uses_no_run_data():
    src = inspect.getsource(R.analytic_sign)
    for banned in ("world", "stream", "Ledger", "run_arm", "cell("):
        assert banned not in src, banned


def test_the_analytic_control_is_the_declared_cost_model():
    u = 100.0
    for m in (4, 32):
        memo = m * DERIVE_COST + (u - m) * LOOKUP_COST
        gen = K_INDUCE * DERIVE_COST + INDUCE_COST + (u - K_INDUCE) * APPLY_COST
        assert R.analytic_sign(m, u) == ("MACHINE" if gen < memo else "PARENT")


def test_the_grid_spans_both_sides_of_the_break_even():
    """A control with only wins in it controls nothing."""
    doc = json.loads(RECEIPT.read_text())
    signs = {r["analytic"] for r in doc["control"]["rows"]}
    assert signs == {"MACHINE", "PARENT"}, (
        "the lam=0 row must contain losses as well as wins")


def test_the_receipt_control_agrees_at_every_extension():
    doc = json.loads(RECEIPT.read_text())
    assert doc["control"]["all_agree"] is True
    for row in doc["control"]["rows"]:
        assert row["observed"] == row["analytic"], row["extension"]


def test_a_control_mismatch_voids_the_run():
    cells = [{"lam": 0.0, "extension": 32, "observed_sign": "MACHINE",
              "analytic_sign_at_lam_zero": "PARENT",
              "ratio_to_oracle_rule_parent": 2.0}]
    t, reason = R._terminal(cells, {"0.0": 32})
    assert t == "VOID_CONTROL_DISAGREES_WITH_THE_COST_MODEL"
    assert "nothing measured under it means anything" in reason


# --- a win at large extension alone must not confirm anything ---------------

def test_a_flat_crossover_refutes_rather_than_confirms():
    """The pilot's failure mode, encoded so it cannot recur silently."""
    cells = [{"lam": l, "extension": 32, "observed_sign": "MACHINE",
              "analytic_sign_at_lam_zero": "MACHINE",
              "ratio_to_oracle_rule_parent": 2.0} for l in P.PERISH_PLAN["sweep"]["lams"]]
    t, reason = R._terminal(cells, {str(l): 32 for l in P.PERISH_PLAN["sweep"]["lams"]})
    assert t == "FROZEN_PREDICTION_REFUTED"
    assert "demoted to a caching result" in reason


def test_the_kill_criterion_names_what_it_would_demote():
    kill = P.PERISH_PLAN["kill_criterion"]
    assert "SYNTHESIS_V1 must be demoted" in kill
    assert "does NOT confirm anything" in kill


def test_the_pilot_failure_is_disclosed_and_its_cause_named():
    d = P.PERISH_PLAN["pilot_disclosure"]
    assert "FAILED ITS OWN CONTROL" in d
    assert "That is false" in d, "the disclosure must name the wrong claim, not just the fix"
    assert "DERIVATIONS, not merely the number of bits" in d


def test_the_pilot_is_published_and_kept_on_a_separate_seed():
    doc = json.loads(RECEIPT.read_text())
    assert doc["pilot"], "the pilot rows must be published, not merely described"
    assert doc["commitment"]["pilot_seed"] != doc["commitment"]["protected_seed"]


# --- the world and the arms -------------------------------------------------

def test_perishability_is_the_only_thing_lam_changes():
    a = P.build_perish_world(16, 8, 0.0, 100)
    b = P.build_perish_world(16, 8, 4.0, 100)
    assert a.base.rule_of == b.base.rule_of
    assert a.base.members == b.base.members
    assert a.derive(0) == b.derive(0), "the ramp must start at the same price"
    assert b.derive(100) > a.derive(100)


def test_lam_zero_is_exactly_e10s_constant_cost():
    w = P.build_perish_world(16, 8, 0.0, 100)
    assert {w.derive(t) for t in range(0, 101, 10)} == {float(DERIVE_COST)}


@pytest.mark.parametrize("arm_id", sorted(A.ARMS))
def test_every_arm_answers_every_demand(arm_id):
    w = P.build_perish_world(16, 8, 4.0, 400)
    s = demand_stream(w.base, 400, 1.0, random.Random(2))
    led = A.run_arm(arm_id, w, s, 5)
    assert led.served == len(s)
    assert led.correctness() == 1.0


def test_no_arm_carries_a_storage_budget():
    """E12 must not reproduce E10 while sharing E10's scarcity machinery."""
    for arm_id, fn in A.ARMS.items():
        src = inspect.getsource(fn)
        for banned in ("budget", "evict", "FACT_BITS", "RULE_BITS"):
            assert banned not in src, (arm_id, banned)


def test_only_the_declared_clairvoyants_read_the_future():
    for arm_id in ("generalizing_arm", "memoizer_parent", "lazy_parent"):
        src = inspect.getsource(A.ARMS[arm_id])
        assert "set(stream)" not in src, arm_id
    assert "set(stream)" in inspect.getsource(A.clairvoyant_memoizer_parent)


def test_the_clairvoyant_buys_at_the_cheapest_moment():
    src = inspect.getsource(A.clairvoyant_memoizer_parent)
    assert "world.derive(0)" in src, (
        "an instance-optimal parent under a rising price must pre-derive at step 0")


def test_the_arm_is_a_memoizer_plus_induction_and_nothing_else():
    """So that arm-against-memoizer is a comparison of one thing."""
    src = inspect.getsource(A.generalizing_arm)
    assert "held.add(answer)" in src, "it must keep what it derives, as the memoizer does"
    assert "INDUCE_COST" in src
    assert "K_INDUCE" in src


# --- the adverse finding is not buried --------------------------------------

def test_the_deep_roots_question_is_answered_beside_the_law_not_under_it():
    doc = json.loads(RECEIPT.read_text())
    block = doc["the_deep_roots_question"]
    assert block["verdict"]
    if doc["predictions"]["P5_eager_beats_the_triggered_arm_somewhere"]:
        assert "NARROWED" in block["verdict"]
        assert block["cells_where_eager_beats_the_triggered_arm"]
    else:
        assert "SURVIVES" in block["verdict"]


def test_p5_was_registered_in_the_direction_least_flattering_to_the_machine():
    p5 = P.PERISH_PLAN["predictions_frozen_before_execution"]["P5_the_deep_roots_question"]
    assert "least flattering to the machine" in p5
    assert "that is the headline" in p5


# --- the receipt ------------------------------------------------------------

def test_the_receipt_calls_one_point_one_point():
    doc = json.loads(RECEIPT.read_text())
    assert doc["terminal"] == "FROZEN_PREDICTION_SURVIVES_ONE_TEST"
    assert "It is ONE point" in doc["terminal_reason"]
    assert "how cheap a confirmation can be" in doc["terminal_reason"]


def test_the_receipt_carries_the_plan_and_no_wall_clock():
    doc = json.loads(RECEIPT.read_text())
    assert doc["commitment"]["commitment"] == P.COMMITMENT.commitment
    assert doc["plan"] == json.loads(json.dumps(P.PERISH_PLAN))
    text = RECEIPT.read_text().lower()
    for banned in ("elapsed", "timestamp", "duration_ms", "wall"):
        assert banned not in text, banned


def test_the_receipt_states_what_it_does_not_establish():
    doc = json.loads(RECEIPT.read_text())
    for phrase in ("deterministic ramp", "bracket the real case",
                   "confirms a law far less than a failure would refute it"):
        assert phrase in doc["what_this_does_not_establish"], phrase
    assert "NONE CLAIMED" in doc["novelty"]
