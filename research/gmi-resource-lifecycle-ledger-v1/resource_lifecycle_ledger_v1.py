#!/usr/bin/env python3
"""Exact, non-scalar GMI resource and lifecycle accounting primitives."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
from typing import Iterable, Mapping


HERE = Path(__file__).resolve().parent

COORDINATES = (
    "build_acquisition",
    "training_development",
    "serving_execution",
    "memory_storage",
    "retrieval_index",
    "verification",
    "update",
    "revision_unlearning",
    "communication",
    "precision",
    "search_discovery",
    "failed_candidates",
    "maintenance",
    "human_ai_design_input",
)

STAGES = ("BUILD", "DEVELOP", "SERVE", "REVISE", "MAINTAIN", "SEARCH")


def _fraction(value: int | Fraction) -> Fraction:
    if isinstance(value, bool):
        raise TypeError("booleans are not resource amounts")
    result = Fraction(value)
    if result < 0:
        raise ValueError("resource amounts must be nonnegative")
    return result


@dataclass(frozen=True)
class ResourceVector:
    values: tuple[Fraction, ...]

    def __post_init__(self) -> None:
        if len(self.values) != len(COORDINATES):
            raise ValueError("resource vector must expose every registered coordinate")
        object.__setattr__(self, "values", tuple(_fraction(v) for v in self.values))

    @classmethod
    def from_mapping(cls, values: Mapping[str, int | Fraction]) -> "ResourceVector":
        missing = set(COORDINATES) - set(values)
        extra = set(values) - set(COORDINATES)
        if missing or extra:
            raise ValueError(f"coordinate mismatch: missing={sorted(missing)}, extra={sorted(extra)}")
        return cls(tuple(_fraction(values[name]) for name in COORDINATES))

    @classmethod
    def zero(cls) -> "ResourceVector":
        return cls((Fraction(0),) * len(COORDINATES))

    def __add__(self, other: "ResourceVector") -> "ResourceVector":
        return ResourceVector(tuple(a + b for a, b in zip(self.values, other.values, strict=True)))

    def as_dict(self) -> dict[str, str]:
        return {name: str(value) for name, value in zip(COORDINATES, self.values, strict=True)}


@dataclass(frozen=True)
class LifecycleEvent:
    stage: str
    charges: ResourceVector
    evidence_id: str

    def __post_init__(self) -> None:
        if self.stage not in STAGES:
            raise ValueError("unregistered lifecycle stage")
        if not self.evidence_id:
            raise ValueError("every charge needs an evidence identifier")


def total(events: Iterable[LifecycleEvent]) -> ResourceVector:
    result = ResourceVector.zero()
    for event in events:
        result = result + event.charges
    return result


def totals_by_stage(events: Iterable[LifecycleEvent]) -> dict[str, ResourceVector]:
    result = {stage: ResourceVector.zero() for stage in STAGES}
    for event in events:
        result[event.stage] = result[event.stage] + event.charges
    return result


def dominates(left: ResourceVector, right: ResourceVector) -> bool:
    no_worse = all(a <= b for a, b in zip(left.values, right.values, strict=True))
    strictly_better = any(a < b for a, b in zip(left.values, right.values, strict=True))
    return no_worse and strictly_better


def pareto_frontier(rows: Mapping[str, ResourceVector]) -> tuple[str, ...]:
    return tuple(
        name
        for name, vector in rows.items()
        if not any(other != name and dominates(other_vector, vector) for other, other_vector in rows.items())
    )


@dataclass(frozen=True)
class FrozenPriceVector:
    prices: tuple[Fraction, ...]
    registration_id: str
    registered_before_outcomes: bool
    digest: str

    @classmethod
    def freeze(
        cls,
        prices: Mapping[str, int | Fraction],
        *,
        registration_id: str,
        registered_before_outcomes: bool,
    ) -> "FrozenPriceVector":
        if set(prices) != set(COORDINATES):
            raise ValueError("prices must cover the complete coordinate registry")
        ordered = tuple(_fraction(prices[name]) for name in COORDINATES)
        if any(value <= 0 for value in ordered):
            raise ValueError("registered prices must be strictly positive")
        return cls(
            ordered,
            registration_id,
            registered_before_outcomes,
            _price_digest(ordered, registration_id),
        )


def _price_digest(prices: tuple[Fraction, ...], registration_id: str) -> str:
    payload = json.dumps(
        {"coordinates": COORDINATES, "prices": [str(v) for v in prices], "registration_id": registration_id},
        separators=(",", ":"),
        sort_keys=True,
    )
    return sha256(payload.encode()).hexdigest()


def scalarize(vector: ResourceVector, prices: FrozenPriceVector) -> Fraction:
    if (
        not prices.registered_before_outcomes
        or not prices.registration_id
        or prices.digest != _price_digest(prices.prices, prices.registration_id)
    ):
        raise ValueError("post-outcome or unauditable scalarization forbidden")
    return sum((amount * price for amount, price in zip(vector.values, prices.prices, strict=True)), Fraction(0))


def exact_order_certificate() -> dict[str, int]:
    """Exhaust a three-coordinate embedding; the other coordinates are zero."""
    vectors = []
    for head in product(range(3), repeat=3):
        vectors.append(ResourceVector(tuple(map(Fraction, head)) + (Fraction(0),) * (len(COORDINATES) - 3)))
    pairs = 0
    dominance_pairs = 0
    reversible_incomparable_pairs = 0
    weight_choices = (
        (Fraction(100), Fraction(1), Fraction(1)),
        (Fraction(1), Fraction(100), Fraction(1)),
        (Fraction(1), Fraction(1), Fraction(100)),
    )
    for index, left in enumerate(vectors):
        for right in vectors[index + 1 :]:
            pairs += 1
            if dominates(left, right) or dominates(right, left):
                dominance_pairs += 1
                better, worse = (left, right) if dominates(left, right) else (right, left)
                for weights in weight_choices:
                    if sum(a * w for a, w in zip(better.values[:3], weights, strict=True)) >= sum(
                        b * w for b, w in zip(worse.values[:3], weights, strict=True)
                    ):
                        raise AssertionError("positive scalarization reversed Pareto dominance")
            else:
                signs = set()
                for weights in weight_choices:
                    delta = sum((a - b) * w for a, b, w in zip(left.values[:3], right.values[:3], weights, strict=True))
                    signs.add((delta > 0) - (delta < 0))
                if {-1, 1} <= signs:
                    reversible_incomparable_pairs += 1
    return {
        "vectors": len(vectors),
        "unordered_pairs": pairs,
        "dominance_pairs": dominance_pairs,
        "price_reversible_incomparable_pairs": reversible_incomparable_pairs,
    }


def validate_registry() -> dict[str, object]:
    ledger = json.loads((HERE / "RESOURCE_LIFECYCLE_LEDGER_V1.json").read_text(encoding="utf-8"))
    if tuple(row["id"] for row in ledger["coordinates"]) != COORDINATES:
        raise ValueError("coordinate registry drifted")
    if any(not {"unit", "boundary", "zero_policy", "evidence"} <= row.keys() for row in ledger["coordinates"]):
        raise ValueError("a coordinate lacks an operational contract")
    if len({row["id"] for row in ledger["coordinates"]}) != len(COORDINATES):
        raise ValueError("duplicate resource coordinate")
    certificate = exact_order_certificate()
    if certificate != {
        "vectors": 27,
        "unordered_pairs": 351,
        "dominance_pairs": 189,
        "price_reversible_incomparable_pairs": 162,
    }:
        raise ValueError("order certificate drifted")
    return {
        "coordinates": len(COORDINATES),
        "stages": len(STAGES),
        **certificate,
        "physical_metering": ledger["physical_metering"]["status"],
        "energy_metering": ledger["energy_metering"]["status"],
    }


if __name__ == "__main__":
    print("GMI_RESOURCE_LIFECYCLE_LEDGER_V1_VALID")
    print(json.dumps(validate_registry(), sort_keys=True))
