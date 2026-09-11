from blind_micro_acquisition import run


def test_all_registered_micro_targets_are_uniquely_identified():
    result = run()
    assert result["all_targets_exactly_identified"] is True
    for row in result["targets"].values():
        assert row["architecture_label_visible_to_learner"] is False
        assert row["prediction_consistent_semantic_classes"] == 1
        assert row["update_consistent_semantic_classes"] == 1
        assert row["exact_target_semantics_recovered"] is True


def test_teaching_rows_are_strict_subsets_of_full_tables():
    result = run()
    for row in result["targets"].values():
        assert row["prediction_teaching_examples"] < row["prediction_total_rows"]
        assert row["update_teaching_examples"] < row["update_total_rows"]
