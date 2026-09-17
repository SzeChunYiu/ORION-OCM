#!/usr/bin/env python3
"""Independent union-find oracle for a supplied exact distance matrix."""

from __future__ import annotations

from fractions import Fraction


def threshold_components(
    matrix: tuple[tuple[Fraction, ...], ...],
    threshold: Fraction,
) -> tuple[tuple[int, ...], ...]:
    if type(matrix) is not tuple or not matrix:
        raise ValueError("distance matrix must be nonempty")
    size = len(matrix)
    if any(type(row) is not tuple or len(row) != size for row in matrix):
        raise ValueError("distance matrix must be square")
    if type(threshold) is not Fraction or threshold <= 0:
        raise ValueError("threshold must be a positive exact Fraction")
    for left in range(size):
        for right in range(size):
            value = matrix[left][right]
            if type(value) is not Fraction or value < 0:
                raise ValueError("distance matrix entries must be nonnegative Fractions")
            if matrix[left][right] != matrix[right][left]:
                raise ValueError("distance matrix must be symmetric")
            if (value == 0) != (left == right):
                raise ValueError("distance matrix must separate indices")

    parent = list(range(size))

    def find(value: int) -> int:
        while parent[value] != value:
            parent[value] = parent[parent[value]]
            value = parent[value]
        return value

    def union(left: int, right: int) -> None:
        root_left, root_right = find(left), find(right)
        if root_left == root_right:
            return
        if root_left < root_right:
            parent[root_right] = root_left
        else:
            parent[root_left] = root_right

    for left in range(size):
        for right in range(left + 1, size):
            if matrix[left][right] <= threshold:
                union(left, right)

    groups: dict[int, list[int]] = {}
    for index in range(size):
        groups.setdefault(find(index), []).append(index)
    return tuple(sorted(tuple(group) for group in groups.values()))
