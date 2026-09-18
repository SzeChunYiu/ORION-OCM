#!/usr/bin/env python3
"""Independent exhaustive oracle for the registered small Floyd design."""

from __future__ import annotations

from collections import Counter
from itertools import product
from math import comb


def exhaustive_floyd_counts(population: int, sample: int) -> dict[tuple[int, ...], int]:
    if type(population) is not int or population <= 0:
        raise ValueError("population must be a positive exact integer")
    if type(sample) is not int or sample <= 0 or sample > population:
        raise ValueError("sample must be positive and no greater than population")
    upper_values = tuple(range(population - sample, population))
    transcript_ranges = tuple(range(value + 1) for value in upper_values)
    counts: Counter[tuple[int, ...]] = Counter()
    for transcript in product(*transcript_ranges):
        selected: set[int] = set()
        for upper_value, draw in zip(upper_values, transcript):
            if draw in selected:
                selected.add(upper_value)
            else:
                selected.add(draw)
        counts[tuple(sorted(selected))] += 1
    if len(counts) != comb(population, sample):
        raise AssertionError("oracle subset support drift")
    return dict(sorted(counts.items()))


if __name__ == "__main__":
    print(exhaustive_floyd_counts(5, 2))
