"""Exact original scalar witnesses through the unchanged V12 operations."""
from fractions import Fraction
from core_v28 import need, scalar, tup

WEIGHTS = ((Fraction(2), Fraction(1)), (Fraction(1), Fraction(2)))


def vector(values):
    tup(values)
    need(all(type(x) is Fraction for x in values), "exact Fraction coordinates required")
    return values


def dot(weights, profile):
    return Fraction(scalar.dot(vector(weights), vector(profile)))


def dominates(left, right):
    return scalar.dominates(vector(left), vector(right))


def strict_dominates(left, right):
    return scalar.strict_dominates(vector(left), vector(right))
