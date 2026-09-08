from __future__ import annotations

import numpy as np

import robust_lifecycle_advice as A


def test_decision_region_crossover_is_0_star_1_star_only():
    assert A.monotone_crossover((0, 0, 0, 1, 1)) == 4
    assert A.monotone_crossover((1, 1)) == 1
    assert A.monotone_crossover((0, 0)) is None
    assert A.monotone_crossover((0, 1, 0)) is None


def test_perfect_decision_bit_recovers_two_region_optimum():
    # Two horizons, two thresholds.  Each horizon has a different unique optimum.
    matrix = np.array([[1.0, 2.0], [2.0, 1.0]])
    solution = A.solve_robust_advice(matrix, (0, 1), 0.0)
    assert solution["certified"] is True
    assert abs(solution["ratio"] - 1.0) <= A.TOL


def test_arbitrary_advice_collapses_to_no_advice_minimax():
    matrix = np.array([[1.0, 2.0], [2.0, 1.0]])
    arbitrary = A.solve_robust_advice(matrix, (0, 1), 1.0)
    assert arbitrary["certified"] is True
    # The horizon-blind zero-sum optimum mixes the two thresholds equally.
    assert abs(arbitrary["ratio"] - 1.5) <= A.TOL


def test_robust_ratio_is_monotone_in_allowed_error_on_synthetic_case():
    matrix = np.array([[1.0, 2.0], [2.0, 1.0]])
    values = [
        A.solve_robust_advice(matrix, (0, 1), epsilon)["ratio"]
        for epsilon in (0.0, 0.1, 0.25, 0.5, 1.0)
    ]
    assert values == sorted(values)
    assert values[0] == 1.0
    assert abs(values[-1] - 1.5) <= A.TOL


def test_max_error_for_target_is_a_valid_boundary():
    matrix = np.array([[1.0, 2.0], [2.0, 1.0]])
    bound = A.max_error_for_target(matrix, (0, 1), 1.2, iterations=28)
    assert 0.0 < bound["epsilon"] < 1.0
    assert bound["ratio"] <= 1.2 + 1e-7
