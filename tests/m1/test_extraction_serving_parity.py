"""Serving-path parity against the incumbent, including ordinary refusal cases."""
from dataclasses import replace
from fractions import Fraction as F
import random

import pytest

from ocm.kso.extraction import pcst_greedy, reacting_subgraph_from_surprise
from ocm.kso.extraction_index import ExtractionIndex
from ocm.kso.extraction_indexed import (
    pcst_greedy_indexed, reacting_subgraph_from_support_indexed,
    reacting_subgraph_from_surprise_indexed,
)
from ocm.kso.navigation import NavigationMode as Mode
from ocm.kso.space import Atom, Hyperedge, KnowledgeSpace
from ocm.kso.warrant import CannotCheck, WarrantProfile as WP


def test_randomized_hypergraph_reaction_and_greedy_match_incumbent():
    rng = random.Random(20260906)
    warrants = (WP.one(), WP.zero(), WP.partial(()), WP.of({"e0"}), WP.of({"e1"}, complete=False))
    for case in range(24):
        ids = tuple(f"a{i}" for i in range(6))
        ks = KnowledgeSpace(
            tuple(Atom(x, "claim", rng.choice(warrants)) for x in ids),
            tuple(Hyperedge(f"e{i}", tuple(rng.sample(ids, rng.randint(1, 3))),
                            tuple(rng.sample(ids, rng.randint(1, 2))), "DEPENDENCE",
                            warrant=rng.choice(warrants)) for i in range(8)))
        index = ExtractionIndex(ks)
        support = tuple(rng.sample(ids, rng.randint(0, 3)))
        seed = tuple(F(x in support) for x in ids)
        rho = {x: rng.choice((-1.0, 0.0, 1.0, 2.0)) for x in ids}
        prizes = {x: F(rng.randint(-2, 8), 2) for x in ids}
        edge_prizes = {e.edge_id: F(rng.randint(-2, 3)) for e in ks.hyperedges}
        for mode in Mode:
            for revoked in ((), ("e0", "e1")):
                kwargs = dict(mode=mode, revoked=revoked)
                expected = reacting_subgraph_from_surprise(ks, rho, seed, **kwargs)
                assert reacting_subgraph_from_support_indexed(ks, rho, support, index=index, **kwargs) == expected
                assert reacting_subgraph_from_surprise_indexed(ks, rho, seed, index=index, **kwargs) == expected
                args = dict(edge_prizes=edge_prizes, lam=F(2, 3), mu=F(1, 2),
                            cost=lambda atoms, edges: F(2 * len(atoms) + len(edges)))
                # Full dataclass parity includes approximation and candidates_considered.
                assert pcst_greedy_indexed(ks, prizes, support, index=index, **args, **kwargs) == pcst_greedy(
                    ks, prizes, support, **args, **kwargs), (case, mode, revoked)


def test_all_tail_closure_is_not_replaced_by_any_tail_reachability():
    ks = KnowledgeSpace(tuple(Atom(x, "claim") for x in ("a", "b", "c")),
                        (Hyperedge("joint", ("a", "b"), ("c",), "DEPENDENCE"),))
    index = ExtractionIndex(ks)
    rho = dict.fromkeys(ks.ids, 1.0)
    warranted = reacting_subgraph_from_support_indexed(ks, rho, ("a",), index=index)
    exploratory = reacting_subgraph_from_support_indexed(ks, rho, ("a",), index=index, mode=Mode.EXPLORATORY)
    enabled = reacting_subgraph_from_support_indexed(ks, rho, ("a", "b"), index=index)
    assert warranted.atoms == frozenset({"a"})
    assert exploratory.atoms == frozenset({"a", "c"})
    assert enabled.atoms == frozenset({"a", "b", "c"})
    assert warranted.edges == exploratory.edges == frozenset()
    assert enabled.edges == frozenset({"joint"})


def test_same_index_rechecks_revocation_and_unknown_warrant():
    ks = KnowledgeSpace((Atom("a", "claim"), Atom("b", "claim", WP.of({"e"}, complete=False))),
                        (Hyperedge("ab", ("a",), ("b",), "DEPENDENCE"),))
    index = ExtractionIndex(ks)
    for revoked, expected in [((), {"a", "b"}), (("e",), {"a"}), ((), {"a", "b"})]:
        result, work = reacting_subgraph_from_support_indexed(
            ks, {"a": 1.0, "b": 1.0}, ("a",), revoked=revoked, index=index, with_work=True)
        assert result.atoms == frozenset(expected)
        assert work.atom_warrant_checks == 2
        assert not work.cold_build_work


def test_index_rejects_a_replaced_snapshot_even_when_ids_match():
    ks = KnowledgeSpace((Atom("a", "claim"), Atom("b", "claim")), ())
    index = ExtractionIndex(ks)
    newer = replace(ks, hyperedges=(Hyperedge("ab", ("a",), ("b",), "DEPENDENCE"),))
    for changed in (replace(ks), newer):
        with pytest.raises(CannotCheck, match="EXTRACTION_INDEX_SNAPSHOT_MISMATCH"):
            reacting_subgraph_from_support_indexed(changed, {"a": 1, "b": 1}, ("a",), index=index)
        with pytest.raises(CannotCheck, match="EXTRACTION_INDEX_SNAPSHOT_MISMATCH"):
            pcst_greedy_indexed(changed, {"a": F(1)}, ("a",), index=index)
    with pytest.raises(TypeError):
        index.incident["a"] = ()


def test_dense_shape_and_sparse_unknown_id_are_not_silently_accepted():
    ks = KnowledgeSpace((Atom("a", "claim"),), ())
    for seed in ((), (F(1), F(0))):
        with pytest.raises(ValueError):
            reacting_subgraph_from_surprise_indexed(ks, {"a": 1}, seed)
    for mode in Mode:
        with pytest.raises(KeyError, match="absent"):
            reacting_subgraph_from_support_indexed(ks, {"a": 1}, ("absent",), mode=mode)
