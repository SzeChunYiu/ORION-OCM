from structured_adaptive_grammar_census import census


def test_registered_counts():
    r = census()
    assert r["registered_histories"] == 21
    assert r["morphology_counts"] == {
        "STATIC": 128,
        "STATE_ADAPTIVE": 4608,
        "TOPOLOGY_ADAPTIVE": 256,
        "FULL_ADAPTIVE": 9216,
    }


def test_developmental_class_counts():
    r = census()
    assert r["developmental_class_counts"] == {
        "STATIC": 6,
        "STATE_ADAPTIVE": 96,
        "TOPOLOGY_ADAPTIVE": 12,
        "FULL_ADAPTIVE": 184,
    }


def test_channel_interaction():
    r = census()
    assert r["state_unique_beyond_static"] == 90
    assert r["topology_unique_beyond_static"] == 6
    assert r["topology_unique_beyond_state_adaptive"] == 6
    assert r["state_unique_beyond_topology_adaptive"] == 90
    assert r["full_unique_beyond_union_of_single_channels"] == 82
    assert r["terminal"] == "STRUCTURED_ADAPTATION_INTERACTION_EXACT__FINITE_STATE_PARENT_SUFFICIENT_FOR_EXPRESSIVITY"
