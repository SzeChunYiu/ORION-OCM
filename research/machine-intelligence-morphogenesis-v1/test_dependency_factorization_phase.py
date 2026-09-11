from dependency_factorization_phase import winner_rows


def index_rows():
    return {(row["ecology"], row["horizon"]): row for row in winner_rows()}


def test_structured_ecology_selects_matching_pair_partition_at_short_horizons():
    rows = index_rows()
    assert rows[("PAIR_01_23", 1)]["winners"] == ["((0, 1), (2, 3))"]
    assert rows[("PAIR_01_23", 4)]["winners"] == ["((0, 1), (2, 3))"]
    assert rows[("PAIR_02_13", 1)]["winners"] == ["((0, 2), (1, 3))"]
    assert rows[("PAIR_02_13", 4)]["winners"] == ["((0, 2), (1, 3))"]


def test_long_horizon_amortizes_monolithic_build_cost():
    rows = index_rows()
    assert rows[("PAIR_01_23", 16)]["winners"] == ["((0, 1, 2, 3),)"]
    assert rows[("PAIR_02_13", 16)]["winners"] == ["((0, 1, 2, 3),)"]
    assert rows[("UNIFORM", 16)]["winners"] == ["((0, 1, 2, 3),)"]


def test_uniform_short_horizon_prefers_no_internal_build():
    rows = index_rows()
    assert rows[("UNIFORM", 1)]["winners"] == ["((0,), (1,), (2,), (3,))"]
