"""Exact finite-vector scalarization, with explicit order and weight contracts."""
from fractions import Fraction


def validate_vector(vector):
    if not isinstance(vector, (tuple, list)):
        raise ValueError("vector must be a tuple or list")
    if any(type(value) not in (int, Fraction) for value in vector):
        raise ValueError("coordinates must be exact integers or fractions")
    return tuple(vector)


def _pair(left, right):
    left, right = validate_vector(left), validate_vector(right)
    if len(left) != len(right):
        raise ValueError("dimension mismatch")
    return left, right


def dot(weights, vector):
    weights, vector = _pair(weights, vector)
    return sum(weight * value for weight, value in zip(weights, vector))


def dominates(x, y):
    """Return x <= y coordinatewise (the minimization orientation)."""
    x, y = _pair(x, y)
    return all(a <= b for a, b in zip(x, y))


def strict_dominates(x, y):
    """Return coordinate domination with at least one strict improvement."""
    x, y = _pair(x, y)
    return all(a <= b for a, b in zip(x, y)) and any(a < b for a, b in zip(x, y))


def separator(x, y, k):
    """Positive weights making x score strictly higher, given x[k] > y[k]."""
    x, y = _pair(x, y)
    if type(k) is not int or not 0 <= k < len(x):
        raise ValueError("invalid separating coordinate")
    difference = tuple(a - b for a, b in zip(x, y))
    pivot = difference[k]
    if pivot <= 0:
        raise ValueError("selected coordinate is not a strict positive difference")
    remainder = sum(abs(value) for index, value in enumerate(difference) if index != k)
    return tuple(remainder + 1 if index == k else pivot for index in range(len(x)))


def reversing_weights(x, y):
    """Return positive (u,v) with u.x > u.y and v.x < v.y for incomparables."""
    x, y = _pair(x, y)
    positive = next((i for i, (a, b) in enumerate(zip(x, y)) if a > b), None)
    negative = next((i for i, (a, b) in enumerate(zip(x, y)) if a < b), None)
    if positive is None or negative is None:
        raise ValueError("vectors are not incomparable")
    return separator(x, y, positive), separator(y, x, negative)


def pareto_minima(points):
    """Original indices of nondominated points, retaining equal duplicates."""
    if not isinstance(points, (tuple, list)):
        raise ValueError("points must be a tuple or list")
    vectors = tuple(validate_vector(point) for point in points)
    if vectors and any(len(vector) != len(vectors[0]) for vector in vectors):
        raise ValueError("dimension mismatch")
    return tuple(index for index, point in enumerate(vectors)
                 if not any(strict_dominates(other, point) for other in vectors))
