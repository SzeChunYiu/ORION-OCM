"""Exact finite calibration for GMI Semantic Proposal Geometry (SPG).

This module tests four semantics:

1. Push a native proposal distribution through a semantic candidate map.
2. Splitting a native candidate into implementation-distinct variants with the
   same semantic effect and preserved total mass leaves semantic mass unchanged.
3. Native proposal count/rank is not a semantic probability; deterministic
   first-hit burden must count actual work.
4. A K1-style history effect can be expressed architecture-neutrally as lower
   semantic surprisal and/or lower first-hit burden for a fresh target class.

All results are finite probability/search arithmetic.  No universal machine-
intelligence law is claimed.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from math import log2
from typing import Dict, Iterable, Mapping, Sequence, Tuple


@dataclass(frozen=True)
class NativeCandidate:
    name: str
    semantic_class: str
    mass: Fraction
    proposal_cost: Fraction = Fraction(1, 1)


@dataclass(frozen=True)
class FirstHit:
    found: bool
    native_rank: int | None
    cumulative_cost: Fraction
    native_candidate: str | None
    semantic_class: str | None


def _validate_candidates(candidates: Iterable[NativeCandidate]) -> Tuple[NativeCandidate, ...]:
    values = tuple(candidates)
    if not values:
        raise ValueError("candidate set must be nonempty")
    names = [c.name for c in values]
    if len(names) != len(set(names)):
        raise ValueError("native candidate names must be unique")
    if any(c.mass < 0 for c in values):
        raise ValueError("candidate mass must be non-negative")
    if any(c.proposal_cost < 0 for c in values):
        raise ValueError("proposal cost must be non-negative")
    total = sum((c.mass for c in values), Fraction(0, 1))
    if total != 1:
        raise ValueError(f"proposal mass must sum to one, got {total}")
    return values


def semantic_pushforward(candidates: Iterable[NativeCandidate]) -> Dict[str, Fraction]:
    values = _validate_candidates(candidates)
    out: Dict[str, Fraction] = {}
    for candidate in values:
        out[candidate.semantic_class] = out.get(candidate.semantic_class, Fraction(0, 1)) + candidate.mass
    assert sum(out.values(), Fraction(0, 1)) == 1
    return dict(sorted(out.items()))


def semantic_target_mass(candidates: Iterable[NativeCandidate], target_classes: Iterable[str]) -> Fraction:
    target = set(target_classes)
    if not target:
        raise ValueError("target class set must be nonempty")
    pushed = semantic_pushforward(candidates)
    return sum((mass for cls, mass in pushed.items() if cls in target), Fraction(0, 1))


def semantic_surprisal_bits(candidates: Iterable[NativeCandidate], target_classes: Iterable[str]) -> float:
    mass = semantic_target_mass(candidates, target_classes)
    if mass <= 0:
        return float("inf")
    return -log2(float(mass))


def first_hit(
    proposal_order: Sequence[NativeCandidate],
    target_classes: Iterable[str],
) -> FirstHit:
    target = set(target_classes)
    if not target:
        raise ValueError("target class set must be nonempty")
    # Here order is execution/search order, not a normalized proposal distribution.
    names = [candidate.name for candidate in proposal_order]
    if len(names) != len(set(names)):
        raise ValueError("ordered native candidates must have unique identities")
    cumulative = Fraction(0, 1)
    for rank, candidate in enumerate(proposal_order, start=1):
        if candidate.proposal_cost < 0:
            raise ValueError("proposal cost must be non-negative")
        cumulative += candidate.proposal_cost
        if candidate.semantic_class in target:
            return FirstHit(True, rank, cumulative, candidate.name, candidate.semantic_class)
    return FirstHit(False, None, cumulative, None, None)


def rank_information_shift(reset_rank: int, continued_rank: int) -> float:
    if reset_rank <= 0 or continued_rank <= 0:
        raise ValueError("ranks must be positive")
    return log2((reset_rank + 1) / (continued_rank + 1))


def split_candidate_preserving_mass(
    candidates: Sequence[NativeCandidate],
    name: str,
    parts: Sequence[Tuple[str, Fraction]],
) -> Tuple[NativeCandidate, ...]:
    if not parts:
        raise ValueError("split parts must be nonempty")
    source = next((candidate for candidate in candidates if candidate.name == name), None)
    if source is None:
        raise KeyError(name)
    part_mass = sum((mass for _, mass in parts), Fraction(0, 1))
    if part_mass != source.mass:
        raise ValueError("split must preserve source mass")
    if len({part_name for part_name, _ in parts}) != len(parts):
        raise ValueError("split part names must be unique")
    out = [candidate for candidate in candidates if candidate.name != name]
    out.extend(
        NativeCandidate(
            name=part_name,
            semantic_class=source.semantic_class,
            mass=mass,
            proposal_cost=source.proposal_cost,
        )
        for part_name, mass in parts
    )
    return tuple(out)


def calibration_receipt() -> dict:
    # Two native candidate spaces with different internal multiplicity but the
    # same semantic proposal geometry.
    coarse = (
        NativeCandidate("target_impl", "TARGET", Fraction(1, 4)),
        NativeCandidate("alt_impl", "ALTERNATIVE", Fraction(1, 4)),
        NativeCandidate("fail_impl", "FAIL", Fraction(1, 2)),
    )
    refined = split_candidate_preserving_mass(
        coarse,
        "target_impl",
        (
            ("target_variant_1", Fraction(1, 16)),
            ("target_variant_2", Fraction(3, 16)),
        ),
    )

    coarse_push = semantic_pushforward(coarse)
    refined_push = semantic_pushforward(refined)

    # A second morphology uses four native hypotheses but induces the same
    # TARGET semantic mass of 1/4.
    bayes_like = (
        NativeCandidate("h1", "TARGET", Fraction(1, 8)),
        NativeCandidate("h2", "TARGET", Fraction(1, 8)),
        NativeCandidate("h3", "ALTERNATIVE", Fraction(1, 4)),
        NativeCandidate("h4", "FAIL", Fraction(1, 2)),
    )

    # K1-style probabilistic improvement: TARGET mass doubles from 1/8 to 1/4.
    reset_prob = (
        NativeCandidate("r_target", "TARGET", Fraction(1, 8)),
        NativeCandidate("r_alt", "ALTERNATIVE", Fraction(3, 8)),
        NativeCandidate("r_fail", "FAIL", Fraction(1, 2)),
    )
    continued_prob = (
        NativeCandidate("c_target_a", "TARGET", Fraction(1, 16)),
        NativeCandidate("c_target_b", "TARGET", Fraction(3, 16)),
        NativeCandidate("c_alt", "ALTERNATIVE", Fraction(1, 4)),
        NativeCandidate("c_fail", "FAIL", Fraction(1, 2)),
    )

    reset_surprisal = semantic_surprisal_bits(reset_prob, {"TARGET"})
    continued_surprisal = semantic_surprisal_bits(continued_prob, {"TARGET"})

    # K1-style deterministic improvement: same semantic target first appears at
    # rank 7 in reset and rank 3 after history. Native masses are irrelevant to
    # this ordered-search fixture; proposal_cost records real work.
    reset_order = tuple(
        NativeCandidate(
            f"reset_{i}",
            "TARGET" if i == 7 else "DISTRACTOR",
            Fraction(1, 7),
            proposal_cost=Fraction(1, 1),
        )
        for i in range(1, 8)
    )
    continued_order = tuple(
        NativeCandidate(
            f"continued_{i}",
            "TARGET" if i == 3 else "DISTRACTOR",
            Fraction(1, 3),
            proposal_cost=Fraction(1, 1),
        )
        for i in range(1, 4)
    )
    reset_hit = first_hit(reset_order, {"TARGET"})
    continued_hit = first_hit(continued_order, {"TARGET"})

    # Native syntactic duplication before TARGET creates actual extra work even
    # if it is semantically redundant. SPG must not erase paid search work.
    duplicated_search = (
        NativeCandidate("dup_1", "DISTRACTOR", Fraction(1, 4), proposal_cost=Fraction(1, 1)),
        NativeCandidate("dup_2", "DISTRACTOR", Fraction(1, 4), proposal_cost=Fraction(1, 1)),
        NativeCandidate("target", "TARGET", Fraction(1, 2), proposal_cost=Fraction(1, 1)),
    )
    compact_search = (
        NativeCandidate("distractor", "DISTRACTOR", Fraction(1, 2), proposal_cost=Fraction(1, 1)),
        NativeCandidate("target", "TARGET", Fraction(1, 2), proposal_cost=Fraction(1, 1)),
    )
    duplicate_hit = first_hit(duplicated_search, {"TARGET"})
    compact_hit = first_hit(compact_search, {"TARGET"})

    return {
        "schema": "GMISemanticProposalGeometryExactReceiptV1",
        "pushforward_refinement": {
            "coarse_native_count": len(coarse),
            "refined_native_count": len(refined),
            "coarse_semantic_distribution": coarse_push,
            "refined_semantic_distribution": refined_push,
            "invariant": coarse_push == refined_push,
        },
        "cross_native_space_target_mass": {
            "coarse": semantic_target_mass(coarse, {"TARGET"}),
            "bayes_like": semantic_target_mass(bayes_like, {"TARGET"}),
        },
        "probabilistic_k1_calibration": {
            "reset_target_mass": semantic_target_mass(reset_prob, {"TARGET"}),
            "continued_target_mass": semantic_target_mass(continued_prob, {"TARGET"}),
            "reset_surprisal_bits": reset_surprisal,
            "continued_surprisal_bits": continued_surprisal,
            "surprisal_reduction_bits": reset_surprisal - continued_surprisal,
        },
        "deterministic_k1_calibration": {
            "reset_first_hit_rank": reset_hit.native_rank,
            "continued_first_hit_rank": continued_hit.native_rank,
            "reset_first_hit_cost": reset_hit.cumulative_cost,
            "continued_first_hit_cost": continued_hit.cumulative_cost,
            "rank_information_shift_bits": rank_information_shift(
                reset_hit.native_rank or 0,
                continued_hit.native_rank or 0,
            ),
        },
        "semantic_duplication_resource_hostile": {
            "compact_first_hit_rank": compact_hit.native_rank,
            "compact_first_hit_cost": compact_hit.cumulative_cost,
            "duplicated_first_hit_rank": duplicate_hit.native_rank,
            "duplicated_first_hit_cost": duplicate_hit.cumulative_cost,
            "interpretation": (
                "Semantic probability aggregation removes irrelevant native identity multiplicity, "
                "but deterministic duplicated proposals still consume real paid search work."
            ),
        },
        "terminal": "GMI_SEMANTIC_PROPOSAL_GEOMETRY_FINITE_EXACT_GREEN_V1",
        "claim_boundary": (
            "Finite probability/search calibration only. Pushforward/first-hit semantics are parent mathematics; "
            "real cross-paradigm developmental prediction remains empirical."
        ),
    }


def jsonable(value):
    if isinstance(value, Fraction):
        return {"numerator": value.numerator, "denominator": value.denominator}
    if isinstance(value, float):
        if value == float("inf"):
            return "inf"
        return value
    if isinstance(value, dict):
        return {str(k): jsonable(v) for k, v in value.items()}
    if isinstance(value, tuple):
        return [jsonable(v) for v in value]
    if isinstance(value, list):
        return [jsonable(v) for v in value]
    return value


if __name__ == "__main__":
    import json

    print(json.dumps(jsonable(calibration_receipt()), indent=2, sort_keys=True))
