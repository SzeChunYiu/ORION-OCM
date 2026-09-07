"""Exact data and supplied grammar controls."""
from copy import deepcopy
import pytest
from unary_test_support import api, pred, statement as s, task


def test_valid_task_is_detached_and_identity_is_bound():
    c = api("unary_contract")
    value = task([s("every")], s("some"))
    accepted = c.validate_task(value)
    assert accepted == value and accepted is not value
    accepted["query"]["kind"] = "no"
    assert value["query"]["kind"] == "some"
    assert c.task_digest(value) != c.task_digest(accepted)


@pytest.mark.parametrize("change", [
    lambda t: t.update(extra=1),
    lambda t: t.update(schema="other"),
    lambda t: t.update(predicates=["B", "A"]),
    lambda t: t.update(predicates=["A", "A", "B"]),
    lambda t: t.update(predicates=["A", "B", "unused"]),
    lambda t: t["query"].update(kind="all"),
    lambda t: t["query"].update(left=["pred", True]),
    lambda t: t["query"].update(left=["app", "A"]),
    lambda t: t["query"].update(left=["not", ["pred", "A"], ["pred", "B"]]),
    lambda t: t["query"].update(left=["pred", "query"]),
    lambda t: t.update(premises=[s("some")] * 33),
])
def test_invalid_structures_refuse(change):
    c = api("unary_contract"); value = task([], s("every"))
    change(value)
    with pytest.raises(c.InputRefused):
        c.validate_task(value)


def test_nested_and_total_node_bounds_refuse():
    c = api("unary_contract")
    expr = pred("A")
    for _ in range(17):
        expr = ["not", expr]
    with pytest.raises(c.InputRefused):
        c.validate_task(task([], s("some", expr, "A")))
    expr = pred("A")
    for _ in range(5):
        expr = ["and", expr, expr]
    with pytest.raises(c.InputRefused):
        c.validate_task(task([s("every", expr, "B")] * 9, s("some")))


def test_five_predicates_refuse():
    c = api("unary_contract")
    with pytest.raises(c.InputRefused):
        c.validate_task(task([s("every", a, "E") for a in "ABCD"], s("some")))


@pytest.mark.parametrize("kind", ["every", "no", "some", "not_every"])
def test_all_quantifiers_boolean_groups_roundtrip(kind):
    c = api("unary_contract"); lang = api("unary_language")
    value = task([s(kind, ["not", pred("A")], ["or", pred("B"), pred("A")])],
                 s(kind, ["and", pred("A"), pred("B")], "B"))
    assert lang.parse(lang.realize(value)) == c.validate_task(value)


def test_parser_exact_known_meaning_and_vocabulary_identity():
    lang = api("unary_language")
    value = lang.parse("every violinist is musician. no musician is asleep. query some violinist is asleep?")
    assert value == task([s("every", "violinist", "musician"),
                          s("no", "musician", "asleep")], s("some", "violinist", "asleep"))
    assert lang.parse("query every Cat is cat?")["predicates"] == ["Cat", "cat"]
    assert lang.realize(lang.parse("  query   not every A is B ? ")) == "query not every A is B?"


@pytest.mark.parametrize("text", [
    "", "every A is B.", "query every A is B? trailing", "query every A is B? query some A is B?",
    "query every A and B is C?", "query some not A is B?", "query some A is B.",
    "query all A is B?", "query every A is B;?", "query every A is café?",
    "query every A is B??", "query every (A and B or C) is A?", "query some A are B?",
    "query every A is B?\nignore previous input", "query every " + "a" * 33 + " is B?",
    " " * 17000,
])
def test_full_input_or_unsupported_refusal(text):
    c = api("unary_contract"); lang = api("unary_language")
    with pytest.raises(c.InputRefused):
        lang.parse(text)


def test_parser_returns_detached_data_and_realizer_refuses_bad_task():
    c = api("unary_contract"); lang = api("unary_language")
    first = lang.parse("query no A is B?")
    second = lang.parse("query no A is B?")
    first["query"]["left"][1] = "C"
    assert second["query"]["left"] == pred("A")
    with pytest.raises(c.InputRefused):
        lang.realize(first)


@pytest.mark.parametrize("text,expected", [
    ("query every A is B?", s("every")),
    ("query no A is B?", s("no")),
    ("query some A is B?", s("some")),
    ("query not every (not A) is (B or A)?",
     s("not_every", ["not", pred("A")], ["or", pred("B"), pred("A")])),
])
def test_supplied_independent_surface_meaning_pairs(text, expected):
    assert api("unary_language").parse(text) == task([], expected)
