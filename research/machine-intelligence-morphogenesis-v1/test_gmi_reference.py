from gmi_reference import (
    FrontierPoint,
    break_even_horizon,
    lifecycle_cost,
    median_rank_information_shift,
    pareto_frontier,
    profile_dominance,
    scalar_profile_score,
)


def test_pareto_frontier_keeps_tradeoffs_and_drops_dominated_points():
    points = [
        FrontierPoint((1.0,), (5.0, 5.0)),
        FrontierPoint((1.0,), (4.0, 6.0)),
        FrontierPoint((1.0,), (6.0, 6.0)),  # dominated by first point
        FrontierPoint((0.8,), (2.0, 2.0)),  # capability/resource tradeoff
    ]
    frontier = pareto_frontier(points)
    assert FrontierPoint((1.0,), (6.0, 6.0)) not in frontier
    assert FrontierPoint((1.0,), (5.0, 5.0)) in frontier
    assert FrontierPoint((1.0,), (4.0, 6.0)) in frontier
    assert FrontierPoint((0.8,), (2.0, 2.0)) in frontier


def test_generality_is_partial_order_across_registered_ecologies():
    a = {
        "smooth": [FrontierPoint((1.0,), (2.0,))],
        "exact": [FrontierPoint((1.0,), (8.0,))],
    }
    b = {
        "smooth": [FrontierPoint((1.0,), (7.0,))],
        "exact": [FrontierPoint((1.0,), (3.0,))],
    }
    # Each wins one ecology; neither dominates the registered family.
    assert profile_dominance(a, b) == (False, False)
    assert profile_dominance(b, a) == (False, False)


def test_family_wide_strict_dominance_requires_no_losses():
    a = {
        "e1": [FrontierPoint((1.0,), (2.0,))],
        "e2": [FrontierPoint((1.0,), (3.0,))],
    }
    b = {
        "e1": [FrontierPoint((1.0,), (4.0,))],
        "e2": [FrontierPoint((1.0,), (3.0,))],
    }
    assert profile_dominance(a, b) == (True, True)
    assert profile_dominance(b, a) == (False, False)


def test_declared_scalarization_can_reverse_rankings():
    a = {
        "smooth": [FrontierPoint((1.0,), (2.0,))],
        "exact": [FrontierPoint((1.0,), (8.0,))],
    }
    b = {
        "smooth": [FrontierPoint((1.0,), (7.0,))],
        "exact": [FrontierPoint((1.0,), (3.0,))],
    }

    utility = lambda p: p.capability[0] - 0.05 * p.resources[0]
    assert scalar_profile_score(a, {"smooth": 9.0, "exact": 1.0}, utility) > scalar_profile_score(
        b, {"smooth": 9.0, "exact": 1.0}, utility
    )
    assert scalar_profile_score(a, {"smooth": 1.0, "exact": 9.0}, utility) < scalar_profile_score(
        b, {"smooth": 1.0, "exact": 9.0}, utility
    )


def test_lifecycle_phase_boundary():
    # High-build/cheap-use morphology vs cheap-build/expensive-use morphology.
    h_star = break_even_horizon(100.0, 1.0, 10.0, 5.0)
    assert h_star == 22.5
    assert lifecycle_cost(100.0, 1.0, 10) > lifecycle_cost(10.0, 5.0, 10)
    assert lifecycle_cost(100.0, 1.0, 100) < lifecycle_cost(10.0, 5.0, 100)


def test_history_rank_shift_is_pre_solution_information_gain_proxy():
    assert median_rank_information_shift([64, 32, 16], [8, 16, 8]) == 2.0
