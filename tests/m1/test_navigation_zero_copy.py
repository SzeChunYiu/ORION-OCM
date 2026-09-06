from __future__ import annotations

from fractions import Fraction

from ocm.kso.navigation import (
    NavigationBudget,
    NavigationOutcome,
    gated_closure,
    gated_seed,
    identification_witness,
    navigate,
    navigation_matrix,
    navigation_matrix_by_pruning,
)
from ocm.kso.space import Atom, Hyperedge, KnowledgeSpace
from ocm.kso.warrant import WarrantProfile


def _space() -> KnowledgeSpace:
    return KnowledgeSpace(
        (
            Atom("a", "claim"),
            Atom("b", "claim"),
            Atom("c", "claim", WarrantProfile.partial(())),
        ),
        (
            Hyperedge("e1", ("a",), ("b",), "DEPENDENCE"),
            Hyperedge("e2", ("b",), ("c",), "DEPENDENCE"),
        ),
    )


def _forbid_atom_map(monkeypatch) -> None:
    def forbidden_copy(_self):
        raise AssertionError("navigation read path must not materialize atom_map copies")

    monkeypatch.setattr(KnowledgeSpace, "atom_map", forbidden_copy)


def test_navigation_read_paths_use_cached_atom_view(monkeypatch) -> None:
    ks = _space()
    _forbid_atom_map(monkeypatch)

    matrix = navigation_matrix(ks)
    assert matrix == navigation_matrix_by_pruning(ks)
    assert matrix.rows == (
        (Fraction(0), Fraction(1), Fraction(0)),
        (Fraction(0), Fraction(0), Fraction(0)),
        (Fraction(0), Fraction(0), Fraction(0)),
    )

    seed = (Fraction(1), Fraction(0), Fraction(0))
    assert gated_seed(ks, seed, ()) == [Fraction(1), Fraction(0), Fraction(0)]
    assert gated_closure(ks, ("a",)) == frozenset({"a", "b"})

    result = navigate(
        ks,
        seed,
        "c",
        NavigationBudget(steps=2, restarts=1, depth=1),
    )
    assert result.outcome is NavigationOutcome.GAP_NOT_FOUND
    assert result.reason == "WARRANT_UNKNOWN_TARGET_CLOSURE_REACHABLE"


def test_identification_witness_uses_cached_atom_view(monkeypatch) -> None:
    ks = _space()
    _forbid_atom_map(monkeypatch)

    witness = identification_witness(
        ks,
        {"a": Fraction(1, 2), "b": Fraction(1, 2), "c": Fraction(0)},
        "a",
    )
    assert witness is not None
    assert witness.kind == "STRUCTURAL_NONIDENTIFIABILITY"
    assert witness.witness_atoms == ("a", "b")
