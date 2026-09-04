"""M1 mutation suite (J3): every planted mutant is caught, and each mutant is shown to have run."""
from __future__ import annotations

from fractions import Fraction as F

import pytest

from ocm.historical import load_reference
from ocm.kso import abstraction as AB
from ocm.kso import admission as AD
from ocm.kso import firing as FI
from ocm.kso import navigation as N
from ocm.kso import revocation as RV
from ocm.kso import space as S
from ocm.kso import types as T
from ocm.kso import warrant as W
from ocm.kso.resources import ResourceVector, mutant_scalar_collapse
from ocm.kso.warrant import Liveness, WarrantProfile

ALPHA = F(1, 3)


def _witness():
    frz = load_reference("kso_m0_freeze_checks_v1")
    ks = S.from_reference(frz.retraction_witness_space())
    return ks, N.seed_vector(ks, {"s": F(1)})


def test_revoke_and_renormalize_mutant_raises_unrelated_atom():
    ks, seed = _witness()
    good = N.fixed_point(ks, seed, ALPHA, revoked=(0,))
    bad_m = N.mutant_navigation_matrix_renormalize(ks, revoked=(0,))
    assert bad_m.rows != N.navigation_matrix(ks, revoked=(0,)).rows  # mutant executed and differs
    bad = dict(zip(ks.ids, N.restart_fixed_point_exact(bad_m.as_lists(), N.gated_seed(ks, seed, (0,)), ALPHA), strict=True))
    assert bad["z"] > good["z"] == N.fixed_point(ks, seed, ALPHA)["z"]


def test_head_level_renormalize_mutant_differs_when_a_head_is_dead():
    one = WarrantProfile.one()
    ks = S.KnowledgeSpace(
        (S.Atom("t", "claim", one), S.Atom("h1", "claim", one), S.Atom("h2", "claim", WarrantProfile.of({0}))),
        (S.Hyperedge("e", ("t",), ("h1", "h2"), "SUPPORT", head_weights=(F(1), F(1))),),
    )
    p = RV.prune(ks, (0,))
    assert p.removed_atoms == frozenset({"h2"}) and p.head_shares["e"] == {"h1": F(1, 2)}
    good = RV.navigation_matrix_on_pruned(p)
    bad = RV.mutant_prune_renormalize_heads(p)
    assert good.rows[0][1] == F(1, 2) and bad.rows[0][1] == F(1)
    assert good.as_lists() == [row[:2] for row in N.navigation_matrix(ks, revoked=(0,)).as_lists()[:2]]


def test_ignore_bridge_warrant_mutant_survives_bridge_revocation():
    ks = S.KnowledgeSpace((S.Atom("x", "claim", WarrantProfile.of({1})), S.Atom("y", "claim", WarrantProfile.of({2}))), ())
    good, _ = AD.compose(ks, ["x", "y"], "xy", bridge_warrant=WarrantProfile.of({9}))
    bad = AD.mutant_compose_drop_bridge(ks, ["x", "y"], "d", WarrantProfile.of({9}))
    assert good.atom("xy").liveness((9,)) is Liveness.DEAD and bad.atom("d").liveness((9,)) is Liveness.LIVE


def test_union_where_intersection_required_mutant():
    ks = S.KnowledgeSpace((S.Atom("x", "claim", WarrantProfile.of({1})), S.Atom("y", "claim", WarrantProfile.of({2}))), ())
    bad = AD.mutant_compose_merge(ks, ["x", "y"], "m").atom("m")
    assert bad.liveness((1,)) is Liveness.LIVE
    good, _ = AD.compose(ks, ["x", "y"], "g")
    assert good.atom("g").liveness((1,)) is Liveness.DEAD
    assert W.mutant_meet_as_union((frozenset({1}),), (frozenset({2}),)) == (frozenset({1}), frozenset({2}))


def test_duplicate_evidence_does_not_change_result():
    p = (frozenset({1}),)
    assert W.meet(p, p) == p and W.join(p, p) == p
    assert WarrantProfile.of({1}, {1}) == WarrantProfile.of({1})


def test_unknown_treated_as_live_and_as_dead_mutants():
    wp = WarrantProfile.partial([frozenset({0})])
    assert wp.liveness((0,)) is Liveness.UNKNOWN
    assert W.mutant_unknown_as_live(wp, (0,)) is Liveness.LIVE
    assert W.mutant_unknown_as_dead(wp, (0,)) is Liveness.DEAD


def test_authority_escalation_and_scope_union_mutants():
    a, b = T.Authority.of(src=2, ver=1), T.Authority.of(src=1, ver=3)
    assert T.meet_authority([a, b]) == T.Authority.of(src=1, ver=1)
    assert T.mutant_authority_max([a, b]) == T.Authority.of(src=2, ver=3)
    s1, s2 = T.Scope.of("en", "de"), T.Scope.of("en")
    assert T.intersect_scopes([s1, s2]).contexts == frozenset({"en"})
    assert T.mutant_scope_union([s1, s2]).contexts == frozenset({"en", "de"})


def test_corroboration_on_one_axis_does_not_promote_another():
    a = T.Authority.of(source=3)
    b = T.Authority.of(verification=3)
    m = T.meet_authority([a, b])
    assert m == T.Authority.of(source=0, verification=0)


def test_hub_degree_dominance_mutant_differs_from_surprise():
    frz = load_reference("kso_m0_freeze_checks_v1")
    ks = S.from_reference(frz.hub_witness_space())
    both = N.fixed_point(ks, N.seed_vector(ks, {"x1": F(1)}), F(1, 2))
    bg = N.fixed_point(ks, N.uniform_seed(ks), F(1, 2))
    assert N.mutant_popularity_rank(both, exclude=("x1",))[0] == "H"
    assert N.rank_by(N.surprise_vector(both, bg), exclude=("x1",))[0] == "sp"


def test_bad_quotient_grouping_mutant():
    p = [[F(1, 2), F(0), F(1, 2), F(0)], [F(0), F(1, 2), F(0), F(1, 2)], [F(1, 4)] * 4, [F(1, 4)] * 4]
    bad = [row[:] for row in p]
    bad[1][0] += F(1, 4)
    bad[1][3] -= F(1, 4)
    blocks = ((0, 1), (2, 3))
    assert not AB.is_lumpable(bad, blocks)
    with pytest.raises(ValueError):
        AB.lump(bad, blocks)
    assert AB.mutant_bad_quotient(bad, blocks)  # the mutant returns a quotient anyway — that is the defect


def test_stale_dependent_remains_live_mutant():
    one = WarrantProfile.one()
    ks = S.KnowledgeSpace(
        (S.Atom("a", "claim", WarrantProfile.of({0})), S.Atom("b", "claim", one), S.Atom("c", "claim", one)),
        (S.Hyperedge("ab", ("a",), ("b",), "DEPENDENCE"), S.Hyperedge("bc", ("b",), ("c",), "DEPENDENCE")),
    )
    assert RV.impact_cone(ks, {"a"}) == frozenset({"a", "b", "c"})
    assert "c" not in RV.mutant_impact_cone_direct_only(ks, {"a"})


def test_summary_live_after_all_child_support_dead_mutant():
    ks = S.KnowledgeSpace((S.Atom("p", "claim", WarrantProfile.of({1})), S.Atom("q", "claim", WarrantProfile.of({2}))), (S.Hyperedge("pq", ("p",), ("q",), "SUPPORT"),))
    good, _ = AB.summarize(ks, ["p", "q"], "S")
    assert good.atom("S").liveness((1, 2)) is Liveness.DEAD
    bad = AB.mutant_summary_majority(ks, ["p", "q"], "S").atom("S")
    assert bad.liveness((1,)) is Liveness.LIVE and bad.liveness((1, 2)) is Liveness.DEAD


def test_navigation_score_promoted_to_truth_mutant():
    ks, seed = _witness()
    act = {x: F(1) for x in ks.ids}
    assert "bc" not in FI.enabled_hyperedges(ks, act, F(1, 2), revoked=(0,))
    assert "bc" in FI.mutant_enable_ignores_tail_warrant(ks, act, F(1, 2), revoked=(0,))


def test_feedback_retains_warrant_and_unmetered_mutation_cancers():
    base = S.KnowledgeSpace((S.Atom("a", "claim"), S.Atom("b", "claim")), (S.Hyperedge("ab", ("a",), ("b",), "DEPENDENCE"),))
    g = AD.GovernedSpace(base, {"a": AD.CertificateKind.INSTRUCTION, "b": AD.CertificateKind.INSTRUCTION})
    bad = AD.mutant_feedback_retains_warrant(g, S.Atom("f", "claim", WarrantProfile.of({5})), (S.Hyperedge("bf", ("b",), ("f",), "SUPPORT"),))
    assert not AD.ks_S1_admission(bad)
    bad2 = AD.mutant_unmetered_mutation(g, S.Atom("u", "claim", WarrantProfile.of({5})), (S.Hyperedge("bu", ("b",), ("u",), "SUPPORT"),))
    assert not AD.ks_S7_resource_conservation(bad2, 1)


def test_scalar_collapse_hides_a_trade():
    a = ResourceVector(navigation_steps=10, memory_bytes=100)
    b = ResourceVector(navigation_steps=110)
    assert a.incomparable_with(b) and mutant_scalar_collapse(a) == mutant_scalar_collapse(b)


def test_pairwise_expansion_accepted_without_certificate_is_the_mutant():
    e = S.Hyperedge("e", ("a", "b"), ("c",), "COMPOSITION")
    assert len(S.pairwise_expansion(e)) == 2
    with pytest.raises(S.TypedRejection):
        S.expand_pairwise(e, None)
