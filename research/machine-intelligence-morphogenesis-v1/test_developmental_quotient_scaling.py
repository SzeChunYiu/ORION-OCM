from developmental_quotient_scaling import census


def test_product_quotient_grows_as_3_pow_n():
    rows = census(max_n=4)
    assert [row["minimal_developmental_quotient_states"] for row in rows] == [3, 9, 27, 81]
    assert all(
        row["minimal_developmental_quotient_states"] == row["expected_3_pow_n"]
        for row in rows
    )


def test_factorized_update_is_local():
    rows = census(max_n=4)
    assert all(row["one_teaching_event_touches_units"] == 1 for row in rows)
