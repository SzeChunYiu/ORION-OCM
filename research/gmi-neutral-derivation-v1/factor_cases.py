"""Deterministic held-graph factor generation; no fitted performance constants."""

from fractions import Fraction
from itertools import combinations, product

from factor_model import Algebra, Factor


def graph_edges(kind, n):
    if kind == "chain":
        return [(i, i + 1) for i in range(n - 1)]
    if kind == "star":
        return [(0, i) for i in range(1, n)]
    if kind == "cycle":
        return [(i, i + 1) for i in range(n - 1)] + [(0, n - 1)]
    if kind == "clique":
        return list(combinations(range(n), 2))
    if kind == "disconnected":
        return [(0, 1), (2, 3)]  # fifth variable is deliberately isolated
    raise ValueError("unknown graph")


def make_case(spec, algebra_name):
    n, q = spec["variables"], spec["domain_size"]
    factors = []
    for index, (left, right) in enumerate(graph_edges(spec["graph"], n)):
        values = []
        for x, y in product(range(q), repeat=2):
            code = (x + 2 * y + index) % (q + 1)
            if algebra_name == "boolean":
                values.append(code != 0)
            elif algebra_name == "rational":
                values.append(Fraction(code + 1, q + 2))
            else:
                values.append(code)
        factors.append(Factor((left, right), tuple(values)))
    return (q,) * n, factors, Algebra(algebra_name)


def direct_value(sizes, factors, algebra):
    """Independent complete assignment interpretation, without elimination."""
    terms = []
    for row in product(*(range(q) for q in sizes)):
        extracted = []
        for factor in factors:
            # Decode all table coordinates independently from Factor.at.
            axes = product(*(range(sizes[v]) for v in factor.scope))
            mapping = dict(zip(axes, factor.values))
            extracted.append(mapping[tuple(row[v] for v in factor.scope)])
        if algebra.name == "boolean":
            terms.append(all(extracted))
        elif algebra.name == "rational":
            value = Fraction(1)
            for item in extracted:
                value *= item
            terms.append(value)
        else:
            terms.append(None if None in extracted else sum(extracted))
    if algebra.name == "boolean":
        return any(terms)
    if algebra.name == "rational":
        return sum(terms, Fraction(0))
    finite = [x for x in terms if x is not None]
    return min(finite) if finite else None
