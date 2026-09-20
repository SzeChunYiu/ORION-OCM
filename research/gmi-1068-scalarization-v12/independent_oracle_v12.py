"""Exact independent component signs, scalar evaluation, and separating witnesses."""
from fractions import Fraction
from itertools import product


def vector(value):
    if type(value) not in (tuple, list):
        raise ValueError("vector must be a list or tuple")
    if any(type(entry) not in (int, Fraction) for entry in value):
        raise ValueError("exact non-boolean rational entries required")
    return tuple(Fraction(entry) for entry in value)


def differences(first, second):
    first, second = vector(first), vector(second)
    if len(first) != len(second):
        raise ValueError("different dimensions")
    return tuple(a - b for a, b in zip(first, second))


def relation(first, second):
    delta = differences(first, second)
    negative = tuple(i for i, value in enumerate(delta) if value < 0)
    positive = tuple(i for i, value in enumerate(delta) if value > 0)
    return {"le": not positive, "strict": bool(negative) and not positive,
            "negative": negative, "positive": positive,
            "incomparable": bool(negative) and bool(positive)}


def score(weights, values):
    weights, values = vector(weights), vector(values)
    if len(weights) != len(values):
        raise ValueError("different dimensions")
    # Accumulate integer numerator/denominator products independently of sum/dot.
    numerator, denominator = 0, 1
    for weight, value in zip(weights, values):
        top = weight.numerator * value.numerator
        bottom = weight.denominator * value.denominator
        numerator, denominator = numerator * bottom + top * denominator, denominator * bottom
        reduced = Fraction(numerator, denominator)
        numerator, denominator = reduced.numerator, reduced.denominator
    return Fraction(numerator, denominator)


def separating_weights(first, second, coordinate):
    delta = differences(first, second)
    if type(coordinate) is not int or not 0 <= coordinate < len(delta) or delta[coordinate] <= 0:
        raise ValueError("chosen coordinate must have positive difference")
    # Independent rational construction: compensate only negative coordinates.
    loss = sum((-value for value in delta if value < 0), Fraction())
    weights = [Fraction(1) for _ in delta]
    weights[coordinate] = (loss + 1) / delta[coordinate]
    return tuple(weights)


def check_separator(first, second, weights, sign=1):
    delta, weights = differences(first, second), vector(weights)
    if type(sign) is not int or sign not in (-1, 1):
        raise ValueError("invalid orientation")
    if len(weights) != len(delta) or any(weight <= 0 for weight in weights):
        raise ValueError("separator must be strictly positive and aligned")
    if sign * score(weights, delta) <= 0:
        raise ValueError("not a strict separator")
    return True


def frontier(points):
    if type(points) not in (tuple, list):
        raise ValueError("finite point sequence required")
    points = tuple(vector(point) for point in points)
    if points and any(len(point) != len(points[0]) for point in points):
        raise ValueError("different dimensions")
    return tuple(i for i, point in enumerate(points)
                 if not any(relation(other, point)["strict"] for other in points))


def normalized(weights):
    weights = vector(weights)
    if not weights or any(weight <= 0 for weight in weights):
        raise ValueError("strictly positive nonempty weights required")
    total = sum(weights, Fraction())
    return tuple(weight / total for weight in weights)


def grids():
    for dimension in range(5):
        yield (dimension, tuple(product((-1, 0, 1), repeat=dimension)),
               tuple(product((1, 2, 3), repeat=dimension)),
               tuple(product((0, 1, 2), repeat=dimension)))
