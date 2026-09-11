from math import isclose

import pytest

from gmi_realization_microscope import (
    LifetimeLine,
    Realization,
    affine_horizon_crossover,
    bounded_search_optimum,
    calibration_receipt,
    complete_lifetime_cost,
    normative_optimum,
    realization_frontier,
    scalar_cost,
    scalar_optimum,
)


def test_semantic_admissibility_precedes_resource_efficiency():
    candidates = (
        Realization("good", True, 1.0, (2.0, 2.0)),
        Realization("wrong_but_free", False, 1.0, (0.0, 0.0)),
    )
    assert tuple(c.name for c in realization_frontier(candidates, capability_floor=1.0)) == (
        "good",
    )


def test_pareto_frontier_retains_incomparable_and_removes_dominated():
    candidates = (
        Realization("A", True, 1.0, (1.0, 4.0)),
        Realization("B", True, 1.0, (4.0, 1.0)),
        Realization("D", True, 1.0, (5.0, 5.0)),
    )
    assert tuple(c.name for c in realization_frontier(candidates, capability_floor=1.0)) == (
        "A",
        "B",
    )


def test_price_vectors_reverse_incomparable_winner():
    candidates = (
        Realization("A", True, 1.0, (1.0, 4.0)),
        Realization("B", True, 1.0, (4.0, 1.0)),
    )
    assert scalar_optimum(candidates, capability_floor=1.0, weights=(1.0, 0.1)) == ("A",)
    assert scalar_optimum(candidates, capability_floor=1.0, weights=(0.1, 1.0)) == ("B",)


def test_negative_price_is_rejected():
    with pytest.raises(ValueError, match="non-negative"):
        scalar_cost((1.0, 2.0), (1.0, -1.0))


def test_affine_horizon_crossover_is_exact():
    high_build = LifetimeLine("high", 10.0, 1.0)
    low_build = LifetimeLine("low", 1.0, 3.0)
    assert isclose(affine_horizon_crossover(high_build, low_build), 4.5)
    assert low_build.cost(2.0) < high_build.cost(2.0)
    assert high_build.cost(10.0) < low_build.cost(10.0)


def test_parallel_lifetime_lines_have_no_unique_crossover():
    assert affine_horizon_crossover(
        LifetimeLine("a", 1.0, 2.0), LifetimeLine("b", 3.0, 2.0)
    ) is None


def test_negative_horizon_is_rejected():
    with pytest.raises(ValueError, match="non-negative"):
        LifetimeLine("a", 1.0, 2.0).cost(-1.0)


def test_discovery_cost_can_reverse_serving_only_ranking():
    serving_a = 5 * 1.0
    serving_b = 5 * 3.0
    assert serving_a < serving_b

    full_a = complete_lifetime_cost(
        discovery_cost=20.0,
        build_cost=0.0,
        per_use_cost=1.0,
        horizon=5.0,
    )
    full_b = complete_lifetime_cost(
        discovery_cost=0.0,
        build_cost=0.0,
        per_use_cost=3.0,
        horizon=5.0,
    )
    assert full_a > full_b


def test_bounded_search_can_miss_normative_optimum():
    candidates = {
        "A": Realization("A", True, 1.0, (5.0,)),
        "B": Realization("B", True, 1.0, (3.0,)),
        "C": Realization("C", True, 1.0, (1.0,)),
    }
    assert normative_optimum(
        candidates.values(), capability_floor=1.0, weights=(1.0,)
    ) == ("C",)
    assert bounded_search_optimum(
        candidates,
        proposal_order=("A", "B", "C"),
        budget=2,
        capability_floor=1.0,
        weights=(1.0,),
    ) == ("B",)


def test_unknown_proposal_identity_is_rejected():
    candidates = {"A": Realization("A", True, 1.0, (1.0,))}
    with pytest.raises(KeyError, match="unknown realization"):
        bounded_search_optimum(
            candidates,
            proposal_order=("missing",),
            budget=1,
            capability_floor=1.0,
            weights=(1.0,),
        )


def test_calibration_receipt_is_frozen():
    receipt = calibration_receipt()
    assert receipt["frontier"] == ("A", "B")
    assert receipt["price_vector_1_optimum"] == ("A",)
    assert receipt["price_vector_2_optimum"] == ("B",)
    assert isclose(receipt["horizon_crossover"], 4.5)
    assert receipt["cost_at_h2"]["LOW_BUILD_HIGH_USE"] < receipt["cost_at_h2"]["HIGH_BUILD_LOW_USE"]
    assert receipt["cost_at_h10"]["HIGH_BUILD_LOW_USE"] < receipt["cost_at_h10"]["LOW_BUILD_HIGH_USE"]
    assert receipt["discovery_reversal"]["serving_only_A"] < receipt["discovery_reversal"]["serving_only_B"]
    assert receipt["discovery_reversal"]["full_lifetime_A"] > receipt["discovery_reversal"]["full_lifetime_B"]
    assert receipt["normative_optimum"] == ("C",)
    assert receipt["bounded_search_optimum"] == ("B",)
    assert receipt["terminal"] == "GMI_REALIZATION_FINITE_CALIBRATION_GREEN_V1"
