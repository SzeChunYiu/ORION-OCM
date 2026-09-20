"""Cached actual parent implementations and strict finite input guards."""
import importlib.util
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]


def need(condition, message):
    if not condition:
        raise ValueError(message)


def nat(value):
    need(type(value) is int and value >= 0, "expected natural integer")
    return value


def index(value, size):
    nat(value)
    need(value < size, "index outside declared set")
    return value


def tup(value):
    need(type(value) is tuple, "expected exact tuple")
    return value


def source(name, package):
    path = ROOT / "research" / package / (name + ".py")
    if name in sys.modules:
        module = sys.modules[name]
        need(Path(module.__file__).resolve() == path.resolve(), "source module collision")
        return module
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


paths = source("paths_v11", "gmi-1068-typed-foundation-v11")
stochastic = source("stochastic_v14", "gmi-1068-stochastic-process-v14")
core26 = source("core_v26", "gmi-1068-admission-structure-v26")
functors = source("functors_v26", "gmi-1068-admission-structure-v26")
restrictions = source("restrictions_v26", "gmi-1068-admission-structure-v26")
resources = source("resource_v26", "gmi-1068-admission-structure-v26")
Typed, Table = core26.Typed, core26.Table
Kernel, Relation = stochastic.Kernel, stochastic.Relation
