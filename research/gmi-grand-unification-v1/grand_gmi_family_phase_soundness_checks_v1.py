#!/usr/bin/env python3
"""Exact checks for FAMILY_PHASE_SOUNDNESS_CORRECTION_V1.

Every number here is a synthetic theorem witness. The checks verify the
soundness of the family-phase selection logic itself: interval well-formedness,
what the crossover statement actually excludes, and which direction a declared
additive regional model may be used in. No empirical hardware cost is claimed.
"""

from fractions import Fraction
from itertools import product
import json


class PhaseInputError(ValueError):
    """A registered family interval is not a well-formed certified bound."""


def validate_intervals(intervals):
    """Reject malformed certified intervals instead of comparing them."""
    if not intervals:
        raise PhaseInputError("no registered family interval")
    for fam, bounds in intervals.items():
        if type(fam) is not str or not fam:
            raise PhaseInputError("family label must be a non-empty string")
        if type(bounds) is not tuple or len(bounds) != 2:
            raise PhaseInputError(f"{fam}: interval must be a (lower, upper) pair")
        lo, hi = bounds
        for value in bounds:
            if type(value) not in (int, Fraction):
                raise PhaseInputError(f"{fam}: non-exact bound {value!r}")
        if lo > hi:
            raise PhaseInputError(f"{fam}: lower bound {lo} exceeds upper bound {hi}")
    return intervals


def unvalidated_robust_winners(intervals):
    """The predecessor rule: compare bounds without validating them."""
    return [
        fam
        for fam, (_, hi) in intervals.items()
        if all(hi < lo for other, (lo, _) in intervals.items() if other != fam)
    ]


def robust_winner(intervals):
    """FP-2 with explicit input validation and explicit abstention."""
    validate_intervals(intervals)
    winners = unvalidated_robust_winners(intervals)
    if len(winners) > 1:
        raise PhaseInputError("validated well-formed intervals cannot have two winners")
    return winners[0] if winners else "UNDECIDED_FROM_CURRENT_EVIDENCE"


# --- Finding 1: the stated crossover condition excludes nothing -------------

WELL_FORMED_GRID = tuple(
    (Fraction(lo), Fraction(hi))
    for lo, hi in product(range(5), repeat=2)
    if lo <= hi
)


def check_stated_crossover_condition_is_vacuous():
    """In every robust-B configuration the predecessor FP-3 condition holds.

    Robust B means `U_B < L_A`. Well-formedness gives `L_B <= U_B` and
    `L_A <= U_A`, so `L_B <= U_B < L_A <= U_A`, hence `U_A >= L_B` already
    holds at the destination. The stated touch/overlap set therefore contains
    every robust-B parameter and cannot identify an intermediate boundary.
    """
    robust_b = 0
    for a, b in product(WELL_FORMED_GRID, repeat=2):
        intervals = {"A": a, "B": b}
        if robust_winner(intervals) != "B":
            continue
        robust_b += 1
        (lower_a, upper_a), (lower_b, upper_b) = a, b
        if not upper_a >= lower_b:
            raise AssertionError("robust-B point escapes the stated condition")
        if not (lower_b <= upper_b < lower_a <= upper_a):
            raise AssertionError("well-formed robust-B chain failed")
    if robust_b == 0:
        raise AssertionError("no robust-B configuration enumerated")
    return {
        "well_formed_intervals_enumerated": len(WELL_FORMED_GRID),
        "ordered_pairs_enumerated": len(WELL_FORMED_GRID) ** 2,
        "robust_b_configurations": robust_b,
        "stated_condition_holds_at_every_robust_b_point": True,
        "stated_condition_identifies_a_boundary": False,
    }


# --- Finding 2: the intended claim needs a connected parameter domain ------


def linear(intercept, slope):
    return lambda s: Fraction(intercept) + Fraction(slope) * s


CONNECTED_BOUNDS = {
    "A": (linear(1, 6), linear(2, 6)),
    "B": (linear(5, -4), linear(6, -4)),
}


def connected_intervals(s):
    return {fam: (lo(s), hi(s)) for fam, (lo, hi) in CONNECTED_BOUNDS.items()}


def check_connected_pairwise_crossover():
    """On a connected domain a two-family transition passes through abstention.

    `f(s) = L_B(s) - U_A(s) = 3 - 10 s` is continuous, positive at `s = 0` and
    negative at `s = 1`, so it has an exact zero at `s* = 3/10`. At that
    parameter neither family is robust.
    """
    start, end = Fraction(0), Fraction(1)
    if robust_winner(connected_intervals(start)) != "A":
        raise AssertionError("A is not robust at the start of the path")
    if robust_winner(connected_intervals(end)) != "B":
        raise AssertionError("B is not robust at the end of the path")

    def gap(s):
        return connected_intervals(s)["B"][0] - connected_intervals(s)["A"][1]

    if not (gap(start) > 0 and gap(end) < 0):
        raise AssertionError("the crossover gap does not change sign")
    # The gap is affine in s, so the intermediate-value root is exact and
    # rational: solve it directly rather than approximating a dyadic bisection.
    slope = gap(end) - gap(start)
    if slope == 0:
        raise AssertionError("the crossover gap is constant")
    root = start + (end - start) * (-gap(start) / slope)
    if gap(root) != 0 or root != Fraction(3, 10):
        raise AssertionError("exact crossover root not recovered")
    at_root = connected_intervals(root)
    if robust_winner(at_root) != "UNDECIDED_FROM_CURRENT_EVIDENCE":
        raise AssertionError("a family is still robust at the touch parameter")
    return {
        "crossover_parameter": str(root),
        "touching_bounds_upper_a_equals_lower_b": str(at_root["A"][1]),
        "neither_family_robust_at_crossover": True,
        "pairwise_claim_requires_connected_domain_and_continuity": True,
    }


def check_discrete_register_counterexample():
    """On a discrete register the transition can skip abstention entirely."""
    register = {
        1: {"A": (Fraction(1), Fraction(2)), "B": (Fraction(5), Fraction(6))},
        2: {"A": (Fraction(7), Fraction(8)), "B": (Fraction(3), Fraction(4))},
    }
    verdicts = {s: robust_winner(rows) for s, rows in register.items()}
    if verdicts != {1: "A", 2: "B"}:
        raise AssertionError("the discrete register does not transition")
    if any(v == "UNDECIDED_FROM_CURRENT_EVIDENCE" for v in verdicts.values()):
        raise AssertionError("the discrete register contains an abstention")
    return {
        "registered_parameters": sorted(register),
        "verdicts": {str(s): v for s, v in verdicts.items()},
        "abstention_parameter_exists": False,
        "discrete_transition_without_boundary": True,
    }


def check_third_family_defeats_pairwise_abstention():
    """A pairwise touch parameter need not make the global verdict undecided."""
    root = Fraction(3, 10)
    intervals = dict(connected_intervals(root))
    if robust_winner(intervals) != "UNDECIDED_FROM_CURRENT_EVIDENCE":
        raise AssertionError("pairwise abstention precondition failed")
    intervals["C"] = (Fraction(1, 2), Fraction(1))
    if robust_winner(intervals) != "C":
        raise AssertionError("the third family is not robustly selected")
    return {
        "pairwise_verdict_at_crossover": "UNDECIDED_FROM_CURRENT_EVIDENCE",
        "three_family_verdict_at_crossover": "C",
        "conclusion_is_pairwise_not_global": True,
    }


# --- Finding 3: unvalidated malformed intervals break the comparison -------


def check_malformed_intervals_require_abstention():
    """Malformed bounds produce two winners and escape the crossover chain."""
    both = {"A": (Fraction(5), Fraction(0)), "B": (Fraction(5), Fraction(0))}
    if unvalidated_robust_winners(both) != ["A", "B"]:
        raise AssertionError("malformed pair does not expose the two-winner defect")
    escaping = {"A": (Fraction(1), Fraction(2)), "B": (Fraction(5), Fraction(0))}
    if "B" not in unvalidated_robust_winners(escaping):
        raise AssertionError("malformed escape witness is not a spurious winner")
    if escaping["A"][1] >= escaping["B"][0]:
        raise AssertionError("malformed escape witness still satisfies the condition")
    rejected = 0
    for rows in (both, escaping):
        try:
            robust_winner(rows)
        except PhaseInputError:
            rejected += 1
    if rejected != 2:
        raise AssertionError("validation accepted a malformed interval")
    malformed_multi_winner = 0
    for a, b in product(product(range(5), repeat=2), repeat=2):
        rows = {"A": (Fraction(a[0]), Fraction(a[1])), "B": (Fraction(b[0]), Fraction(b[1]))}
        if len(unvalidated_robust_winners(rows)) > 1:
            malformed_multi_winner += 1
            if rows["A"][0] <= rows["A"][1] and rows["B"][0] <= rows["B"][1]:
                raise AssertionError("well-formed intervals produced two winners")
    if malformed_multi_winner == 0:
        raise AssertionError("no malformed multi-winner configuration enumerated")
    return {
        "unvalidated_two_winner_witness": ["A", "B"],
        "malformed_point_escapes_stated_condition": True,
        "validated_rule_rejects_malformed_input": True,
        "grid_configurations_enumerated": 625,
        "malformed_multi_winner_configurations": malformed_multi_winner,
        "well_formed_multi_winner_configurations": 0,
    }


# --- Finding 4: an upper bound is not a term of a lower bound --------------

REGISTERED_REGIONAL_BOUNDS = {
    "neural_smooth_upper": 4,
    "neural_exact_lower": 8,
    "non_neural_smooth_lower": 9,
    "non_neural_exact_upper": 3,
    "bridge_upper": 1,
}


def check_pure_family_lower_bound_misuse():
    """The predecessor hybrid witness summed upper bounds into lower bounds.

    A sound lower bound on a pure family is a sum of registered *lower* bounds.
    The neural smooth-region lower bound was never registered, so with only
    non-negativity the sound pure-neural bound equals `8`, which does not
    strictly exceed the hybrid upper bound `8`.
    """
    r = REGISTERED_REGIONAL_BOUNDS
    hybrid_upper = r["neural_smooth_upper"] + r["non_neural_exact_upper"] + r["bridge_upper"]
    defective_neural_lower = r["neural_smooth_upper"] + r["neural_exact_lower"]
    defective_non_neural_lower = r["non_neural_smooth_lower"] + r["non_neural_exact_upper"]
    sound_neural_lower = 0 + r["neural_exact_lower"]
    sound_non_neural_lower = r["non_neural_smooth_lower"] + 0
    if (hybrid_upper, defective_neural_lower, defective_non_neural_lower) != (8, 12, 12):
        raise AssertionError("predecessor arithmetic not reproduced")
    if not (hybrid_upper < defective_neural_lower and hybrid_upper < defective_non_neural_lower):
        raise AssertionError("predecessor verdict not reproduced")
    if hybrid_upper < sound_neural_lower:
        raise AssertionError("the sound neural bound still excludes the pure family")
    if not hybrid_upper < sound_non_neural_lower:
        raise AssertionError("the sound non-neural exclusion should survive")
    # A compatible evidence world in which the predecessor verdict is wrong.
    world = {"neural_smooth": 0, "neural_exact": 8}
    pure_neural_cost = world["neural_smooth"] + world["neural_exact"]
    if pure_neural_cost > r["neural_smooth_upper"] + r["neural_exact_lower"]:
        raise AssertionError("witness world violates the registered bounds")
    if pure_neural_cost < r["neural_exact_lower"]:
        raise AssertionError("witness world violates the registered exact lower bound")
    if not pure_neural_cost <= hybrid_upper:
        raise AssertionError("witness world does not tie the hybrid upper bound")
    return {
        "hybrid_upper_bound": hybrid_upper,
        "predecessor_pure_neural_lower_bound": defective_neural_lower,
        "predecessor_pure_non_neural_lower_bound": defective_non_neural_lower,
        "predecessor_bounds_mix_upper_into_lower": True,
        "sound_pure_neural_lower_bound": sound_neural_lower,
        "sound_pure_non_neural_lower_bound": sound_non_neural_lower,
        "sound_non_neural_exclusion_survives": True,
        "sound_neural_exclusion_fails": True,
        "compatible_world_pure_neural_cost": pure_neural_cost,
        "corrected_verdict": "UNDECIDED_FROM_CURRENT_EVIDENCE",
    }


def check_repaired_registration_recovers_hybrid():
    """Registering the missing regional lower bounds restores the verdict."""
    repaired = dict(REGISTERED_REGIONAL_BOUNDS)
    repaired["neural_smooth_lower"] = 4
    repaired["non_neural_exact_lower"] = 3
    hybrid_upper = (
        repaired["neural_smooth_upper"]
        + repaired["non_neural_exact_upper"]
        + repaired["bridge_upper"]
    )
    pure_neural_lower = repaired["neural_smooth_lower"] + repaired["neural_exact_lower"]
    pure_non_neural_lower = repaired["non_neural_smooth_lower"] + repaired["non_neural_exact_lower"]
    for name, (lo, hi) in {
        "neural_smooth": (repaired["neural_smooth_lower"], repaired["neural_smooth_upper"]),
        "non_neural_exact": (repaired["non_neural_exact_lower"], repaired["non_neural_exact_upper"]),
    }.items():
        if lo > hi:
            raise AssertionError(f"{name}: repaired registration is malformed")
    if not (pure_neural_lower == 12 and pure_non_neural_lower == 12):
        raise AssertionError("repaired pure-family bounds not recovered")
    if not hybrid_upper < min(pure_neural_lower, pure_non_neural_lower):
        raise AssertionError("repaired hybrid verdict not recovered")
    return {
        "registered_regional_lower_bounds_required": ["neural_smooth_lower", "non_neural_exact_lower"],
        "hybrid_upper_bound": hybrid_upper,
        "sound_pure_neural_lower_bound": pure_neural_lower,
        "sound_pure_non_neural_lower_bound": pure_non_neural_lower,
        "hybrid_robustly_selected_after_repair": True,
    }


# --- Finding 5: regional sums bound decomposed candidates only -------------


def check_decomposition_closure_is_required():
    """Excluding a pure family by a regional sum presupposes decomposition.

    The additive regional law was declared to *compose* a hybrid upper bound.
    Using it as a *necessity* for pure competitors additionally requires that
    every admissible pure realization factors through the registered regions.
    A monolithic realization is not bound by the regional sum.
    """
    hybrid_upper = 8
    regional_pure_neural_lower = 12
    monolithic_pure_neural_cost = 6
    if not regional_pure_neural_lower > hybrid_upper:
        raise AssertionError("decomposed exclusion precondition failed")
    if monolithic_pure_neural_cost >= hybrid_upper:
        raise AssertionError("the monolithic witness does not beat the hybrid bound")
    verdict_with_closure = (
        "HYBRID" if hybrid_upper < regional_pure_neural_lower else "UNDECIDED_FROM_CURRENT_EVIDENCE"
    )
    candidate_costs = {"HYBRID_UPPER": hybrid_upper, "PURE_NEURAL": monolithic_pure_neural_cost}
    verdict_without_closure = (
        "HYBRID"
        if all(
            hybrid_upper < cost for name, cost in candidate_costs.items() if name != "HYBRID_UPPER"
        )
        else "UNDECIDED_FROM_CURRENT_EVIDENCE"
    )
    if verdict_with_closure != "HYBRID":
        raise AssertionError("closed-class verdict not reproduced")
    if verdict_without_closure != "UNDECIDED_FROM_CURRENT_EVIDENCE":
        raise AssertionError("open-class verdict should abstain")
    return {
        "hybrid_upper_bound": hybrid_upper,
        "regional_sum_pure_neural_lower_bound": regional_pure_neural_lower,
        "monolithic_pure_neural_cost": monolithic_pure_neural_cost,
        "verdict_under_decomposition_closed_class": verdict_with_closure,
        "verdict_without_decomposition_closure": verdict_without_closure,
        "regional_sum_is_a_necessity_only_for_decomposed_candidates": True,
    }


def run():
    return {
        "terminal": "GRAND_GMI_FAMILY_PHASE_SOUNDNESS_CORRECTION_GREEN_AT_FINITE_SCOPE",
        "stated_crossover_condition_is_vacuous": check_stated_crossover_condition_is_vacuous(),
        "connected_pairwise_crossover": check_connected_pairwise_crossover(),
        "discrete_register_counterexample": check_discrete_register_counterexample(),
        "third_family_defeats_pairwise_abstention": check_third_family_defeats_pairwise_abstention(),
        "malformed_intervals_require_abstention": check_malformed_intervals_require_abstention(),
        "pure_family_lower_bound_misuse": check_pure_family_lower_bound_misuse(),
        "repaired_registration_recovers_hybrid": check_repaired_registration_recovers_hybrid(),
        "decomposition_closure_is_required": check_decomposition_closure_is_required(),
        "empirical_hardware_cost_claimed": False,
        "claim_ceiling": "finite synthetic selection-logic witnesses only",
    }


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))
