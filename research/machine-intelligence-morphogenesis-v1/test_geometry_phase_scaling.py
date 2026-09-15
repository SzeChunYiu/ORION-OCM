from geometry_phase_scaling import evaluate


def test_registered_phase_scaling_holds():
    r = evaluate()
    assert r["terminal"] == "GEOMETRY_PHASE_SCALING_PREDICTION_HELD_AT_REGISTERED_SIZES"
    assert [row["m"] for row in r["rows"]] == [7, 8, 9, 10]
    for row in r["rows"]:
        assert row["additive"]["winner"] == "LOCAL"
        assert row["chunk"]["winner"] == "CHUNK"
        assert row["chunk"]["LOCAL_over_CHUNK"] == 9.0
