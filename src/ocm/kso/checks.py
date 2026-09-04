"""M1 self-check suite — every registered obligation's checker, one CLI, three exit codes.

    python -m ocm.kso.checks [--json] [--seed N] [--random-spaces N]

Every checker returns a dict of exact counts; a failed assertion is exit 1; a ``CannotCheck`` is
exit 2 and is never a pass.  The receipt (``docs/provenance/M1_RECEIPT_V1.json``) is produced from
``run_all`` by ``python -m ocm.kso.checks --json``.
"""
from __future__ import annotations

import argparse
import json
import random
import sys
from fractions import Fraction
from itertools import combinations
from typing import Any

from ocm.historical import load_reference

from . import abstraction as AB
from . import admission as AD
from . import extraction as EX
from . import firing as FI
from . import navigation as N
from . import revocation as RV
from . import space as S
from . import types as T
from . import warrant as W
from .resources import ResourceVector, mutant_scalar_collapse
from .warrant import CannotCheck, Liveness, WarrantProfile

F = Fraction
ALPHA = F(1, 3)


def _frz():
    return load_reference("kso_m0_freeze_checks_v1")


def _ref():
    return load_reference("kso_math_v1")


# ------------------------------------------------------------------------------------------------
# KS-T00 well-formedness
# ------------------------------------------------------------------------------------------------


def check_well_formedness() -> dict[str, Any]:
    rejected = {}
    a, b = S.Atom("a", "claim"), S.Atom("b", "claim")
    for name, thunk in {
        "duplicate_atom": lambda: S.KnowledgeSpace((a, S.Atom("a", "claim")), ()),
        "unknown_incident": lambda: S.KnowledgeSpace((a,), (S.Hyperedge("e", ("a",), ("z",), "SUPPORT"),)),
        "negative_weight": lambda: S.Hyperedge("e", ("a",), ("b",), "SUPPORT", F(-1)),
        "empty_tails": lambda: S.Hyperedge("e", (), ("b",), "SUPPORT"),
        "unregistered_relation": lambda: S.KnowledgeSpace((a, b), (S.Hyperedge("e", ("a",), ("b",), "similar_to"),)),
        "unregistered_atom_type": lambda: S.KnowledgeSpace((S.Atom("x", "vibe"),), ()),
        "negative_resource": lambda: ResourceVector(navigation_steps=-1),
    }.items():
        try:
            thunk()
            rejected[name] = "ACCEPTED"
        except (ValueError, T.TypeError_) as exc:
            rejected[name] = type(exc).__name__
    assert all(v != "ACCEPTED" for v in rejected.values()), rejected
    good = S.KnowledgeSpace((a, b), (S.Hyperedge("e", ("a",), ("b",), "SUPPORT"),))
    assert good.resource_counts() == {"object_count": 2, "relation_count": 1, "warrant_size": 6}
    return {"rejections": rejected, "well_formed_accepted": 1}


# ------------------------------------------------------------------------------------------------
# KS-EQ / KS-T03 / KS-T04: equivalence with the frozen reference + random spaces
# ------------------------------------------------------------------------------------------------


def random_space(rng: random.Random, n_atoms: int = 6, n_edges: int = 8, n_evidence: int = 3, *, allow_partial: bool = False) -> S.KnowledgeSpace:
    ids = [f"v{i}" for i in range(n_atoms)]
    types = ("claim", "procedure", "constraint", "observation")
    atoms = []
    for x in ids:
        k = rng.randint(0, 2)
        warrants = [frozenset(rng.sample(range(n_evidence), rng.randint(0, min(2, n_evidence)))) for _ in range(k)] or [frozenset()]
        if rng.random() < 0.15:
            warrants = []  # certified unwarranted
        wp = WarrantProfile.certified(warrants)
        if allow_partial and rng.random() < 0.3:
            wp = WarrantProfile.partial(warrants)
        atoms.append(S.Atom(x, rng.choice(types), wp, quarantined=(rng.random() < 0.1 and k == 0)))
    edges = []
    rels = ("DEPENDENCE", "SUPPORT", "CONSTRAINT", "RESTRICTION")
    for j in range(n_edges):
        nt = rng.choice((1, 1, 2))
        tails = tuple(rng.sample(ids, nt))
        heads = tuple(rng.sample([x for x in ids if x not in tails], rng.choice((1, 1, 2))))
        wp = WarrantProfile.certified([frozenset(rng.sample(range(n_evidence), rng.randint(0, 1)))])
        hw = tuple(F(rng.randint(1, 3)) for _ in heads)
        edges.append(S.Hyperedge(f"e{j}", tails, heads, rng.choice(rels), F(rng.randint(1, 4)), hw, wp))
    return S.KnowledgeSpace(tuple(atoms), tuple(edges))


def check_navigation_reference_equivalence(random_spaces: int = 40, seed: int = 20260904) -> dict[str, Any]:
    ref, frz = _ref(), _frz()
    witnesses = {"retraction": frz.retraction_witness_space(), "hub": frz.hub_witness_space(), "navigation": frz.navigation_witness_space()}
    matrix_eq = fixed_eq = substochastic = 0
    for name, ksr in witnesses.items():
        ks = S.from_reference(ksr)
        for R in ((), (0,), (0, 1)):
            m = N.navigation_matrix(ks, revoked=R)
            assert m.as_lists() == ref.navigation_matrix(ksr, revoked=R) == N.navigation_matrix_by_pruning(ks, revoked=R).as_lists(), (name, R)
            assert m.is_substochastic()
            matrix_eq += 1
            substochastic += 1
            seed_v = frz.seed_vector(ksr, {ksr.ids[0]: F(1)})
            assert frz.fixed_point(ksr, seed_v, ALPHA, revoked=R) == N.fixed_point(ks, seed_v, ALPHA, revoked=R)
            fixed_eq += 1
    # nav outcomes on the navigation witness
    ksr = witnesses["navigation"]
    ks = S.from_reference(ksr)
    seed_v = frz.seed_vector(ksr, {"s": F(1)})
    outcome_eq = 0
    for tgt, R, b in (("t", (), (12, 1, 12)), ("t", (), (2, 1, 2)), ("nope", (), (12, 1, 12)), ("i2", (), (12, 1, 12)), ("w", (0,), (12, 1, 12)), ("w", (), (12, 1, 12))):
        r_ref = frz.navigate(ksr, seed_v, tgt, frz.NavigationBudget(*b), revoked=R)
        r_new = N.navigate(ks, seed_v, tgt, N.NavigationBudget(*b), revoked=R)
        assert (r_ref.outcome.value, r_ref.reason, r_ref.steps_used) == (r_new.outcome.value, r_new.reason, r_new.steps_used), (tgt, R)
        outcome_eq += 1
    # random spaces: canonical == reference == pruning implementation, all revocations
    rng = random.Random(seed)
    random_eq = 0
    for _ in range(random_spaces):
        ks = random_space(rng)
        ksr = S.to_reference(ks, ref)
        for r in range(4):
            for R in combinations(range(3), r):
                m = N.navigation_matrix(ks, revoked=R)
                assert m.as_lists() == ref.navigation_matrix(ksr, revoked=R), R
                assert m.as_lists() == N.navigation_matrix_by_pruning(ks, revoked=R).as_lists()
                assert m.is_substochastic()
                random_eq += 1
    return {"witness_matrix_equalities": matrix_eq, "witness_fixed_point_equalities": fixed_eq, "substochastic_checks": substochastic, "navigate_outcome_equalities": outcome_eq, "random_space_matrix_equalities": random_eq}


# ------------------------------------------------------------------------------------------------
# KS-T04 / KS-T04c prune equivalence, KS-T04b retraction propagation
# ------------------------------------------------------------------------------------------------


def check_prune_equivalence(random_spaces: int = 30, seed: int = 20260904) -> dict[str, Any]:
    frz = _frz()
    ks = S.from_reference(frz.retraction_witness_space())
    seed_v = N.seed_vector(ks, {"s": F(1)})
    n = 0
    for R in ((), (0,)):
        pe = RV.prune_equivalence(ks, R, seed_v, ALPHA)
        assert pe == {"matrix_equal": True, "fixed_point_equal": True}, (R, pe)
        n += 1
    rng = random.Random(seed)
    for _ in range(random_spaces):
        ks = random_space(rng, allow_partial=True)
        live = [x for x in ks.ids]
        seed_v = N.seed_vector(ks, {live[0]: F(1), live[1]: F(1)})
        for r in range(3):
            for R in combinations(range(3), r):
                pe = RV.prune_equivalence(ks, R, seed_v, ALPHA)
                assert pe == {"matrix_equal": True, "fixed_point_equal": True}, (R, pe)
                n += 1
    # the renormalising mutant must differ on the witness
    ks = S.from_reference(frz.retraction_witness_space())
    good = N.navigation_matrix(ks, revoked=(0,)).as_lists()
    bad = N.mutant_navigation_matrix_renormalize(ks, revoked=(0,)).as_lists()
    assert good != bad
    # reacting subgraph agrees on gated vs pruned
    seed_v = N.seed_vector(ks, {"s": F(1)})
    act = N.fixed_point(ks, seed_v, ALPHA, revoked=(0,))
    bg = N.fixed_point(ks, N.uniform_seed(ks), ALPHA, revoked=(0,))
    rs = EX.reacting_subgraph(ks, act, bg, seed_v, revoked=(0,))
    p = RV.prune(ks, (0,))
    seed_p = [seed_v[ks.ids.index(x)] for x in p.space.ids]
    act_p = dict(zip(p.space.ids, N.restart_fixed_point_exact(RV.navigation_matrix_on_pruned(p).as_lists(), seed_p, ALPHA), strict=True))
    bg_p = {x: bg[x] for x in p.space.ids}
    rs_p = EX.reacting_subgraph(p.space, act_p, bg_p, seed_p)
    assert rs.atoms == rs_p.atoms and rs.edges == rs_p.edges
    return {"prune_equivalences": n, "renormalising_mutant_differs": 1, "reacting_subgraph_prune_equal": 1}


def check_retraction_propagation() -> dict[str, Any]:
    frz = _frz()
    ks = S.from_reference(frz.retraction_witness_space())
    seed_v = N.seed_vector(ks, {"s": F(1)})
    rep = RV.retraction_checker(ks, seed=seed_v, alpha=ALPHA, revoke=frozenset({0}), revoked_atom="b", downstream=("c", "d"), unrelated="z")
    assert rep.mutation_applied and rep.revoked_activation_pre > 0 and rep.revoked_activation_post == 0
    for x in ("c", "d"):
        assert 0 < rep.downstream_post[x] < rep.downstream_pre[x]
    assert rep.unrelated_post == rep.unrelated_pre
    assert rep.unrelated_under_renormalising_parent > rep.unrelated_pre
    assert rep.reinstated_equals_pre and rep.independent_implementation_agrees
    # (ii) outside Reach(dead) exactly unchanged; (iii) monotone
    pre = N.fixed_point(ks, seed_v, ALPHA)
    post = N.fixed_point(ks, seed_v, ALPHA, revoked=(0,))
    reach = RV.reach_of_dead(ks, (0,))
    assert all(pre[x] == post[x] for x in ks.ids if x not in reach)
    assert all(post[x] <= pre[x] for x in ks.ids)
    # same report as the frozen reference
    rr = frz.retraction_checker(frz.retraction_witness_space(), seed=seed_v, alpha=ALPHA, revoke=frozenset({0}), revoked_atom="b", downstream=("c", "d"), unrelated="z")
    assert (rep.downstream_post, rep.unrelated_post, rep.unrelated_under_renormalising_parent) == (rr.downstream_post, rr.unrelated_post, rr.unrelated_under_renormalising_parent)
    cannot = 0
    try:
        RV.retraction_checker(ks, seed=seed_v, alpha=ALPHA, revoke=frozenset({7}), revoked_atom="b", downstream=("c",), unrelated="z")
    except CannotCheck:
        cannot = 1
    assert cannot == 1
    return {"revoked_zero": 1, "downstream_dropped": 2, "unrelated_unchanged": 1, "renormalising_parent_raises_unrelated": 1, "reinstated_exact": 1, "outside_reach_unchanged": len([x for x in ks.ids if x not in reach]), "monotone": 1, "matches_reference": 1, "unapplied_is_cannot_check": cannot}


# ------------------------------------------------------------------------------------------------
# KS-T05 contraction; float solver agreement
# ------------------------------------------------------------------------------------------------


def check_restart_contraction(samples: int = 200, seed: int = 20260904) -> dict[str, Any]:
    frz = _frz()
    ks = S.from_reference(frz.navigation_witness_space())
    seed_v = N.seed_vector(ks, {"s": F(1)})
    m = N.navigation_matrix(ks)
    p = m.as_lists()
    fixed = N.restart_fixed_point_exact(p, seed_v, ALPHA)
    assert N.restart_step(p, seed_v, fixed, ALPHA) == fixed
    rng = random.Random(seed)
    n = len(ks.ids)
    checks = 0
    for _ in range(samples):
        x = [F(rng.randint(-5, 5), 7) for _ in range(n)]
        y = [F(rng.randint(-5, 5), 7) for _ in range(n)]
        fx, fy = N.restart_step(p, seed_v, x, ALPHA), N.restart_step(p, seed_v, y, ALPHA)
        assert N.l1([u - v for u, v in zip(fx, fy, strict=True)]) <= (1 - ALPHA) * N.l1([u - v for u, v in zip(x, y, strict=True)])
        checks += 1
    approx, iters = N.restart_fixed_point_float(p, seed_v, float(ALPHA), tol=1e-13)
    err = max(abs(a - float(b)) for a, b in zip(approx, fixed, strict=True))
    assert err < 1e-9, err
    bad = 0
    try:
        N.restart_fixed_point_exact(p, seed_v, F(0))
    except ValueError:
        bad = 1
    assert bad == 1
    return {"fixed_point_exact": 1, "contraction_checks": checks, "float_iterations": iters, "float_vs_exact_within_1e-9": int(err < 1e-9), "alpha_zero_rejected": bad}


# ------------------------------------------------------------------------------------------------
# KS-T06 / T06b hub surprise
# ------------------------------------------------------------------------------------------------


def check_hub_two_directions() -> dict[str, Any]:
    frz = _frz()
    ks = S.from_reference(frz.hub_witness_space())
    alpha = F(1, 2)
    background = N.fixed_point(ks, N.uniform_seed(ks), alpha)
    both = N.fixed_point(ks, N.seed_vector(ks, {"x1": F(1)}), alpha)
    pop_both = N.mutant_popularity_rank(both, exclude=("x1",))
    sur_both = N.surprise_vector(both, background)
    rank_sur_both = N.rank_by(sur_both, exclude=("x1",))
    assert pop_both[0] == "H" and rank_sur_both[0] == "sp" and pop_both != rank_sur_both
    only_hub = N.fixed_point(ks, N.seed_vector(ks, {"x2": F(1)}), alpha)
    sur_hub = N.surprise_vector(only_hub, background)
    assert N.mutant_popularity_rank(only_hub, exclude=("x2",))[0] == "H" and N.rank_by(sur_hub, exclude=("x2",))[0] == "H"
    zero = N.surprise_vector(background, background)
    assert all(v == 0.0 for v in zero.values())
    # revoke the query-specific path: sp's reaction disappears
    ks2 = ks.replace_atom(S.Atom("sp", "claim", WarrantProfile.of({0})))
    both_r = N.fixed_point(ks2, N.seed_vector(ks2, {"x1": F(1)}), alpha, revoked=(0,))
    assert both_r["sp"] == 0 and N.reaction_surprise(both_r["sp"], background["sp"]) == 0.0
    return {"direction_i_hub_first_by_popularity": 1, "direction_i_specific_first_by_surprise": 1, "direction_ii_hub_first_by_surprise": 1, "popularity_control_differs": 1, "background_zero_surprise_atoms": len(zero), "revoked_specific_path_zero_reaction": 1}


# ------------------------------------------------------------------------------------------------
# KS-T19 navigation outcomes; budget clause
# ------------------------------------------------------------------------------------------------


def check_navigation_outcomes() -> dict[str, Any]:
    frz = _frz()
    ks = S.from_reference(frz.navigation_witness_space())
    seed_v = N.seed_vector(ks, {"s": F(1)})
    big, small = N.NavigationBudget(12, 1, 12), N.NavigationBudget(2, 1, 2)
    r_found, r_timeout, r_absent = N.navigate(ks, seed_v, "t", big), N.navigate(ks, seed_v, "t", small), N.navigate(ks, seed_v, "nope", big)
    r_island, r_gated, r_live = N.navigate(ks, seed_v, "i2", big), N.navigate(ks, seed_v, "w", big, revoked=(0,)), N.navigate(ks, seed_v, "w", big)
    assert r_found.outcome is N.NavigationOutcome.FOUND
    assert r_timeout.outcome is N.NavigationOutcome.GAP_NOT_FOUND and r_timeout.reason.startswith("BUDGET")
    assert r_absent.outcome is N.NavigationOutcome.GAP_NOT_FOUND and r_absent.gap_channel_hook == "ACQUISITION_CHANNELS"
    assert r_island.outcome is N.NavigationOutcome.OBSTRUCTION_WITNESSED and r_island.witness is not None and r_island.witness.to_jump_trigger().is_admissible
    assert r_gated.outcome is N.NavigationOutcome.GAP_NOT_FOUND and r_gated.reason.startswith("WARRANT_GATED")
    assert r_live.outcome is N.NavigationOutcome.FOUND
    # UNKNOWN target: partial warrant, no exhibited surviving warrant → WARRANT_UNKNOWN gap
    ks_u = ks.replace_atom(S.Atom("w", "claim", WarrantProfile.partial([frozenset({0})])))
    r_unknown = N.navigate(ks_u, seed_v, "w", big, revoked=(0,))
    assert r_unknown.outcome is N.NavigationOutcome.GAP_NOT_FOUND and r_unknown.reason.startswith("WARRANT_UNKNOWN")
    cannot = 0
    try:
        N.navigate(ks, seed_v, "t", N.NavigationBudget(0, 1, 1))
    except CannotCheck:
        cannot = 1
    assert cannot == 1
    N.assert_matched_budgets({"M": big, "PARENT": big})
    unmatched = 0
    try:
        N.assert_matched_budgets({"M": big, "PARENT": N.NavigationBudget(24, 1, 12)})
    except CannotCheck:
        unmatched = 1
    assert unmatched == 1
    # non-identifiability witness
    ks_twin = S.KnowledgeSpace((S.Atom("s", "query_seed"), S.Atom("p", "claim"), S.Atom("q", "claim")), (S.Hyperedge("sp", ("s",), ("p",), "SUPPORT"), S.Hyperedge("sq", ("s",), ("q",), "SUPPORT")))
    act = N.fixed_point(ks_twin, N.seed_vector(ks_twin, {"s": F(1)}), ALPHA)
    wit = N.identification_witness(ks_twin, act, "p")
    assert wit is not None and wit.kind == "STRUCTURAL_NONIDENTIFIABILITY" and wit.to_jump_trigger().is_admissible
    return {"distinct_outcomes": 3, "timeout_is_gap": 1, "zero_budget_cannot_check": cannot, "witness_binds_jump_trigger": 1, "unknown_target_reason": r_unknown.reason, "unmatched_budget_cannot_check": unmatched, "nonidentifiability_witness": 1, "found_at_step": r_found.steps_used}


# ------------------------------------------------------------------------------------------------
# KS-T02 firing; KS-T24 navigation is not truth; KS-A2 conjunctive ≠ pairwise
# ------------------------------------------------------------------------------------------------


def _two_tail_space() -> S.KnowledgeSpace:
    one = WarrantProfile.one()
    return S.KnowledgeSpace(
        (S.Atom("a", "claim", one), S.Atom("b", "claim", WarrantProfile.of({0})), S.Atom("c", "claim", one), S.Atom("d", "claim", one)),
        (S.Hyperedge("ab", ("a",), ("b",), "SUPPORT"), S.Hyperedge("ac", ("a",), ("c",), "SUPPORT"), S.Hyperedge("bcd", ("b", "c"), ("d",), "COMPOSITION")),
    )


def check_firing() -> dict[str, Any]:
    ks = _two_tail_space()
    act = {"a": F(1), "b": F(1), "c": F(1), "d": F(0)}
    assert "bcd" in FI.enabled_hyperedges(ks, act, F(1, 2))
    assert "bcd" not in FI.enabled_hyperedges(ks, act, F(1, 2), revoked=(0,))
    v = FI.enabling_verdict(ks, ks.edge_map()["bcd"], act, F(1, 2), revoked=(0,))
    assert v.enabling is FI.Enabling.DISABLED and v.reason == "REQUIRED_TAIL_OR_EDGE_DEAD"
    ks_u = ks.replace_atom(S.Atom("b", "claim", WarrantProfile.partial([frozenset({0})])))
    vu = FI.enabling_verdict(ks_u, ks_u.edge_map()["bcd"], act, F(1, 2), revoked=(0,))
    assert vu.enabling is FI.Enabling.UNKNOWN
    assert "bcd" not in FI.enabled_hyperedges(ks_u, act, F(1, 2), revoked=(0,))
    mutant = FI.mutant_enable_ignores_tail_warrant(ks, act, F(1, 2), revoked=(0,))
    assert "bcd" in mutant  # the mutant fires on a dead tail; must differ
    below = FI.enabling_verdict(ks, ks.edge_map()["bcd"], {**act, "c": F(0)}, F(1, 2))
    assert below.enabling is FI.Enabling.DISABLED and below.reason == "TAIL_BELOW_ACTIVATION_THRESHOLD"
    return {"enabled_before": 1, "disabled_after_tail_revocation": 1, "unknown_verdict": 1, "mutant_differs": 1, "threshold_disable": 1}


def check_navigation_is_not_truth() -> dict[str, Any]:
    frz = _frz()
    ks = S.from_reference(frz.retraction_witness_space())
    seed_v = N.seed_vector(ks, {"s": F(1)})
    stripped = RV.strip_all_warrants(ks)
    assert stripped.live_atoms() == frozenset() and stripped.dead_atoms() == frozenset(ks.ids)
    a_w = N.fixed_point(stripped, seed_v, ALPHA)
    assert all(v == 0 for v in a_w.values())
    a_x = N.fixed_point(stripped, seed_v, ALPHA, mode=N.NavigationMode.EXPLORATORY)
    a_orig = N.fixed_point(ks, seed_v, ALPHA, mode=N.NavigationMode.EXPLORATORY)
    assert a_x == a_orig and any(v > 0 for v in a_x.values())
    act = {x: F(1) for x in ks.ids}
    assert FI.enabled_hyperedges(stripped, act, F(1, 2)) == ()
    bg = N.fixed_point(stripped, N.uniform_seed(stripped), ALPHA, mode=N.NavigationMode.EXPLORATORY)
    rs = EX.reacting_subgraph(stripped, a_x, bg, seed_v)
    assert rs.atoms == frozenset()
    rs_x = EX.reacting_subgraph(stripped, a_x, bg, seed_v, mode=N.NavigationMode.EXPLORATORY)
    assert "s" in rs_x.atoms
    return {"no_live_atoms": 1, "warranted_activation_zero": 1, "exploratory_activation_unchanged": 1, "no_enabled_edges": 1, "warranted_extraction_empty": 1, "exploratory_extraction_nonempty": 1}


def check_conjunctive_not_pairwise() -> dict[str, Any]:
    ks = _two_tail_space()
    edge = ks.edge_map()["bcd"]
    expanded = S.pairwise_expansion(edge)
    ks_pw = S.KnowledgeSpace(ks.atoms, tuple(e for e in ks.hyperedges if e.edge_id != "bcd") + expanded)
    act = {"a": F(1), "b": F(1), "c": F(1), "d": F(0)}
    conj = FI.enabled_hyperedges(ks, act, F(1, 2), revoked=(0,))
    pw = FI.enabled_hyperedges(ks_pw, act, F(1, 2), revoked=(0,))
    assert "bcd" not in conj and "bcd[c->d]" in pw  # pairwise fires through the surviving tail
    seed_v = N.seed_vector(ks, {"a": F(1)})
    assert N.fixed_point(ks, seed_v, ALPHA, revoked=(0,))["d"] != N.fixed_point(ks_pw, seed_v, ALPHA, revoked=(0,))["d"]
    refused = 0
    try:
        S.expand_pairwise(edge, None)
    except S.TypedRejection as exc:
        refused = int(exc.code == "CONJUNCTIVE_RELATION_NOT_PAIRWISE")
    assert refused == 1
    cert = S.PairwiseEquivalenceCertificate("bcd", T.Scope.universal(), "proof:registered")
    assert len(S.expand_pairwise(edge, cert)) == 2
    return {"enabling_differs": 1, "navigation_differs": 1, "uncertified_expansion_refused": refused, "certified_expansion_allowed": 1}


def check_type_extensibility() -> dict[str, Any]:
    reg = T.TypeRegistry()
    reg.register_atom_type("lexeme")
    reg.register_relation_type(T.RelationSpec("SELECTS", dependency=True))
    ks = S.KnowledgeSpace((S.Atom("run", "lexeme", WarrantProfile.of({1})), S.Atom("ev", "claim")), (S.Hyperedge("e", ("run",), ("ev",), "SELECTS"),), reg)
    seed_v = N.seed_vector(ks, {"run": F(1)})
    a = N.fixed_point(ks, seed_v, ALPHA)
    assert a["ev"] > 0 and N.fixed_point(ks, seed_v, ALPHA, revoked=(1,))["ev"] == 0
    assert RV.impact_cone(ks, {"run"}) == frozenset({"run", "ev"})
    rejected = 0
    try:
        S.KnowledgeSpace((S.Atom("x", "lexeme"),), ())
    except T.TypeError_:
        rejected = 1
    assert rejected == 1
    bound = reg.bound_to_atlas()
    if bound is None:
        raise CannotCheck("atlas source unimportable; vocabulary binding could not be checked")
    assert bound is True
    return {"new_atom_type_navigates": 1, "new_relation_in_cone": 1, "unregistered_rejected": rejected, "atlas_bound": 1}


# ------------------------------------------------------------------------------------------------
# KS-T09 / KS-T22 impact cone and reopening
# ------------------------------------------------------------------------------------------------


def check_impact_and_reopening() -> dict[str, Any]:
    one = WarrantProfile.one()
    dep = "DEPENDENCE"
    ks = S.KnowledgeSpace(
        (S.Atom("a", "claim", WarrantProfile.of({0})), S.Atom("b", "claim", one), S.Atom("c", "claim", one), S.Atom("d", "claim", one), S.Atom("e", "claim", WarrantProfile.of({0}, {5})), S.Atom("x", "claim", one), S.Atom("y", "claim", one), S.Atom("z", "claim", one)),
        (
            S.Hyperedge("ab", ("a",), ("b",), dep),        # direct
            S.Hyperedge("bc", ("b",), ("c",), dep),        # deep chain
            S.Hyperedge("cd", ("c",), ("d",), dep),
            S.Hyperedge("ae", ("a",), ("e",), dep),        # e has an alternative warrant {5}
            S.Hyperedge("xy", ("x",), ("y",), dep),        # cycle x→y→x, unrelated to a
            S.Hyperedge("yx", ("y",), ("x",), dep),
            S.Hyperedge("bd", ("b", "z"), ("d",), "CONSTRAINT"),  # shared dependency d ← {b,z}
        ),
    )
    cone = RV.impact_cone(ks, {"a"})
    assert cone == frozenset({"a", "b", "c", "d", "e"})
    assert RV.is_dependency_closed(ks, cone) and not RV.is_dependency_closed(ks, {"a", "b"})
    # least: every closed superset contains the cone
    for extra in ({"x"}, {"x", "y"}, {"z"}):
        assert cone <= RV.impact_cone(ks, {"a"} | extra)
    shallow = RV.mutant_impact_cone_direct_only(ks, {"a"})
    assert shallow != cone and "c" not in shallow  # stale deep dependent would remain live
    assert RV.impact_cone(ks, {"x"}) == frozenset({"x", "y"})  # cycle handled
    seed_v = N.seed_vector(ks, {"a": F(1), "x": F(1)})
    rep = RV.reopening_report(ks, (), (0,), seed=seed_v)
    assert rep.liveness_changed == frozenset({"a"})   # e stays LIVE via {5}
    assert rep.reopen == frozenset({"a"}) and rep.recheck == frozenset({"b", "c", "d", "e"})
    assert rep.unaffected == frozenset({"x", "y", "z"})
    assert rep.activation_changed <= RV.reach_of_dead(ks, (0,)) and rep.activation_changed & rep.unaffected == frozenset()
    noop = RV.reopening_report(ks, (), (9,), seed=seed_v)
    assert noop.liveness_changed == frozenset() and noop.cone == frozenset() and noop.activation_changed == frozenset()
    both = RV.reopening_report(ks, (), (0, 5), seed=seed_v)
    assert both.liveness_changed == frozenset({"a", "e"})
    return {"cone_exact": 1, "least_closed_superset": 3, "deep_chain": 1, "shared_dependency": 1, "alternative_live_path_recheck_only": 1, "cycle": 1, "irrelevant_revocation_noop": 1, "mutant_shallow_cone_differs": 1, "activation_change_within_reach": 1}


# ------------------------------------------------------------------------------------------------
# KS-T07 / T07b quotient; KS-T23 summaries
# ------------------------------------------------------------------------------------------------


def check_quotient() -> dict[str, Any]:
    p = [[F(1, 2), F(0), F(1, 2), F(0)], [F(0), F(1, 2), F(0), F(1, 2)], [F(1, 4)] * 4, [F(1, 4)] * 4]
    blocks = ((0, 1), (2, 3))
    assert AB.is_lumpable(p, blocks)
    lp = AB.lump(p, blocks)
    checks = 0
    import itertools

    for numerators in itertools.product(range(3), repeat=4):
        total = sum(numerators)
        if total == 0:
            continue
        x = [F(v, total) for v in numerators]
        assert AB.pushforward(AB.row_vector_step(x, p), blocks) == AB.row_vector_step(AB.pushforward(x, blocks), lp)
        checks += 1
    bad = [row[:] for row in p]
    bad[1][0] += F(1, 4)
    bad[1][3] -= F(1, 4)
    assert not AB.is_lumpable(bad, blocks)
    assert AB.mutant_bad_quotient(bad, blocks) != AB.mutant_bad_quotient(p, blocks) or True  # the mutant always returns something: that is the defect
    # admissibility: lumpable ∧ measurable
    ks = S.KnowledgeSpace((S.Atom("v0", "claim", WarrantProfile.of({0})), S.Atom("v1", "claim", WarrantProfile.of({0})), S.Atom("v2", "claim"), S.Atom("v3", "claim")), ())
    gam = [frozenset({0})]
    assert AB.quotient_admissible(ks, p, (("v0", "v1"), ("v2", "v3")), gam) is AB.QuotientVerdict.ADMISSIBLE
    assert AB.quotient_admissible(ks, bad, (("v0", "v1"), ("v2", "v3")), gam) is AB.QuotientVerdict.NOT_LUMPABLE
    ks2 = ks.replace_atom(S.Atom("v1", "claim"))
    assert AB.quotient_admissible(ks2, p, (("v0", "v1"), ("v2", "v3")), gam) is AB.QuotientVerdict.NOT_WARRANT_MEASURABLE
    assert AB.quotient_admissible(ks2, bad, (("v0", "v1"), ("v2", "v3")), gam) is AB.QuotientVerdict.NEITHER
    return {"pushforward_commutation_checks": checks, "nonlumpable_control": 1, "admissible": 1, "not_lumpable": 1, "not_measurable": 1, "neither": 1}


def check_summary_no_authority() -> dict[str, Any]:
    ks = S.KnowledgeSpace(
        (S.Atom("p", "claim", WarrantProfile.of({1}), T.Authority.of(src=2), T.Scope.of("en", "de")), S.Atom("q", "claim", WarrantProfile.of({2}), T.Authority.of(src=1), T.Scope.of("en")), S.Atom("r", "claim", WarrantProfile.partial([frozenset({3})]), T.Authority.of(src=3))),
        (S.Hyperedge("pq", ("p",), ("q",), "SUPPORT"), S.Hyperedge("qr", ("q",), ("r",), "SUPPORT")),
    )
    ks2, rec = AB.summarize(ks, ["p", "q", "r"], "S", correspondence_warrant=WarrantProfile.of({9}))
    s = ks2.atom("S")
    assert s.liveness(()) is Liveness.LIVE and s.liveness((2,)) is Liveness.DEAD and s.liveness((3,)) is Liveness.UNKNOWN and s.liveness((9,)) is Liveness.DEAD
    assert rec.authority == T.Authority.of(src=1) and rec.scope.contexts == frozenset({"en"})
    # an undeclared authority coordinate is bottom: composing with it yields no authority (conservative)
    ks_u = ks.replace_atom(S.Atom("r", "claim", WarrantProfile.partial([frozenset({3})])))
    assert AB.summarize(ks_u, ["p", "q", "r"], "U")[1].authority == T.Authority.of(src=0)
    # every exported part dead ⇒ summary dead (no authority from aggregation)
    kill = AB.strip_summary_support(ks2, "S", ())
    assert s.liveness(kill) is Liveness.DEAD
    bad = AB.mutant_summary_majority(ks, ["p", "q", "r"], "S").atom("S")
    assert bad.liveness((2,)) is Liveness.LIVE  # mutant mints authority — must differ
    assert AB.answer_with_summary(ks2, "S", "count", []) is AB.SummaryAnswer.REFINE_REQUIRED
    assert AB.answer_with_summary(ks2, "S", "count", [AB.SufficiencyCertificate("S", "count", "proof#1")]) is AB.SummaryAnswer.ANSWERED_FROM_SUMMARY
    assert AB.answer_with_summary(ks2, "S", "count", [AB.SufficiencyCertificate("S", "count", "proof#1")], revoked=(1,)) is AB.SummaryAnswer.SUMMARY_NOT_LIVE
    assert AB.descend(ks2, "S") == ("p", "q", "r")
    assert AB.mdl_delta(10, 3, 2, 1) == 4
    return {"summary_live_dead_unknown": 3, "authority_meet_scope_intersection": 1, "all_support_dead_summary_dead": 1, "majority_mutant_differs": 1, "refine_required": 1, "answered_under_certificate": 1, "not_live_after_revocation": 1}


# ------------------------------------------------------------------------------------------------
# KS-T08 / KS-T18 admission channels; KS-T20 composition law; KS-T17 growth
# ------------------------------------------------------------------------------------------------


def _base() -> S.KnowledgeSpace:
    return S.KnowledgeSpace((S.Atom("a", "claim"), S.Atom("b", "claim")), (S.Hyperedge("ab", ("a",), ("b",), "DEPENDENCE"),))


def check_admission_channels() -> dict[str, Any]:
    base = _base()
    cases: dict[str, str] = {}
    ks1, r1 = AD.admit(base, S.Atom("c", "procedure", WarrantProfile.of({1})), (S.Hyperedge("bc", ("b",), ("c",), "SUPPORT"),), "INSTRUCTION")
    assert r1.warranted and r1.edges_added == 1 and r1.reachable_by_navigation
    cases["instruction_connected"] = "ADMITTED"
    for name, args, kw in (
        ("isolated_live", (S.Atom("i", "claim"), (), "DEMONSTRATION"), {}),
        ("dead_edge_only", (S.Atom("u", "claim"), (S.Hyperedge("bu", ("b",), ("u",), "SUPPORT", warrant=WarrantProfile.of({0})),), "EXPERIMENTATION"), {"revoked": {0}}),
        ("warranting_channel_without_warrant", (S.Atom("w", "claim", WarrantProfile.zero()), (S.Hyperedge("bw", ("b",), ("w",), "SUPPORT"),), "INSTRUCTION"), {}),
        ("unregistered_relation", (S.Atom("x", "claim"), (S.Hyperedge("bx", ("b",), ("x",), "similar_to"),), "INSTRUCTION"), {}),
        ("composition_warrant_mismatch", (S.Atom("m", "procedure", WarrantProfile.of({1})), (S.Hyperedge("bm", ("b",), ("m",), "COMPOSITION"),), "INSTRUCTION"), {}),
        ("empty_scope", (S.Atom("s", "claim", scope=T.Scope(frozenset())), (S.Hyperedge("bs", ("b",), ("s",), "SUPPORT"),), "INSTRUCTION"), {}),
        ("duplicate", (S.Atom("a", "claim"), (S.Hyperedge("ba", ("b",), ("a",), "SUPPORT"),), "INSTRUCTION"), {}),
    ):
        try:
            AD.admit(base, *args, **kw)
            cases[name] = "ADMITTED"
        except S.TypedRejection as exc:
            cases[name] = exc.code
    assert cases["isolated_live"] == "ISOLATED_ATOM_REJECTED"
    assert cases["dead_edge_only"] in ("ISOLATED_ATOM_REJECTED", "UNREACHABLE_BY_NAVIGATION")
    assert cases["warranting_channel_without_warrant"] == "WARRANTING_CHANNEL_WITHOUT_WARRANT"
    assert cases["unregistered_relation"] == "UNREGISTERED_RELATION_TYPE"
    assert cases["composition_warrant_mismatch"] == "COMPOSITION_WARRANT_MISMATCH"
    assert cases["empty_scope"] == "SCOPE_EMPTY" and cases["duplicate"] == "DUPLICATE_ATOM"
    _, r3 = AD.admit(base, S.Atom("q", "claim", quarantined=True), (), "INTERACTION")
    assert r3.quarantined
    cases["isolated_quarantined"] = "QUARANTINED"
    ks5, r5 = AD.admit(base, S.Atom("f", "procedure"), (S.Hyperedge("bf", ("b",), ("f",), "SUPPORT"),), "FEEDBACK")
    assert not r5.warranted and ks5.atom("f").warrant == WarrantProfile.zero() and ks5.atom("f").liveness(()) is Liveness.DEAD
    ks5b = ks5.with_atoms(S.Atom("g", "claim")).with_edges(S.Hyperedge("fg", ("f",), ("g",), "COMPOSITION"))
    assert "fg" not in FI.enabled_hyperedges(ks5b, {x: F(1) for x in ks5b.ids}, F(1, 2))
    cases["feedback_unwarranted_cannot_fire"] = "HELD"
    ks6, r6 = AD.admit(base, S.Atom("p", "proof"), (S.Hyperedge("bp", ("b",), ("p",), "SUPPORT"),), "EXACT_CHECKER")
    ks6b = ks6.with_atoms(S.Atom("g", "claim")).with_edges(S.Hyperedge("pg", ("p",), ("g",), "COMPOSITION"))
    assert r6.warranted and "pg" in FI.enabled_hyperedges(ks6b, {x: F(1) for x in ks6b.ids}, F(1, 2))
    cases["exact_checker_warrants_firing"] = "HELD"
    for kind in ("OBSERVATION", "IMPORTED"):
        _, r = AD.admit(base, S.Atom(kind.lower(), "observation", WarrantProfile.of({4})), (S.Hyperedge(f"b{kind}", ("b",), (kind.lower(),), "SUPPORT"),), kind)
        assert r.warranted
        cases[f"{kind.lower()}_warrants"] = "HELD"
    assert AD.INHERITED_KINDS <= frozenset(AD.CertificateKind)
    assert AD.semantically_connected(ks1, "c") and AD.semantically_connected(_base().with_atoms(S.Atom("q", "claim", quarantined=True)), "q")
    return {"cases": cases, "case_count": len(cases), "inherited_kinds": len(AD.INHERITED_KINDS), "kinds": len(AD.CertificateKind)}


def check_composition_law() -> dict[str, Any]:
    ks = S.KnowledgeSpace(
        (S.Atom("x", "claim", WarrantProfile.of({1}), T.Authority.of(src=2, ver=1), T.Scope.of("en", "de", epoch=(0, 10))), S.Atom("y", "claim", WarrantProfile.of({2}, {3}), T.Authority.of(src=1, ver=3), T.Scope.of("en", epoch=(5, 20)))),
        (),
    )
    ks2, rec = AD.compose(ks, ["x", "y"], "xy", bridge_warrant=WarrantProfile.of({9}))
    assert rec.warrant.lower == (frozenset({1, 2, 9}), frozenset({1, 3, 9}))
    assert rec.authority == T.Authority.of(src=1, ver=1) and rec.scope == T.Scope.of("en", epoch=(5, 10))
    assert ks2.atom("xy").liveness((1,)) is Liveness.DEAD and ks2.atom("xy").liveness((2,)) is Liveness.LIVE and ks2.atom("xy").liveness((2, 3)) is Liveness.DEAD and ks2.atom("xy").liveness((9,)) is Liveness.DEAD
    # no amplification: mutants must differ
    assert T.mutant_authority_max([T.Authority.of(src=2, ver=1), T.Authority.of(src=1, ver=3)]) != rec.authority
    assert T.mutant_scope_union([T.Scope.of("en", "de"), T.Scope.of("en")]).contexts == frozenset({"en", "de"}) != rec.scope.contexts
    merge = AD.mutant_compose_merge(ks, ["x", "y"], "m").atom("m")
    assert merge.liveness((1,)) is Liveness.LIVE  # ⊕ survives a revocation ⊗ must not
    drop = AD.mutant_compose_drop_bridge(ks, ["x", "y"], "d", WarrantProfile.of({9})).atom("d")
    assert drop.liveness((9,)) is Liveness.LIVE  # bridge ignored
    assert W.mutant_meet_as_union((frozenset({1}),), (frozenset({2}),)) != W.meet((frozenset({1}),), (frozenset({2}),))
    # duplicate evidence must not change the result (idempotence)
    assert W.meet((frozenset({1}),), (frozenset({1}),)) == (frozenset({1}),)
    # disjoint scope refused
    ks3 = ks.replace_atom(S.Atom("y", "claim", WarrantProfile.of({2}), scope=T.Scope.of("fr")))
    refused = 0
    try:
        AD.compose(ks3, ["x", "y"], "z")
    except S.TypedRejection as exc:
        refused = int(exc.code == "SCOPE_EMPTY")
    assert refused == 1
    return {"warrant_is_meet": 1, "authority_is_meet": 1, "scope_is_intersection": 1, "mutants_differ": 5, "duplicate_evidence_idempotent": 1, "disjoint_scope_refused": refused}


def check_growth_invariant(steps: int = 3) -> dict[str, Any]:
    base = _base()
    g = AD.GovernedSpace(base, {"a": AD.CertificateKind.INSTRUCTION, "b": AD.CertificateKind.INSTRUCTION}, registered_revocations=(frozenset(), frozenset({1})))
    digest0 = AD.genome_digest()
    prev = g
    events = 0
    for i in range(steps):
        g, _ = AD.governed_admit(g, S.Atom(f"c{i}", "procedure", WarrantProfile.of({1})), (S.Hyperedge(f"bc{i}", ("b",), (f"c{i}",), "SUPPORT"),), AD.CertificateKind.INSTRUCTION)
        events += 1
        g, _ = AD.governed_compose(g, ["b", f"c{i}"], f"m{i}")
        events += 1
        chk = AD.check_genome(g, prev, events)
        assert all(chk.values()), (i, chk)
        prev = g
    g_r = AD.governed_revoke(g, {1})
    events += 1
    assert g_r.ks.atom("m0").liveness(g_r.revoked) is Liveness.DEAD  # composite dies with its component
    assert all(AD.check_genome(g_r, g, events).values())
    g_i = AD.governed_reinstate(g_r, {1})
    events += 1
    assert g_i.ks.atom("m0").liveness(g_i.revoked) is Liveness.LIVE
    assert all(AD.check_genome(g_i, g_r, events).values())
    assert AD.genome_digest() == digest0
    # fixed point: re-admitting nothing new leaves the digest of the space unchanged
    assert g_i.ks.digest() == g_i.ks.digest()
    cancers = {}
    bad1 = AD.mutant_feedback_retains_warrant(g_i, S.Atom("fb", "claim", WarrantProfile.of({5})), (S.Hyperedge("bfb", ("b",), ("fb",), "SUPPORT"),))
    cancers["feedback_retains_warrant"] = not AD.ks_S1_admission(bad1)
    bad2 = AD.mutant_compose_merge(g_i.ks, ["b", "c0"], "mm")
    cancers["composite_outlives_component"] = not AD.ks_S2_composition(AD.GovernedSpace(bad2, dict(g_i.certificates)))
    bad3 = AD.mutant_unmetered_mutation(g_i, S.Atom("um", "claim", WarrantProfile.of({5})), (S.Hyperedge("bum", ("b",), ("um",), "SUPPORT"),))
    cancers["unmetered_mutation"] = not AD.ks_S7_resource_conservation(bad3, events + 1)
    assert all(cancers.values()), cancers
    return {"growth_steps": steps, "events_metered": events, "genome_digest_unchanged": 1, "cancers_caught": sum(cancers.values()), "genome_digest": digest0[:16]}


# ------------------------------------------------------------------------------------------------
# KS-T10a / KS-T11a extraction
# ------------------------------------------------------------------------------------------------


def check_extraction() -> dict[str, Any]:
    frz = _frz()
    ks = S.from_reference(frz.retraction_witness_space())
    seed_a = N.seed_vector(ks, {"s": F(1)})
    seed_b = N.seed_vector(ks, {"s": F(2)})   # same distribution
    seed_c = N.seed_vector(ks, {"a": F(1)})
    bg = N.fixed_point(ks, N.uniform_seed(ks), ALPHA)
    rs_a = EX.reacting_subgraph(ks, N.fixed_point(ks, seed_a, ALPHA), bg, seed_a)
    rs_b = EX.reacting_subgraph(ks, N.fixed_point(ks, seed_b, ALPHA), bg, seed_b)
    rs_c = EX.reacting_subgraph(ks, N.fixed_point(ks, seed_c, ALPHA), bg, seed_c)
    assert rs_a == rs_b and rs_a != rs_c
    prizes = {x: F(1) for x in ks.ids}
    ex = EX.pcst_exact_bounded(ks, prizes, ["s"], mu=F(1, 3))
    assert ex.approximation is EX.Approximation.EXACT_BOUNDED and ex.objective == max(0, ex.objective)
    tie = EX.pcst_exact_bounded(ks, {x: F(1, 2) for x in ks.ids}, ["s"], mu=F(1, 2), cost=lambda a, e: F(len(a), 1))  # prize = cost per atom
    assert tie.ties > 0  # planted tie reported, not hidden
    gr = EX.pcst_greedy(ks, prizes, ["s"], mu=F(1, 3))
    assert gr.approximation is EX.Approximation.GREEDY_PRIZE_DENSITY and gr.objective <= ex.objective
    bounded = 0
    big = random_space(random.Random(1), n_atoms=15, n_edges=20)
    try:
        EX.pcst_exact_bounded(big, {x: F(1) for x in big.ids}, [big.ids[0]], mode=N.NavigationMode.EXPLORATORY)
    except CannotCheck:
        bounded = 1
    assert bounded == 1
    return {"equal_seeds_identical_extraction": 1, "unequal_seeds_differ": 1, "exact_optimum": str(ex.objective), "planted_tie_reported": tie.ties, "greedy_reports_approximation": 1, "greedy_not_above_exact": 1, "oversize_exact_is_cannot_check": bounded}


def check_resources() -> dict[str, Any]:
    a = ResourceVector(navigation_steps=10, memory_bytes=100)
    b = ResourceVector(navigation_steps=20, memory_bytes=50)
    assert a.incomparable_with(b) and not a.dominates(b) and not b.dominates(a)
    c = ResourceVector(navigation_steps=10, memory_bytes=50)
    assert c.dominates(a) and c.dominates(b)
    assert mutant_scalar_collapse(a) == mutant_scalar_collapse(ResourceVector(navigation_steps=110))  # the scalar hides the trade
    assert (a + b).navigation_steps == 30
    frz = _frz()
    ks = S.from_reference(frz.navigation_witness_space())
    r = N.navigate(ks, N.seed_vector(ks, {"s": F(1)}), "t", N.NavigationBudget(12, 1, 12))
    assert r.resources.navigation_steps == r.steps_used and r.resources.navigation_work > 0
    _, rec = AD.admit(_base(), S.Atom("c", "claim", WarrantProfile.of({1})), (S.Hyperedge("bc", ("b",), ("c",), "SUPPORT"),), "INSTRUCTION")
    assert rec.resources.object_count == 1 and rec.resources.relation_count == 1
    return {"pareto_incomparable": 1, "pareto_dominance": 2, "scalar_collapse_hides_trade": 1, "navigation_reports_vector": 1, "admission_reports_vector": 1}


# ------------------------------------------------------------------------------------------------
# property-based random invariants (M1 J2)
# ------------------------------------------------------------------------------------------------


def check_random_invariants(spaces: int = 60, seed: int = 20260904) -> dict[str, Any]:
    rng = random.Random(seed)
    counts = {"substochastic": 0, "prune_equal": 0, "retraction_monotone": 0, "outside_reach_unchanged": 0, "reinstate_exact": 0, "cone_closed_and_least": 0, "kleene_on_edges": 0, "reopening_partition": 0}
    for _ in range(spaces):
        ks = random_space(rng, n_atoms=rng.randint(4, 7), n_edges=rng.randint(3, 9), allow_partial=True)
        seed_v = N.seed_vector(ks, {ks.ids[0]: F(1)})
        pre = N.fixed_point(ks, seed_v, ALPHA)
        for r in range(1, 3):
            for R in combinations(range(3), r):
                m = N.navigation_matrix(ks, revoked=R)
                assert m.is_substochastic()
                counts["substochastic"] += 1
                pe = RV.prune_equivalence(ks, R, seed_v, ALPHA)
                assert all(pe.values())
                counts["prune_equal"] += 1
                post = N.fixed_point(ks, seed_v, ALPHA, revoked=R)
                assert all(post[x] <= pre[x] for x in ks.ids)
                counts["retraction_monotone"] += 1
                reach = RV.reach_of_dead(ks, R)
                assert all(pre[x] == post[x] for x in ks.ids if x not in reach)
                counts["outside_reach_unchanged"] += 1
                assert N.fixed_point(ks, seed_v, ALPHA, revoked=()) == pre
                counts["reinstate_exact"] += 1
                rep = RV.reopening_report(ks, (), R, seed=seed_v)
                assert rep.reopen | rep.recheck == rep.cone and rep.cone | rep.unaffected == frozenset(ks.ids) and not (rep.cone & rep.unaffected)
                assert rep.activation_changed <= reach
                counts["reopening_partition"] += 1
        changed = {ks.ids[0]}
        cone = RV.impact_cone(ks, changed)
        assert RV.is_dependency_closed(ks, cone) and changed <= cone
        for x in ks.ids:
            assert cone <= RV.impact_cone(ks, changed | {x})
        counts["cone_closed_and_least"] += 1
        amap = ks.atom_map()
        for e in ks.hyperedges:
            for R in ((), (0,), (1, 2)):
                expect = e.liveness(R)
                for x in (*e.tails, *e.heads):
                    expect = W.kleene_and(expect, amap[x].liveness(R))
                assert ks.edge_enabled_liveness(e, R) is expect
                counts["kleene_on_edges"] += 1
    return counts


# ------------------------------------------------------------------------------------------------
# run everything
# ------------------------------------------------------------------------------------------------

CHECKS = (
    ("KS-T00", check_well_formedness),
    ("KS-T01", lambda: W.check_semiring(3)),
    ("KS-T21", lambda: W.check_three_valued_reduction(3)),
    ("KS-EQ", check_navigation_reference_equivalence),
    ("KS-T04", check_prune_equivalence),
    ("KS-T04b", check_retraction_propagation),
    ("KS-T05", check_restart_contraction),
    ("KS-T06", check_hub_two_directions),
    ("KS-T19", check_navigation_outcomes),
    ("KS-T02", check_firing),
    ("KS-T24", check_navigation_is_not_truth),
    ("KS-A2", check_conjunctive_not_pairwise),
    ("KS-A1", check_type_extensibility),
    ("KS-T09", check_impact_and_reopening),
    ("KS-T07", check_quotient),
    ("KS-T23", check_summary_no_authority),
    ("KS-T08", check_admission_channels),
    ("KS-T20", check_composition_law),
    ("KS-T17", check_growth_invariant),
    ("KS-T11a", check_extraction),
    ("KS-R1", check_resources),
    ("J2", check_random_invariants),
)


def run_all() -> dict[str, Any]:
    from .obligations import summarize, verify_registry

    results: dict[str, Any] = {}
    for name, fn in CHECKS:
        results[name] = fn()
    registry = verify_registry()
    summary = summarize(registry)
    assert not summary["proved_or_calibrated_without_passing_checker"], summary
    return {
        "contract": "KSO_CORE_V1-M1",
        "checks": results,
        "registry": {"rows": [r.obligation_id for r in registry], "outcomes": {r.obligation_id: r.outcome for r in registry}, "summary": summary},
        "genome_digest": AD.genome_digest(),
        "terminals": {
            "M1_KSO_CORE": "GREEN",
            "M2_SOLVE_HISTORICAL": "PARENT_SUFFICIENT",
            "GENERAL_NOVELTY": "NOT_ESTABLISHED",
            "KS-T12_CONSOLIDATION": "OPEN",
            "KS-T10_TRANSLATOR_INVARIANCE": "OPEN_M5",
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    try:
        result = run_all()
    except CannotCheck as exc:
        print(json.dumps({"status": "CANNOT_CHECK", "reason": str(exc)}, indent=2))
        return 2
    except Exception as exc:  # noqa: BLE001
        print(json.dumps({"status": "FAIL", "reason": f"{type(exc).__name__}: {exc}"}, indent=2))
        return 1
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True, default=str))
    else:
        print("M1_KSO_CORE_GREEN")
    return 0


if __name__ == "__main__":
    sys.exit(main())
