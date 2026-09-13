#!/usr/bin/env python3
"""Exact checks for FAMILY_FRONTIER_PHASE_THEOREM_V1.

All numeric profiles here are synthetic theorem witnesses. They verify selection
logic only and are not empirical claims about real hardware.
"""

import json


class PhaseInputError(ValueError):
    """A registered family interval is not a well-formed certified bound."""


def robust_scalar_winner(intervals):
    # Malformed bounds must be rejected rather than compared: two families with
    # `lower > upper` both satisfy the unvalidated robustness test. See
    # FAMILY_PHASE_SOUNDNESS_CORRECTION_V1.md.
    if not intervals:
        raise PhaseInputError("no registered family interval")
    for fam, (lo, hi) in intervals.items():
        if lo > hi:
            raise PhaseInputError(f"{fam}: lower bound {lo} exceeds upper bound {hi}")
    winners = []
    for fam, (lo, hi) in intervals.items():
        if all(hi < other_lo for other, (other_lo, other_hi) in intervals.items() if other != fam):
            winners.append(fam)
    assert len(winners) <= 1
    return winners[0] if winners else "UNDECIDED_FROM_CURRENT_EVIDENCE"


def phase_intervals(s):
    rows = {
        "NEURAL": (4 + s, 5 + s),
        "NON_NEURAL": (1 + 2 * s, 2 + 2 * s),
    }
    if s >= 6:
        rows["HYBRID"] = (3 + s // 2, 4 + s // 2)
    return rows


def vector_dominates_upper_lower(upper_a, lower_b):
    return all(a <= b for a, b in zip(upper_a, lower_b)) and any(a < b for a, b in zip(upper_a, lower_b))


def main():
    expected = {
        1: "NON_NEURAL",
        2: "UNDECIDED_FROM_CURRENT_EVIDENCE",
        3: "UNDECIDED_FROM_CURRENT_EVIDENCE",
        4: "UNDECIDED_FROM_CURRENT_EVIDENCE",
        5: "NEURAL",
        6: "HYBRID",
        7: "HYBRID",
        8: "HYBRID",
    }

    observed = {}
    for s in range(1, 9):
        observed[s] = robust_scalar_winner(phase_intervals(s))
        assert observed[s] == expected[s]

    # FP-1 vector robust-exclusion witness.
    upper_a = (4, 7, 3)
    lower_b = (5, 7, 9)
    assert vector_dominates_upper_lower(upper_a, lower_b)
    assert not vector_dominates_upper_lower((6, 7, 3), lower_b)

    # FP-5 hybrid-decomposition witness under a declared additive scalar model.
    # A pure-family lower bound sums registered *lower* bounds only. The
    # predecessor witness summed `neural_smooth_upper` and
    # `nonneural_exact_upper` into lower bounds; both regional lower bounds are
    # now registered explicitly. The exclusion is valid only over candidates
    # that factor through the registered regions.
    neural_smooth_lower = 4
    neural_smooth_upper = 4
    neural_exact_lower = 8
    nonneural_smooth_lower = 9
    nonneural_exact_lower = 3
    nonneural_exact_upper = 3
    bridge_upper = 1
    assert neural_smooth_lower <= neural_smooth_upper
    assert nonneural_exact_lower <= nonneural_exact_upper
    hybrid_upper = neural_smooth_upper + nonneural_exact_upper + bridge_upper
    pure_neural_lower = neural_smooth_lower + neural_exact_lower
    pure_nonneural_lower = nonneural_smooth_lower + nonneural_exact_lower
    assert hybrid_upper == 8
    assert pure_neural_lower == 12
    assert pure_nonneural_lower == 12
    assert hybrid_upper < min(pure_neural_lower, pure_nonneural_lower)
    # Without the registered smooth-region neural lower bound, non-negativity
    # alone gives 8, which does not strictly exceed the hybrid upper bound.
    unregistered_neural_lower = 0 + neural_exact_lower
    assert not hybrid_upper < unregistered_neural_lower

    # FP-4 semantics alone cannot choose a family: opposite legal resource
    # orderings over response-equivalent realizations reverse selection.
    world_1 = {"NEURAL": 1, "NON_NEURAL": 2}
    world_2 = {"NEURAL": 2, "NON_NEURAL": 1}
    assert min(world_1, key=world_1.get) == "NEURAL"
    assert min(world_2, key=world_2.get) == "NON_NEURAL"

    receipt = {
        "terminal": "GRAND_GMI_FAMILY_FRONTIER_PHASE_TRANCHE_ALL_GREEN",
        "task_scales_checked": 8,
        "phase_verdicts": {str(k): v for k, v in observed.items()},
        "robust_vector_exclusion_witness": True,
        "hybrid_upper_bound": hybrid_upper,
        "pure_neural_lower_bound": pure_neural_lower,
        "pure_non_neural_lower_bound": pure_nonneural_lower,
        "pure_family_lower_bounds_sum_registered_lower_bounds": True,
        "hybrid_exclusion_requires_decomposition_closed_candidates": True,
        "hybrid_robustly_selected_in_synthetic_decomposition": True,
        "response_equivalent_family_selection_can_reverse_with_resource_model": True,
        "empirical_hardware_cost_claimed": False,
    }
    print(json.dumps(receipt, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
