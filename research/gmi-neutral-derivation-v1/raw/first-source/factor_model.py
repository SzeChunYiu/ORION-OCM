"""Finite factor tables and exact, explicitly chosen semiring operations."""

from dataclasses import dataclass
from fractions import Fraction
from itertools import product
from math import prod


@dataclass(frozen=True)
class Factor:
    scope: tuple
    values: tuple

    def at(self, assignment, sizes):
        index = 0
        for variable in self.scope:
            index = index * sizes[variable] + assignment[variable]
        return self.values[index]


@dataclass(frozen=True)
class Algebra:
    name: str

    def __post_init__(self):
        if self.name not in ("boolean", "rational", "min_plus"):
            raise ValueError("unknown algebra")

    @property
    def zero(self):
        return {"boolean": False, "rational": Fraction(0), "min_plus": None}[self.name]

    @property
    def one(self):
        return {"boolean": True, "rational": Fraction(1), "min_plus": 0}[self.name]

    def add(self, left, right):
        if self.name == "boolean":
            return left or right
        if self.name == "rational":
            return left + right
        if left is None:
            return right
        if right is None:
            return left
        return min(left, right)

    def multiply(self, left, right):
        if self.name == "boolean":
            return left and right
        if self.name == "rational":
            return left * right
        return None if left is None or right is None else left + right

    def valid(self, value):
        if self.name == "boolean":
            return type(value) is bool
        if self.name == "rational":
            return isinstance(value, Fraction) and value >= 0
        return value is None or (type(value) is int and value >= 0)


def assignments(scope, sizes):
    for row in product(*(range(sizes[v]) for v in scope)):
        yield dict(zip(scope, row))


def validate(sizes, factors, algebra):
    if any(type(size) is not int or size < 1 for size in sizes):
        raise ValueError("domains must have positive integral size")
    for factor in factors:
        if len(set(factor.scope)) != len(factor.scope):
            raise ValueError("repeated variable in factor")
        if any(type(v) is not int or not 0 <= v < len(sizes) for v in factor.scope):
            raise ValueError("unknown variable")
        if len(factor.values) != prod(sizes[v] for v in factor.scope):
            raise ValueError("table length does not match its scope")
        if not all(algebra.valid(value) for value in factor.values):
            raise ValueError("value is outside the selected semiring")


def encoded_bits(value):
    """Canonical scalar payload-size coordinate, excluding container overhead."""
    if value is None or type(value) is bool:
        return 1
    if isinstance(value, Fraction):
        return max(1, value.numerator.bit_length()) + value.denominator.bit_length()
    return max(1, value.bit_length())


def serialize_value(value):
    if isinstance(value, Fraction):
        return f"{value.numerator}/{value.denominator}"
    return value
