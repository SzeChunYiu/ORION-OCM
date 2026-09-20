"""Strict inputs and actual immutable context, frontier and source helpers."""
from fractions import Fraction
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
        raise ValueError("immutable source binding mismatch")
    return module


parent = source_module("core_v20", "gmi-1068-frontier-simulation-v20/core_v20.py")
frontier = source_module("_gmi_transports_frontier_v20", "gmi-1068-frontier-simulation-v20/frontier_v20.py")
old_af = source_module("_gmi_original_af_v24", "gmi-833-af-barrier-context-v1/af_core_v1.py")
old_choice = source_module("_gmi_original_choice_v24", "gmi-833-morphology-selection-schema-v1/morphology_selection_schema_v1.py")
Context, checked, observe = parent.Context, parent.checked, parent.observe
need, index, nat, subset = parent.need, parent.index, parent.nat, parent.subset


def rational(value):
    need(type(value) is Fraction, "exact Fraction required")
    return value


def ids(values):
    need(type(values) is tuple, "canonical ID tuple required")
    need(all(type(v) is str and v for v in values), "nonempty string IDs required")
    need(len(set(values)) == len(values), "duplicate ID")
    return values


def code_context(admitted, defined, relation):
    n = len(admitted)
    context = Context(n, n, admitted, defined,
                      tuple(i if defined[i] else None for i in range(n)), relation)
    checked(context)
    return context
