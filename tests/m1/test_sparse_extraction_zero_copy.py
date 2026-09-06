from __future__ import annotations

from fractions import Fraction as F

from ocm.kso.extraction import pcst_exact_bounded, pcst_greedy, reacting_subgraph_from_surprise
from ocm.kso.navigation import NavigationMode
from ocm.kso.navigation_sparse import sparse_activation, sparse_navigation_matrix
from ocm.kso.space import Atom, Hyperedge, KnowledgeSpace
from ocm.kso.warrant import WarrantProfile as WP


def _space() -> KnowledgeSpace:
    return KnowledgeSpace(
        (
            Atom("a", "claim"),
            Atom("b", "claim", WP.of({"ev:b"})),
            Atom("c", "claim"),
        ),
        (
            Hyperedge("ab", ("a",), ("b",), "DEPENDENCE"),
            Hyperedge("bc", ("b",), ("c",), "DEPENDENCE"),
        ),
    )


def test_sparse_navigation_read_paths_never_materialize_detached_atom_map(monkeypatch):
    ks = _space()

    def forbidden_copy(_self):
        raise AssertionError("sparse navigation read path must use atom_view")

    monkeypatch.setattr(KnowledgeSpace, "atom_map", forbidden_copy)

    matrix = sparse_navigation_matrix(ks)
    assert matrix.ids == ks.ids
    assert matrix.incidences == 2

    activation, iterations, incidences = sparse_activation(
        ks,
        (F(1), F(0), F(0)),
        0.5,
        tol=1e-9,
    )
    assert set(activation) == set(ks.ids)
    assert iterations >= 1
    assert incidences == 2


def test_extraction_read_paths_never_materialize_detached_atom_map(monkeypatch):
    ks = _space()

    def forbidden_copy(_self):
        raise AssertionError("extraction read path must use atom_view")

    monkeypatch.setattr(KnowledgeSpace, "atom_map", forbidden_copy)

    seed = (F(1), F(0), F(0))
    rho = {"a": 1.0, "b": 1.0, "c": 0.0}
    reacting = reacting_subgraph_from_surprise(ks, rho, seed)
    assert reacting.atoms == frozenset({"a", "b"})
    assert reacting.edges == frozenset({"ab"})

    prizes = {"a": F(0), "b": F(4), "c": F(1)}
    exact = pcst_exact_bounded(ks, prizes, ("a",), lam=F(0), mu=F(1), max_atoms=4)
    greedy = pcst_greedy(ks, prizes, ("a",), lam=F(0), mu=F(1))
    assert exact.atoms == frozenset({"a", "b"})
    assert greedy.atoms == exact.atoms


def test_zero_copy_change_preserves_revocation_gating(monkeypatch):
    ks = _space()

    def forbidden_copy(_self):
        raise AssertionError("read path must not fall back to atom_map")

    monkeypatch.setattr(KnowledgeSpace, "atom_map", forbidden_copy)

    revoked = frozenset({"ev:b"})
    matrix = sparse_navigation_matrix(ks, revoked=revoked, mode=NavigationMode.WARRANTED)
    assert matrix.incidences == 0

    seed = (F(1), F(0), F(0))
    rho = {"a": 1.0, "b": 1.0, "c": 1.0}
    reacting = reacting_subgraph_from_surprise(ks, rho, seed, revoked=revoked)
    assert reacting.atoms == frozenset({"a"})
    assert reacting.edges == frozenset()
