"""Domain operators and fixed host checkers; learned records contain data only."""
from dataclasses import replace
from fractions import Fraction
from types import MappingProxyType

from ocm.kso.types import Scope
from ocm.language.interpret import interpret, Verdict
from ocm.language.meaning import canonical
from ocm.learning import methods as M
from ocm.runtime.solve import OperatorSpec, Status
from packed_chart import interpret_packed
from vessel_state import LANG, GEN, PRIM, SCOPE, payload, restore_language

CATALOGUE = ("language:interpret", "polynomial:guided", "polynomial:primitive")
# Truth after an independent polynomial check depends on the task and trusted DSL,
# not on the revocable search heuristic that happened to discover the program.
TRUTH_SUPPORT = MappingProxyType({CATALOGUE[0]: (LANG,), CATALOGUE[1]: (PRIM,), CATALOGUE[2]: (PRIM,)})


def language_proposal(ks, request, revoked, guided=False):
    if request["kind"] != "language":
        return {"status": "NOT_APPLICABLE"}
    lexicon, constructions = restore_language(ks)
    result = interpret_packed(request["utterance"], lexicon, constructions, revoked=revoked)
    i = result.interpretation
    return {"status": i.verdict.value, "meaning": None if i.meaning is None else i.meaning.as_dict(),
            "digest": None if i.meaning is None else canonical(i.meaning)[1], "stats": result.stats.__dict__}


def language_check(ks, request, output, revoked):
    if request["kind"] != "language":
        return Status.FAIL
    lexicon, constructions = restore_language(ks)
    reference = interpret(request["utterance"], lexicon, constructions, revoked=revoked)
    if reference.verdict is not Verdict.INTERPRETED:
        return Status.CANNOT_CHECK
    expected = canonical(reference.meaning)[1]
    from ocm.language.meaning import MeaningGraph
    try:
        return Status.PASS if (output["status"] == "INTERPRETED" and output["digest"] == expected
            and canonical(MeaningGraph.from_dict(output["meaning"]))[1] == expected) else Status.FAIL
    except (KeyError, TypeError, ValueError):
        return Status.FAIL


def polynomial_proposal(ks, request, revoked, guided=False):
    if request["kind"] != "polynomial":
        return {"status": "NOT_APPLICABLE"}
    task = M.PolynomialTask("query", tuple(Fraction(c) for c in request["coefficients"]))
    method = M.GeneratorMethod()
    if guided:
        data = payload(ks, GEN)
        if set(data) != {"kind", "fragments", "training_tasks"}:
            raise ValueError("unexpected generator fields")
        method = M.GeneratorMethod(tuple(tuple(p) for p in data["fragments"]), tuple(data["training_tasks"]))
    return M.solve(task, M.SearchBudget(request.get("slots", 1000), request.get("max_length", 4)), method).as_dict()


def polynomial_check(ks, request, output, revoked):
    if request["kind"] != "polynomial":
        return Status.FAIL
    if output.get("status") in {"BUDGET_EXHAUSTED", "EXHAUSTED_DECLARED_GRAMMAR"}:
        return Status.CANNOT_CHECK
    try:
        import sympy as sp
        if sp.__version__ != "1.14.0":
            return Status.CANNOT_CHECK
        program = M.checked_program(output["program"])
        if len(program) > request.get("max_length", 4):
            return Status.FAIL
        x = sp.Symbol("x")
        expression = x
        for instruction in program:
            expression = {"inc": lambda: expression + 1, "dec": lambda: expression - 1,
                "double": lambda: 2 * expression, "square": lambda: expression ** 2}[instruction]()
        coefficients = tuple(Fraction(str(c)) for c in reversed(sp.Poly(expression, x, domain=sp.QQ).all_coeffs()))
        task = M.PolynomialTask("query", tuple(Fraction(c) for c in request["coefficients"]))
        return Status.PASS if (output.get("status") == "VERIFIED_POLYNOMIAL_IDENTITY"
            and output.get("task_fingerprint") == task.fingerprint and coefficients == task.coefficients) else Status.FAIL
    except ImportError:
        return Status.CANNOT_CHECK
    except (KeyError, TypeError, ValueError, ZeroDivisionError):
        return Status.FAIL


CHECKERS = MappingProxyType({CATALOGUE[0]: language_check,
    CATALOGUE[1]: polynomial_check, CATALOGUE[2]: polynomial_check})
PROPOSERS = MappingProxyType({CATALOGUE[0]: language_proposal,
    CATALOGUE[1]: polynomial_proposal, CATALOGUE[2]: polynomial_proposal})


def make_catalogue(ks, query_id, revoked, fault=None):
    """Every query gets all three descriptors; SV applicability performs selection."""
    request = payload(ks, query_id)
    inputs = ((query_id, LANG), (query_id, GEN, PRIM), (query_id, PRIM))
    result = []
    for index, name in enumerate(CATALOGUE):
        proposer, checker = PROPOSERS[name], CHECKERS[name]
        def backend(field, operator_id, context, proposer=proposer, guided=index == 1):
            output = proposer(field, request, revoked, guided)
            if fault == "wrong_output" and output.get("program") is not None:
                output = {**output, "program": ["dec"]}
            return output
        def check(output, checker=checker):
            return checker(ks, request, output, revoked)
        op = OperatorSpec(name, "1", backend, inputs[index], scope=SCOPE, checker=check)
        if fault == "wrong_scope":
            op = replace(op, scope=Scope.of("outside-pilot"))
        # Fault injection is host test configuration, never learned/query data.
        result.append(replace(op, checker=None) if fault == "missing_checker" else op)
    return tuple(result)
