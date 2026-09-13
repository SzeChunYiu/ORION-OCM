#!/usr/bin/env python3
"""Exact boundary checks for GIR; the punctured-line proof is in the theorem.

For finite rational targets in R minus finitely many rational points, the
infimum radius is half the target diameter. Feasibility additionally requires
that their closed tolerance-ball intersection contain an allowed output.
This analytic subclass does not stand in for arbitrary measurable selection.
"""
from __future__ import annotations

import argparse
import json
from fractions import Fraction
from itertools import product
from pathlib import Path


def feasible_center(targets, tolerance, removed=()):
    """Return an exact feasible center in the punctured line, or None.

The intersection is [max(targets)-tolerance, min(targets)+tolerance].
If it has positive length, m+1 distinct interior points cannot all belong to
the m removed points. A singleton intersection must itself be allowed.
"""
    targets = tuple(Fraction(value) for value in targets)
    tolerance = Fraction(tolerance)
    removed = frozenset(Fraction(value) for value in removed)
    if not targets or tolerance < 0:
        raise ValueError("Require nonempty targets and nonnegative tolerance")
    if any(value in removed for value in targets):
        raise ValueError("Targets must belong to the declared output space")
    lower = max(targets) - tolerance
    upper = min(targets) + tolerance
    if lower > upper:
        return None
    if lower == upper:
        return None if lower in removed else lower
    denominator = len(removed) + 2
    for numerator in range(1, denominator):
        point = lower + (upper - lower) * Fraction(numerator, denominator)
        if point not in removed:
            return point
    raise AssertionError("Finite excluded points exhausted a larger candidate set")


def error(center, targets):
    return max(abs(center - value) for value in targets)


def run():
    targets = (Fraction(-1), Fraction(1))
    boundary = feasible_center(targets, 1, removed=(0,))
    sequence = tuple(Fraction(1, n) for n in range(1, 65))
    strict_slacks = tuple(Fraction(1, n) for n in range(1, 65))
    sequence_errors = tuple(error(point, targets) for point in sequence)
    strict_centers = tuple(
        feasible_center(targets, 1 + slack, removed=(0,))
        for slack in strict_slacks
    )

    finite_cases = 0
    valid_centers = 0
    corrected_gate_agreements = 0
    value_only_false_licenses = 0
    for pair in product((-2, -1, 1, 2), repeat=2):
        radius = Fraction(max(pair) - min(pair), 2)
        midpoint = Fraction(max(pair) + min(pair), 2)
        for step in range(9):
            tolerance = Fraction(step, 4)
            center = feasible_center(pair, tolerance, removed=(0,))
            finite_cases += 1
            # Independent closed-interval characterization for one puncture.
            feasible = radius < tolerance or (radius == tolerance and midpoint != 0)
            corrected_gate_agreements += (center is not None) == feasible
            valid_centers += center is None or (
                center != 0 and error(center, pair) <= tolerance
            )
            value_only_false_licenses += radius <= tolerance and center is None

    # Global radius can be attained without optimizing every smaller fiber.
    fibers = ((Fraction(-1), Fraction(1)), (Fraction(-1), Fraction(3)))
    global_outputs = tuple(feasible_center(fiber, 2, removed=(0,)) for fiber in fibers)
    global_error = max(error(point, fiber) for point, fiber in zip(global_outputs, fibers))
    multiple_punctures = (Fraction(-1, 2), Fraction(0), Fraction(1, 2))
    multi_center = feasible_center(targets, 2, removed=multiple_punctures)
    checks = {
        "radius_one_equality_rejects_unattained_center": boundary is None,
        "approximating_sequence_never_attains": all(value > 1 for value in sequence_errors),
        "sequence_exact_error_formula": all(
            loss == 1 + abs(point) for point, loss in zip(sequence, sequence_errors)
        ),
        "sequence_errors_strictly_decrease": all(
            first > second for first, second in zip(sequence_errors, sequence_errors[1:])
        ),
        "all_positive_slacks_have_valid_centers": all(
            point is not None and point != 0 and error(point, targets) <= 1 + slack
            for point, slack in zip(strict_centers, strict_slacks)
        ),
        "restored_center_attains_boundary": feasible_center(targets, 1) == 0,
        "below_radius_rejected_even_without_puncture": feasible_center(targets, Fraction(3, 4)) is None,
        "finite_outputs_attain_different_minimum": min(error(point, targets) for point in (-1, 1)) == 2,
        "all_subclass_centers_valid": valid_centers == finite_cases == 144,
        "all_subclass_gates_correct": corrected_gate_agreements == finite_cases,
        "old_value_only_gate_has_counterexamples": value_only_false_licenses == 4,
        "global_attainment_does_not_require_all_fiber_minima": (
            feasible_center(fibers[0], 1, removed=(0,)) is None and global_error == 2
        ),
        "finite_punctures_cannot_block_interval_interior": (
            multi_center is not None
            and multi_center not in multiple_punctures
            and error(multi_center, targets) <= 2
        ),
    }
    green = all(checks.values())
    return {
        "terminal": "GRAND_GMI_GENERALIZATION_ATTAINMENT_TRANCHE_" + ("ALL_GREEN" if green else "RED"),
        "all_checks_green": green,
        "determinism": "exact-rational-no-rng",
        "scope": "Finite rational targets in R with finitely many points removed; analytic proof in GIR section 7",
        "checks": checks,
        "observed": {
            "finite_boundary_cases": finite_cases,
            "corrected_gate_agreements": corrected_gate_agreements,
            "value_only_false_licenses": value_only_false_licenses,
            "strict_slack_cases": len(strict_slacks),
            "approximating_sequence_cases": len(sequence),
        },
        "unattained_boundary": {
            "output_space": "R minus {0}",
            "targets": [-1, 1],
            "infimum_radius": 1,
            "tolerance": 1,
            "feasible_center": None,
            "error_identity": "max(|y+1|, |y-1|) = 1+|y| > 1 for all allowed y",
        },
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    result = run()
    output = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.out:
        args.out.write_text(output, encoding="utf-8")
    print(output, end="")
    return 0 if result["all_checks_green"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
