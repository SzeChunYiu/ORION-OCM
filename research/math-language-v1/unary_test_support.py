"""Authored test data only; no solver semantics."""
import importlib
import importlib.util


def api(name):
    assert importlib.util.find_spec(name) is not None, "missing semantic module: " + name
    return importlib.import_module(name)


def pred(name):
    return ["pred", name]


def statement(kind, left="A", right="B"):
    return {"kind": kind, "left": pred(left) if isinstance(left, str) else left,
            "right": pred(right) if isinstance(right, str) else right}


def task(premises, query):
    names = set()
    def walk(expr):
        if expr[0] == "pred":
            names.add(expr[1])
        else:
            for child in expr[1:]:
                walk(child)
    for item in [*premises, query]:
        walk(item["left"]); walk(item["right"])
    return {"schema": "ocm.unary-task.v1", "predicates": sorted(names),
            "premises": premises, "query": query}
