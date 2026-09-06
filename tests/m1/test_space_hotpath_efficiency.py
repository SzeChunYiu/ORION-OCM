from __future__ import annotations

import hashlib
from dataclasses import replace

import pytest

from ocm.kso import space as S
from ocm.kso.types import TypeRegistry


def _space() -> S.KnowledgeSpace:
    atoms = (S.Atom("a", "claim"), S.Atom("b", "claim"))
    edges = (S.Hyperedge("ab", ("a",), ("b",), "DEPENDENCE"),)
    return S.KnowledgeSpace(atoms, edges, TypeRegistry())


def _fresh_digest(ks: S.KnowledgeSpace) -> str:
    body = {"atoms": [a.as_dict() for a in ks.atoms],
            "hyperedges": [e.as_dict() for e in ks.hyperedges]}
    return hashlib.sha256(S.canonical_json(body).encode("utf-8")).hexdigest()


def test_unchanged_digest_matches_current_canonical_content():
    ks = _space()
    assert ks.digest() == ks.digest() == _fresh_digest(ks)
    assert "_digest_value" not in ks.__dict__


@pytest.mark.parametrize("target", ["atom", "edge"])
@pytest.mark.parametrize("alias", ["original", "as_dict", "lookup_view"])
@pytest.mark.parametrize("mutation", ["append", "replace"])
def test_digest_tracks_nested_metadata_aliases(target, alias, mutation):
    payload = {"samples": [1, 2], "label": "before"}
    ks = _space()
    if target == "atom":
        item = replace(ks.atoms[0], meta=(("payload", payload),))
        ks = ks.replace_atom(item)
        view_item = ks.atom_view["a"]
    else:
        item = replace(ks.hyperedges[0], meta=(("payload", payload),))
        ks = replace(ks, hyperedges=(item,))
        view_item = ks.edge_view["ab"]
    before = ks.digest()
    assert before == _fresh_digest(ks)
    if alias == "original":
        exposed = payload
    elif alias == "as_dict":
        exposed = item.as_dict()["meta"]["payload"]
    else:
        exposed = dict(view_item.meta)["payload"]
    if mutation == "append":
        exposed["samples"].append(3)
    else:
        exposed["label"] = "after"
    expected = _fresh_digest(ks)
    assert expected != before  # The control must actually change canonical content.
    assert ks.digest() == expected
    assert ks.digest() == expected


def test_structural_successors_have_independent_digest_and_indexes():
    ks = _space()
    original = ks.digest()
    old_view = ks.atom_view
    grown = ks.with_atoms(S.Atom("c", "claim"))
    grown = grown.with_edges(S.Hyperedge("bc", ("b",), ("c",), "DEPENDENCE"))
    assert grown.digest() == _fresh_digest(grown) != original
    assert ks.digest() == original
    assert "c" not in old_view and "c" in grown.atom_view
    assert "bc" not in ks.edge_view and "bc" in grown.edge_view


def test_evidence_universe_is_cached_per_structural_space():
    ks = _space()
    first = ks.evidence_universe()
    assert first is ks.evidence_universe()
    assert "_evidence_universe_value" in ks.__dict__
    grown = ks.with_atoms(S.Atom("c", "claim"))
    assert "_evidence_universe_value" not in grown.__dict__


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
    detached_edges = ks.edge_map()
    detached_edges.clear()
    assert "ab" in ks.edge_view


@pytest.mark.parametrize("withdraw", ["atom_type", "relation_type"])
@pytest.mark.parametrize("edit", ["atom", "edge", "empty_atoms", "empty_edges"])
def test_additions_revalidate_existing_content_after_registry_change(withdraw, edit):
    ks = _space()
    if withdraw == "atom_type":
        ks.registry.atom_types.remove("claim")
        reason = "UNREGISTERED_ATOM_TYPE"
    else:
        del ks.registry.relation_types["DEPENDENCE"]
        reason = "UNREGISTERED_RELATION_TYPE"
    with pytest.raises(ValueError, match=reason):
        if edit == "atom":
            ks.with_atoms(S.Atom("c", "goal"))
        elif edit == "edge":
            ks.with_edges(S.Hyperedge("ba", ("b",), ("a",), "SUPPORT"))
        elif edit == "empty_atoms":
            ks.with_atoms()
        else:
            ks.with_edges()


def test_additions_still_enforce_affected_invariants():
    ks = _space()
    with pytest.raises(ValueError, match="duplicate atom id"):
        ks.with_atoms(S.Atom("a", "claim"))
    with pytest.raises(ValueError, match="duplicate edge id"):
        ks.with_edges(S.Hyperedge("ab", ("a",), ("b",), "DEPENDENCE"))
    with pytest.raises(ValueError, match="references an unknown atom"):
        ks.with_edges(S.Hyperedge("missing", ("a",), ("nope",), "DEPENDENCE"))
