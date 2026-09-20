"""Actual immutable V19 operations and strict shared guards."""
import importlib.util
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
PARENT = ROOT / "research/gmi-1068-arrows-only-v19"


def source_module(name):
    path = PARENT / (name + ".py")
    if name in sys.modules:
        module = sys.modules[name]
        if Path(module.__file__).resolve() != path:
            raise ValueError("same-name source collision")
        return module
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


old_partial = source_module("partial_v19")
old_categories = source_module("categories_v19")
old_responses = source_module("responses_v19")
Table, Typed = old_partial.Table, old_categories.Typed
need, index = old_partial.need, old_partial.index


def nat(value):
    need(type(value) is int and value >= 0, "expected natural integer")
    return value


def permutation(values, size):
    nat(size)
    need(type(values) is tuple and len(values) == size, "permutation shape")
    for value in values:
        index(value, size)
    need(len(set(values)) == size, "permutation must be bijective")
    return values
