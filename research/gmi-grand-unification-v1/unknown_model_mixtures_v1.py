"""Exact finite-mixture minimax certificates for per-model expected work."""
from fractions import Fraction as F
from itertools import combinations


def solve_linear(matrix, rhs):
    a = [[F(v) for v in row]+[F(y)] for row, y in zip(matrix, rhs)]
    n = len(a)
    for col in range(n):
        pivot = next((r for r in range(col, n) if a[r][col]), None)
        if pivot is None:
            return None
        a[col], a[pivot] = a[pivot], a[col]
        divisor = a[col][col]
        a[col] = [x/divisor for x in a[col]]
        for r in range(n):
            if r != col:
                factor = a[r][col]
                a[r] = [x-factor*y for x, y in zip(a[r], a[col])]
    return tuple(row[-1] for row in a)


def minimax_mixture(costs):
    """Nature picks its fixed model before the private mixture is sampled."""
    costs = tuple(costs)
    if not costs:
        return dict(value=None, mixture=(), development=dict(bases=0, feasible_vertices=0))
    k = len(costs[0])
    if not k or any(len(v) != k or any(isinstance(x, bool) or not isinstance(x, (int, F)) or x < 0 for x in v) for v in costs):
        raise ValueError("finite nonnegative rational cost vectors required")
    best, witness, bases, vertices = None, (), 0, 0
    for r in range(1, min(k, len(costs))+1):
        for support in combinations(range(len(costs)), r):
            for active in combinations(range(k), r):
                bases += 1
                matrix = [[1]*r+[0]]+[[costs[i][j] for i in support]+[-1] for j in active]
                result = solve_linear(matrix, [1]+[0]*r)
                if result is None:
                    continue
                weights, z = result[:-1], result[-1]
                if any(w < 0 for w in weights) or any(sum(w*costs[i][j] for i, w in zip(support, weights)) > z for j in range(k)):
                    continue
                vertices += 1
                if best is None or z < best:
                    best = z
                    witness = tuple((i, w) for i, w in zip(support, weights) if w)
    if best is None:
        raise AssertionError("nonempty finite minimax polytope has no vertex certificate")
    return dict(value=best, mixture=witness, development=dict(bases=bases, feasible_vertices=vertices))


def charged_minimax(costs, setup):
    if isinstance(setup, bool) or not isinstance(setup, (int, F)) or setup < 0:
        raise ValueError("finite nonnegative exact setup work required")
    costs = tuple(costs)
    mixed = minimax_mixture(costs)
    if not costs:
        return None
    return min(min(map(max, costs)), mixed["value"]+setup)
