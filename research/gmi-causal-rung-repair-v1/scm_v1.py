"""Exact binary endogenous X,Y with arbitrary shared finite hidden root."""
from fractions import Fraction as F
from itertools import product

TYPES = tuple(product((0, 1), repeat=3))  # factual X, Y(0), Y(1)
INTERVENTIONS = tuple(product((None, 0, 1), repeat=2))

def probability(value):
    if type(value) not in (int, F) or not 0 <= value <= 1:
        raise ValueError('exact rational probability required')
    return F(value)

def model(weights):
    weights = tuple(probability(w) for w in weights)
    if len(weights) != 8 or sum(weights) != 1:
        raise ValueError('eight normalized response-type masses required')
    return weights

def law(weights, intervention=(None, None)):
    weights = model(weights)
    if (type(intervention) is not tuple or len(intervention) != 2
            or any(v is not None and (type(v) is not int or v not in (0, 1))
                   for v in intervention)):
        raise ValueError('intervene only on endogenous X,Y')
    ix, iy = intervention
    out = [F(0)] * 4
    for (actual_x, y0, y1), mass in zip(TYPES, weights):
        x = actual_x if ix is None else ix
        y = (y0, y1)[x] if iy is None else iy
        out[2*x+y] += mass
    return tuple(out)

def complete_laws(weights):
    return tuple(law(weights, action) for action in INTERVENTIONS)

def evidence(weights):
    p = law(weights)
    return p, sum(law(weights, (0, None))[1::2]), sum(law(weights, (1, None))[1::2])

def necessity(weights):
    weights = model(weights)
    d = law(weights)[3]
    if not d:
        raise ValueError('undefined conditioning event X=1,Y=1')
    return weights[TYPES.index((1, 0, 1))] / d

def from_units(rows):
    rows = tuple(rows)
    if not rows or any(type(row) is not tuple or len(row) != 3
                       or any(type(v) is not int or v not in (0, 1) for v in row)
                       for row in rows):
        raise ValueError('nonempty binary root-unit rows required')
    return model(tuple(F(rows.count(t), len(rows)) for t in TYPES))
