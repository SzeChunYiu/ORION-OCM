"""Strict immutable-parent loading and shared structural checks."""
from dataclasses import fields, is_dataclass
import importlib.util
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]


def need(condition, message):
    if not condition:
        raise ValueError(message)


def tup(value):
    need(type(value) is tuple, "exact tuple required")
    return value


def nat(value):
    need(type(value) is int and value >= 0, "strict natural required")
    return value


def index(value, size):
    nat(value)
    need(value < size, "index outside declared domain")
    return value


def source(path):
    name = path.stem
    if name in sys.modules:
        need(Path(sys.modules[name].__file__).resolve() == path.resolve(), "parent identity drift")
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


PINS = json.loads(Path(__file__).with_name("SOURCE_PINS_V29.json").read_text())
MODULES = {Path(p).stem: source(ROOT / p) for p in PINS["python_load_order"]}
partial, categories = MODULES["partial_v19"], MODULES["categories_v19"]
paths, semantic = MODULES["paths_v11"], MODULES["semantic_v9"]
syntax, trees = MODULES["syntax_v25"], MODULES["trees_v25"]
presentations, information, named = (MODULES[x] for x in
                                    ("presentations_v25", "information_v25", "named_v25"))
functors, restrictions, resources = (MODULES[x] for x in
                                    ("functors_v26", "restrictions_v26", "resource_v26"))
survivor_audit, optional_audit, parent_audit = (MODULES[x] for x in
    ("audit_survivors_v25", "audit_optional_v26", "audit_parents_v27"))


def typed_key(value):
    if value is None:
        return ("none",)
    if type(value) in (bool, int, str):
        return (type(value).__name__, value)
    if is_dataclass(value) and not isinstance(value, type):
        return ("dataclass", type(value),
                tuple((f.name, typed_key(getattr(value, f.name))) for f in fields(value)))
    if type(value) is tuple:
        return ("tuple", tuple(typed_key(x) for x in value))
    if type(value) is dict:
        return ("dict", tuple(sorted(
            ((typed_key(k), typed_key(v)) for k, v in value.items()), key=repr)))
    raise ValueError("unsupported exact certificate value")


def same_record(actual, expected):
    need(type(actual) is type(expected), "certificate class mismatch")
    need(typed_key(actual) == typed_key(expected), "certificate content drift")


def checked_graph(graph):
    tup(graph)
    need(len(graph) == 2, "graph shape")
    n, edges = graph
    nat(n)
    for edge in tup(edges):
        tup(edge)
        need(len(edge) == 2, "edge shape")
        for endpoint in edge:
            index(endpoint, n)
    return paths.validate(graph)


def checked_path(graph, path):
    n, edges = checked_graph(graph)
    tup(path)
    need(len(path) == 2, "path shape")
    index(path[0], n)
    for edge in tup(path[1]):
        index(edge, len(edges))
    return paths.canonical(graph, path)
