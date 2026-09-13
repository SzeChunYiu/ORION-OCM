"""Exact finite witnesses for ARC-5 (checklist item 32).

ARC-5a: bounded creation inside a predeclared potential register preserves the
ARC-1 per-row certificate; unbudgeted/over-budget creation is refused.
ARC-5b(i): certificates hold out to n=512 with monotone tightening.
ARC-5b(ii): hostile unbounded-creation witness spends k*w*alpha > alpha.

Exact Fractions only. CPython 3.8 safe.
"""

from fractions import Fraction as F


def tail_upper_2(n, epsilon, terms=8):
    """Binary-alphabet ARC tail bound (mirror of row_confidence_v1, self-contained)."""
    if type(n) is not int or n < 1:
        raise ValueError("positive visit index required")
    if not isinstance(epsilon, F) or not F(0) <= epsilon <= F(1):
        raise ValueError("exact rational epsilon in [0,1] required")
    if epsilon == F(1):
        return F(0)
    x, term, lower = 2 * n * epsilon * epsilon, F(1), F(1)
    for j in range(1, terms + 1):
        term *= x / j
        lower += term
    return min(F(1), F(2) / lower)


def grid_radius(n, alpha, weight, terms=8):
    """Least passing j/n radius, self-contained mirror of radius(2,n,...)."""
    if type(n) is not int or n < 0:
        raise ValueError("nonnegative visit index required")
    for v in (alpha, weight):
        if not isinstance(v, F) or not F(0) < v < F(1):
            raise ValueError("alpha/weight must be exact rationals in (0,1)")
    if n == 0:
        return F(1)
    target = alpha * weight / (n * (n + 1))
    low, high = 0, n
    while low < high:
        mid = (low + high) // 2
        if tail_upper_2(n, F(mid, n), terms) <= target:
            high = mid
        else:
            low = mid + 1
    return F(low, n)


class PotentialRegister(object):
    """Finite potential rows with predeclared weights; creation spends budget."""

    def __init__(self, weights, budget):
        weights = tuple(weights)
        if not weights or any(not isinstance(w, F) or w <= 0 for w in weights):
            raise ValueError("positive exact weights required")
        if sum(weights) > 1:
            raise ValueError("extended weights must sum to at most one")
        if type(budget) is not int or budget < 0 or budget > len(weights) - 1:
            raise ValueError("budget must cover at most the creatable rows")
        self.weights = weights
        self.budget = budget
        self.created = [True] + [False] * (len(weights) - 1)
        self.spent = 0

    def create(self, j):
        if type(j) is not int or not 0 <= j < len(self.weights):
            raise ValueError("row index out of potential register")
        if self.created[j]:
            raise ValueError("row already live")
        if self.spent >= self.budget:
            raise ValueError("creation budget exhausted")
        self.created[j] = True
        self.spent += 1
        return self.weights[j]

    def live_weights(self):
        return [w for w, live in zip(self.weights, self.created) if live]


def hostile_budget_spend(weight, creations):
    """Total alpha-fraction spent if each of `creations` new rows demands `weight`."""
    if not isinstance(weight, F) or weight <= 0:
        raise ValueError("positive exact weight required")
    if type(creations) is not int or creations < 0:
        raise ValueError("nonnegative creation count required")
    return creations * weight


def summable_weights(n):
    """Candidate infinite budget w_j = 2^{-j-2}; partial sums stay below 1."""
    if type(n) is not int or n < 1:
        raise ValueError("positive term count required")
    return [F(1, 2 ** (j + 2)) for j in range(n)]
