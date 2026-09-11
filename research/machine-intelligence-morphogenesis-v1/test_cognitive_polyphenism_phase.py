from cognitive_polyphenism_phase import (
    PhaseParams,
    expected_costs,
    registered_receipt,
    stale_probability_uniform,
)


def test_stale_probability_boundaries():
    assert stale_probability_uniform(1, 0.0) == 0.0
    assert stale_probability_uniform(1, 0.2) == 0.2
    assert stale_probability_uniform(10, 1.0) == 1.0


def test_registered_positive_region_prefers_polyphenic_lazy():
    p = PhaseParams(
        k=16,
        q=0.05,
        poly_serve=1.15,
        core_update=1.0,
        compile_cost=2.5,
        eager_serve=1.2,
        eager_update_per_phenotype=2.0,
        fixed_match=1.0,
        fixed_mismatch=6.0,
    )
    costs = expected_costs(p)
    assert costs["POLYPHENIC_LAZY"] < costs["EAGER_STATIC_HYBRID"]
    assert costs["POLYPHENIC_LAZY"] < costs["BEST_SINGLE_FIXED"]


def test_low_diversity_negative_twin_reverses_winner():
    p = PhaseParams(
        k=2,
        q=0.10,
        poly_serve=1.15,
        core_update=1.0,
        compile_cost=2.5,
        eager_serve=1.2,
        eager_update_per_phenotype=2.0,
        fixed_match=1.0,
        fixed_mismatch=6.0,
    )
    costs = expected_costs(p)
    assert costs["EAGER_STATIC_HYBRID"] < costs["POLYPHENIC_LAZY"]


def test_expensive_compile_negative_twin_reverses_winner():
    p = PhaseParams(
        k=16,
        q=0.05,
        poly_serve=1.15,
        core_update=1.0,
        compile_cost=8.0,
        eager_serve=1.2,
        eager_update_per_phenotype=2.0,
        fixed_match=1.0,
        fixed_mismatch=6.0,
    )
    costs = expected_costs(p)
    assert costs["EAGER_STATIC_HYBRID"] < costs["POLYPHENIC_LAZY"]


def test_receipt_has_one_positive_and_two_negative_twins():
    receipt = registered_receipt()
    winners = {row["name"]: row["winner"] for row in receipt["scenarios"]}
    assert winners["P_PLUS_HETEROGENEOUS"] == "POLYPHENIC_LAZY"
    assert winners["N_TWIN_LOW_DIVERSITY"] == "EAGER_STATIC_HYBRID"
    assert winners["N_TWIN_EXPENSIVE_COMPILATION"] == "EAGER_STATIC_HYBRID"
