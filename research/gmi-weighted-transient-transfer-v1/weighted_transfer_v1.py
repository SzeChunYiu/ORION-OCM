"""Exact finite sufficient certificates; no general confidence-set inference."""
from dataclasses import dataclass
from fractions import Fraction as F

def exact(x):
    if type(x) not in (int, F):
        raise ValueError("finite arithmetic requires integers/Fractions")
    return F(x)

@dataclass(frozen=True)
class Model:
    rows: tuple
    charges: tuple

def model(rows, charges):
    value = Model(tuple(tuple(tuple(exact(p) for p in row) for row in acts)
                        for acts in rows),
                  tuple(tuple(exact(c) for c in acts) for acts in charges))
    validate(value)
    return value

def validate(value):
    n = len(value.rows)
    if not n or len(value.charges) != n:
        raise ValueError("nonempty complete nonterminal register required")
    for acts, costs in zip(value.rows, value.charges):
        if not acts or len(acts) != len(costs):
            raise ValueError("complete common action/charge register required")
        for row, cost in zip(acts, costs):
            if len(row) != n + 2 or any(exact(p) < 0 for p in row):
                raise ValueError("each row includes both labelled terminals")
            if sum(row) != 1 or exact(cost) < 0:
                raise ValueError("probability or nonnegative charge violation")

def certificate(vertices, nominal, weights, beta, ceiling, initial):
    """All rows of all supplied vertices AND nominal define the envelope.

    Return sufficient bounds for their rowwise convex hull. Whether this hull
    contains the true law or a desired statistical region is a separate premise.
    """
    if not vertices:
        raise ValueError("no supplied confidence envelope")
    models = tuple(vertices) + (nominal,)
    for item in models:
        validate(item)
    shape = tuple(map(len, nominal.rows))
    if any(tuple(map(len, m.rows)) != shape for m in models):
        raise ValueError("model interfaces differ")
    n = len(shape)
    w = tuple(map(exact, weights))
    mu = tuple(map(exact, initial))
    b, c = exact(beta), exact(ceiling)
    if len(w) != n or any(v < 1 for v in w) or not 0 <= b < 1 or c < 0:
        raise ValueError("invalid weighted geometric certificate")
    if len(mu) != n + 2 or any(p < 0 for p in mu) or sum(mu) != 1:
        raise ValueError("invalid common initial law")
    eta = zeta = epsilon = F(0)
    for item in models:
        for x, acts in enumerate(item.rows):
            for a, row in enumerate(acts):
                ref = nominal.rows[x][a]
                if sum(row[y] * w[y] for y in range(n)) > b * w[x]:
                    raise ValueError("drift fails, including an unseen row")
                if item.charges[x][a] > c * w[x]:
                    raise ValueError("charge envelope fails")
                eta = max(eta, sum(w[y] * abs(row[y] - ref[y])
                                  for y in range(n)) / w[x])
                zeta = max(zeta, abs(item.charges[x][a] -
                                    nominal.charges[x][a]) / w[x])
                epsilon = max(epsilon, sum(abs(p-q) for p,q in zip(row, ref))/2)
    mass = sum(mu[x] * w[x] for x in range(n))
    return dict(beta=b, ceiling=c, initial_weight=mass, eta=eta, zeta=zeta,
                epsilon=epsilon, expected_steps=mass/(1-b),
                expected_cost=c*mass/(1-b),
                cost_error=mass*(zeta/(1-b)+c*eta/(1-b)**2),
                terminal_error=min(F(1), epsilon*mass/(1-b)))

def tails(cert, horizon):
    if type(horizon) is not int or horizon < 0:
        raise ValueError("nonnegative integer horizon required")
    mass = cert["initial_weight"] * cert["beta"]**horizon
    return dict(survival=min(F(1), mass), alive_weight=mass,
                expected_remaining_cost=cert["ceiling"]*mass/(1-cert["beta"]))
