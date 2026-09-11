from structured_adaptive_basis_census import run


def _arm(result, cross_cell, operators):
    wanted = set(operators)
    return next(
        arm
        for arm in result["arms"]
        if arm["cross_cell"] == cross_cell and set(arm["operators"]) == wanted
    )


def test_full_structured_census_registered_counts():
    result = run()
    local = _arm(result, False, {"NOT", "AND", "XOR"})
    cross = _arm(result, True, {"NOT", "AND", "XOR"})
    assert local["developmental_classes"] == 95
    assert cross["developmental_classes"] == 294
    assert cross["current_behavior_classes"] == 4
    assert cross["update_semantic_classes"] == 22
    assert cross["output_semantic_classes"] == 14


def test_not_is_resource_useful_but_not_reach_necessary_at_registered_scope():
    result = run()
    full = _arm(result, True, {"NOT", "AND", "XOR"})
    reduced = _arm(result, True, {"AND", "XOR"})
    assert reduced["developmental_classes"] == full["developmental_classes"] == 294
    assert full["mean_min_compilation_cost"] < reduced["mean_min_compilation_cost"]


def test_cross_cell_access_expands_bounded_developmental_reach():
    result = run()
    assert result["derived_findings"]["cross_cell_reach_gain"] == 199
    assert result["derived_findings"]["and_xor_matches_full_cross_reach"] is True
    assert result["derived_findings"]["not_reduces_mean_cost_despite_equal_reach"] is True
