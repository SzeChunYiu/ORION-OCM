from __future__ import annotations

from fractions import Fraction as F
from itertools import product
import json

FREEZE_COMMIT = "e4d6f9ef941e1b7dfc958c8f8446c7890f40d2a7"
CLAIM = "FINITE_SCALING_BOTTLENECK_AND_CROSSOVER_LAWS_AT_REGISTERED_SCOPE"
N_MAX = 128
ETA = F(1, 20)
AXES = ("work", "memory", "verify")


def req(morphology, n):
    if type(n) is not int or n < 1:
        raise ValueError("n must be positive int")
    if morphology == "Q":
        return (n * n, 2 * n, n)
    if morphology == "L":
        return (9 * n + 12, n + 4, 2 * n)
    raise ValueError("unknown morphology")


def _winner(a, b, a_name, b_name):
    return a_name if a < b else b_name if b < a else "TIE"


def work_winner(n):
    q, l = req("Q", n)[0], req("L", n)[0]
    return _winner(q, l, "Q", "L")


def verify_winner(n):
    q, l = req("Q", n)[2], req("L", n)[2]
    return _winner(q, l, "Q", "L")


def smooth_control_winner(n):
    if type(n) is not int or n < 1:
        raise ValueError("n must be positive int")
    return _winner(3 * n + 1, 5 * n + 7, "A", "B")


def finite_relative_correction(n):
    if type(n) is not int or n < 1:
        raise ValueError("n must be positive int")
    return F(12, 9 * n)


def frac(value):
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def slack(resources, requirements):
    if len(resources) != len(requirements) or not resources:
        raise ValueError("dimension mismatch")
    if any(type(q) is not int or q <= 0 for q in requirements):
        raise ValueError("requirements must be positive ints")
    if any(type(b) is not int or b < 0 for b in resources):
        raise ValueError("resources must be nonnegative ints")
    ratios = tuple(F(b, q) for b, q in zip(resources, requirements))
    sigma = min(ratios)
    bottlenecks = tuple(
        AXES[i] if len(requirements) == 3 else str(i)
        for i, ratio in enumerate(ratios)
        if ratio == sigma
    )
    return sigma, bottlenecks, ratios


def feasible(resources, requirements):
    sigma, _, _ = slack(resources, requirements)
    return sigma >= 1


def dominates(a, b):
    if len(a) != len(b):
        raise ValueError("dimension mismatch")
    return all(x <= y for x, y in zip(a, b)) and any(x < y for x, y in zip(a, b))


def exhaustive_bottleneck():
    cases = 0
    failures = 0
    for requirements in product((1, 2, 3), repeat=3):
        for resources in product(range(5), repeat=3):
            cases += 1
            direct = all(b >= q for b, q in zip(resources, requirements))
            via_slack = feasible(resources, requirements)
            if direct != via_slack:
                failures += 1
    return {"cases": cases, "failures": failures, "all_green": failures == 0}


def build_receipt():
    transitions = []
    previous = None
    for n in range(1, N_MAX + 1):
        winner = work_winner(n)
        if previous is not None and winner != previous:
            transitions.append({"from_n": n - 1, "to_n": n, "from": previous, "to": winner})
        previous = winner
    expected_transition = [{"from_n": 10, "to_n": 11, "from": "Q", "to": "L"}]
    if transitions != expected_transition:
        raise RuntimeError(f"unexpected work transition: {transitions}")
    if any(work_winner(n) != "Q" for n in range(1, 11)):
        raise RuntimeError("Q winner range mismatch")
    if any(work_winner(n) != "L" for n in range(11, N_MAX + 1)):
        raise RuntimeError("L winner range mismatch")

    asymptotic_n10 = _winner(9 * 10, 10 * 10, "L", "Q")
    exact_n10 = work_winner(10)
    if asymptotic_n10 != "L" or exact_n10 != "Q":
        raise RuntimeError("frozen extrapolation hostile failed")
    first_within = min(n for n in range(1, 10000) if finite_relative_correction(n) <= ETA)
    if first_within != 27:
        raise RuntimeError("finite correction boundary mismatch")

    control_winners = [smooth_control_winner(n) for n in range(1, N_MAX + 1)]
    control_transitions = sum(a != b for a, b in zip(control_winners, control_winners[1:]))
    if set(control_winners) != {"A"} or control_transitions:
        raise RuntimeError("smooth control fabricated crossover")

    q11 = req("Q", 11)
    l11 = req("L", 11)
    threshold = {
        "requirements_L_n11": list(l11),
        "below": {"resources": [110, 15, 22], "feasible": feasible((110, 15, 22), l11)},
        "at": {"resources": [111, 15, 22], "feasible": feasible((111, 15, 22), l11)},
        "memory_negative_twin": {
            "resources": [10**6, 14, 10**6],
            "feasible": feasible((10**6, 14, 10**6), l11),
        },
    }
    if threshold["below"]["feasible"] or not threshold["at"]["feasible"] or threshold["memory_negative_twin"]["feasible"]:
        raise RuntimeError("threshold witness failed")

    saturation_before = slack((200, 15, 22), l11)
    saturation_after = slack((10**6, 15, 22), l11)
    if not feasible((200, 15, 22), l11) or not feasible((10**6, 15, 22), l11):
        raise RuntimeError("saturation feasibility failed")
    if saturation_before[0] != saturation_after[0]:
        raise RuntimeError("saturation slack unexpectedly changed")

    reversal = {"work_winner_n11": work_winner(11), "verify_winner_n11": verify_winner(11)}
    if reversal != {"work_winner_n11": "L", "verify_winner_n11": "Q"}:
        raise RuntimeError("price-vector reversal failed")
    pareto = {"Q_dominates_L": dominates(q11, l11), "L_dominates_Q": dominates(l11, q11)}
    if any(pareto.values()):
        raise RuntimeError("n=11 should be Pareto nondominated")

    bottleneck_control = exhaustive_bottleneck()
    if not bottleneck_control["all_green"]:
        raise RuntimeError("bottleneck theorem control failed")

    return {
        "schema": "FiniteScalingBottleneckReceiptV1",
        "issue": 774,
        "parent_issue": 602,
        "freeze_commit": FREEZE_COMMIT,
        "claim_ceiling": CLAIM,
        "resource_laws": {
            "Q": {"work": "n^2", "memory": "2n", "verify": "n"},
            "L": {"work": "9n+12", "memory": "n+4", "verify": "2n"},
            "price_vectors": {"work_only": [1, 0, 0], "verify_only": [0, 0, 1]},
        },
        "work_crossover": {
            "continuous_positive_root": "(9+sqrt(129))/2",
            "decimal_display": "10.178908345800274",
            "D_10": req("Q", 10)[0] - req("L", 10)[0],
            "D_11": req("Q", 11)[0] - req("L", 11)[0],
            "integer_transition_count": len(transitions),
            "integer_transitions": transitions,
            "Q_wins_n_1_through_10": all(work_winner(n) == "Q" for n in range(1, 11)),
            "L_wins_n_11_through_128": all(work_winner(n) == "L" for n in range(11, 129)),
            "terminology": "MORPHOLOGY_SELECTION_CROSSOVER",
        },
        "finite_size_correction": {
            "setup_term": 12,
            "relative_correction": "4/(3n)",
            "tolerance": frac(ETA),
            "first_n_within_tolerance": first_within,
            "n10_relative_correction": frac(finite_relative_correction(10)),
            "asymptotic_n10_winner": asymptotic_n10,
            "exact_n10_winner": exact_n10,
            "disposition": "ASYMPTOTIC_9N_NOT_EXACT_FINITE_LAW",
        },
        "smooth_vs_crossover": {
            "Q_real_extension": "x^2",
            "L_real_extension": "9x+12",
            "both_smooth_for_x_gt_0": True,
            "smooth_control": {
                "A": "3n+1",
                "B": "5n+7",
                "winner": "A",
                "transition_count_n1_128": control_transitions,
            },
            "thermodynamic_phase_transition_proved": False,
        },
        "bottleneck": {
            "theorem": "feasible iff min_i b_i/q_i >= 1",
            "exact_exhaustive_control": bottleneck_control,
            "threshold_n11": threshold,
            "saturation_control": {
                "before_extra_work": {
                    "resources": [200, 15, 22],
                    "sigma": frac(saturation_before[0]),
                    "bottlenecks": list(saturation_before[1]),
                    "feasible": True,
                },
                "after_extra_work": {
                    "resources": [10**6, 15, 22],
                    "sigma": frac(saturation_after[0]),
                    "bottlenecks": list(saturation_after[1]),
                    "feasible": True,
                },
                "binary_feasibility_unchanged": True,
            },
        },
        "nonuniversality": {
            "n11_Q_resources": list(q11),
            "n11_L_resources": list(l11),
            **reversal,
            "pareto": pareto,
            "full_vector_nondominance": not any(pareto.values()),
        },
        "terminology": {
            "within_morphology": "SMOOTH_WITHIN_MORPHOLOGY_SCALING",
            "selection": "MORPHOLOGY_SELECTION_CROSSOVER",
            "capability": "CAPABILITY_REACHABILITY_THRESHOLD",
            "forbidden": "THERMODYNAMIC_PHASE_TRANSITION_PROVED",
        },
        "forbidden_claims": [
            "THERMODYNAMIC_PHASE_TRANSITION_PROVED",
            "UNIVERSAL_SCALING_EXPONENT",
            "UNIVERSAL_BEST_MORPHOLOGY",
            "REAL_SCALE_EXTRAPOLATION_PROVED",
            "COMPLETE_GMI",
        ],
    }


def main():
    print(json.dumps(build_receipt(), sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
