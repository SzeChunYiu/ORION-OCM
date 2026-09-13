"""Independent finite-action oracle and exact coefficient-risk controls."""

from fractions import Fraction as F


def group(nin, nout, generators):
    identity = (tuple(range(nin)), tuple(range(nout)))
    seen, queue = {identity}, [identity]
    products = 0
    for a, b in queue:
        for c, d in generators:
            products += 1
            pair = (tuple(c[a[i]] for i in range(nin)),
                    tuple(d[b[i]] for i in range(nout)))
            if pair not in seen:
                seen.add(pair)
                queue.append(pair)
    return tuple(queue), products


def predict(nin, nout, generators, allowed):
    actions, products = group(nin, nout, generators)
    cells = {(r, c) for r in range(nout) for c in range(nin + 1)}
    orbits = []
    while cells:
        r, c = min(cells)
        orbit = frozenset((pout[r], pin[c] if c < nin else nin)
                          for pin, pout in actions)
        cells -= orbit
        if orbit <= allowed:
            orbits.append(orbit)
    core = set().union(*orbits) if orbits else set()
    fixed_sum = sum(sum(pout[r] == r and (c == nin or pin[c] == c)
                        for r, c in core) for pin, pout in actions)
    if fixed_sum % len(actions):
        raise ValueError("Burnside count not integral")
    return {"orbits": tuple(orbits), "dimension": fixed_sum // len(actions),
            "group_size": len(actions), "generator_products": products,
            "core": core}


def check_certificate(compiled, prediction):
    ncols = compiled["nin"] + 1
    expected = {frozenset(r * ncols + c for r, c in orbit)
                for orbit in prediction["orbits"]}
    actual = set()
    instructions = []
    for k, v in enumerate(compiled["basis"]):
        if len(v) != ncols * compiled["nout"] or any(x not in (0, 1) for x in v):
            return False
        actual.add(frozenset(i for i, x in enumerate(v) if x))
        instructions.extend((i // ncols, i % ncols, k) for i, x in enumerate(v) if x)
    return (actual == expected and len(compiled["basis"]) == len(expected)
            and compiled["dimension"] == prediction["dimension"] == len(expected)
            and tuple(instructions) == compiled["instructions"]
            and compiled["counters"]["active_entries"] == len(instructions)
            and compiled["counters"]["rank"] == ncols * compiled["nout"] - len(expected))


def project(vector, orbits, ncols):
    result = [F(0)] * len(vector)
    for orbit in orbits:
        ids = [r * ncols + c for r, c in orbit]
        mean = sum(F(vector[i]) for i in ids) / len(ids)
        for i in ids:
            result[i] = mean
    return tuple(result)


def norm2(vector):
    return sum(F(x) ** 2 for x in vector)


def exact_risk(theta, orbits, ncols):
    """Noise uniform over ±coordinate axes, covariance I/D; no simulation."""
    dim = len(theta)
    risk = F(0)
    for i in range(dim):
        for sign in (-1, 1):
            z = list(theta)
            z[i] += sign
            estimate = project(z, orbits, ncols)
            risk += norm2(a - b for a, b in zip(estimate, theta)) / (2 * dim)
    projection = project(theta, orbits, ncols)
    bias = norm2(a - b for a, b in zip(projection, theta))
    predicted = bias + F(len(orbits), dim)
    return risk, predicted, bias
