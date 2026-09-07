"""Actual cache-key construction work remains observable on warm mask hits."""
from unary_test_support import api, pred, statement as s, task


def test_nested_warm_hit_counts_every_cache_key_node():
    engine = api("unary_solver").RegionSolver(["A", "B"])
    nested = ["and", pred("A"), ["not", pred("B")]]
    value = task([], s("some", nested, "B"))
    cold, warm = engine.solve(value), engine.solve(value)
    assert cold["status"] == warm["status"] == "CONTRADICTED"
    assert warm["counters"]["cache_misses"] == 0
    assert warm["counters"]["cache_hits"] == warm["counters"]["expression_nodes"] == 4
    # Each polarity constructs a four-node left key and a one-node right key.
    assert warm["counters"].get("cache_key_nodes") == 2 * (4 + 1)
    assert warm["counters"]["cache_key_nodes"] > warm["counters"]["expression_nodes"]
    assert api("unary_verify").verify_result(value, warm)
