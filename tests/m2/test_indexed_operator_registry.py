from __future__ import annotations

from ocm.kso.space import Atom, KnowledgeSpace
from ocm.kso.warrant import WarrantProfile as WP
from ocm.operators.indexed_registry import IndexedOperatorRegistry
from ocm.operators.registry import BackendKind, OperatorRegistry, OperatorSpec


def _ks() -> KnowledgeSpace:
    return KnowledgeSpace(
        (
            Atom("x", "claim", WP.of({1})),
            Atom("y", "claim", WP.of({2})),
            Atom("z", "claim", WP.of({3})),
        ),
        (),
    )


def _op(name: str, inputs=(), *, preconditions=(), warrant=None) -> OperatorSpec:
    return OperatorSpec(
        name,
        "1",
        BackendKind.PROGRAMMATIC,
        lambda ks, args: {},
        tuple(inputs),
        preconditions=tuple(preconditions),
        warrant=WP.one() if warrant is None else warrant,
    )


def _catalogue():
    ops = [
        _op("zero"),
        _op("x-only", ("x",)),
        _op("xy", ("x", "y")),
        _op("needs-z", ("x",), preconditions=("z",)),
        _op("dead-op", ("x",), warrant=WP.of({99})),
    ]
    ops.extend(_op(f"noise-{i}", (f"noise:{i}",)) for i in range(200))
    return ops


def _populate(registry):
    for op in _catalogue():
        registry.register(op)
    return registry


def test_indexed_registry_has_exact_full_scan_applicability_parity():
    ks = _ks()
    reference = _populate(OperatorRegistry())
    indexed = _populate(IndexedOperatorRegistry())

    cases = [
        ((), frozenset()),
        (("x",), frozenset()),
        (("x", "y"), frozenset()),
        (("x", "y", "z"), frozenset()),
        (("x", "y", "z"), frozenset({2})),
        (("x", "y", "z"), frozenset({99})),
    ]
    for pool, revoked in cases:
        expected = [op.operator_id for op in reference.applicable(ks, pool, revoked=revoked)]
        actual = [op.operator_id for op in indexed.applicable(ks, pool, revoked=revoked)]
        assert actual == expected


def test_candidate_index_prunes_irrelevant_catalogue_before_exact_checks():
    indexed = _populate(IndexedOperatorRegistry())
    keys = indexed.candidate_keys(("x", "y"))

    # zero, x-only, xy, needs-z and dead-op are the only structural candidates;
    # the 200 unrelated operators are never offered to exact applicability.
    assert len(keys) == 5
    assert len(keys) < len(indexed.operators) / 20
    stats = indexed.index_stats()
    assert stats["operators"] == 205
    assert stats["zero_input_operators"] == 1


def test_indexed_applicability_uses_read_only_atom_view(monkeypatch):
    indexed = _populate(IndexedOperatorRegistry())
    ks = _ks()

    def forbidden_copy(_self):
        raise AssertionError("indexed applicability must not materialize atom_map copies")

    monkeypatch.setattr(KnowledgeSpace, "atom_map", forbidden_copy)
    assert [op.operator_id for op in indexed.applicable(ks, ("x", "y"))] == [
        "dead-op",
        "needs-z",
        "x-only",
        "xy",
        "zero",
    ]


def test_index_rebuilds_from_prepopulated_catalogue():
    reference = _populate(OperatorRegistry())
    indexed = IndexedOperatorRegistry(reference.operators, reference.certificates)
    assert indexed.candidate_keys(("x", "y")) == (
        "dead-op@1",
        "needs-z@1",
        "x-only@1",
        "xy@1",
        "zero@1",
    )
