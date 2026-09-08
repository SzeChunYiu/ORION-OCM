from __future__ import annotations

from fractions import Fraction as F

import pytest

import r0d_paid_decision_region as R


def test_decision_region_and_ecd_stop_before_full_identification():
    problem = R.partition_problem()
    lookup = F(1, 4)
    identity = R.solve(problem, "P-ID", policy_lookup_cost=lookup)
    ecd = R.solve(problem, "P-ECD", policy_lookup_cost=lookup)
    drd = R.solve(problem, "P-DRD", policy_lookup_cost=lookup)
    paid = R.solve(problem, "P-PAID", policy_lookup_cost=lookup)

    assert identity.total_cost == F(11, 4)
    assert identity.worst_probe_count == 2
    assert ecd.total_cost == drd.total_cost == paid.total_cost == F(3, 2)
    assert ecd.worst_probe_count == drd.worst_probe_count == paid.worst_probe_count == 1
    assert drd.total_cost < identity.total_cost


def test_region_predicate_price_has_exact_five_eighths_break_even():
    problem = R.partition_problem()
    lookup = F(1, 4)
    identity = R.solve(problem, "P-ID", policy_lookup_cost=lookup)
    below = R.solve(problem, "P-DRD", policy_lookup_cost=lookup, region_predicate_cost=F(1, 2))
    tie = R.solve(problem, "P-DRD", policy_lookup_cost=lookup, region_predicate_cost=F(5, 8))
    above = R.solve(problem, "P-DRD", policy_lookup_cost=lookup, region_predicate_cost=F(3, 4))

    assert below.total_cost == F(5, 2) < identity.total_cost
    assert tie.total_cost == identity.total_cost == F(11, 4)
    assert above.total_cost == F(3) > identity.total_cost
    assert below.worst_probe_count == tie.worst_probe_count == above.worst_probe_count == 1


def test_fewer_probes_can_cost_more_when_region_predicate_is_charged():
    problem = R.partition_problem()
    lookup = F(1, 4)
    identity = R.solve(problem, "P-ID", policy_lookup_cost=lookup)
    naive_drd = R.solve(
        problem,
        "P-DRD",
        policy_lookup_cost=lookup,
        region_predicate_cost=F(1),
    )

    assert identity.total_cost == F(11, 4)
    assert naive_drd.total_cost == F(7, 2)
    assert naive_drd.worst_probe_count == 1 < identity.worst_probe_count == 2
    assert naive_drd.total_cost > identity.total_cost


def test_safe_action_does_not_imply_economic_stop():
    problem = R.economic_problem(F(2))
    root = frozenset(problem.hypotheses)
    assert R.cheapest_common_action(problem, root) == ("safe", F(10))

    identity = R.solve(problem, "P-ID", policy_lookup_cost=F(1, 4))
    drd = R.solve(problem, "P-DRD", policy_lookup_cost=F(1, 4))
    paid = R.solve(problem, "P-PAID", policy_lookup_cost=F(1, 4))

    assert identity.total_cost == paid.total_cost == F(7, 2)
    assert identity.root_choice == paid.root_choice == "PROBE:which"
    assert drd.total_cost == F(41, 4)
    assert drd.root_choice == "STOP"
    assert paid.total_cost < drd.total_cost


def test_paid_information_has_exact_35_over_4_break_even():
    lookup = F(1, 4)
    below = R.solve(R.economic_problem(F(8)), "P-PAID", policy_lookup_cost=lookup)
    tie = R.solve(R.economic_problem(F(35, 4)), "P-PAID", policy_lookup_cost=lookup)
    above = R.solve(R.economic_problem(F(9)), "P-PAID", policy_lookup_cost=lookup)

    assert below.total_cost == F(19, 2) < F(41, 4)
    assert below.root_choice == "PROBE:which"
    assert tie.total_cost == F(41, 4)
    assert above.total_cost == F(41, 4)
    assert above.root_choice == "STOP"


def test_paid_parent_stops_when_information_is_too_expensive():
    problem = R.economic_problem(F(10))
    identity = R.solve(problem, "P-ID", policy_lookup_cost=F(1, 4))
    drd = R.solve(problem, "P-DRD", policy_lookup_cost=F(1, 4))
    paid = R.solve(problem, "P-PAID", policy_lookup_cost=F(1, 4))

    assert identity.total_cost == F(23, 2)
    assert drd.total_cost == paid.total_cost == F(41, 4)
    assert paid.root_choice == "STOP"
    assert paid.terminal_action == "safe"


def test_identical_complete_legal_transcript_with_disjoint_actions_is_detected():
    problem = R.misspecification_collision_problem()
    collisions = R.observation_action_collisions(problem)
    assert collisions == [{
        "transcript": ["same"],
        "worlds": ["declared_like", "out_of_class_hostile"],
    }]
    with pytest.raises(R.Unsolvable):
        R.solve(problem, "P-DRD")


def test_ecd_requires_a_registered_partition_and_rejects_bad_models():
    with pytest.raises(ValueError, match="P-ECD requires"):
        R.solve(R.economic_problem(F(2)), "P-ECD")

    bad = R.Problem(
        hypotheses=("h",),
        safe_actions={"h": frozenset()},
        action_costs={},
        probes=(),
        probe_costs={},
        outcomes={},
    )
    with pytest.raises(ValueError, match="no protected action"):
        bad.validate()


def test_receipt_preserves_source_custody_and_no_ml_claim_boundary():
    receipt = R.build_receipt()
    assert receipt["terminal"] == "R0D_EXECUTABLE_PARENT_ESTABLISHED_SYNTHETIC_ONLY"
    assert receipt["ml_authorized"] is False
    assert receipt["source_custody"]["DEV5"]["commit"] == "a0c4931629263ee92fe676e479445b188af5df6e"
    assert receipt["source_custody"]["DEV6"]["commit"] == "f676a34e022fff710a05cede0ea6027a8c390e28"
    assert receipt["source_custody"]["X1"]["commit"] == "2ba88a80593a8e3ddcbedaf6520da5bc7fddbed3"
    assert receipt["cases"]["predicate_cost_can_dominate"]["fewer_probes_but_more_total_cost"] is True
    assert receipt["cases"]["observation_hypothesis_class_hostile"]["collision_count"] == 1
    assert any("operational R0D terminal remains unearned" in item for item in receipt["claim_boundary"])
