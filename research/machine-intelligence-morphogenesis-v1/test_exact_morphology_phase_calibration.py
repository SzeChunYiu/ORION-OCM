from exact_morphology_phase_calibration import census


def test_phase_frontier_counts():
    r = census()
    assert r["perfect_morphologies"] == 996
    assert r["pareto_morphologies"] == 12
    assert r["pareto_resource_vectors"] == [
        [3, 0.5, 0.0, 0.0, 1],
        [4, 0.0, 0.5, 0.5, 1],
    ]


def test_phase_boundary_registration():
    r = census()
    assert r["scalar_boundary"] == "topology wins iff w_state > 2*w_desc + w_edge + H*w_message"
    assert r["terminal"] == "EXACT_MORPHOLOGY_PHASE_BOUNDARY_CALIBRATED__RESOURCE_RATIONAL_PARENT_OWNED"
