from __future__ import annotations

from ocm.kso.warrant import Liveness, WarrantProfile, all_profiles, leq, powerset
from ocm.kso.warrant_expr import (
    CompiledWarrantInterval,
    all_of,
    any_of,
    evidence_leaf,
)


def _intervals(n: int):
    profiles = all_profiles(n)
    return [WarrantProfile(lower, upper) for lower in profiles for upper in profiles if leq(lower, upper)]


def test_compiled_interval_matches_all_small_production_intervals_and_compositions():
    intervals = _intervals(2)
    revocations = powerset((0, 1))

    for interval in intervals:
        compiled = CompiledWarrantInterval.from_warrant_profile(interval)
        for revoked in revocations:
            assert compiled.liveness(revoked) is interval.liveness(revoked)

    for left in intervals:
        cleft = CompiledWarrantInterval.from_warrant_profile(left)
        for right in intervals:
            cright = CompiledWarrantInterval.from_warrant_profile(right)
            joined = cleft.join(cright)
            met = cleft.meet(cright)
            production_join = left.join(right)
            production_meet = left.meet(right)
            for revoked in revocations:
                assert joined.liveness(revoked) is production_join.liveness(revoked)
                assert met.liveness(revoked) is production_meet.liveness(revoked)


def test_factored_expression_avoids_explicit_cross_product_on_structured_support_family():
    compiled = CompiledWarrantInterval.from_warrant_profile(WarrantProfile.one())
    production = WarrantProfile.one()
    expression = None

    for i in range(8):
        pair_profile = WarrantProfile.of({f"a{i}"}, {f"b{i}"})
        production = production.meet(pair_profile)
        pair_expr = any_of(evidence_leaf(f"a{i}"), evidence_leaf(f"b{i}"))
        expression = pair_expr if expression is None else all_of(expression, pair_expr)

    assert len(production.lower) == 2**8
    assert expression is not None
    # 16 leaves + 8 OR nodes + one flattened AND root.
    assert expression.node_count == 25

    compiled = CompiledWarrantInterval(expression, expression)
    assert compiled.liveness(()) is Liveness.LIVE
    assert compiled.liveness({"a0", "b0"}) is Liveness.DEAD
    assert compiled.liveness({"a0", "a1", "a2", "a3", "a4", "a5", "a6", "a7"}) is Liveness.LIVE


def test_upper_only_evidence_is_visible_to_reverse_dependency_accounting():
    interval = WarrantProfile((), (frozenset({"upper-only"}),))
    compiled = CompiledWarrantInterval.from_warrant_profile(interval)

    assert compiled.lower_evidence == frozenset()
    assert compiled.upper_evidence == frozenset({"upper-only"})
    assert compiled.all_evidence == frozenset({"upper-only"})
    assert compiled.liveness(()) is Liveness.UNKNOWN
    assert compiled.liveness({"upper-only"}) is Liveness.DEAD


def test_expression_factories_are_structurally_shared_and_deterministic():
    a1 = evidence_leaf("a")
    a2 = evidence_leaf("a")
    b = evidence_leaf("b")
    assert a1 is a2
    assert any_of(a1, b) == any_of(b, a2)
    assert all_of(a1, b, a1) == all_of(b, a2)
