"""Optimization guards: structural caches must never become warrant caches."""
from dataclasses import asdict, replace
from fractions import Fraction
import copy
import pickle

import pytest

from ocm.kso.admission import admit
from ocm.kso.navigation import (NavigationMode, fixed_point, gated_closure,
                                navigation_matrix, positive_activation_support,
                                structural_denominators, ungated_closure)
from ocm.kso.navigation_sparse import SparseMatrix, sparse_activation, sparse_fixed_point_certified
from ocm.kso.revocation import impact_cone, reopening_report
from ocm.kso.space import Atom, Hyperedge, KnowledgeSpace, TypedRejection
from ocm.kso.types import RelationSpec, TypeRegistry
from ocm.kso.warrant import CannotCheck, WarrantProfile


def witness():
    return KnowledgeSpace(
        (Atom("a", "claim", WarrantProfile.of({"a"})),
         Atom("b", "claim", WarrantProfile.of({"b"}, {"backup"})),
         Atom("c", "claim"), Atom("d", "claim", WarrantProfile.partial(({"d"},))),
         Atom("unrelated", "claim")),
        (Hyperedge("joint", ("a", "b"), ("c", "d"), "DEPENDENCE",
                   head_weights=(Fraction(1), Fraction(3)), warrant=WarrantProfile.of({"edge"})),
         Hyperedge("back", ("c",), ("a",), "SUPPORT"),
         Hyperedge("zero", ("c",), ("unrelated",), "RESTRICTION", weight=Fraction(0))),
        TypeRegistry(),
    )


def slow_closure(ks, start, revoked=(), *, conjunctive=False, dependency_types=None):
    live = ks.live_atoms(revoked)
    reached = set(start) & live if conjunctive else set(start)
    while True:
        before = reached.copy()
        for e in ks.hyperedges:
            if dependency_types is not None and e.relation_type not in dependency_types:
                continue
            if conjunctive:
                if set(e.tails) <= reached and e.warrant.is_live(revoked):
                    reached.update(set(e.heads) & live)
            elif set(e.tails) & reached:
                reached.update(e.heads)
        if reached == before:
            return frozenset(reached)


def test_admission_revocation_iterables_have_identical_effect():
    ks = KnowledgeSpace((Atom("a", "claim", WarrantProfile.of({"revoked"})),
                         Atom("b", "claim")), ())
    edge = Hyperedge("joint", ("a", "b"), ("new",), "SUPPORT")
    for revoked in ({"revoked"}, iter(("revoked",))):
        with pytest.raises(TypedRejection, match="UNREACHABLE_BY_NAVIGATION"):
            admit(ks, Atom("new", "claim"), (edge,), "INSTRUCTION", revoked=revoked)


def test_lookup_caches_preserve_public_copies_and_persistent_edits():
    ks = witness()
    original_digest, original_dict = ks.digest(), asdict(ks)
    # Warm every structural cache before an edit or external map mutation.
    assert ks.atom("a").atom_id == "a"
    assert ks.incident_edges("a") == (ks.hyperedges[0], ks.hyperedges[1])
    assert ks.outgoing_edges("a") == (ks.hyperedges[0],)
    atom_map, edge_map = ks.atom_map(), ks.edge_map()
    atom_map.clear()
    edge_map.clear()
    assert ks.atom("a").atom_id == "a" and len(ks.edge_map()) == 3
    with pytest.raises(TypedRejection, match="UNKNOWN_ATOM"):
        ks.atom("missing")
    assert ks.incident_edges("missing") == ks.outgoing_edges("missing") == ()
    replaced = ks.replace_atom(replace(ks.atom("a"), warrant=WarrantProfile.zero()))
    added = ks.with_atoms(Atom("new", "claim")).with_edges(Hyperedge("new-edge", ("a",), ("new",), "SUPPORT"))
    removed = ks.without(("b",))
    assert not replaced.atom("a").is_live(()) and ks.atom("a").is_live(())
    assert added.ids[-1] == "new" and added.outgoing_edges("a")[-1].edge_id == "new-edge"
    assert removed.outgoing_edges("a") == () and "b" not in removed.atom_map()
    assert ks.digest() == original_digest and asdict(ks) == original_dict
    for duplicate in (copy.deepcopy(ks), pickle.loads(pickle.dumps(ks))):
        assert duplicate == ks and duplicate.atom_map() == ks.atom_map()
        assert duplicate.outgoing_edges("a") == ks.outgoing_edges("a")


def test_constructor_takes_immutable_snapshot_of_sequence_inputs():
    atoms = [Atom("a", "claim"), Atom("b", "claim")]
    tails, heads, weights = ["a"], ["b"], [Fraction(1)]
    edges = [Hyperedge("edge", tails, heads, "SUPPORT", head_weights=weights)]
    ks = KnowledgeSpace(atoms, edges)
    original = ks.digest()
    assert ks.outgoing_edges("a") == tuple(edges)
    atoms.clear()
    edges.clear()
    tails.clear()
    heads.clear()
    weights.clear()
    assert ks.ids == ("a", "b") and ks.digest() == original
    assert ungated_closure(ks, ("a",)) == frozenset({"a", "b"})


@pytest.mark.parametrize("revoked", [(), ("a",), ("b",), ("b", "backup"), ("d",), ("edge",), ("irrelevant",)])
def test_indexed_walkers_match_independent_fixed_point(revoked):
    ks = witness()
    for seeds in ((), ("a",), ("a", "b"), ("unrelated",)):
        assert ungated_closure(ks, seeds) == slow_closure(ks, seeds)
        assert gated_closure(ks, seeds, revoked) == slow_closure(ks, seeds, revoked, conjunctive=True)
        for dep in (ks.registry.dependency_types, frozenset(), frozenset({"RESTRICTION"})):
            assert impact_cone(ks, seeds, dep) == slow_closure(ks, seeds, dependency_types=dep)


def test_registry_dependency_mutation_cannot_stale_structural_cache():
    ks = witness()
    assert impact_cone(ks, ("a",)) == frozenset({"a", "c", "d"})
    ks.registry.register_relation_type(RelationSpec("RESTRICTION", dependency=True))
    assert impact_cone(ks, ("a",)) == frozenset({"a", "c", "d", "unrelated"})


def test_revocation_unrelated_reinstatement_and_relevance_after_cache_warmup():
    ks = witness()
    seed = [Fraction(1, 3), Fraction(1, 3), Fraction(0), Fraction(0), Fraction(1, 3)]
    before = fixed_point(ks, seed, Fraction(1, 3))
    frozen_denoms = structural_denominators(ks)
    for revoked in (("a",), ("edge",), ("d",), ("b", "backup"), ("irrelevant",), ()):
        # Exercise the indexed paths between changing warrant states.
        ungated_closure(ks, ("a",))
        reopening_report(ks, (), revoked)
        exact = fixed_point(ks, seed, Fraction(1, 3), revoked=revoked)
        approx, _, _ = sparse_activation(ks, seed, 1 / 3, revoked=revoked)
        assert max(abs(float(exact[x]) - approx[x]) for x in ks.ids) < 1e-9
        assert exact["unrelated"] == before["unrelated"]
        assert structural_denominators(ks) == frozen_denoms
        if revoked == ("a",):
            assert exact["a"] == exact["c"] == exact["d"] == 0
        if revoked in (("irrelevant",), ()):
            assert exact == before
    relevance = {"DEPENDENCE": Fraction(0)}
    first = navigation_matrix(ks, relevance=relevance)
    relevance["DEPENDENCE"] = Fraction(1)
    assert navigation_matrix(ks, relevance=relevance) != first
    assert navigation_matrix(ks, relevance=lambda key: relevance.get(key, 1)) == navigation_matrix(ks, relevance=relevance)
    assert navigation_matrix(ks, revoked=("a",), mode=NavigationMode.EXPLORATORY).rows == navigation_matrix(ks).rows


def test_index_resources_count_only_materialized_index_containers():
    ks = witness()
    initial = ks.index_resources()
    assert initial.index_size == len(ks.atoms)  # ids was materialized by validation
    ks.atom("a")
    ks.edge_map()
    ks.incident_edges("a")
    ks.outgoing_edges("a")
    charged = ks.index_resources()
    assert charged.index_size > initial.index_size
    assert charged.memory_bytes > initial.memory_bytes > 0
    assert ks.resource_counts() == {"object_count": 5, "relation_count": 3, "warrant_size": 18}
    assert ks.index_resources() == charged  # observing storage never allocates more indexes


@pytest.mark.parametrize("alpha", [Fraction(1, 100), Fraction(1, 3), Fraction(1)])
@pytest.mark.parametrize("revoked", [(), ("a",), ("edge",), ("d",), ("b", "backup")])
def test_exact_positive_support_matches_rational_activation(alpha, revoked):
    ks = witness()
    for seed in ([Fraction(1), Fraction(0), Fraction(0), Fraction(0), Fraction(0)],
                 [Fraction(0), Fraction(0), Fraction(0), Fraction(0), Fraction(1)]):
        exact = fixed_point(ks, seed, alpha, revoked=revoked)
        assert positive_activation_support(ks, seed, alpha, revoked=revoked) == frozenset(x for x, value in exact.items() if value > 0)


def test_positive_support_is_not_conjunctive_firing_or_zero_weight_structure():
    ks = witness()
    seed = [Fraction(1), Fraction(0), Fraction(0), Fraction(0), Fraction(0)]
    support = positive_activation_support(ks, seed, Fraction(1, 3))
    assert support == frozenset({"a", "c", "d"})
    assert gated_closure(ks, ("a",)) == frozenset({"a"})
    assert "unrelated" in ungated_closure(ks, ("a",))
    zero_share = replace(ks.hyperedges[0], head_weights=(Fraction(1), Fraction(0)))
    changed = replace(ks, hyperedges=(zero_share, *ks.hyperedges[1:]))
    assert "d" not in positive_activation_support(changed, seed, Fraction(1, 3))


@pytest.mark.parametrize("size", [2, 199, 200, 201])
def test_admission_uses_exact_positive_support_without_solving_magnitudes(size, monkeypatch):
    from ocm.kso import navigation

    def no_magnitude_solve(*args, **kwargs):
        raise AssertionError("admission needs positive support, not activation magnitudes")

    monkeypatch.setattr(navigation, "restart_fixed_point_exact", no_magnitude_solve)
    ks = KnowledgeSpace(tuple(Atom(f"v{i}", "claim") for i in range(size)),
                        (Hyperedge("normal", ("v0",), ("v1",), "SUPPORT"),))
    tiny = Hyperedge("tiny", ("v0",), ("new",), "SUPPORT", weight=Fraction(1, 10**400))
    _, receipt = admit(ks, Atom("new", "claim"), (tiny,), "INSTRUCTION")
    assert receipt.reachable_by_navigation
    with pytest.raises(TypedRejection, match="UNREACHABLE_BY_NAVIGATION"):
        admit(ks, Atom("new", "claim"), (replace(tiny, weight=Fraction(0)),), "INSTRUCTION")
    with pytest.raises(TypedRejection, match="UNREACHABLE_BY_NAVIGATION"):
        admit(ks, Atom("new", "claim"), (tiny,), "INSTRUCTION", alpha=Fraction(1))


def test_sparse_tolerance_bounds_error_even_for_small_restart_mass():
    matrix = SparseMatrix(("self",), (((0, 1.0),),), 1)
    result = sparse_fixed_point_certified(matrix, [1.0], 0.01, tol=1e-6)
    assert abs(Fraction(result.activation[0]) - 1) <= result.error_bound_l1 <= Fraction(1e-6)
    assert result.error_bound_l1 == result.residual_l1 / (1 - result.contraction)
    with pytest.raises(CannotCheck, match="precision cannot certify"):
        sparse_fixed_point_certified(matrix, [1.0], 0.01, tol=1e-20)
    with pytest.raises(CannotCheck, match="within 1 steps"):
        sparse_fixed_point_certified(matrix, [1.0], 0.01, max_iter=1)


@pytest.mark.parametrize("seed,alpha,tol", [([], .5, 1e-6), ([float("nan")], .5, 1e-6),
                                         ([-1.0], .5, 1e-6), ([1.0], 0, 1e-6),
                                         ([1.0], .5, 0), ([1.0], .5, float("inf"))])
def test_sparse_certificate_rejects_invalid_inputs(seed, alpha, tol):
    with pytest.raises(ValueError):
        sparse_fixed_point_certified(SparseMatrix(("a",), (((0, 1.0),),), 1), seed, alpha, tol=tol)


def test_sparse_certificate_checks_the_represented_operator_contraction():
    with pytest.raises(CannotCheck, match="no certified contraction"):
        sparse_fixed_point_certified(SparseMatrix(("a",), (((0, 2.0),),), 1), [1.0], .5)
    with pytest.raises(ValueError, match="matrix entries"):
        sparse_fixed_point_certified(SparseMatrix(("a",), (((1, 1.0),),), 1), [1.0], .5)


def test_scaling_reports_actual_admission_algorithm_and_configured_skip():
    from ocm.evaluation.scaling import run_size

    completed = run_size(8)
    assert completed["admission"]["wall_s"] is not None
    assert completed["admission"]["note"] == "exact positive matrix support (all sizes, KS-T05)"
    skipped = run_size(8, skip_admit_above=7)
    assert skipped["admission"]["wall_s"] is None
    assert skipped["admission"]["note"] == "SKIPPED: exceeds configured skip_admit_above"
