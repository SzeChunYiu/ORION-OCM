from prefix_tree_geometry_calibration import (
    BALANCED_DEPTHS,
    BIASED_DEPTHS,
    build_receipt,
    expected_depth,
    phase_threshold,
    prior_from_depths,
)


def test_structure_derives_priors():
    assert prior_from_depths(BALANCED_DEPTHS) == (0.25, 0.25, 0.25, 0.25)
    assert prior_from_depths(BIASED_DEPTHS) == (0.5, 0.25, 0.125, 0.125)


def test_expected_depth_formula():
    assert expected_depth(BALANCED_DEPTHS, 0.37) == 2.0
    assert abs(expected_depth(BIASED_DEPTHS, 0.37) - (3.0 - 1.5 * 0.37)) < 1e-12


def test_phase_boundary():
    assert phase_threshold(1, 1.0) > 1.0
    assert abs(phase_threshold(8, 1.0) - 0.75) < 1e-12
    assert build_receipt()["terminal"] == "STRUCTURE_TO_GEOMETRY_EXACT_PREFIX_CALIBRATION__CODING_PARENT"
