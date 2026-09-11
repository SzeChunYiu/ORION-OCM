from factorization_scaling_calibration import build_receipt, factored_step, program_step


def test_factored_and_program_steps_match():
    assert factored_step((0, 1, 1), (1, 0, 1)) == (1, 1, 0)
    assert program_step((0, 1, 1), (1, 0, 1)) == (1, 1, 0)


def test_scaling_receipt_has_expected_growth():
    r = build_receipt()
    rows = r["rows"]
    assert rows[0]["flat_transition_entries"] == 4
    assert rows[7]["flat_transition_entries"] == 65536
    assert rows[7]["factored_execution_xor_ops"] == 8
    assert rows[15]["flat_transition_entries"] == 4 ** 16
    assert r["terminal"] == "FACTORIZATION_EXPONENTIAL_VS_FLAT__GENERAL_PROGRAM_PARENT_COMPACT"
