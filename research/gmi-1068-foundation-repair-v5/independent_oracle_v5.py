"""Independent finite oracles; imports no foundation implementation.

These operate on known-valid explicit category presentations. They do not
certify an arbitrary presentation, infinite category, or empirical coverage.
"""

from fractions import Fraction
from itertools import combinations
from math import lcm


def powerset(values):
    values = tuple(values)
    for size in range(len(values) + 1):
        yield from (frozenset(s) for s in combinations(values, size))


def reference_admissibility(identities, compose, allowed):
    """Compute the least composition-closed superset via fixed-point iteration."""
    seed = frozenset(allowed)
    closure = set(seed)
    while True:
        enlarged = closure | {
            result for (first, second), result in compose.items()
            if {first, second}.issubset(closure)
        }
        if enlarged == closure:
            break
        closure = enlarged
    units_present = not (set(identities) - seed)
    closed = closure == set(seed)
    return {"identities": units_present, "composition": closed,
            "subcategory": units_present and closed}


def reference_aggregates(profile, weights):
    """Independent sorted extrema and common-denominator integer arithmetic."""
    ordered = sorted(Fraction(value) for value in profile)
    terms = [Fraction(value) * Fraction(weight)
             for value, weight in zip(profile, weights, strict=True)]
    denominator = lcm(*(term.denominator for term in terms))
    numerator = sum(term.numerator * (denominator // term.denominator)
                    for term in terms)
    return {"min": ordered[0], "max": ordered[-1],
            "weighted": Fraction(numerator, denominator)}


def cyclic_three():
    return 3, (0,), {(a, b): (a + b) % 3 for a in range(3) for b in range(3)}


def walking_arrow():
    # Arrow 0=id_A, 1=id_B, 2=A->B. The right argument acts second.
    return 3, (0, 1), {(0, 0): 0, (1, 1): 1,
                       (0, 2): 2, (2, 1): 2}


def resource_category(limit):
    # Independently construct through combinations, not nested inequality loops.
    nodes = tuple(range(limit + 1))
    labels = tuple(sorted([(i, i) for i in nodes] + list(combinations(nodes, 2))))
    lookup = {pair: index for index, pair in enumerate(labels)}
    identities = tuple(lookup[(node, node)] for node in nodes)
    compose = {}
    for first, (start, middle) in enumerate(labels):
        for second, (other_middle, end) in enumerate(labels):
            if middle == other_middle:
                compose[first, second] = lookup[start, end]
    return labels, (len(labels), identities, compose)
