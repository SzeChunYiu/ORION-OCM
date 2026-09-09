from __future__ import annotations

import decision_core as D


def test_common_action_is_exactly_decision_region_containment():
    states = ("m0", "m1", "m2")
    actions = ("a", "b", "c")
    good = {
        "m0": {"a", "b"},
        "m1": {"b", "c"},
        "m2": {"b"},
    }
    version = ("m0", "m1", "m2")
    gamma = D.common_actions(version, good)
    regions = D.decision_regions(states, actions, good)
    contained = D.contained_decision_actions(version, regions)
    assert gamma == frozenset({"b"})
    assert gamma == contained


def test_shares_an_optimum_is_not_transitive_and_pairwise_overlap_is_not_enough():
    # Non-transitivity: x1~x2 and x2~x3 but not x1~x3.
    opt = {
        "x1": {"a"},
        "x2": {"a", "b"},
        "x3": {"b"},
    }
    assert opt["x1"] & opt["x2"]
    assert opt["x2"] & opt["x3"]
    assert not (opt["x1"] & opt["x3"])

    # Helly-style trap: all pairs overlap but no action works for the whole fiber.
    triangle = (
        {"a", "b"},
        {"b", "c"},
        {"c", "a"},
    )
    for i in range(3):
        for j in range(i + 1, 3):
            assert triangle[i] & triangle[j]
    assert not set.intersection(*(set(value) for value in triangle))


def test_feature_sufficiency_requires_one_common_optimum_per_whole_fiber():
    states = ("x1", "x2", "x3")
    actions = ("a", "b", "c")
    costs = {
        ("x1", "a"): 0, ("x1", "b"): 0, ("x1", "c"): 1,
        ("x2", "a"): 1, ("x2", "b"): 0, ("x2", "c"): 0,
        ("x3", "a"): 0, ("x3", "b"): 1, ("x3", "c"): 0,
    }
    one_fiber = {state: "z" for state in states}
    assert D.fiber_common_optima(states, actions, costs, one_fiber)["z"] == frozenset()
    assert D.exact_feature_sufficient(states, actions, costs, one_fiber) is False

    separated = {"x1": "left", "x2": "middle", "x3": "right"}
    assert D.exact_feature_sufficient(states, actions, costs, separated) is True


def test_feature_regret_floor_is_exact_and_zero_iff_common_optimum_here():
    states = ("x0", "x1")
    actions = ("a0", "a1")
    weights = {"x0": 0.5, "x1": 0.5}
    costs = {
        ("x0", "a0"): 0.0, ("x0", "a1"): 10.0,
        ("x1", "a0"): 10.0, ("x1", "a1"): 0.0,
    }
    collided = {"x0": "same", "x1": "same"}
    report = D.feature_regret_floor(states, actions, costs, weights, collided)
    assert report["full_information_cost"] == 0.0
    assert report["feature_cost"] == 5.0
    assert report["regret"] == 5.0

    full = {"x0": "x0", "x1": "x1"}
    report = D.feature_regret_floor(states, actions, costs, weights, full)
    assert report["regret"] == 0.0
    assert D.exact_feature_sufficient(states, actions, costs, full) is True


def test_common_safe_action_does_not_imply_metareasoning_should_stop():
    states = ("unknown", "m0", "m1")
    stop_cost = {"unknown": 10.0, "m0": 0.0, "m1": 0.0}
    cognitive_actions = {"unknown": ("probe",), "m0": (), "m1": ()}
    action_cost = {("unknown", "probe"): 1.0}
    transitions = {
        ("unknown", "probe"): ((0.5, "m0"), (0.5, "m1")),
    }
    values, policies = D.finite_meta_dp(
        states, stop_cost, cognitive_actions, action_cost, transitions, budget=1
    )
    assert values[0]["unknown"] == 10.0
    assert values[1]["unknown"] == 1.0
    assert policies[1]["unknown"] == "probe"


def test_current_output_equality_is_not_lifecycle_bisimulation():
    states = ("s0", "s1", "live", "dead")
    actions = {state: ("act",) for state in states}
    # s0 and s1 have the same current protected output/contract.
    contract = {
        ("s0", "act"): ("answer", "verified"),
        ("s1", "act"): ("answer", "verified"),
        ("live", "act"): ("answer", "verified"),
        ("dead", "act"): ("none", "revoked"),
    }
    transitions = {
        ("s0", "act"): ((1.0, "live"),),
        ("s1", "act"): ((1.0, "dead"),),
        ("live", "act"): ((1.0, "live"),),
        ("dead", "act"): ((1.0, "dead"),),
    }
    # Try to merge s0/s1 while keeping live/dead distinct: successor mass differs.
    blocks = {"s0": "current", "s1": "current", "live": "live", "dead": "dead"}
    assert D.is_contract_bisimulation(states, actions, contract, transitions, blocks) is False

    refined = {"s0": "s0", "s1": "s1", "live": "live", "dead": "dead"}
    assert D.is_contract_bisimulation(states, actions, contract, transitions, refined) is True


def test_observation_collision_with_disjoint_safe_sets_has_no_common_safe_action():
    good = {"theta_in": {"a"}, "theta_out": {"b"}}
    assert D.common_actions(("theta_in", "theta_out"), good) == frozenset()


def test_componentwise_dominance_equals_price_independent_direction_and_incomparability_has_witnesses():
    assert D.price_independent_dominates((1, 2, 3), (1, 4, 5)) is True
    assert D.price_independent_dominates((1, 5), (2, 4)) is False
    a_wins, b_wins = D.incomparable_price_witnesses((1, 5), (2, 4))
    assert a_wins == 0
    assert b_wins == 1


def test_local_method_saving_can_be_reversed_by_overhead():
    # Method A saves 50 but adds 60 overhead: whole machine loses.
    assert D.local_gain_beats_overhead(50, 160, 100, 100) is False
    assert 50 + 160 > 100 + 100
    # Same method saving with only 10 added overhead wins.
    assert D.local_gain_beats_overhead(50, 110, 100, 100) is True
    assert 50 + 110 < 100 + 100


def test_multislope_pruning_removes_options_that_pay_more_for_no_rate_gain():
    slopes = (
        (0.0, 10.0, "rent"),
        (4.0, 8.0, "useful"),
        (5.0, 9.0, "dominated"),
        (9.0, 3.0, "invest"),
    )
    pruned = D.prune_dominated_slopes(slopes)
    assert tuple(item[2] for item in pruned) == ("rent", "useful", "invest")
    assert D.multislope_monotone(pruned) is True
