"""Independent finite enumerations and path semantics; no production imports."""
from fractions import Fraction as Q
from itertools import product

GRID = (Q(0), Q(1, 3), Q(1, 2), Q(2, 3), Q(1))


def kernels():
    for n, m in product(range(3), repeat=2):
        rows = tuple(r for r in product(GRID, repeat=m) if sum(r) == 1)
        for matrix in product(rows, repeat=n):
            yield n, m, matrix


def relations():
    for n, m in product(range(3), repeat=2):
        rows = tuple(frozenset(j for j in range(m) if mask & (1 << j))
                     for mask in range(1, 1 << m))
        for matrix in product(rows, repeat=n):
            yield n, m, matrix


def maps():
    for n, m in product(range(3), repeat=2):
        for targets in product(range(m), repeat=n):
            yield n, m, targets


def path_sum(arrows):
    """Sum over full intermediate-state assignments, never nested matrix products."""
    n, m = arrows[0][0], arrows[-1][1]
    middle = tuple(range(a[1]) for a in arrows[:-1])
    output = []
    for start in range(n):
        row = []
        for end in range(m):
            total = Q(0)
            for interior in product(*middle):
                states = (start,) + interior + (end,)
                weight = Q(1)
                for i, arrow in enumerate(arrows):
                    weight *= arrow[2][states[i]][states[i + 1]]
                total += weight
            row.append(total)
        output.append(tuple(row))
    return n, m, tuple(output)


def reachable(arrows):
    output = []
    for start in range(arrows[0][0]):
        current = {start}
        for arrow in arrows:
            current = {j for i in current for j in arrow[2][i]}
        output.append(frozenset(current))
    return arrows[0][0], arrows[-1][1], tuple(output)


def positive_support(kernel):
    return kernel[0], kernel[1], tuple(frozenset(j for j, value in enumerate(row)
                                               if value > 0) for row in kernel[2])


def deterministic_kernel(mapping):
    n, m, targets = mapping
    return n, m, tuple(tuple(Q(int(j == target)) for j in range(m)) for target in targets)


def deterministic_relation(mapping):
    return mapping[0], mapping[1], tuple(frozenset((j,)) for j in mapping[2])


def compose_maps(first, second):
    return first[0], second[1], tuple(second[2][j] for j in first[2])


def as_tuple(arrow):
    return arrow.n, arrow.m, arrow.rows
