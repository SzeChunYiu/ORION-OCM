"""Exact calibration for morphology-selection non-identifiability.

The same semantic obligation can have different realization winners when
resource prices or physical response costs change.  A bounded morphogenetic
search can also miss the normative optimum.

These are ordinary decision/resource/search facts.  The module exists to stop
GMI from overclaiming an obligation-signature -> architecture map.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isclose
from typing import Dict, Iterable, Mapping, Sequence, Tuple


Vector = Tuple[float, ...]


@dataclass(frozen=True)
class Candidate:
    name: str
    semantically_admissible: bool
    raw_resources: Vector


def scalar_cost(resources: Vector, prices: Vector) -> float:
    if len(resources) != len(prices):
        raise ValueError("resource/pricing dimensions differ")
    if any(x < 0 for x in resources):
        raise ValueError("resource values must be non-negative")
    if any(w < 0 for w in prices):
        raise ValueError("prices must be non-negative")
    return sum(x * w for x, w in zip(resources, prices))


def winner(candidates: Iterable[Candidate], prices: Vector) -> Tuple[str, ...]:
    feasible = [c for c in candidates if c.semantically_admissible]
    if not feasible:
        return ()
    scored = [(scalar_cost(c.raw_resources, prices), c.name) for c in feasible]
    best = min(score for score, _ in scored)
    return tuple(sorted(name for score, name in scored if isclose(score, best)))


def hardware_response(
    base_candidates: Mapping[str, Candidate],
    multipliers: Mapping[str, Vector],
) -> Tuple[Candidate, ...]:
    out = []
    for name, candidate in base_candidates.items():
        if name not in multipliers:
            raise KeyError(f"missing hardware multiplier for {name}")
        mult = multipliers[name]
        if len(mult) != len(candidate.raw_resources):
            raise ValueError("hardware multiplier dimension mismatch")
        out.append(
            Candidate(
                name=name,
                semantically_admissible=candidate.semantically_admissible,
                raw_resources=tuple(x * m for x, m in zip(candidate.raw_resources, mult)),
            )
        )
    return tuple(out)


def bounded_search_winner(
    candidates: Mapping[str, Candidate],
    proposal_order: Sequence[str],
    budget: int,
    prices: Vector,
) -> Tuple[str, ...]:
    if budget < 0:
        raise ValueError("budget must be non-negative")
    seen = []
    for name in proposal_order[:budget]:
        if name not in candidates:
            raise KeyError(name)
        seen.append(candidates[name])
    return winner(seen, prices)


def calibration_receipt() -> dict:
    # Same obligation; A/B are both semantically exact but trade resources.
    base = {
        "A": Candidate("A", True, (2.0, 8.0)),
        "B": Candidate("B", True, (8.0, 2.0)),
        "CHEAP_WRONG": Candidate("CHEAP_WRONG", False, (0.0, 0.0)),
    }

    price_1 = (1.0, 0.1)
    price_2 = (0.1, 1.0)
    price_winner_1 = winner(base.values(), price_1)
    price_winner_2 = winner(base.values(), price_2)

    # Same price vector, but the physical response of A/B changes.
    uniform_price = (1.0, 1.0)
    hw1 = hardware_response(
        base,
        {
            "A": (0.5, 0.5),
            "B": (2.0, 2.0),
            "CHEAP_WRONG": (1.0, 1.0),
        },
    )
    hw2 = hardware_response(
        base,
        {
            "A": (2.0, 2.0),
            "B": (0.5, 0.5),
            "CHEAP_WRONG": (1.0, 1.0),
        },
    )
    hardware_winner_1 = winner(hw1, uniform_price)
    hardware_winner_2 = winner(hw2, uniform_price)

    # Normative optimum C exists but the bounded proposal order does not reach it.
    search_space = {
        "A": Candidate("A", True, (5.0,)),
        "B": Candidate("B", True, (3.0,)),
        "C": Candidate("C", True, (1.0,)),
    }
    normative = winner(search_space.values(), (1.0,))
    bounded = bounded_search_winner(
        search_space,
        proposal_order=("A", "B", "C"),
        budget=2,
        prices=(1.0,),
    )

    return {
        "schema": "GMIMorphologySelectionNoGoReceiptV1",
        "obligation_identity": "SAME_REGISTERED_SEMANTIC_OBLIGATION",
        "price_reversal": {
            "raw_candidates": {k: v.raw_resources for k, v in base.items()},
            "price_1": price_1,
            "winner_1": price_winner_1,
            "price_2": price_2,
            "winner_2": price_winner_2,
        },
        "hardware_reversal": {
            "price": uniform_price,
            "winner_hardware_1": hardware_winner_1,
            "winner_hardware_2": hardware_winner_2,
        },
        "bounded_discovery": {
            "normative_winner": normative,
            "proposal_order": ("A", "B", "C"),
            "budget": 2,
            "found_winner": bounded,
        },
        "terminal": "GMI_DEMAND_ONLY_MORPHOLOGY_SELECTION_NO_GO_GREEN_V1",
        "claim_boundary": (
            "Exact finite decision/resource/search calibration only; no new architecture-selection theorem."
        ),
    }


if __name__ == "__main__":
    import json

    print(json.dumps(calibration_receipt(), indent=2, sort_keys=True))
