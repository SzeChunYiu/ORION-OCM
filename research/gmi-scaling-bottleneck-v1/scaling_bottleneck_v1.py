#!/usr/bin/env python3
"""Exact finite scaling/bottleneck microscope for #774 / #602 Section U."""

from __future__ import annotations

from fractions import Fraction
import json
from typing import Iterable

CLAIM_CEILING = "FINITE_SCALING_BOTTLENECK_AND_CROSSOVER_LAWS_AT_REGISTERED_SCOPE"
MAX_N = 128
TOLERANCE = Fraction(1, 20)
RESOURCE_NAMES = ("work", "memory", "verify")
P_WORK = (Fraction(1), Fraction(0), Fraction(0))
P_VERIFY = (Fraction(0), Fraction(0), Fraction(1))


def require_n(n: int) -> None:
    if isinstance(n, bool) or not isinstance(n, int) or n < 1:
        raise ValueError("n must be a positive integer")


def resources(morphology: str, n: int) -> tuple[int, int, int]:
    require_n(n)
    if morphology == "Q":
        return (n * n, 2 * n, n)
    if morphology == "L":
        return (9 * n + 12, n + 4, 2 * n)
    raise ValueError("unknown morphology")


def charged_cost(resource_vector: Iterable[int | Fraction], price: Iterable[int | Fraction]) -> Fraction:
    rv = tuple(Fraction(value) for value in resource_vector)
    pv = tuple(Fraction(value) for value in price)
    if len(rv) != len(pv) or not rv:
        raise ValueError("resource and price vectors must be nonempty and same-length")
    return sum((r * p for r, p in zip(rv, pv)), Fraction(0))


def winner(n: int, price: tuple[Fraction, Fraction, Fraction]) -> str:
    q = charged_cost(resources("Q", n), price)
    l = charged_cost(resources("L", n), price)
    if q < l:
        return "Q"
    if l < q:
        return "L"
    return "TIE"


def work_delta(n: int) -> int:
    require_n(n)
    return n * n - 9 * n - 12


def zero_intercept_l_work(n: int) -> int:
    require_n(n)
    return 9 * n


def finite_relative_correction(n: int) -> Fraction:
    require_n(n)
    return Fraction(4, 3 * n)


def first_tolerance_n(tolerance: Fraction = TOLERANCE) -> int:
    tolerance = Fraction(tolerance)
    if tolerance <= 0:
        raise ValueError("tolerance must be positive")
    n = 1
    while finite_relative_correction(n) > tolerance:
        n += 1
    return n


def bottleneck_status(
    available: Iterable[int | Fraction],
    requirements: Iterable[int | Fraction],
    names: Iterable[str] | None = None,
) -> dict:
    b = tuple(Fraction(value) for value in available)
    q = tuple(Fraction(value) for value in requirements)
    if not b or len(b) != len(q):
        raise ValueError("available and requirements must be nonempty and same-length")
    if any(value < 0 for value in b):
        raise ValueError("available resources must be nonnegative")
    if any(value <= 0 for value in q):
        raise ValueError("requirements must be strictly positive")
    labels = tuple(names) if names is not None else tuple(str(i) for i in range(len(q)))
    if len(labels) != len(q) or len(set(labels)) != len(labels):
        raise ValueError("resource names must be unique and dimension-matched")
    ratios = tuple(bi / qi for bi, qi in zip(b, q))
    sigma = min(ratios)
    bottlenecks = [label for label, ratio in zip(labels, ratios) if ratio == sigma]
    return {
        "sigma": sigma,
        "feasible": sigma >= 1,
        "bottlenecks": bottlenecks,
        "ratios": dict(zip(labels, ratios)),
    }


def pareto_dominates(left: Iterable[int], right: Iterable[int]) -> bool:
    a = tuple(left)
    b = tuple(right)
    if not a or len(a) != len(b):
        raise ValueError("vectors must be nonempty and same-length")
    return all(x <= y for x, y in zip(a, b)) and any(x < y for x, y in zip(a, b))


def fraction_text(value: Fraction | int) -> str:
    f = Fraction(value)
    return str(f.numerator) if f.denominator == 1 else f"{f.numerator}/{f.denominator}"


def canonical_status(status: dict) -> dict:
    return {
        "sigma": fraction_text(status["sigma"]),
        "feasible": status["feasible"],
        "bottlenecks": list(status["bottlenecks"]),
        "ratios": {key: fraction_text(value) for key, value in status["ratios"].items()},
    }


def build_receipt() -> dict:
    work_winners = [winner(n, P_WORK) for n in range(1, MAX_N + 1)]
    switches = [
        {"from_n": n, "to_n": n + 1, "from": work_winners[n - 1], "to": work_winners[n]}
        for n in range(1, MAX_N)
        if work_winners[n - 1] != work_winners[n]
    ]

    q11 = resources("Q", 11)
    l11 = resources("L", 11)
    fail = bottleneck_status((110, 15, 22), l11, RESOURCE_NAMES)
    passed = bottleneck_status((111, 15, 22), l11, RESOURCE_NAMES)
    memory_twin = bottleneck_status((111000, 14, 22), l11, RESOURCE_NAMES)

    smooth_control_winners = ["A" if 3 * n + 1 < 5 * n + 7 else "B" if 5 * n + 7 < 3 * n + 1 else "TIE"
                              for n in range(1, MAX_N + 1)]
    smooth_control_switches = [
        n for n in range(1, MAX_N)
        if smooth_control_winners[n - 1] != smooth_control_winners[n]
    ]

    return {
        "schema": "GMI_SCALING_BOTTLENECK_RECEIPT_V1",
        "claim_ceiling": CLAIM_CEILING,
        "enumerated_integer_sizes": {"first": 1, "last": MAX_N, "count": MAX_N},
        "work_crossover": {
            "continuous_positive_root": "(9+sqrt(129))/2",
            "root_bracket": {"lower_strict": 10, "upper_strict": 11},
            "delta_at_10": work_delta(10),
            "delta_at_11": work_delta(11),
            "switches": switches,
            "winner_counts": {"Q": work_winners.count("Q"), "L": work_winners.count("L"), "TIE": work_winners.count("TIE")},
            "first_strict_L_integer": next(n for n in range(1, MAX_N + 1) if winner(n, P_WORK) == "L"),
        },
        "finite_size_correction": {
            "formula": "4/(3n)",
            "tolerance": fraction_text(TOLERANCE),
            "first_licensed_integer": first_tolerance_n(),
            "correction_at_26": fraction_text(finite_relative_correction(26)),
            "correction_at_27": fraction_text(finite_relative_correction(27)),
            "n10_exact": {
                "Q_work": resources("Q", 10)[0],
                "L_work": resources("L", 10)[0],
                "winner": winner(10, P_WORK),
            },
            "n10_zero_intercept": {
                "Q_work": resources("Q", 10)[0],
                "L_work_approx": zero_intercept_l_work(10),
                "winner": "L" if zero_intercept_l_work(10) < resources("Q", 10)[0] else "Q",
            },
            "exact_finite_extrapolation_failure_at_n10": True,
        },
        "smooth_vs_crossover": {
            "underlying_laws_smooth": True,
            "registered_term": "MORPHOLOGY_SELECTION_CROSSOVER",
            "thermodynamic_phase_transition_claimed": False,
            "no_crossover_control": {
                "A": "3n+1",
                "B": "5n+7",
                "switches": smooth_control_switches,
                "winner_counts": {"A": smooth_control_winners.count("A"), "B": smooth_control_winners.count("B"), "TIE": smooth_control_winners.count("TIE")},
            },
        },
        "n11_bottleneck": {
            "L_requirements": dict(zip(RESOURCE_NAMES, l11)),
            "below_work_threshold": canonical_status(fail),
            "exact_threshold": canonical_status(passed),
            "memory_negative_twin": canonical_status(memory_twin),
        },
        "n11_resource_nonuniversality": {
            "Q": dict(zip(RESOURCE_NAMES, q11)),
            "L": dict(zip(RESOURCE_NAMES, l11)),
            "Q_pareto_dominates_L": pareto_dominates(q11, l11),
            "L_pareto_dominates_Q": pareto_dominates(l11, q11),
            "work_only_winner": winner(11, P_WORK),
            "verification_only_winner": winner(11, P_VERIFY),
            "winner_reversal": winner(11, P_WORK) != winner(11, P_VERIFY),
        },
        "forbidden_claims": [
            "THERMODYNAMIC_PHASE_TRANSITION_PROVED",
            "UNIVERSAL_SCALING_EXPONENT",
            "UNIVERSAL_BEST_MORPHOLOGY",
            "REAL_SCALE_EXTRAPOLATION_PROVED",
            "COMPLETE_GMI",
        ],
    }


def main() -> int:
    print(json.dumps(build_receipt(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
