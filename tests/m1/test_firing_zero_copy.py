from __future__ import annotations

from fractions import Fraction

from ocm.kso.firing import Enabling, enabled_hyperedges, enabling_verdict
from ocm.kso.space import Atom, Hyperedge, KnowledgeSpace


def _space() -> KnowledgeSpace:
    return KnowledgeSpace(
        (Atom("a", "claim"), Atom("b", "claim"), Atom("c", "claim")),
        (
            Hyperedge("e1", ("a",), ("b",), "DEPENDENCE"),
            Hyperedge("e2", ("b",), ("c",), "DEPENDENCE"),
        ),
    )


def test_enabling_uses_read_only_atom_view_not_detached_copy(monkeypatch) -> None:
    ks = _space()

    def forbidden_copy(_self):
        raise AssertionError("firing hot path must not materialize atom_map copies")

    monkeypatch.setattr(KnowledgeSpace, "atom_map", forbidden_copy)
    verdict = enabling_verdict(
        ks,
        ks.edge_view["e1"],
        {"a": Fraction(1, 1)},
        Fraction(1, 1000),
    )
    assert verdict.enabling is Enabling.ENABLED


def test_enabled_hyperedges_keeps_exact_semantics_without_atom_map_copy(monkeypatch) -> None:
    ks = _space()

    def forbidden_copy(_self):
        raise AssertionError("one full atom-map copy per edge is forbidden")

    monkeypatch.setattr(KnowledgeSpace, "atom_map", forbidden_copy)
    enabled = enabled_hyperedges(
        ks,
        {"a": Fraction(1, 1), "b": Fraction(0, 1)},
        Fraction(1, 2),
    )
    assert enabled == ("e1",)
