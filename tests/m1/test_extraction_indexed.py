from __future__ import annotations

from fractions import Fraction as F

import pytest

from ocm.kso.extraction import pcst_greedy, reacting_subgraph_from_surprise
from ocm.kso.extraction_indexed import pcst_greedy_indexed, reacting_subgraph_from_surprise_indexed
from ocm.kso.navigation import NavigationMode
from ocm.kso.space import Atom, Hyperedge, KnowledgeSpace
from ocm.kso.warrant import WarrantProfile as WP


def _space() -> KnowledgeSpace:
    atoms = [
        Atom("a", "claim"),
        Atom("b", "claim"),
        Atom("c", "claim", WP.of({"ev:c"})),
        Atom("d", "claim"),
    ]
    edges = [
        Hyperedge("ab", ("a",), ("b",), "DEPENDENCE"),
        Hyperedge("bc", ("b",), ("c",), "DEPENDENCE"),
        Hyperedge("bd", ("b",), ("d",), "DEPENDENCE"),
    ]
    for i in range(50):
        left, right = f"n{i}:a", f"n{i}:b"
        atoms.extend((Atom(left, "claim"), Atom(right, "claim")))
        edges.append(Hyperedge(f"noise:{i}", (left,), (right,), "DEPENDENCE"))
    return KnowledgeSpace(tuple(atoms), tuple(edges))


@pytest.mark.parametrize("mode", [NavigationMode.WARRANTED, NavigationMode.EXPLORATORY])
@pytest.mark.parametrize("revoked", [frozenset(), frozenset({"ev:c"})])
def test_indexed_greedy_extraction_matches_full_scan_reference(mode, revoked):
    ks = _space()
    prizes = {"a": F(0), "b": F(5), "c": F(5), "d": F(1)}
    expected = pcst_greedy(ks, prizes, ("a",), revoked=revoked, mode=mode, lam=F(0), mu=F(1))
    actual = pcst_greedy_indexed(ks, prizes, ("a",), revoked=revoked, mode=mode, lam=F(0), mu=F(1))
    assert actual == expected


def test_warm_indexed_extraction_does_not_touch_disconnected_distractor_edges():
    ks = _space()
    # Make the global adjacency-build cost explicit before measuring warm local work.
    assert ks.incident_edges("a")
    prizes = {"a": F(0), "b": F(5), "c": F(5), "d": F(1)}

    result, work = pcst_greedy_indexed(ks, prizes, ("a",), lam=F(0), mu=F(1), with_work=True)

    assert result.atoms == frozenset({"a", "b", "c"})
    assert work.cold_incident_index_build is False
    assert work.distinct_edges_examined <= 3
    assert work.distinct_edges_examined < len(ks.hyperedges) / 10


def test_cold_index_build_is_reported_instead_of_hidden():
    ks = _space()
    prizes = {"a": F(0), "b": F(5), "c": F(5), "d": F(1)}
    _, work = pcst_greedy_indexed(ks, prizes, ("a",), lam=F(0), mu=F(1), with_work=True)
    assert work.cold_incident_index_build is True


def test_indexed_reacting_subgraph_matches_reference():
    ks = _space()
    seed = tuple(F(1) if atom_id == "a" else F(0) for atom_id in ks.ids)
    rho = {atom_id: 1.0 if atom_id in {"a", "b", "c"} else 0.0 for atom_id in ks.ids}

    for mode in (NavigationMode.WARRANTED, NavigationMode.EXPLORATORY):
        for revoked in (frozenset(), frozenset({"ev:c"})):
            expected = reacting_subgraph_from_surprise(ks, rho, seed, revoked=revoked, mode=mode)
            actual = reacting_subgraph_from_surprise_indexed(ks, rho, seed, revoked=revoked, mode=mode)
            assert actual == expected
