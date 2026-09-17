#!/usr/bin/env python3
"""Independent direct oracle for finite semantic-collapse statistics.

This module deliberately imports neither the primary metric implementation nor
the parent's quotient routine.  It consumes already-observed immutable semantic
keys and uses direct equality scans.
"""

from __future__ import annotations

from fractions import Fraction
from typing import Sequence


def _fraction_pair(value: Fraction) -> tuple[int, int]:
    return (value.numerator, value.denominator)


def direct_collapse_statistics(keys: Sequence[object]) -> dict[str, object]:
    rows = tuple(keys)
    if not rows:
        raise ValueError("oracle requires a nonempty finite key sequence")

    # First-occurrence bins are intentionally independent of Counter/groupby.
    representatives: list[object] = []
    multiplicities: list[int] = []
    for key in rows:
        for index, representative in enumerate(representatives):
            if key == representative:
                multiplicities[index] += 1
                break
        else:
            representatives.append(key)
            multiplicities.append(1)

    direct_pairs = 0
    for left in range(len(rows)):
        for right in range(left + 1, len(rows)):
            direct_pairs += int(rows[left] == rows[right])

    histogram: dict[int, int] = {}
    for multiplicity in multiplicities:
        histogram[multiplicity] = histogram.get(multiplicity, 0) + 1

    presentation_count = len(rows)
    class_count = len(representatives)
    collapsed = presentation_count - class_count
    total_pairs = presentation_count * (presentation_count - 1) // 2
    pair_fraction = Fraction(direct_pairs, total_pairs) if total_pairs else Fraction(0, 1)
    singleton_count = sum(value == 1 for value in multiplicities)
    return {
        "presentation_count": presentation_count,
        "semantic_class_count": class_count,
        "collapsed_presentation_count": collapsed,
        "collapse_fraction": _fraction_pair(Fraction(collapsed, presentation_count)),
        "equivalent_unordered_pair_count": direct_pairs,
        "total_unordered_pair_count": total_pairs,
        "pair_collision_fraction": _fraction_pair(pair_fraction),
        "singleton_class_count": singleton_count,
        "singleton_presentation_fraction": _fraction_pair(Fraction(singleton_count, presentation_count)),
        "multiplicity_histogram": tuple(sorted(histogram.items())),
    }

