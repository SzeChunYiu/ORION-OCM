#!/usr/bin/env python3
"""Independent all-pairs Pareto oracle; imports no primary implementation."""

from __future__ import annotations


def maximal_indices(rows: object) -> tuple[int, ...]:
    """Return maximal row indices when every integer coordinate is maximized."""
    if type(rows) is not tuple or not rows:
        raise ValueError("rows must be a nonempty tuple")
    width = None
    normalized: list[tuple[int, ...]] = []
    for row in rows:
        if type(row) is not tuple or not row:
            raise ValueError("each row must be a nonempty tuple")
        if any(type(value) is not int for value in row):
            raise ValueError("oracle coordinates must be exact integers")
        if width is None:
            width = len(row)
        if len(row) != width:
            raise ValueError("oracle rows must have equal width")
        normalized.append(row)
    if len(set(normalized)) != len(normalized):
        raise ValueError("oracle rows must be duplicate-free")

    maximal: list[int] = []
    for candidate_index, candidate in enumerate(normalized):
        beaten = False
        for rival_index, rival in enumerate(normalized):
            if rival_index == candidate_index:
                continue
            weak = True
            strict = False
            for coordinate in range(width or 0):
                if rival[coordinate] < candidate[coordinate]:
                    weak = False
                    break
                if rival[coordinate] > candidate[coordinate]:
                    strict = True
            if weak and strict:
                beaten = True
                break
        if not beaten:
            maximal.append(candidate_index)
    return tuple(maximal)

