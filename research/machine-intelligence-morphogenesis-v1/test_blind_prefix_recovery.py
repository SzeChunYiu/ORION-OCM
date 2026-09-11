from blind_prefix_recovery import build_receipt


def test_all_registered_predictions_recovered():
    r = build_receipt()
    assert r["candidate_count"] == 13
    assert all(row["prediction_recovered"] for row in r["rows"])
    assert [row["winning_classes"][0] for row in r["rows"]] == [
        "BIASED_TO_SECOND_PAIR",
        "BIASED_TO_SECOND_PAIR",
        "BALANCED",
        "BIASED_TO_FIRST_PAIR",
        "BIASED_TO_FIRST_PAIR",
    ]
    assert r["terminal"] == "BLIND_RECOVERY_CALIBRATED_ON_PREFIX_CODE_PARENT"
