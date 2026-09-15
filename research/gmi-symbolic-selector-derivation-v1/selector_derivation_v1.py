#!/usr/bin/env python3
"""Exact B14 selector-family microscope for issue #602.

The candidate language contains only finite input subsets and primitive
emitters (constants or input projections).  Architecture/family names are not
part of the search.  All results use exhaustive integer enumeration.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from itertools import product
from typing import Callable, Iterable

Bit = int
Point = tuple[Bit, ...]
Emitter = tuple[str, Callable[[Point], Bit]]


@dataclass(frozen=True)
class Selector:
    family: str
    description: str
    mask: int
    description_atoms: int


@dataclass(frozen=True)
class Rule:
    selector: Selector
    emitter_name: str


def domain(arity: int) -> tuple[Point, ...]:
    return tuple(product((0, 1), repeat=arity))


def emitters(arity: int) -> tuple[Emitter, ...]:
    values: list[Emitter] = [("0", lambda _x: 0), ("1", lambda _x: 1)]
    for index in range(arity):
        values.append((f"x{index}", lambda x, index=index: x[index]))
    return tuple(values)


def _mask(points: tuple[Point, ...], predicate: Callable[[Point], bool]) -> int:
    return sum(1 << index for index, point in enumerate(points) if predicate(point))


def positional_selectors(arity: int) -> tuple[Selector, ...]:
    """Conjunctions of coordinate=value atoms; None is a wildcard."""
    points = domain(arity)
    selectors = []
    for pattern in product((0, 1, None), repeat=arity):
        mask = _mask(
            points,
            lambda point, pattern=pattern: all(
                atom is None or point[index] == atom
                for index, atom in enumerate(pattern)
            ),
        )
        selectors.append(
            Selector(
                "positional",
                " & ".join(
                    f"x{index}={atom}"
                    for index, atom in enumerate(pattern)
                    if atom is not None
                )
                or "TRUE",
                mask,
                sum(atom is not None for atom in pattern),
            )
        )
    return tuple(selectors)


def equality_selectors(arity: int) -> tuple[Selector, ...]:
    """Conjunctions of coordinate equality/inequality atoms.

    A relation value is None (unconstrained), 0 (=), or 1 (!=).  Unsatisfiable
    conjunctions are discarded, and duplicate semantic subsets retain their
    shortest descriptions.
    """
    points = domain(arity)
    pairs = tuple((left, right) for left in range(arity) for right in range(left + 1, arity))
    shortest: dict[int, Selector] = {}
    for relations in product((None, 0, 1), repeat=len(pairs)):
        mask = _mask(
            points,
            lambda point, relations=relations: all(
                relation is None
                or (point[left] != point[right]) == bool(relation)
                for relation, (left, right) in zip(relations, pairs)
            ),
        )
        if not mask:
            continue
        atoms = sum(relation is not None for relation in relations)
        description = " & ".join(
            f"x{left}{'!=' if relation else '='}x{right}"
            for relation, (left, right) in zip(relations, pairs)
            if relation is not None
        ) or "TRUE"
        candidate = Selector("equality", description, mask, atoms)
        previous = shortest.get(mask)
        if previous is None or (atoms, description) < (
            previous.description_atoms,
            previous.description,
        ):
            shortest[mask] = candidate
    return tuple(sorted(shortest.values(), key=lambda selector: selector.mask))


def arbitrary_subset_selectors(arity: int) -> tuple[Selector, ...]:
    """Every nonempty subset, charged as a full truth-table bit mask."""
    size = 1 << arity
    return tuple(
        Selector("arbitrary_subset", f"mask:{mask:0{size}b}", mask, size)
        for mask in range(1, 1 << size)
    )


def sound_rules(
    arity: int,
    target: Callable[[Point], Bit],
    selectors: Iterable[Selector],
) -> tuple[Rule, ...]:
    points = domain(arity)
    rules = []
    for selector in selectors:
        for emitter_name, emitter in emitters(arity):
            if all(
                not (selector.mask >> index) & 1 or emitter(point) == target(point)
                for index, point in enumerate(points)
            ):
                rules.append(Rule(selector, emitter_name))
    return tuple(rules)


def minimum_cover(
    arity: int,
    target: Callable[[Point], Bit],
    selectors: Iterable[Selector],
) -> tuple[tuple[int, int], tuple[Rule, ...]]:
    """Return lexicographic minimum (rule count, selector atoms/bits).

    Breadth-first dynamic programming visits every reachable coverage mask at
    each rule depth.  Within a depth it retains the least selector-description
    burden for that mask, so the returned pair is an exact finite certificate.
    """
    rules = sound_rules(arity, target, selectors)
    full = (1 << (1 << arity)) - 1
    queue = deque([(0, 0, tuple())])
    for depth in range(1, (1 << arity) + 1):
        next_by_mask: dict[int, tuple[int, tuple[Rule, ...]]] = {}
        while queue:
            current_mask, current_cost, chosen = queue.popleft()
            for rule in rules:
                new_mask = current_mask | rule.selector.mask
                if new_mask == current_mask:
                    continue
                new_cost = current_cost + rule.selector.description_atoms
                candidate = (new_cost, chosen + (rule,))
                previous = next_by_mask.get(new_mask)
                if previous is None or candidate[0] < previous[0]:
                    next_by_mask[new_mask] = candidate
        if full in next_by_mask:
            cost, chosen = next_by_mask[full]
            return (depth, cost), chosen
        queue.extend((mask, cost, chosen) for mask, (cost, chosen) in next_by_mask.items())
    raise ValueError("target is not expressible by this selector/emitter repertoire")


def xor_01(point: Point) -> Bit:
    return point[0] ^ point[1]


def mux_012(point: Point) -> Bit:
    """Use x1 when x0=1 and x2 when x0=0."""
    return point[1] if point[0] else point[2]


def truth_table(arity: int, target: Callable[[Point], Bit]) -> str:
    return "".join(str(target(point)) for point in domain(arity))


def evaluate() -> dict[str, object]:
    arity = 3
    families = {
        "positional": positional_selectors(arity),
        "equality": equality_selectors(arity),
        "arbitrary_subset": arbitrary_subset_selectors(arity),
    }
    obligations = {"xor_01": xor_01, "mux_012": mux_012}
    results: dict[str, object] = {}
    for obligation_name, target in obligations.items():
        family_results = {}
        for family_name, selectors in families.items():
            score, cover = minimum_cover(arity, target, selectors)
            family_results[family_name] = {
                "rules": score[0],
                "selector_description_atoms_or_bits": score[1],
                "cover": [
                    {
                        "selector": rule.selector.description,
                        "emitter": rule.emitter_name,
                    }
                    for rule in cover
                ],
            }
        results[obligation_name] = {
            "truth_table_lexicographic_000_to_111": truth_table(arity, target),
            "families": family_results,
        }
    return {
        "schema": "GMI_602_B14_SELECTOR_DERIVATION_V1",
        "scope": {"arity": arity, "domain_size": 1 << arity, "output": "one bit"},
        "selector_family_sizes": {name: len(selectors) for name, selectors in families.items()},
        "emitter_repertoire": [name for name, _emitter in emitters(arity)],
        "obligations": results,
    }


if __name__ == "__main__":
    import json

    print(json.dumps(evaluate(), indent=2, sort_keys=True))
