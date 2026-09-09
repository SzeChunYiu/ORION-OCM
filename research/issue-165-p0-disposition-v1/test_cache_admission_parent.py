"""Exact controls for the linear cache-admission / ski-rental parent."""
from fractions import Fraction

from cache_admission_parent import (
    LinearCache,
    cache_admission_equals_ski_rental,
    clairvoyant_cost,
    competitive_ratio,
    density_break_even_horizon,
    deterministic_buy_request,
    exact_minimax_threshold,
    is_affine_lifetime,
    known_horizon_admit,
    linear_qualification,
    max_competitive_ratio,
    nonlinear_adapt_witness,
    online_deterministic_cost,
)


def test_known_horizon_break_even():
    cache = LinearCache(10, 30, 1)
    assert known_horizon_admit(cache, 3) is False
    assert known_horizon_admit(cache, 4) is True
    assert clairvoyant_cost(cache, 3) == 30
    assert clairvoyant_cost(cache, 4) == 34


def test_reuse_density_shifts_break_even():
    cache = LinearCache(10, 30, 1)
    assert density_break_even_horizon(cache, 0) is None
    assert known_horizon_admit(cache, 100, density=0) is False
    assert density_break_even_horizon(cache, Fraction(1, 2)) == 7
    assert known_horizon_admit(cache, 6, Fraction(1, 2)) is False
    assert known_horizon_admit(cache, 7, Fraction(1, 2)) is True


def test_cache_admission_is_ski_rental():
    cache = LinearCache(10, 30, 1)
    assert all(cache_admission_equals_ski_rental(cache, h) for h in range(1, 25))


def test_deterministic_two_competitive():
    cache = LinearCache(10, 30, 1)
    assert deterministic_buy_request(cache) == 4
    assert max_competitive_ratio(cache, 24) <= 2
    assert competitive_ratio(cache, 4) <= 2
    assert online_deterministic_cost(cache, 1) == 10


def test_nonlinear_lifetime_is_adapt_not_adopt():
    semantic = {1: Fraction(22), 2: Fraction(24), 3: Fraction(27), 4: Fraction(31), 5: Fraction(36)}
    inverse = {h: Fraction(10 * h) for h in range(1, 6)}
    assert is_affine_lifetime(inverse) is True
    assert is_affine_lifetime(semantic) is False
    witness = nonlinear_adapt_witness()
    assert witness["semantic_is_affine"] is False
    assert witness["reduction"] == "ADAPT"
    assert witness["import_competitive_guarantee"] is False
    tau_star, _ratio = exact_minimax_threshold(inverse, semantic, 5)
    assert tau_star != witness["forced_ski_rental_threshold"]


def test_qualification_receipt_has_no_ml_residual():
    receipt = linear_qualification()
    assert receipt["two_competitive"] is True
    assert receipt["cache_admission_is_ski_rental"] is True
    assert receipt["ml_residual"] is False
    assert receipt["reduction"] == "ADOPT"
    assert receipt["nonlinear_witness"]["reduction"] == "ADAPT"
