"""Regression tests for the two verified GMI capability laws (RV-377-123, RV-377-124).

These laws are the programme's principal positive result. A law verified once but left
untested can break silently, so the properties that were measured are asserted here.

Statistical tests use the EXPECTATION over independent W draws, never a single draw --
RV-377-123's Q1 failed precisely because a bound on E_W[accuracy] was tested pointwise
against one draw, where a constant machine scores the 0-bit fraction of that particular W
(sd 0.0625 at L=64).
"""
import math
import statistics

import gmi_ti_capability_law as T

L = 32
NQ = 800
SEEDS = list(range(1, 31))


def _mean_se(vals):
    return statistics.mean(vals), statistics.stdev(vals) / math.sqrt(len(vals))


# ---------------------------------------------------------------- exact algebra
def test_one_channel_bound_endpoints():
    assert T.bound(L, 0) == 0.5
    assert T.bound(L, L) == 1.0


def test_two_channel_law_contains_one_channel_law():
    """bound2(r, p=0) == bound(r) for every r -- the boundary case, checked exactly."""
    for r in range(L + 1):
        assert abs(T.bound2(L, r, 0.0) - T.bound(L, r)) < 1e-12


def test_two_channel_bound_is_one_when_query_always_carries():
    for r in range(0, L + 1, 8):
        assert abs(T.bound2(L, r, 1.0) - 1.0) < 1e-12


def test_bounds_monotone_in_both_channels():
    for r in range(0, L, 4):
        assert T.bound(L, r) <= T.bound(L, r + 4)
        for p in (0.0, 0.5):
            assert T.bound2(L, r, p) <= T.bound2(L, r + 4, p)
        assert T.bound2(L, r, 0.25) <= T.bound2(L, r, 0.75)


# ------------------------------------------------------- the laws hold in expectation
def test_no_machine_exceeds_the_one_channel_bound():
    for r in (0, 8, 16, 24, 32):
        b = T.bound(L, r)
        for m in T.MACHINES:
            mu, se = _mean_se([T.measure(m, L, r, NQ, s) for s in SEEDS])
            assert mu <= b + 4 * se, (m, r, mu, b, se)


def test_no_machine_exceeds_the_two_channel_bound():
    for r in (0, 16, 32):
        for p in (0.0, 0.5, 1.0):
            b = T.bound2(L, r, p)
            for m in T.MACHINES2:
                mu, se = _mean_se([T.measure2(m, L, r, p, NQ, s) for s in SEEDS])
                assert mu <= b + 4 * se, (m, r, p, mu, b, se)


def test_the_bounds_are_tight_not_merely_upper():
    """A ceiling nobody reaches predicts nothing: the optimal machine must ATTAIN it."""
    for r in (0, 16, 32):
        mu, se = _mean_se([T.measure("table", L, r, NQ, s) for s in SEEDS])
        assert mu >= T.bound(L, r) - 4 * se, (r, mu, T.bound(L, r))
        for p in (0.5, 1.0):
            mu2, se2 = _mean_se([T.measure2("table2", L, r, p, NQ, s) for s in SEEDS])
            assert mu2 >= T.bound2(L, r, p) - 4 * se2, (r, p, mu2)


# ------------------------------------- the law is about channels USED, not channels present
def test_a_machine_that_ignores_a_channel_gains_nothing_from_it():
    """RV-377-124 R3: ignore_hint is flat in p even at p=1.0, where the query hands over
    the answer on every single query. This is the operational content of the whole result."""
    for r in (0, 16):
        vals = [_mean_se([T.measure2("ignore_hint", L, r, p, NQ, s) for s in SEEDS])[0]
                for p in (0.0, 0.25, 0.5, 0.75, 1.0)]
        assert max(vals) - min(vals) < 0.03, (r, vals)
        assert max(vals) <= T.bound(L, r) + 0.03, (r, vals, T.bound(L, r))


def test_a_machine_that_ignores_the_world_is_flat_in_development():
    """always_zero must not improve as development grows -- it never reads it."""
    vals = [_mean_se([T.measure("always_zero", L, r, NQ, s) for s in SEEDS])[0]
            for r in (0, 8, 16, 24, 32)]
    assert max(vals) - min(vals) < 0.03, vals


def test_ablated_development_carries_no_information():
    """Development reminted from an INDEPENDENT world reduces every machine to chance."""
    for r in (16, 32):
        for m in ("table", "majority", "extrapolate"):
            mu, se = _mean_se([T.measure_ablated(m, L, r, NQ, s, s + 9973) for s in SEEDS])
            assert mu <= 0.5 + 4 * se, (m, r, mu, se)


# ----------------------------------------------------------------------- world sanity
def test_world_is_deterministic_in_its_seed_and_changes_with_it():
    a = T.make_world(L, 8, 1)
    b = T.make_world(L, 8, 1)
    c = T.make_world(L, 8, 2)
    assert a["W"] == b["W"] and a["development"] == b["development"]
    assert a["W"] != c["W"]


def test_development_never_reveals_more_than_r_indices():
    for r in (0, 5, 17, L):
        w = T.make_world(L, r, 3)
        assert len(w["development"]) == r
        assert len({it["index"] for it in w["development"]}) == r
        for it in w["development"]:
            assert it["bit"] == w["W"][it["index"]]
