"""Hostile tests for the four-term lifecycle ledger.

The ledger exists to stop one specific thing: a cost term that is absent rather
than wrong.  An absent term has no error bar, does not announce itself, and moves
the SIGN of a comparison rather than its magnitude.  So the tests below spend
most of their effort on the incomplete case, and one of them reproduces the exact
inversion that a free storage term produced in a real study.
"""

from __future__ import annotations

import pathlib
import random
import sys

import pytest

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import lifecycle_ledger as L
from ocm.kso.resources import COORDINATES, ResourceVector as RV

FLAT = {name: 1.0 for name in COORDINATES}


def _ledger(**over):
    base = dict(
        subject="compiled verdict table", parent="naive scan", population="fixture",
        parent_cost=RV(composition_work=1000),
        preparation=L.charged("PREPARATION", RV(composition_work=50)),
        per_use=L.charged("PER_USE", RV(composition_work=1)),
        occupancy=L.charged("OCCUPANCY", RV(memory_bytes=2)),
        invalidation=L.charged("INVALIDATION", RV(composition_work=50)),
        epochs=3, uses=400, steps_held=100, invalidations=2)
    base.update(over)
    return L.LifecycleLedger(**base)


# --- a charge is priced or declared uncharged, never neither -----------------

def test_a_charge_cannot_be_both_priced_and_uncharged():
    with pytest.raises(ValueError):
        L.Charge(term="PER_USE", vector=RV(), uncharged_reason="also this")


def test_a_charge_cannot_be_silently_empty():
    """The whole failure mode in one test: a term left out must not be
    constructible as an innocuous blank."""
    with pytest.raises(ValueError) as caught:
        L.Charge(term="PER_USE")
    assert "exactly what this ledger exists to catch" in str(caught.value)


def test_an_uncharged_term_needs_a_real_reason():
    with pytest.raises(ValueError):
        L.uncharged("OCCUPANCY", "   ")


def test_a_charge_cannot_sit_in_the_wrong_slot():
    with pytest.raises(ValueError):
        _ledger(occupancy=L.charged("PER_USE", RV(memory_bytes=2)))


def test_an_unknown_term_is_refused():
    with pytest.raises(ValueError):
        L.charged("MAINTENANCE", RV())


def test_the_four_terms_are_the_four_both_lanes_found():
    assert L.TERMS == ("PREPARATION", "PER_USE", "OCCUPANCY", "INVALIDATION")


# --- multiplicities ----------------------------------------------------------

def test_an_object_that_was_never_built_has_no_ledger():
    with pytest.raises(ValueError):
        _ledger(epochs=0)


def test_more_invalidations_than_epochs_is_refused():
    with pytest.raises(ValueError):
        _ledger(epochs=2, invalidations=5)


def test_a_negative_multiplicity_is_refused():
    with pytest.raises(ValueError):
        _ledger(uses=-1)


def test_the_fixed_side_is_multiplied_by_epochs_not_paid_once():
    """A representation rebuilt after every reset pays preparation every time.
    Charging it once is how a lifecycle claim becomes optimistic."""
    one = _ledger(epochs=1, invalidations=0)
    many = _ledger(epochs=5, invalidations=4)
    assert many.total().composition_work > one.total().composition_work


# --- the identity ------------------------------------------------------------

def test_the_sum_of_the_parts_is_the_whole():
    assert _ledger().identity()["holds"]


def test_the_identity_holds_over_random_ledgers():
    rng = random.Random(20260908)
    for _ in range(200):
        def vector():
            return RV(**{name: rng.randrange(0, 5) for name in COORDINATES})
        epochs = rng.randrange(1, 6)
        led = _ledger(preparation=L.charged("PREPARATION", vector()),
                      per_use=L.charged("PER_USE", vector()),
                      occupancy=L.charged("OCCUPANCY", vector()),
                      invalidation=L.charged("INVALIDATION", vector()),
                      epochs=epochs, uses=rng.randrange(0, 50),
                      steps_held=rng.randrange(0, 50),
                      invalidations=rng.randrange(0, epochs + 1))
        assert led.identity()["holds"]


def test_scaling_a_vector_is_repeated_addition():
    rng = random.Random(7)
    for _ in range(50):
        vector = RV(**{name: rng.randrange(0, 9) for name in COORDINATES})
        n = rng.randrange(0, 6)
        summed = RV()
        for _ in range(n):
            summed = summed + vector
        assert L._scale(vector, n) == summed


# --- the rule that matters ---------------------------------------------------

def test_an_incomplete_ledger_may_not_claim_a_net_benefit():
    led = _ledger(occupancy=L.uncharged("OCCUPANCY", "storage was not metered"))
    scalar = L.scalar_margin(led, FLAT)
    assert scalar["margin"] > 0, "the fixture must be one that WOULD look like a win"
    assert scalar["net_benefit_claimable"] is False
    assert scalar["claim_strength"] == "BOUND_ONLY"
    assert "OCCUPANCY" in scalar["why_not_claimable"]


def test_an_incomplete_ledger_reports_its_terminal_as_a_bound():
    led = _ledger(invalidation=L.uncharged("INVALIDATION", "no drift data yet"))
    doc = L.report(led, FLAT)
    assert doc["terminal"] == "INCOMPLETE_LEDGER_BOUND_ONLY"
    assert doc["terms"]["INVALIDATION"]["charged"] is False
    assert doc["terms"]["INVALIDATION"]["reason"] == "no drift data yet"


def test_the_reading_says_which_direction_an_uncharged_term_can_move_things():
    led = _ledger(occupancy=L.uncharged("OCCUPANCY", "not metered"))
    reading = L.pareto_verdict(led)["reading"]
    assert "UPPER BOUND" in reading
    assert "only move the comparison against the object" in reading


def test_charging_a_previously_uncharged_term_never_helps_the_object():
    """A cost cannot be negative, so billing something previously free can only
    shrink the margin. If this ever fails, some term is being credited."""
    rng = random.Random(11)
    for _ in range(100):
        vector = RV(**{name: rng.randrange(0, 7) for name in COORDINATES})
        free = _ledger(occupancy=L.uncharged("OCCUPANCY", "not metered"))
        billed = _ledger(occupancy=L.charged("OCCUPANCY", vector))
        assert L.scalar_margin(billed, FLAT)["margin"] <= \
            L.scalar_margin(free, FLAT)["margin"]


def test_a_complete_ledger_may_claim_one():
    scalar = L.scalar_margin(_ledger(), FLAT)
    assert scalar["claim_strength"] == "MEASURED"
    assert scalar["net_benefit_claimable"] is True
    assert scalar["why_not_claimable"] is None


# --- prices travel with the number -------------------------------------------

def test_a_scalar_margin_requires_every_coordinate_to_have_a_declared_price():
    with pytest.raises(ValueError) as caught:
        L.scalar_margin(_ledger(), {"memory_bytes": 1.0})
    assert "missing" in str(caught.value)


def test_a_negative_price_is_refused():
    prices = dict(FLAT, memory_bytes=-1.0)
    with pytest.raises(ValueError):
        L.scalar_margin(_ledger(), prices)


def test_the_prices_are_published_with_the_margin_they_produced():
    scalar = L.scalar_margin(_ledger(), FLAT)
    assert set(scalar["prices"]) == set(COORDINATES)


def test_the_pareto_verdict_never_needs_a_price():
    verdict = L.pareto_verdict(_ledger())
    assert "prices" not in verdict


def test_coordinates_that_disagree_are_reported_incomparable_not_averaged():
    led = _ledger(parent_cost=RV(composition_work=100, memory_bytes=100000),
                  occupancy=L.charged("OCCUPANCY", RV(memory_bytes=1)))
    assert L.pareto_verdict(led)["verdict"] == "INCOMPARABLE_WITHOUT_A_PRICE"


# --- break-even --------------------------------------------------------------

def test_an_object_that_costs_more_per_use_has_no_horizon_rather_than_a_huge_one():
    led = _ledger(per_use=L.charged("PER_USE", RV(composition_work=999)))
    out = L.break_even_uses(led, FLAT)
    assert out["break_even_uses"] is None
    assert "no reuse horizon repays it" in out["why"]
    assert "the fixed cost is not the obstacle" in out["why"]


def test_an_incomplete_ledger_has_no_horizon_only_a_floor():
    led = _ledger(preparation=L.uncharged("PREPARATION", "build was not instrumented"))
    out = L.break_even_uses(led, FLAT)
    assert out["break_even_uses"] is None
    assert out["claim_strength"] == "BOUND_ONLY"


def test_the_break_even_is_where_the_margin_actually_turns():
    led = _ledger()
    horizon = L.break_even_uses(led, FLAT)["break_even_uses"]
    assert horizon is not None
    parent_per_use = L.scalar_margin(led, FLAT)["parent_value"] / led.uses
    at = _ledger(uses=horizon, parent_cost=RV(
        composition_work=round(parent_per_use * horizon)))
    below = _ledger(uses=horizon - 1, parent_cost=RV(
        composition_work=round(parent_per_use * (horizon - 1))))
    assert L.scalar_margin(at, FLAT)["margin"] >= 0
    assert L.scalar_margin(below, FLAT)["margin"] < \
        L.scalar_margin(at, FLAT)["margin"]


# --- right censoring ---------------------------------------------------------

def test_a_censored_window_says_its_totals_are_floors():
    reading = L.pareto_verdict(_ledger(right_censored=True))["reading"]
    assert "still in use" in reading
    assert L.report(_ledger(right_censored=True))["right_censored"] is True


# --- the regression this ledger was built from -------------------------------

def test_a_free_storage_term_inverts_a_real_published_ordering():
    """X7 measured this. With storage free, an arm that compiles every index and
    an arm that compiles only what is demanded win 13 and 14 of 18 settings and
    look like the same lever. Charge storage at two bits a cell and they become 2
    and 13. The ledger must reproduce that inversion: eager holds the whole
    extension, demand holds only what was asked for, and nothing else differs."""
    extension_cells, demanded_cells = 16, 14
    def arm(cells: int, occupancy_charged: bool):
        occupancy = (L.charged("OCCUPANCY", RV(memory_bytes=2 * cells))
                     if occupancy_charged else
                     L.uncharged("OCCUPANCY", "X6 charged the table nothing to hold"))
        return L.LifecycleLedger(
            subject=f"table holding {cells} cells", parent="naive scan",
            population="X7 level 3, skewed demand",
            parent_cost=RV(composition_work=1000),
            preparation=L.charged("PREPARATION", RV(composition_work=40)),
            per_use=L.charged("PER_USE", RV(composition_work=1)),
            occupancy=occupancy,
            invalidation=L.charged("INVALIDATION", RV(composition_work=40)),
            epochs=20, uses=400, steps_held=400, invalidations=19)

    free_eager = L.scalar_margin(arm(extension_cells, False), FLAT)
    free_demand = L.scalar_margin(arm(demanded_cells, False), FLAT)
    assert free_eager["margin"] == free_demand["margin"], (
        "with storage free the two arms are indistinguishable, which is exactly the "
        "reading X6 published and X7 overturned")
    assert free_eager["net_benefit_claimable"] is False, (
        "and neither of them may claim a net benefit while the term is uncharged")

    billed_eager = L.scalar_margin(arm(extension_cells, True), FLAT)
    billed_demand = L.scalar_margin(arm(demanded_cells, True), FLAT)
    assert billed_demand["margin"] > billed_eager["margin"], (
        "charging storage must separate the arm that holds everything from the one "
        "that holds what was asked for")
    assert billed_eager["margin"] < free_eager["margin"]


def test_the_ledger_authorizes_nothing():
    doc = L.report(_ledger(), FLAT)
    text = doc["what_this_does_not_establish"]
    assert "does not authorize" in text
    assert "no policy, lifecycle gate or production behaviour is" in text
