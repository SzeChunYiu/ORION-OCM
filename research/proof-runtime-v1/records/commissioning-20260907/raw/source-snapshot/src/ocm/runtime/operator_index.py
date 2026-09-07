"""Exact candidate index for the operators consumed by runtime.solve.

This is a physical view of an immutable supplied catalogue, not another
operator authority or learned policy. Each operator is posted under its rarest
required input. Every structurally applicable operator must have that anchor
in the active set. Final warrant checks remain in compose_stage.
"""
from __future__ import annotations

from collections import Counter
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from types import MappingProxyType
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .solve import OperatorSpec


@dataclass(frozen=True, slots=True)
class OperatorSelection:
    operators: tuple[OperatorSpec, ...]
    work: Mapping[str, int]


class SolveOperatorIndex(Sequence):
    """Reusable, order-preserving view of frozen Solve OperatorSpec objects.

    Rebuild for a changed catalogue. Warrant revocation requires no rebuild:
    this view does not cache liveness, scope, checker output, or authority.
    Empty-input operators remain candidates and their cost is fully counted.
    """

    def __init__(self, operators: Iterable[OperatorSpec]):
        self._operators = tuple(operators)
        required = []
        for op in self._operators:
            if not isinstance(op.input_atoms, tuple) or any(not isinstance(x, str) for x in op.input_atoms):
                raise ValueError("IMMUTABLE_INPUT_CONTRACT_REQUIRED")
            required.append(frozenset(op.input_atoms))
        self._required = tuple(required)
        frequencies = Counter(atom for inputs in required for atom in inputs)
        postings: dict[str, list[int]] = {}
        zero = []
        for position, inputs in enumerate(required):
            if not inputs:
                zero.append(position)
                continue
            anchor = min(inputs, key=lambda atom: (frequencies[atom], atom))
            postings.setdefault(anchor, []).append(position)
        self._postings = MappingProxyType({atom: tuple(rows) for atom, rows in postings.items()})
        self._zero = tuple(zero)
        self._memberships = sum(len(inputs) for inputs in required)

    def __len__(self) -> int:
        return len(self._operators)

    def __getitem__(self, item):
        return self._operators[item]

    def __iter__(self):
        return iter(self._operators)

    @property
    def build_work(self) -> dict[str, int]:
        return {"catalogue_operators": len(self), "input_memberships": self._memberships,
                "anchor_postings": sum(len(rows) for rows in self._postings.values()),
                "zero_input_operators": len(self._zero)}

    def select(self, atoms: Iterable[str]) -> OperatorSelection:
        pool = frozenset(atoms)
        positions = list(self._zero)
        postings_examined = len(self._zero)
        for atom in pool:
            rows = self._postings.get(atom, ())
            postings_examined += len(rows)
            positions.extend(rows)
        # An operator has exactly one anchor, so positions cannot repeat.
        # Original supplied order is policy: solve selects the first pass.
        considered = sorted(positions)
        selected = tuple(self._operators[i] for i in considered if self._required[i] <= pool)
        return OperatorSelection(selected, MappingProxyType({
            "catalogue_operators": len(self), "index_probes": len(pool),
            "postings_examined": postings_examined, "operators_considered": len(considered),
            "structural_candidates": len(selected),
        }))
