"""Observe added cache storage without charging shared entries twice."""
import sys

import pytest

from ocm.kso import space as S


def _space(with_evidence=True):
    warrant = S.WarrantProfile.of if with_evidence else lambda *args: S.WarrantProfile.one()
    return S.KnowledgeSpace(
        (S.Atom("a", "claim", warrant({"a-support"})),
         S.Atom("b", "claim", warrant({"b-support"}))),
        (S.Hyperedge("e", ("a",), ("b",), "SUPPORT",
                     warrant=warrant({"edge-support"})),),
    )


@pytest.mark.parametrize("cache,evidence", [
    ("atom_view", True), ("edge_view", True),
    ("evidence_universe", True), ("evidence_universe", False),
])
def test_materialized_cache_storage_counts_own_containers_once(cache, evidence):
    ks = _space(evidence)
    ks.atom_map()
    ks.edge_map()  # Existing index dictionaries already own and charge these entries.
    before = ks.index_resources()
    digest = ks.digest()
    value = ks.evidence_universe() if cache == "evidence_universe" else getattr(ks, cache)
    after = ks.index_resources()
    assert after.memory_bytes - before.memory_bytes == sys.getsizeof(value)
    # Proxy objects share dictionaries; only the evidence set owns new entry slots.
    assert after.index_size - before.index_size == (len(value) if cache == "evidence_universe" else 0)
    assert ks.index_resources() == after
    assert ks.digest() == digest


def test_observing_resources_does_not_materialize_optional_caches():
    ks = _space()
    keys = frozenset(ks.__dict__)
    before = ks.index_resources()
    assert frozenset(ks.__dict__) == keys
    assert ks.index_resources() == before
    assert frozenset(ks.__dict__) == keys
