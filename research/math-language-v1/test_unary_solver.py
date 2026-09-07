"""Semantic verdict, certificate and conventional cache controls."""
from copy import deepcopy
import pytest
from unary_test_support import api, pred, statement as s, task


@pytest.mark.parametrize("premises,query,status", [
    ([s("every", "A", "B"), s("no", "B", "C")], s("some", "A", "C"), "CONTRADICTED"),
    ([s("every", "A", "B"), s("no", "B", "C")], s("no", "A", "C"), "ENTAILED"),
    ([s("every")], s("some"), "UNKNOWN"),
    ([], s("every", "A", "A"), "ENTAILED"),
    ([], s("not_every", "A", "A"), "CONTRADICTED"),
    ([s("some"), s("no")], s("every"), "INCONSISTENT"),
    ([s("every", "A", ["not", pred("A")])], s("no", "A", "A"), "ENTAILED"),
    ([s("no", "A", "A"), s("no", ["not", pred("A")], ["not", pred("A")])],
     s("some", "A", "A"), "INCONSISTENT"),
])
def test_expected_status_and_independent_certificates(premises, query, status):
    solver = api("unary_solver"); verifier = api("unary_verify")
    value = task(premises, query); result = solver.solve(value)
    assert result["status"] == status
    assert verifier.verify_result(value, result)


def test_distinct_existential_witnesses_are_not_joined():
    solver = api("unary_solver"); verifier = api("unary_verify")
    value = task([s("some", "A", "B"), s("some", "A", ["not", pred("B")])], s("some", "B", ["not", pred("B")]))
    result = solver.solve(value)
    assert result["status"] == "CONTRADICTED"
    assert len(result["premises"]["world"]) >= 2
    assert verifier.verify_result(value, result)


def test_unknown_has_both_actual_models():
    result = api("unary_solver").solve(task([], s("some")))
    assert result["query_true"]["kind"] == result["query_false"]["kind"] == "model"
    assert result["query_true"]["world"] != result["query_false"]["world"]


def test_cached_masks_and_revision_of_premises():
    solver = api("unary_solver")
    engine = solver.RegionSolver(["A", "B"])
    value = task([s("every")], s("some"))
    first, warm = engine.solve(value), engine.solve(value)
    assert first["status"] == warm["status"] == "UNKNOWN"
    assert first["counters"]["cache_misses"] > 0
    assert warm["counters"]["cache_misses"] == 0 and warm["counters"]["cache_hits"] > 0
    changed = task([s("every"), s("some")], s("some"))
    assert engine.solve(changed)["status"] == "ENTAILED"
    assert engine.solve(value)["status"] == "UNKNOWN"


def test_malformed_task_has_no_semantic_verdict():
    result = api("unary_solver").solve({"schema": "bad"})
    assert result["status"] == "INPUT_REFUSED"
    assert not api("unary_verify").verify_result({"schema": "bad"}, result)


@pytest.mark.parametrize("mutation", [
    lambda r: r.update(status="ENTAILED"),
    lambda r: r.update(task_sha256="0" * 64),
    lambda r: r.update(extra=True),
    lambda r: r["premises"].update(world=[]),
    lambda r: r["query_true"].update(world=[False]),
    lambda r: r["query_true"].update(world=[999]),
    lambda r: r["query_true"].update(world=[0]),
    lambda r: r["query_false"].update(world=r["query_true"]["world"]),
    lambda r: r["query_true"].update(extra="untrusted"),
    lambda r: r["counters"].update(cache_hits=-1),
])
def test_model_and_result_tampering_refuses(mutation):
    value = task([], s("some")); result = api("unary_solver").solve(value)
    mutation(result)
    assert not api("unary_verify").verify_result(value, result)


@pytest.mark.parametrize("mutation", [
    lambda c: c.update(cover=[]),
    lambda c: c.update(cover=[True]),
    lambda c: c.update(cover=[1]),
    lambda c: c.update(obligation="other"),
    lambda c: c.update(obligation=True),
    lambda c: c.update(cover=[0, 0]),
])
def test_unsat_cover_tampering_refuses(mutation):
    value = task([s("no"), s("some")], s("every"))
    result = api("unary_solver").solve(value)
    mutation(result["premises"])
    assert not api("unary_verify").verify_result(value, result)


def test_verifier_does_not_call_optimized_solver(monkeypatch):
    solver = api("unary_solver"); verifier = api("unary_verify")
    value = task([s("every")], s("every"))
    result = solver.solve(value)
    def forbidden(*a, **k):
        raise AssertionError("optimized solve is not a certificate checker")
    monkeypatch.setattr(solver.RegionSolver, "solve", forbidden)
    monkeypatch.setattr(solver, "solve", forbidden)
    assert verifier.verify_result(value, result)


def test_four_predicates_supported_and_boolean_masks_correct():
    value = task([s("every", ["or", pred("A"), pred("B")], ["and", pred("C"), pred("D")])],
                 s("every", "A", "D"))
    result = api("unary_solver").solve(value)
    assert result["status"] == "ENTAILED"
    assert api("unary_verify").verify_result(value, result)
