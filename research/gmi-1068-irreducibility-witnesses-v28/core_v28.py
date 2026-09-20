"""Strict adapters loading the immutable context, path and recovery parents once."""
from dataclasses import dataclass
from fractions import Fraction
import importlib.util
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]


def need(condition, message):
    if not condition:
        raise ValueError(message)


def tup(value):
    need(type(value) is tuple, "exact tuple required")
    return value


def index(value, size):
    need(type(value) is int and 0 <= value < size, "strict index outside domain")
    return value


def source(name, package):
    path = ROOT / "research" / package / (name + ".py")
    if name in sys.modules:
        need(Path(sys.modules[name].__file__).resolve() == path.resolve(), "parent module identity drift")
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


semantic = source("semantic_v9", "gmi-1068-r0-foundation-repair-v9")
paths = source("paths_v11", "gmi-1068-typed-foundation-v11")
scalar = source("scalarization_v12", "gmi-1068-scalarization-v12")
contexts = source("context_v15", "gmi-1068-partial-context-v15")
history = source("history_v16", "gmi-1068-corrected-targets-v16")
algebra = source("algebra_v16", "gmi-1068-corrected-targets-v16")
partial = source("partial_v19", "gmi-1068-arrows-only-v19")
categories = source("categories_v19", "gmi-1068-arrows-only-v19")


def typed_key(value):
    if value is None:
        return ("none",)
    if type(value) is bool:
        return ("bool", value)
    if type(value) is int:
        return ("int", value)
    if type(value) is Fraction:
        return ("fraction", value.numerator, value.denominator)
    if type(value) is str:
        return ("str", value)
    if type(value) is tuple:
        return ("tuple", tuple(typed_key(x) for x in value))
    raise ValueError("unsupported exact observation value")


def checked_history(graph, path):
    tup(graph)
    need(len(graph) == 2, "graph shape")
    size, edges = graph
    need(type(size) is int and size >= 0, "nonnegative object count")
    for edge in tup(edges):
        tup(edge)
        need(len(edge) == 2, "edge shape")
        for endpoint in edge:
            index(endpoint, size)
    tup(path)
    need(len(path) == 2, "history shape")
    index(path[0], size)
    for edge in tup(path[1]):
        index(edge, len(edges))
    return paths.canonical(graph, path)


@dataclass(frozen=True)
class Encoded:
    context: object
    roster: tuple
    decoder: tuple

    def __post_init__(self):
        need(type(self.context) is contexts.Context, "actual Context required")
        tup(self.roster)
        tup(self.decoder)
        need(len(self.roster) == self.context.n and len(self.decoder) == self.context.m, "codec dimension")
        for path in self.roster:
            tup(path)
            need(len(path) == 2, "history label shape")
            need(type(path[0]) is int and path[0] >= 0, "strict source label")
            for edge in tup(path[1]):
                need(type(edge) is int and edge >= 0, "strict edge label")
        keys = tuple(typed_key(x) for x in self.roster)
        need(len(set(keys)) == len(keys), "duplicate history label")
        need(all(type(x) is Fraction for x in self.decoder), "exact external fractions required")
        need(len(set(self.decoder)) == len(self.decoder), "noninjective value codec")

    def observe(self, position):
        tag, value = contexts.observe(self.context, position)
        return tag, self.decoder[value] if tag == "VALUE" else None
