from micro_derivation_search import run


def test_common_microbasis_derives_all_registered_targets():
    result = run()
    assert result["search"]["prediction_semantic_classes"] == 702
    assert result["search"]["update_semantic_classes"] == 1979
    for target in result["targets"].values():
        assert target["prediction"] is not None
        assert target["update"] is not None


def test_registered_minimum_sizes_are_stable():
    result = run()["targets"]
    assert result["NEURAL_LIKE_DISCRETE_THRESHOLD_LEARNER"]["prediction"]["size"] == 6
    assert result["NEURAL_LIKE_DISCRETE_THRESHOLD_LEARNER"]["update"]["size"] == 6
    assert result["SYMBOLIC_RULE_MICRO"]["prediction"]["size"] == 3
    assert result["SYMBOLIC_RULE_MICRO"]["update"]["size"] == 6
    assert result["EVIDENCE_ACCUMULATOR_MICRO"]["prediction"]["size"] == 3
    assert result["EVIDENCE_ACCUMULATOR_MICRO"]["update"]["size"] == 3
    assert result["PROGRAMMATIC_REGISTER_MICRO"]["prediction"]["size"] == 4
    assert result["PROGRAMMATIC_REGISTER_MICRO"]["update"]["size"] == 4


def test_no_architecture_label_is_a_basis_primitive():
    result = run()
    forbidden = set(result["basis"]["forbidden_architecture_macros"])
    primitive_text = " ".join(result["basis"]["unary"] + result["basis"]["binary"] + result["basis"]["ternary"])
    assert all(name not in primitive_text for name in forbidden)
