from developmental_quotient_scaling import census


def test_product_quotient_grows_as_3_pow_n():
    rows = census(max_n=5)
    assert [row["minimal_developmental_quotient_states"] for row in rows] == [
        3,
        9,
        27,
        81,
        243,
    ]
    assert all(
        row["minimal_developmental_quotient_states"] == row["expected_3_pow_n"]
        for row in rows
    )


def test_flat_transition_table_grows_as_2n_3n():
    rows = census(max_n=5)
    assert [row["flat_transition_entries"] for row in rows] == [6, 36, 162, 648, 2430]
    assert all(
        row["flat_transition_entries"]
        == 2 * row["n_units"] * (3 ** row["n_units"])
        for row in rows
    )


def test_factorized_rule_is_shared_and_update_is_local():
    rows = census(max_n=5)
    assert all(row["shared_local_rule_entries"] == 6 for row in rows)
    assert [row["factorized_state_cells"] for row in rows] == [1, 2, 3, 4, 5]
    assert all(row["one_teaching_event_touches_units"] == 1 for row in rows)
