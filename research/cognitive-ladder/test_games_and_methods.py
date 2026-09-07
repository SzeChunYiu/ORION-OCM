"""Tests for the exact game families and the registered method languages."""

from __future__ import annotations

import math

import pytest

from games import MultiHeapGame, SubtractionGame, Work, eventual_period
from methods import (Admissibility, BitsAccounting, Combiner, CombinerLanguage,
                     GrundyRuleLanguage, XOR_LOOKALIKES_ON_BINARY_VALUES, data_bits)

MOVE_SETS = [(1, 2), (1, 2, 3), (1, 3, 4), (1, 2, 4), (2, 3, 7), (1, 4, 5), (1, 5, 6)]


@pytest.mark.parametrize("moves", MOVE_SETS)
def test_grundy_periodicity_is_witnessed_not_assumed(moves):
    pre, per = eventual_period(moves)
    table = SubtractionGame(moves).grundy_upto(200)
    for n in range(pre, 200):
        assert table[n] == table[pre + (n - pre) % per]


def test_period_is_not_bounded_by_max_move():
    """SUB(1,3,4) has period 7 while its largest move is 4."""
    assert eventual_period((1, 3, 4))[1] == 7


def test_nim_p_positions_are_the_xor_zero_positions():
    g = MultiHeapGame.nim(3, 10)
    assert g.is_p_position([1, 2, 3])
    assert not g.is_p_position([1, 2, 4])


def test_joint_state_space_grows_exponentially_in_heaps():
    """The position-cache parent's cost is exponential where a method's is not."""
    two = MultiHeapGame(SubtractionGame((1, 3, 4)), 2).joint_state_count(20)
    three = MultiHeapGame(SubtractionGame((1, 3, 4)), 3).joint_state_count(20)
    assert three == two * 21


def test_work_counter_is_charged_for_every_expansion():
    w = Work()
    SubtractionGame((1, 2, 3)).grundy_upto(10, work=w)
    assert w.expansions == 11
    assert w.table_writes == 11


def test_version_space_count_is_exact_and_shrinks_with_evidence():
    L = GrundyRuleLanguage(max_preperiod=2, max_period=12, max_value=4)
    table = SubtractionGame((1, 3, 4)).grundy_upto(64)
    counts = [L.consistent_count([(n, table[n]) for n in range(k)]) for k in (0, 4, 10, 20)]
    assert counts == sorted(counts, reverse=True)
    assert counts[0] == L.size()
    assert counts[-1] >= 1


def test_binary_channel_leaves_more_hypotheses_than_the_full_channel():
    """Observing only is-P is a weaker channel and must be charged as such."""
    L = GrundyRuleLanguage(max_preperiod=1, max_period=8, max_value=3)
    table = SubtractionGame((1, 2, 3)).grundy_upto(64)
    ev = [(n, table[n]) for n in range(12)]
    binary = [(n, table[n] == 0) for n in range(12)]
    assert L.consistent_count_binary(binary) > L.consistent_count(ev)


def test_induced_rule_extrapolates_beyond_training_support():
    L = GrundyRuleLanguage(max_preperiod=2, max_period=12, max_value=4)
    table = SubtractionGame((1, 3, 4)).grundy_upto(200)
    rule = L.induce([(n, table[n]) for n in range(20)])
    assert rule is not None
    assert all(rule.grundy(n) == table[n] for n in range(20, 201))


def test_bits_accounting_reports_what_the_evidence_actually_supplied():
    L = GrundyRuleLanguage(max_preperiod=2, max_period=12, max_value=4)
    table = SubtractionGame((1, 3, 4)).grundy_upto(64)
    b = BitsAccounting.build(L.language_id, L.size(),
                             L.consistent_count([(n, table[n]) for n in range(20)]))
    assert b.prior_bits > 0
    assert 0 < b.acquired_bits <= b.prior_bits
    assert math.isclose(b.acquired_bits + b.residual_bits, b.prior_bits, abs_tol=1e-9)


def test_a_language_containing_one_hypothesis_acquires_nothing():
    """The prior-dominance guard: a hand-picked language teaches nothing."""
    b = BitsAccounting.build("L(one)", 1, 1)
    assert b.prior_bits == 0.0
    assert b.acquired_bits == 0.0


def test_verbatim_cache_fails_the_compression_test():
    """CL-D1 excludes an answer cache by construction, not by measurement."""
    ev_bits = data_bits([(n, 0) for n in range(30)], 4)
    cache = Admissibility.build(bits_method=ev_bits, bits_data=ev_bits, bits_residual=0.0,
                                extrapolation_probes=0, extrapolation_failures=0,
                                independence_ok=True)
    assert not cache.admissible
    assert cache.verdict == "INADMISSIBLE_NO_COMPRESSION"


def test_a_compressing_rule_that_never_extrapolated_is_still_inadmissible():
    a = Admissibility.build(bits_method=20.0, bits_data=60.0, bits_residual=0.0,
                            extrapolation_probes=0, extrapolation_failures=0,
                            independence_ok=True)
    assert a.verdict == "INADMISSIBLE_NO_EXTRAPOLATION"


def test_admissible_requires_all_three_conditions():
    a = Admissibility.build(bits_method=20.0, bits_data=60.0, bits_residual=0.0,
                            extrapolation_probes=50, extrapolation_failures=0,
                            independence_ok=True)
    assert a.admissible
    dep = Admissibility.build(bits_method=20.0, bits_data=60.0, bits_residual=0.0,
                              extrapolation_probes=50, extrapolation_failures=0,
                              independence_ok=False)
    assert dep.verdict == "INADMISSIBLE_CHECKER_NOT_INDEPENDENT"


def test_the_registered_decoy_combiners_really_are_indistinguishable_on_binary_values():
    """The CL-3 requirement, verified rather than asserted."""
    import itertools
    from methods import COMBINERS
    for name in XOR_LOOKALIKES_ON_BINARY_VALUES:
        for k in (1, 2, 3, 4):
            for vs in itertools.product((0, 1), repeat=k):
                assert (COMBINERS[name](vs) == 0) == (COMBINERS["XOR"](vs) == 0), (name, vs)


def test_the_decoy_combiners_are_separated_by_larger_grundy_values():
    """Held-out worlds must break the tie the training draw could not.

    (1, 3) is the separating position: its XOR is 2 so it is an N-position, while
    every binary-value lookalike reads it as a P-position.
    """
    from methods import COMBINERS
    L = CombinerLanguage()
    positions = [(1, 3), (1, 1), (2, 3), (2, 2), (1, 2, 3), (3, 5)]
    ev = [(p, COMBINERS["XOR"](p) == 0) for p in positions]
    survivors = {c.name for c in L.consistent(ev)}
    assert survivors == {"XOR"}


def test_no_lookalike_survives_a_single_separating_position():
    from methods import COMBINERS
    L = CombinerLanguage()
    ev = [((1, 3), False)]
    survivors = {c.name for c in L.consistent(ev)}
    assert "XOR" in survivors
    assert not (set(XOR_LOOKALIKES_ON_BINARY_VALUES) & survivors)
    assert COMBINERS["XOR"]((1, 3)) == 2


def test_decoy_pool_is_non_empty_or_the_family_is_too_easy():
    L = GrundyRuleLanguage(max_preperiod=1, max_period=10, max_value=4)
    table = SubtractionGame((1, 3, 4)).grundy_upto(200)
    decoys = L.decoys([(n, table[n]) for n in range(8)], lambda n: table[n], 60, limit=5)
    assert decoys, "no decoys means the extrapolation test is vacuous"
