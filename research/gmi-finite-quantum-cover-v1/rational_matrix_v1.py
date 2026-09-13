"""Exact real rational arithmetic for supplied witnesses; not a feasibility solver."""
from fractions import Fraction as F


def require(condition, message):
    if not condition:
        raise ValueError(message)


def vector(values):
    require(type(values) in (tuple, list) and bool(values), "empty/nonvector")
    require(all(type(x) is int or isinstance(x, F) for x in values),
            "witness entries must be exact rationals, not floats or bools")
    return tuple(F(x) for x in values)


def matrix(rows, n=None):
    require(type(rows) in (tuple, list) and bool(rows), "empty/nonmatrix")
    out = tuple(vector(row) for row in rows)
    require(len({len(row) for row in out}) == 1, "ragged matrix")
    if n is not None:
        require(len(out) == n and len(out[0]) == n, "wrong square matrix dimension")
    return out


def dot(a, b):
    require(len(a) == len(b), "dot dimension mismatch")
    return sum((x * y for x, y in zip(a, b)), F(0))


def transpose(a):
    return tuple(zip(*a))


def multiply(a, b):
    require(len(a[0]) == len(b), "product dimension mismatch")
    return tuple(tuple(dot(row, col) for col in transpose(b)) for row in a)


def add(a, b):
    require(len(a) == len(b) and len(a[0]) == len(b[0]), "sum dimension mismatch")
    return tuple(tuple(x + y for x, y in zip(row, other)) for row, other in zip(a, b))


def scale(c, a):
    return tuple(tuple(c * x for x in row) for row in a)


def identity(n):
    return tuple(tuple(F(i == j) for j in range(n)) for i in range(n))


def zero(n):
    return scale(F(0), identity(n))


def ray_state(v):
    v = vector(v)
    norm = dot(v, v)
    require(norm > 0, "state ray must be nonzero")
    return tuple(tuple(x * y / norm for y in v) for x in v)


def trace(a):
    require(len(a) == len(a[0]), "trace must be square")
    return sum((a[i][i] for i in range(len(a))), F(0))


def mv(a, v):
    return tuple(dot(row, v) for row in a)


def encode(value):
    if isinstance(value, F):
        return str(value)
    if isinstance(value, dict):
        return {str(k): encode(v) for k, v in value.items()}
    if isinstance(value, (tuple, list)):
        return [encode(x) for x in value]
    return value
