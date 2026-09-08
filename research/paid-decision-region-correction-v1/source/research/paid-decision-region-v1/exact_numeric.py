"""Verbatim PR159 represented-rational and finite-ID foundation.
Source: qualified decision_core.py c0705b32136f53843595c6bae9d0e750e682cbe92af9a4d0de3289140f8df10b.
Only the two function bodies are reused; provenance is in REUSE.json.
"""
from fractions import Fraction
from math import isfinite


def _rational(value):
    if type(value) not in (int, Fraction, float):
        raise TypeError("numeric input must be int, Fraction, or finite float")
    if type(value) is float and not isfinite(value):
        raise ValueError("numeric input must be finite")
    return Fraction(value)


def _items(values, name, allow_empty=False):
    values = tuple(values)
    if len(set(values)) != len(values) or (not values and not allow_empty):
        raise ValueError(name + " must contain distinct IDs and be nonempty")
    return values

