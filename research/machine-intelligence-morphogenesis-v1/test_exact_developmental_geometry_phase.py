from exact_developmental_geometry_phase import census


def test_exact_phase_reversal():
    r = census()
    add = r["expected_first_hit_proposals"]["additive_feedback"]
    chunk = r["expected_first_hit_proposals"]["chunk_feedback"]
    assert add["LOCAL"]["fraction"] == "247/29"
    assert add["CHUNK"]["fraction"] == "223/21"
    assert add["winner"] == "LOCAL"
    assert chunk["LOCAL"]["fraction"] == "30/1"
    assert chunk["CHUNK"]["fraction"] == "10/3"
    assert chunk["winner"] == "CHUNK"
    assert r["same_hypothesis_space"] is True
    assert r["same_legal_move_set"] is True
