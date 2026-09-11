from fractions import Fraction

import pytest

from gmi_cross_paradigm_bias_phase import (
    ALL_CONCEPTS,
    LEARNERS,
    NONTHRESHOLD_CONCEPTS,
    THRESHOLD_CONCEPTS,
    THRESHOLD_FRACTION,
    bayes_prior,
    calibration_receipt,
    ecology_score,
    exact_rows,
    heldout_expected_accuracy,
)


EXPECTED = {
    1: {
        "EXEMPLAR_MEMORY": (Fraction(1, 2), Fraction(1, 2)),
        "SYMBOLIC_THRESHOLD": (Fraction(13, 18), Fraction(35, 78)),
        "BAYES_THRESHOLD_MIX": (Fraction(15259, 25200), Fraction(51941, 109200)),
        "PARAMETRIC_PERCEPTRON": (Fraction(41, 60), Fraction(119, 260)),
    },
    2: {
        "EXEMPLAR_MEMORY": (Fraction(1, 2), Fraction(1, 2)),
        "SYMBOLIC_THRESHOLD": (Fraction(7, 9), Fraction(17, 39)),
        "BAYES_THRESHOLD_MIX": (Fraction(33784, 51975), Fraction(104816, 225225)),
        "PARAMETRIC_PERCEPTRON": (Fraction(53, 72), Fraction(139, 312)),
    },
    3: {
        "EXEMPLAR_MEMORY": (Fraction(1, 2), Fraction(1, 2)),
        "SYMBOLIC_THRESHOLD": (Fraction(73, 90), Fraction(167, 390)),
        "BAYES_THRESHOLD_MIX": (Fraction(24113, 34650), Fraction(68287, 150150)),
        "PARAMETRIC_PERCEPTRON": (Fraction(187, 240), Fraction(453, 1040)),
    },
    4: {
        "EXEMPLAR_MEMORY": (Fraction(1, 2), Fraction(1, 2)),
        "SYMBOLIC_THRESHOLD": (Fraction(5, 6), Fraction(11, 26)),
        "BAYES_THRESHOLD_MIX": (Fraction(49, 66), Fraction(127, 286)),
        "PARAMETRIC_PERCEPTRON": (Fraction(49, 60), Fraction(111, 260)),
    },
}


def test_registered_concept_universe():
    assert len(ALL_CONCEPTS) == 32
    assert len(THRESHOLD_CONCEPTS) == 6
    assert len(NONTHRESHOLD_CONCEPTS) == 26
    assert THRESHOLD_FRACTION == Fraction(3, 16)


def test_exact_class_averages():
    rows = exact_rows()
    for m, expected_m in EXPECTED.items():
        for learner, (threshold_expected, nonthreshold_expected) in expected_m.items():
            assert rows[m][learner]["threshold_score"] == threshold_expected
            assert rows[m][learner]["nonthreshold_score"] == nonthreshold_expected


def test_uniform_concept_ecology_is_exact_half_for_all_learners_and_m():
    rows = exact_rows()
    for row in rows.values():
        for values in row.values():
            assert values["uniform_concept_ecology_score"] == Fraction(1, 2)


def test_threshold_biased_realizations_share_exact_phase_crossing():
    receipt = calibration_receipt()
    for m in receipt["training_sizes"]:
        assert receipt["crossover_probability_vs_unbiased_half_baseline"][m]["EXEMPLAR_MEMORY"] is None
        for learner in (
            "SYMBOLIC_THRESHOLD",
            "BAYES_THRESHOLD_MIX",
            "PARAMETRIC_PERCEPTRON",
        ):
            assert receipt["crossover_probability_vs_unbiased_half_baseline"][m][learner] == Fraction(3, 16)


def test_bias_is_beneficial_above_and_harmful_below_uniform_ecology():
    rows = exact_rows()
    p_low = Fraction(1, 10)
    p_high = Fraction(1, 2)
    for m, row in rows.items():
        for learner in (
            "SYMBOLIC_THRESHOLD",
            "BAYES_THRESHOLD_MIX",
            "PARAMETRIC_PERCEPTRON",
        ):
            threshold_score = row[learner]["threshold_score"]
            nonthreshold_score = row[learner]["nonthreshold_score"]
            assert ecology_score(
                p_threshold=p_low,
                threshold_score=threshold_score,
                nonthreshold_score=nonthreshold_score,
            ) < Fraction(1, 2)
            assert ecology_score(
                p_threshold=p_high,
                threshold_score=threshold_score,
                nonthreshold_score=nonthreshold_score,
            ) > Fraction(1, 2)


def test_bayes_prior_is_normalized_and_universal_support():
    weights = bayes_prior()
    assert sum(weights.values(), Fraction(0, 1)) == 1
    assert all(weights[f] > 0 for f in ALL_CONCEPTS)


def test_invalid_training_size_rejected():
    concept = ALL_CONCEPTS[0]
    with pytest.raises(ValueError):
        heldout_expected_accuracy(concept, 0, LEARNERS["EXEMPLAR_MEMORY"])
    with pytest.raises(ValueError):
        heldout_expected_accuracy(concept, len(ALL_CONCEPTS), LEARNERS["EXEMPLAR_MEMORY"])


def test_receipt_claim_boundary_is_scoped():
    receipt = calibration_receipt()
    assert receipt["terminal"] == "GMI_CROSS_PARADIGM_BIAS_PHASE_FINITE_EXACT_GREEN_V1"
    text = receipt["claim_boundary"].lower()
    assert "finite" in text
    assert "no universal gmi law" in text
    assert "no" in text and "modern neural-network equivalence" in text
