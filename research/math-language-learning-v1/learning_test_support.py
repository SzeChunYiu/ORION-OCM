"""Authored acquisition inputs; no hidden held-out generator."""
import importlib
import importlib.util
from unary_test_support import pred, statement as s, task
from unary_solver import solve

def api(name):
    assert importlib.util.find_spec(name) is not None, "missing learned-rule module: "+name
    return importlib.import_module(name)

def chain():
    return [s("every","P0","P1"),s("no","P1","P2")],s("no","P0","P2")

def rule():
    p,q=chain()
    return api("unary_rule_contract").seal_rule(["P0","P1","P2"],p,q)

def training(which="B"):
    t=task([s("every","A","B"),s("no","B","C"),s("some",which,which)],s("no","A","C"))
    return {"task":t,"result":solve(t)}
