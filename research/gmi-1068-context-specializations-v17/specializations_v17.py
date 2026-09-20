"""Declared scalar, Boolean, product and information orders on actual contexts."""
from dataclasses import dataclass

from core_v17 import Context, checked, flags, observe


@dataclass(frozen=True)
class Encoded:
    context: Context
    labels: tuple

    def __post_init__(self):
        checked(self.context)
        if type(self.labels) is not tuple or len(self.labels) != self.context.m:
            raise ValueError("one label per context value required")
        try:
            unique = len(set(self.labels)) == len(self.labels)
        except TypeError as exc:
            raise ValueError("hashable labels required") from exc
        if not unique:
            raise ValueError("distinct labels required")


def decoded(encoded, history):
    if type(encoded) is not Encoded:
        raise ValueError("Encoded context required")
    tag, value = observe(encoded.context, history)
    return tag, encoded.labels[value] if tag == "VALUE" else None


def inputs(admitted, values):
    flags(admitted)
    if type(values) is not tuple or len(values) != len(admitted):
        raise ValueError("one value or undefined marker per history required")


def encode(admitted, values, relation):
    inputs(admitted, values)
    labels = tuple(dict.fromkeys(v for v in values if v is not None))
    indices = {v: i for i, v in enumerate(labels)}
    defined = tuple(v is not None for v in values)
    coded = tuple(indices[v] if v is not None else None for v in values)
    ordering = tuple(tuple(bool(relation(a, b)) for b in labels) for a in labels)
    return Encoded(Context(len(admitted), len(labels), admitted, defined, coded, ordering), labels)


def utility(admitted, values):
    inputs(admitted, values)
    if any(v is not None and type(v) is not int for v in values):
        raise ValueError("integer utility or undefined required")
    return encode(admitted, values, lambda a, b: a <= b)


def acceptance(admitted, values):
    inputs(admitted, values)
    if any(v is not None and type(v) is not bool for v in values):
        raise ValueError("Boolean acceptance or undefined required")
    return encode(admitted, values, lambda a, b: not a or b)


def acceptance_numeric(admitted, values):
    acceptance(admitted, values)
    return utility(admitted, tuple(None if v is None else int(v) for v in values))


def vector(admitted, values, dimension, prefer_lower=False):
    inputs(admitted, values)
    if type(dimension) is not int or dimension < 0 or type(prefer_lower) is not bool:
        raise ValueError("nonnegative dimension and Boolean preference required")
    for value in values:
        if value is not None and (type(value) is not tuple or len(value) != dimension
                                  or any(type(v) is not int for v in value)):
            raise ValueError("integer vector of declared dimension required")
    relation = (lambda a, b: all(x >= y for x, y in zip(a, b))) if prefer_lower else (
        lambda a, b: all(x <= y for x, y in zip(a, b)))
    return encode(admitted, values, relation)


def confidence(admitted, values, hypotheses):
    inputs(admitted, values)
    if type(hypotheses) is not int or hypotheses < 0:
        raise ValueError("nonnegative hypothesis count required")
    for value in values:
        if value is not None and (type(value) is not frozenset or not value
                                  or any(type(v) is not int or not 0 <= v < hypotheses
                                         for v in value)):
            raise ValueError("nonempty subset of declared hypotheses required")
    return encode(admitted, values, lambda a, b: b <= a)
