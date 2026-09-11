from fractions import Fraction

from cross_paradigm_drift_calibration import (
    calibration_rows,
    exact_constant_drift_hitting_time,
)


def test_exact_constant_drift_hitting_time():
    assert exact_constant_drift_hitting_time(Fraction(1), Fraction(1, 4)) == 4
    assert exact_constant_drift_hitting_time(Fraction(8), Fraction(2)) == 4


def test_registered_family_times():
    rows = calibration_rows()
    assert rows["program_search"]["FAST_X"]["predicted_hitting_time"] == "4"
    assert rows["program_search"]["FAST_Y"]["predicted_hitting_time"] == "16"
    assert rows["bayesian_update"]["PRIOR_PLUS"]["predicted_hitting_time"] == "2"
    assert rows["bayesian_update"]["PRIOR_MINUS"]["predicted_hitting_time"] == "4"
    assert rows["quadratic_gradient"]["FAST_X"]["predicted_hitting_time"] == "4"
    assert rows["quadratic_gradient"]["FAST_Y"]["predicted_hitting_time"] == "18"
