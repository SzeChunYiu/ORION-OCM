from developmental_quotient_minimizer import (
    developmental_fixture,
    minimize_mealy,
)


def normalize(blocks):
    return {frozenset(block) for block in blocks}


def test_developmental_fixture_exact_quotient():
    states, events, transition = developmental_fixture()
    blocks = normalize(minimize_mealy(states, events, transition))
    assert blocks == {
        frozenset({0}),
        frozenset({1}),
        frozenset({2, 3}),
    }


def test_current_query_behaviour_is_coarser_than_developmental_quotient():
    states, _events, transition = developmental_fixture()
    query_events = ("q0", "q1")
    blocks = normalize(minimize_mealy(states, query_events, transition))
    assert blocks == {
        frozenset({0, 1}),
        frozenset({2, 3}),
    }
