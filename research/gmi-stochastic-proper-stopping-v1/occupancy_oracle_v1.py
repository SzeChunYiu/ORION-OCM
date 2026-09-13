"""Independent finite oracle: closed subsets + determinant-based flow vertices."""
from fractions import Fraction as F
from itertools import combinations, permutations, product


def independent_viable(model):
    """Union proper-from-start regions across original tables, with traps retained."""
    n, viable = model.goal, set()
    for choices in product(*(range(len(row)) if row else (None,)
                             for row in model.rows)):
        p = [model.rows[s][a].probability if a is not None
             else tuple(F(int(t == s)) for t in range(n+1))
             for s, a in enumerate(choices)]
        bad = set()
        for bits in range(1, 1 << n):
            group = {s for s in range(n) if bits >> s & 1}
            if all(sum(p[s][t] for t in group) == 1 for s in group):
                bad |= group
        while True:
            more = bad | {s for s in range(n) if any(p[s][t] for t in bad)}
            if more == bad:
                break
            bad = more
        viable |= set(range(n)) - bad
    return tuple(sorted(viable))


def determinant(matrix):
    n, result = len(matrix), F(0)
    for order in permutations(range(n)):
        inversions = sum(order[i] > order[j]
                         for i in range(n) for j in range(i+1, n))
        term = F((-1)**inversions)
        for i, j in enumerate(order):
            term *= matrix[i][j]
        result += term
    return result


def cramer(matrix, rhs):
    denom = determinant(matrix)
    if not denom:
        return None
    return tuple(
        determinant([[rhs[i] if j == k else matrix[i][j]
                      for j in range(len(matrix))]
                     for i in range(len(matrix))]) / denom
        for k in range(len(matrix))
    )


def flow_vertices(model, domain, injection=None):
    """Return lexical min(sum expected costs, sum expected actions) with α>0."""
    n = len(domain)
    if not n:
        return (F(0), F(0)), 1
    alpha = tuple(F(x) for x in (injection or (1,)*n))
    if len(alpha) != n or any(x <= 0 for x in alpha):
        raise ValueError("strictly positive injection at every viable state required")
    columns, costs = [], []
    allowed = set(domain) | {model.goal}
    for state in domain:
        for a in model.rows[state]:
            if any(p and t not in allowed for t, p in enumerate(a.probability)):
                continue
            columns.append(tuple(F(int(state == t))-a.probability[t] for t in domain))
            costs.append(a.cost)
    best, accepted = None, 0
    for basis in combinations(range(len(columns)), n):
        matrix = [[columns[j][i] for j in basis] for i in range(n)]
        solution = cramer(matrix, alpha)
        if solution is None or any(y < 0 for y in solution):
            continue
        # Check every conservation row, rather than trusting the solver.
        if any(sum(columns[j][i]*y for j, y in zip(basis, solution))
               != alpha[i] for i in range(n)):
            raise RuntimeError("Cramer output violates conservation")
        pair = (sum(costs[j]*y for j, y in zip(basis, solution)), sum(solution))
        accepted += 1
        if best is None or pair < best:
            best = pair
    if best is None:
        raise ValueError("no feasible flow vertex")
    return best, accepted
