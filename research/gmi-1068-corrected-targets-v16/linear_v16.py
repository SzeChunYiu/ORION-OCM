"""Exact finite linear evaluation; basis extraction does not certify linearity."""
from fractions import Fraction


def vector(value):
    if type(value) is not tuple or any(type(x) is not Fraction for x in value):
        raise ValueError("canonical tuple of exact Fraction values required")
    return value


def scalar(value):
    if type(value) is not Fraction:
        raise ValueError("exact Fraction result required")
    return value


def weighted(coeffs, profile):
    vector(coeffs)
    vector(profile)
    if len(coeffs) != len(profile):
        raise ValueError("coefficient/profile dimension mismatch")
    return sum((a * b for a, b in zip(coeffs, profile)), Fraction(0))


def basis_coefficients(function, dimension):
    if not callable(function) or type(dimension) is not int or dimension < 0:
        raise ValueError("callable and nonnegative dimension required")
    scalar(function(tuple(Fraction(0) for _ in range(dimension))))
    return tuple(scalar(function(tuple(Fraction(int(i == j))
                                       for j in range(dimension))))
                 for i in range(dimension))


def representation_at(function, coeffs, profile):
    if not callable(function):
        raise ValueError("callable required")
    value = weighted(coeffs, profile)
    return scalar(function(profile)) == value


def nonnegative(coeffs):
    return all(value >= 0 for value in vector(coeffs))


def normalized(coeffs):
    return sum(vector(coeffs), Fraction(0)) == 1
