"""Pinned partial-context and continuation interfaces shared by this study."""
import importlib.util
from pathlib import Path
import sys

RESEARCH = Path(__file__).resolve().parents[1]


def source_module(name, relative):
    path = RESEARCH / relative
    if name not in sys.modules:
        spec = importlib.util.spec_from_file_location(name, path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
    module = sys.modules[name]
    if Path(module.__file__).resolve() != path.resolve():
        raise ValueError("inherited module binding mismatch")
    return module


context = source_module("_gmi_context_bridge_v17", "gmi-1068-context-specializations-v17/core_v17.py")
legacy = source_module("_gmi_immutable_continuation_v8", "gmi-1068-continuation-v8/continuation_v8.py")
Context, checked, observe = context.Context, context.checked, context.observe
LegacyMachine, budget_lift = legacy.Machine, legacy.budget_lift


def need(condition, message):
    if not condition:
        raise ValueError(message)


def nat(value):
    need(type(value) is int and value >= 0, "nonnegative integer required")
    return value


def index(value, size):
    need(type(value) is int and 0 <= value < size, "index outside declared domain")
    return value


def subset(values, size):
    need(type(values) is tuple, "canonical index tuple required")
    for value in values:
        index(value, size)
    need(len(set(values)) == len(values), "duplicate set member")
    return values


def relation(matrix, size):
    need(type(matrix) is tuple and len(matrix) == size, "relation dimension")
    need(all(type(row) is tuple and len(row) == size
             and all(type(value) is bool for value in row) for row in matrix),
         "canonical Boolean matrix required")
    return matrix


def order(matrix):
    need(type(matrix) is tuple, "canonical order tuple required")
    relation(matrix, len(matrix))
    return context.order(matrix)
