"""Read a complete finite task table; infer affine support and all symmetries."""

from fractions import Fraction as F
from itertools import permutations, product


def infer(table, nin, nout):
    if type(nin) is not int or type(nout) is not int or min(nin, nout) < 1:
        raise ValueError("positive integer dimensions required")
    domain = tuple(product((0, 1), repeat=nin))
    if set(table) != set(domain) or any(len(y) != nout for y in table.values()):
        raise ValueError("complete typed Boolean cube required")
    base = tuple(F(v) for v in table[(0,) * nin])
    columns = []
    for i in range(nin):
        key = tuple(int(j == i) for j in range(nin))
        columns.append(tuple(F(v) - b for v, b in zip(table[key], base)))
    arithmetic = nin * nout
    matrix = tuple(tuple(columns[c][r] for c in range(nin)) + (base[r],)
                   for r in range(nout))
    for x in domain:
        for r in range(nout):
            predicted = base[r] + sum(columns[c][r] * x[c] for c in range(nin))
            arithmetic += 2 * nin + 1
            if predicted != F(table[x][r]):
                raise ValueError("task is not affine on the declared cube")
    allowed = {(r, c) for r in range(nout) for c in range(nin + 1) if matrix[r][c]}
    generators = []
    checks = 0
    pairs = 0
    for pin in permutations(range(nin)):
        for pout in permutations(range(nout)):
            pairs += 1
            equal = True
            aug = pin + (nin,)
            for r in range(nout):
                for c in range(nin + 1):
                    checks += 1
                    equal = equal and matrix[r][c] == matrix[pout[r]][aug[c]]
            if equal:
                generators.append((pin, pout))
    return {"matrix": matrix, "allowed": allowed, "generators": tuple(generators),
            "counters": {"table_rows": len(domain), "affinity_rational_arithmetic": arithmetic,
                         "permutation_pairs": pairs, "coefficient_slots_visited": checks,
                         "accepted_pairs": len(generators)}}
