"""Non-compensatory resource vector (contract §19; M1 G).

Coordinates are never collapsed into one score inside the core; comparison is Pareto.  Every
reference mechanic reports a vector.  Parent: multi-objective dominance; ORION-V2
``component_value.CostVector`` (the same discipline with a tolerance).
"""
from __future__ import annotations

from dataclasses import dataclass, fields
from typing import Any

COORDINATES = (
    "object_count",
    "relation_count",
    "warrant_size",
    "index_size",
    "navigation_steps",
    "navigation_work",
    "composition_work",
    "memory_bytes",
    "io_calls",
    "verification_calls",
    "update_work",
)


@dataclass(frozen=True, slots=True)
class ResourceVector:
    object_count: int = 0
    relation_count: int = 0
    warrant_size: int = 0
    index_size: int = 0
    navigation_steps: int = 0
    navigation_work: int = 0
    composition_work: int = 0
    memory_bytes: int = 0
    io_calls: int = 0
    verification_calls: int = 0
    update_work: int = 0

    def __post_init__(self) -> None:
        for f in fields(self):
            if getattr(self, f.name) < 0:
                raise ValueError(f"resource coordinate must be non-negative: {f.name}")

    def __add__(self, other: "ResourceVector") -> "ResourceVector":
        return ResourceVector(**{f.name: getattr(self, f.name) + getattr(other, f.name) for f in fields(self)})

    def as_dict(self) -> dict[str, int]:
        return {f.name: getattr(self, f.name) for f in fields(self)}

    def no_worse_than(self, other: "ResourceVector") -> bool:
        return all(getattr(self, f.name) <= getattr(other, f.name) for f in fields(self))

    def dominates(self, other: "ResourceVector") -> bool:
        return self.no_worse_than(other) and self != other

    def incomparable_with(self, other: "ResourceVector") -> bool:
        return not self.no_worse_than(other) and not other.no_worse_than(self)


def mutant_scalar_collapse(v: ResourceVector, weights: dict[str, float] | None = None) -> float:
    """Wrong: collapsing the vector to one favourable scalar hides trades (contract §19)."""
    w = weights or {}
    return sum(w.get(k, 1.0) * x for k, x in v.as_dict().items())


@dataclass(slots=True)
class Meter:
    """Running resource ledger for a governed space (KS-S7: every mutation is metered)."""

    total: ResourceVector = ResourceVector()
    events: int = 0

    def charge(self, delta: ResourceVector) -> "Meter":
        if delta == ResourceVector():
            raise ValueError("unmetered mutation: a zero resource delta cannot be charged (KS-S7 / MEG-30)")
        self.total = self.total + delta
        self.events += 1
        return self

    def as_dict(self) -> dict[str, Any]:
        return {"total": self.total.as_dict(), "events": self.events}
