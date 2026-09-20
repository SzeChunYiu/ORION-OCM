"""Strict exact affine inputs and immutable partial-context/frontier parents."""
from dataclasses import dataclass
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
frontier = source_module("_gmi_affine_frontier_v20", "gmi-1068-frontier-simulation-v20/frontier_v20.py")
Context, checked, observe = parent.Context, parent.checked, parent.observe
need, index = parent.need, parent.index


def rational(value):
    need(type(value) is Fraction, "exact Fraction required")
    return value


@dataclass(frozen=True)
class AffineFamily:
    ids: tuple
    intercepts: tuple
    slopes: tuple
    admitted: tuple
    defined: tuple

    def __post_init__(self):
        fields = (self.ids, self.intercepts, self.slopes, self.admitted, self.defined)
        need(all(type(v) is tuple for v in fields), "canonical tuples required")
        need(all(len(v) == len(self.ids) for v in fields), "family dimension")
        need(all(type(v) is str and v for v in self.ids), "nonempty string IDs required")
        need(len(set(self.ids)) == len(self.ids), "duplicate candidate ID")
        for value in self.intercepts + self.slopes:
            rational(value)
        need(all(type(v) is bool for v in self.admitted + self.defined), "Boolean flags required")


def family_checked(family):
    need(type(family) is AffineFamily, "validated AffineFamily required")
    return family


def parameters(family, t):
    family_checked(family)
    rational(t)
    return tuple(a + b * t for a, b in zip(family.intercepts, family.slopes))


def interval(family, lo, hi):
    family_checked(family)
    rational(lo)
    rational(hi)
    need(lo <= hi, "reversed interval")
