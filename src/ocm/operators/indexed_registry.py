"""Exact operator-catalogue discrimination index for issue #115 FK-4.

The production :class:`OperatorRegistry` remains the reference implementation.
This additive registry narrows the set of operators that need exact applicability
checks by indexing required input-atom identities.  Candidate generation is
structural only; final warrant and precondition checks are unchanged.

A retrieval/index miss is never an epistemic statement.  This index is exact for
the registered catalogue and does not use similarity or learned scores.
"""
from __future__ import annotations

from typing import Hashable, Iterable

from ocm.kso.space import KnowledgeSpace

from .registry import OperatorRegistry, OperatorSpec


class IndexedOperatorRegistry(OperatorRegistry):
    """OperatorRegistry with an exact inverted index over required input atoms."""

    def __init__(self, operators=None, certificates=None):
        super().__init__(
            operators={} if operators is None else dict(operators),
            certificates={} if certificates is None else {k: list(v) for k, v in certificates.items()},
        )
        self._by_input_atom: dict[str, set[str]] = {}
        self._zero_input: set[str] = set()
        self._rebuild_index()

    def _rebuild_index(self) -> None:
        self._by_input_atom.clear()
        self._zero_input.clear()
        for key, op in self.operators.items():
            required = frozenset(op.input_atoms)
            if not required:
                self._zero_input.add(key)
            for atom_id in required:
                self._by_input_atom.setdefault(atom_id, set()).add(key)

    def register(self, op: OperatorSpec) -> str:
        key = super().register(op)
        required = frozenset(op.input_atoms)
        if not required:
            self._zero_input.add(key)
        for atom_id in required:
            self._by_input_atom.setdefault(atom_id, set()).add(key)
        return key

    def candidate_keys(self, atoms: Iterable[str]) -> tuple[str, ...]:
        """Return every operator whose registered input identities are in ``atoms``.

        The result is an exact structural superset for applicability: warrant and
        precondition checks still run in :meth:`applicable`.
        """

        pool = frozenset(atoms)
        keys = set(self._zero_input)
        for atom_id in pool:
            keys.update(self._by_input_atom.get(atom_id, ()))
        return tuple(sorted(key for key in keys if set(self.operators[key].input_atoms) <= pool))

    def applicable(self, ks: KnowledgeSpace, atoms: Iterable[str], revoked: Iterable[Hashable] = ()) -> list[OperatorSpec]:
        rv = frozenset(revoked)
        amap = ks.atom_view
        out: list[OperatorSpec] = []
        for key in self.candidate_keys(atoms):
            op = self.operators[key]
            if not op.warrant.is_live(rv) or any(not amap[x].is_live(rv) for x in op.input_atoms):
                continue
            if any(p not in amap or not amap[p].is_live(rv) for p in op.preconditions):
                continue
            out.append(op)
        return sorted(out, key=lambda o: (o.operator_id, o.version))

    def index_stats(self) -> dict[str, int]:
        """Logical index counters; not a recursive-memory or performance claim."""

        return {
            "operators": len(self.operators),
            "input_keys": len(self._by_input_atom),
            "postings": sum(len(keys) for keys in self._by_input_atom.values()),
            "zero_input_operators": len(self._zero_input),
        }
