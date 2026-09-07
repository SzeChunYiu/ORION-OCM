"""Small boundary regressions found during self-review."""
from copy import deepcopy
import pytest
from unary_test_support import api, pred, statement as s, task


def test_internal_quantifier_tag_is_not_surface_grammar():
    c = api("unary_contract")
    with pytest.raises(c.InputRefused):
        api("unary_language").parse("query not_every A is B?")


def test_counter_includes_region_tests_used_to_build_predicate_masks():
    engine = api("unary_solver").RegionSolver(["A", "B"])
    first = engine.solve(task([], s("some")))
    warm = engine.solve(task([], s("some")))
    assert first["counters"].get("predicate_region_tests") == 8
    assert warm["counters"].get("predicate_region_tests") == 0


def test_empty_existential_condition_has_valid_unsat_certificate_without_cover():
    value = task([], s("some", "A", ["not", pred("A")]))
    result = api("unary_solver").solve(value)
    assert result["status"] == "CONTRADICTED"
    assert result["query_true"] == {"kind": "unsat", "obligation": 0, "cover": []}
    assert api("unary_verify").verify_result(value, result)


def test_wrong_cache_vocabulary_is_input_refusal():
    engine = api("unary_solver").RegionSolver(["A"])
    assert engine.solve(task([], s("some")))["status"] == "INPUT_REFUSED"


@pytest.mark.parametrize("field,value", [("schema", "other"), ("status", True),
                                       ("query_false", None), ("counters", {})])
def test_result_protocol_mutations_refuse(field, value):
    data = task([], s("some"))
    result = api("unary_solver").solve(data); result[field] = value
    assert not api("unary_verify").verify_result(data, result)


def test_model_duplicate_and_negative_regions_refuse():
    data = task([], s("some")); verifier = api("unary_verify")
    original = api("unary_solver").solve(data)
    for world in ([0, 0], [-1], [0.0]):
        result = deepcopy(original); result["premises"]["world"] = world
        assert not verifier.verify_result(data, result)


def test_cyclic_ast_refuses_with_registered_bound():
    c = api("unary_contract")
    value = task([], s("every", "A", "A"))
    expr = ["not"]; expr.append(expr); value["query"]["left"] = expr
    with pytest.raises(c.InputRefused):
        c.validate_task(value)
