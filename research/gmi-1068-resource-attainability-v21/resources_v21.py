"""Concrete ordered accumulators; no universal residual operation is assumed."""
from core_v21 import nat, need

KINDS = ("nat", "vector", "peak", "mixed", "signed")


def kind_checked(kind):
    need(type(kind) is str and kind in KINDS, "undeclared resource semantics")
    return kind


def resource(kind, value):
    kind_checked(kind)
    if kind in ("vector", "mixed"):
        need(type(value) is tuple and len(value) == 2, "two resource coordinates required")
        for coordinate in value:
            nat(coordinate)
    elif kind == "signed":
        need(type(value) is int, "signed integer resource required")
    else:
        nat(value)
    return value


def identity(kind):
    kind_checked(kind)
    return (0, 0) if kind in ("vector", "mixed") else 0


def combine(kind, left, right):
    resource(kind, left)
    resource(kind, right)
    if kind == "vector":
        return left[0] + right[0], left[1] + right[1]
    if kind == "mixed":
        return left[0] + right[0], max(left[1], right[1])
    if kind == "peak":
        return max(left, right)
    return left + right


def le(kind, left, right):
    resource(kind, left)
    resource(kind, right)
    if kind in ("vector", "mixed"):
        return left[0] <= right[0] and left[1] <= right[1]
    return left <= right


def prefix_fold(kind, costs, initial, capacity):
    resource(kind, initial)
    resource(kind, capacity)
    need(type(costs) is tuple, "canonical cost word required")
    for cost in costs:
        resource(kind, cost)
    prefixes = [initial]
    for cost in costs:
        prefixes.append(combine(kind, prefixes[-1], cost))
    return tuple(prefixes), all(le(kind, spent, capacity) for spent in prefixes)
