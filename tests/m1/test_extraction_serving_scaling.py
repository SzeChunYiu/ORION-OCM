"""Distractor-growth falsification, cold accounting, and genuinely global control."""
from fractions import Fraction as F

import pytest

from ocm.kso.extraction import reacting_subgraph_from_surprise
from ocm.kso.extraction_index import ExtractionIndex
from ocm.kso.extraction_indexed import (
    pcst_greedy_indexed, reacting_subgraph_from_support_indexed,
    reacting_subgraph_from_surprise_indexed,
)
from ocm.kso.space import Atom, Hyperedge, KnowledgeSpace


def _components(factor):
    atoms, edges = [], []
    for i in range(factor):
        prefix = "r" if i == 0 else f"noise:{i}"
        a, b, c = (f"{prefix}:{suffix}" for suffix in "abc")
        atoms.extend(Atom(x, "claim") for x in (a, b, c))
        edges.extend((Hyperedge(f"{prefix}:ab", (a,), (b,), "DEPENDENCE"),
                      Hyperedge(f"{prefix}:bc", (b,), (c,), "DEPENDENCE")))
    return KnowledgeSpace(tuple(atoms), tuple(edges))


def _local_counts(work):
    return {k: v for k, v in work.as_dict().items() if k not in ("total_objects", "total_relations")}


def test_1000x_disconnected_growth_keeps_warm_reaction_and_greedy_work_fixed():
    baseline = None
    for factor in (1, 10, 100, 1000):
        ks = _components(factor)
        index = ExtractionIndex(ks)
        assert index.build_work["edge_entries_scanned"] == 4 * factor
        assert index.build_work["incident_postings_built"] == 4 * factor
        assert index.build_work["outgoing_postings_built"] == 2 * factor
        assert index.build_work["atom_entries_built"] == 3 * factor
        reaction, rw = reacting_subgraph_from_support_indexed(
            ks, {"r:a": 1, "r:b": 1, "r:c": 1}, ("r:a",), index=index, with_work=True)
        greedy, gw = pcst_greedy_indexed(
            ks, {"r:a": F(0), "r:b": F(5), "r:c": F(5)}, ("r:a",),
            lam=F(0), mu=F(1), index=index, with_work=True)
        assert reaction.atoms == greedy.atoms == frozenset({"r:a", "r:b", "r:c"})
        assert rw.total_objects == gw.total_objects == 3 * factor
        assert rw.distinct_edges_examined == gw.distinct_edges_examined == 2
        measured = (_local_counts(rw), _local_counts(gw))
        if baseline is None:
            baseline = measured
        assert measured == baseline


def test_warm_queries_cannot_read_any_disconnected_atom_or_edge(monkeypatch):
    ks = _components(100)
    index = ExtractionIndex(ks)
    dense_seed = tuple(F(atom_id == "r:a") for atom_id in ks.ids)
    def atom_get(self, name):
        if not object.__getattribute__(self, "atom_id").startswith("r:"):
            raise AssertionError("disconnected atom read")
        return object.__getattribute__(self, name)
    def edge_get(self, name):
        if not object.__getattribute__(self, "edge_id").startswith("r:"):
            raise AssertionError("disconnected edge read")
        return object.__getattribute__(self, name)
    def forbidden(*args):
        raise AssertionError("detached map or full-field iterator")
    monkeypatch.setattr(Atom, "__getattribute__", atom_get)
    monkeypatch.setattr(Hyperedge, "__getattribute__", edge_get)
    monkeypatch.setattr(KnowledgeSpace, "atom_map", forbidden)
    monkeypatch.setattr(KnowledgeSpace, "edge_map", forbidden)
    reaction = reacting_subgraph_from_support_indexed(
        ks, {"r:a": 1, "r:b": 1, "r:c": 1}, ("r:a",), index=index)
    greedy = pcst_greedy_indexed(ks, {"r:a": F(0), "r:b": F(5), "r:c": F(5)},
                                ("r:a",), lam=F(0), mu=F(1), index=index)
    assert reaction.atoms == greedy.atoms == frozenset({"r:a", "r:b", "r:c"})
    # The same hostile must detect the incumbent whole-field liveness scan.
    with pytest.raises(AssertionError, match="disconnected atom read"):
        reacting_subgraph_from_surprise(ks, {"r:a": 1, "r:b": 1, "r:c": 1}, dense_seed)


def test_dense_adapter_reports_the_global_seed_scan():
    ks = _components(100)
    index = ExtractionIndex(ks)
    dense = tuple(F(atom_id == "r:a") for atom_id in ks.ids)
    sparse, sw = reacting_subgraph_from_support_indexed(
        ks, {"r:a": 1, "r:b": 1, "r:c": 1}, ("r:a",), index=index, with_work=True)
    result, dw = reacting_subgraph_from_surprise_indexed(
        ks, {"r:a": 1, "r:b": 1, "r:c": 1}, dense, index=index, with_work=True)
    assert result == sparse
    assert dw.dense_seed_entries_examined == dw.seed_entries_examined == 300
    assert sw.dense_seed_entries_examined == 0 and sw.seed_entries_examined == 1


def test_automatic_preparation_reports_cold_construction_once():
    ks = _components(10)
    for attempt in range(2):
        _, work = reacting_subgraph_from_support_indexed(
            ks, {"r:a": 1, "r:b": 1, "r:c": 1}, ("r:a",), with_work=True)
        assert work.cold_incident_index_build is (attempt == 0)
        assert work.cold_build_work["edge_entries_scanned"] == (40 if attempt == 0 else 0)
        assert work.cold_build_work["incident_postings_built"] == (40 if attempt == 0 else 0)
        assert work.cold_build_work["atom_entries_built"] == (30 if attempt == 0 else 0)


@pytest.mark.parametrize("size", (3, 30, 300))
def test_globally_connected_reaction_honestly_reports_global_work(size):
    ids = tuple(f"a{i}" for i in range(size))
    ks = KnowledgeSpace(tuple(Atom(x, "claim") for x in ids),
                        tuple(Hyperedge(f"e{i}", (ids[i],), (ids[i+1],), "DEPENDENCE")
                              for i in range(size - 1)))
    index = ExtractionIndex(ks)
    result, work = reacting_subgraph_from_support_indexed(
        ks, dict.fromkeys(ids, 1.0), (ids[0],), index=index, with_work=True)
    assert result.atoms == frozenset(ids)
    assert work.distinct_atoms_examined == size
    assert work.distinct_edges_examined == size - 1
    assert work.outgoing_postings_examined == size - 1
    assert work.incident_postings_examined == 2 * (size - 1)
