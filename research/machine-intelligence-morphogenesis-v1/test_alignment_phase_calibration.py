from alignment_phase_calibration import (
    Q_STRUCTURED,
    Q_UNIFORM,
    build_receipt,
    lifetime_cost,
    phase_threshold,
)


def test_threshold_moves_down_with_horizon():
    assert phase_threshold(4, 1.0) > phase_threshold(16, 1.0) > phase_threshold(256, 1.0)


def test_winner_reverses_around_threshold():
    h = 16
    p = phase_threshold(h, 1.0)
    assert lifetime_cost(p + 1e-6, h, 1.0, Q_STRUCTURED) < lifetime_cost(p + 1e-6, h, 1.0, Q_UNIFORM)
    assert lifetime_cost(p - 1e-6, h, 1.0, Q_STRUCTURED) > lifetime_cost(p - 1e-6, h, 1.0, Q_UNIFORM)


def test_receipt_terminal():
    assert build_receipt()["terminal"] == "ECOLOGY_BIAS_ALIGNMENT_PHASE_EXACT__INFORMATION_THEORY_PARENT"
