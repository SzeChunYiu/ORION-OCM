from fractions import Fraction

import pytest

from gmi_semantic_proposal_geometry_exact import (
    NativeCandidate,
    calibration_receipt,
    first_hit,
    semantic_pushforward,
    semantic_surprisal_bits,
    semantic_target_mass,
    split_candidate_preserving_mass,
)


def test_pushforward_refinement_is_exactly_invariant():
    receipt = calibration_receipt()
    row = receipt["pushforward_refinement"]
    assert row["coarse_native_count"] == 3
    assert row["refined_native_count"] == 4
    assert row["invariant"] is True
    assert row["coarse_semantic_distribution"] == {
        "ALTERNATIVE": Fraction(1, 4),
        "FAIL": Fraction(1, 2),
        "TARGET": Fraction(1, 4),
    }
    assert row["refined_semantic_distribution"] == row["coarse_semantic_distribution"]


def test_different_native_spaces_can_induce_same_semantic_target_mass():
    row = calibration_receipt()["cross_native_space_target_mass"]
    assert row["coarse"] == Fraction(1, 4)
    assert row["bayes_like"] == Fraction(1, 4)


def test_probabilistic_k1_shift_is_exactly_one_bit():
    row = calibration_receipt()["probabilistic_k1_calibration"]
    assert row["reset_target_mass"] == Fraction(1, 8)
    assert row["continued_target_mass"] == Fraction(1, 4)
    assert row["reset_surprisal_bits"] == pytest.approx(3.0)
    assert row["continued_surprisal_bits"] == pytest.approx(2.0)
    assert row["surprisal_reduction_bits"] == pytest.approx(1.0)


def test_deterministic_k1_shift_is_exactly_one_bit():
    row = calibration_receipt()["deterministic_k1_calibration"]
    assert row["reset_first_hit_rank"] == 7
    assert row["continued_first_hit_rank"] == 3
    assert row["reset_first_hit_cost"] == Fraction(7, 1)
    assert row["continued_first_hit_cost"] == Fraction(3, 1)
    assert row["rank_information_shift_bits"] == pytest.approx(1.0)


def test_semantically_redundant_deterministic_proposals_still_cost_work():
    row = calibration_receipt()["semantic_duplication_resource_hostile"]
    assert row["compact_first_hit_rank"] == 2
    assert row["compact_first_hit_cost"] == Fraction(2, 1)
    assert row["duplicated_first_hit_rank"] == 3
    assert row["duplicated_first_hit_cost"] == Fraction(3, 1)


def test_split_must_preserve_probability_mass():
    candidates = (
        NativeCandidate("x", "TARGET", Fraction(1, 2)),
        NativeCandidate("y", "OTHER", Fraction(1, 2)),
    )
    with pytest.raises(ValueError, match="preserve source mass"):
        split_candidate_preserving_mass(
            candidates,
            "x",
            (("x1", Fraction(1, 4)), ("x2", Fraction(1, 8))),
        )


def test_probability_candidate_set_must_normalize():
    bad = (
        NativeCandidate("a", "A", Fraction(1, 3)),
        NativeCandidate("b", "B", Fraction(1, 3)),
    )
    with pytest.raises(ValueError, match="sum to one"):
        semantic_pushforward(bad)


def test_zero_target_mass_has_infinite_surprisal():
    candidates = (
        NativeCandidate("a", "A", Fraction(1, 2)),
        NativeCandidate("b", "B", Fraction(1, 2)),
    )
    assert semantic_target_mass(candidates, {"TARGET"}) == 0
    assert semantic_surprisal_bits(candidates, {"TARGET"}) == float("inf")


def test_first_hit_counts_actual_proposal_cost_not_semantic_classes():
    order = (
        NativeCandidate("a", "DISTRACTOR", Fraction(1, 3), Fraction(2, 1)),
        NativeCandidate("b", "DISTRACTOR", Fraction(1, 3), Fraction(5, 1)),
        NativeCandidate("c", "TARGET", Fraction(1, 3), Fraction(7, 1)),
    )
    hit = first_hit(order, {"TARGET"})
    assert hit.native_rank == 3
    assert hit.cumulative_cost == Fraction(14, 1)


def test_claim_boundary_remains_finite_and_parent_owned():
    receipt = calibration_receipt()
    assert receipt["terminal"] == "GMI_SEMANTIC_PROPOSAL_GEOMETRY_FINITE_EXACT_GREEN_V1"
    boundary = receipt["claim_boundary"].lower()
    assert "finite" in boundary
    assert "parent mathematics" in boundary
    assert "remains empirical" in boundary
