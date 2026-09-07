"""Independent finite model oracle; no masks or production AST evaluators."""
from itertools import product
import pytest
from unary_test_support import api, pred, statement as s, task


def members(expr, world, names):
    if expr[0] == "pred":
        return {i for i, obj in enumerate(world) if obj[names.index(expr[1])]}
    if expr[0] == "not":
        return set(range(len(world))) - members(expr[1], world, names)
    left, right = (members(child, world, names) for child in expr[1:])
    return left & right if expr[0] == "and" else left | right


def holds(stmt, world, names):
    left, right = members(stmt["left"], world, names), members(stmt["right"], world, names)
    return {"every": left <= right, "no": not (left & right),
            "some": bool(left & right), "not_every": bool(left - right)}[stmt["kind"]]


def expected(value, worlds):
    live = [w for w in worlds if all(holds(p, w, value["predicates"]) for p in value["premises"])]
    if not live:
        return "INCONSISTENT"
    answers = {holds(value["query"], w, value["predicates"]) for w in live}
    return "ENTAILED" if answers == {True} else "CONTRADICTED" if answers == {False} else "UNKNOWN"


@pytest.mark.parametrize("n", [1, 2, 3])
def test_exhaustive_nonempty_worlds_for_atomic_and_boolean_family(n):
    solver = api("unary_solver"); verifier = api("unary_verify")
    names = list("ABC"[:n]); regions = list(product([False, True], repeat=n))
    worlds = [tuple(r for i, r in enumerate(regions) if choice & (1 << i))
              for choice in range(1, 1 << len(regions))]
    atoms = [s(kind, a, b) for kind in ("every", "no", "some", "not_every") for a in names for b in names]
    premise_sets = [[]] + [[p] for p in atoms]
    premise_sets += [[s(a, names[0], names[-1]), s(b, names[-1], names[0])]
                     for a, b in product(("every", "no", "some", "not_every"), repeat=2)]
    queries = atoms + [s("every", ["not", ["or", pred(names[0]), pred(names[-1])]],
                                ["and", ["not", pred(names[0])], ["not", pred(names[-1])]])]
    checked = 0
    for premises, query in product(premise_sets, queries):
        value = task(premises, query)
        if value["predicates"] != names:
            continue
        result = solver.solve(value)
        assert result["status"] == expected(value, worlds), value
        assert verifier.verify_result(value, result), value
        checked += 1
    assert checked > 0
