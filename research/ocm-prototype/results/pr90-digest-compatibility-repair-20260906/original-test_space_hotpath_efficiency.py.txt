from __future__ import annotations

import pytest

from ocm.kso import space as S


def _space() -> S.KnowledgeSpace:
    atoms = (
        S.Atom("a", "claim"),
        S.Atom("b", "claim"),
    )
    edges = (S.Hyperedge("ab", ("a",), ("b",), "DEPENDENCE"),)
    return S.KnowledgeSpace(atoms, edges)


def test_digest_is_cached_per_immutable_space(monkeypatch):
    ks = _space()
    first = ks.digest()
    assert "_digest_value" in ks.__dict__

    def fail_if_reencoded(_value):
        raise AssertionError("cached immutable KSO digest was recomputed")

    monkeypatch.setattr(S, "canonical_json", fail_if_reencoded)
    assert ks.digest() == first


def test_evidence_universe_is_cached_per_immutable_space():
    ks = _space()
    first = ks.evidence_universe()
    second = ks.evidence_universe()
    assert first is second
    assert "_evidence_universe_value" in ks.__dict__


def test_atom_and_edge_views_are_read_only_and_zero_copy():
    ks = _space()
    assert ks.atom_view["a"] is ks.atom("a")
    assert ks.edge_view["ab"] is ks.hyperedges[0]
    with pytest.raises(TypeError):
        ks.atom_view["x"] = ks.atom("a")  # type: ignore[index]
    with pytest.raises(TypeError):
        ks.edge_view["x"] = ks.hyperedges[0]  # type: ignore[index]

    detached = ks.atom_map()
    detached.pop("a")
    assert "a" in ks.atom_view


def test_local_additions_skip_full_space_revalidation(monkeypatch):
    ks = _space()

    def fail_full_validation(_self):
        raise AssertionError("local persistent addition called full-space validate")

    monkeypatch.setattr(S.KnowledgeSpace, "validate", fail_full_validation)
    grown = ks.with_atoms(S.Atom("c", "claim"))
    grown = grown.with_edges(S.Hyperedge("bc", ("b",), ("c",), "DEPENDENCE"))
    assert grown.ids == ("a", "b", "c")
    assert grown.edge_view["bc"].heads == ("c",)


def test_local_additions_still_enforce_affected_invariants():
    ks = _space()
    with pytest.raises(ValueError, match="duplicate atom id"):
        ks.with_atoms(S.Atom("a", "claim"))
    with pytest.raises(ValueError, match="duplicate edge id"):
        ks.with_edges(S.Hyperedge("ab", ("a",), ("b",), "DEPENDENCE"))
    with pytest.raises(ValueError, match="references an unknown atom"):
        ks.with_edges(S.Hyperedge("missing", ("a",), ("nope",), "DEPENDENCE"))
