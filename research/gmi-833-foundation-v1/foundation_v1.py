#!/usr/bin/env python3
"""Exact helpers and executable hostiles for #833 foundation v1.

The deductive theorems live in FOUNDATION_THEOREMS_V1.md.  This module checks
finite consequences, schema contracts, prior classification, and Pareto laws.
It deliberately does not turn finite enumeration into a universal proof.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from itertools import permutations, product
import json
from pathlib import Path
from typing import Iterable, Mapping, Sequence

HERE = Path(__file__).resolve().parent

PRIOR_CATEGORIES = (
    "architectural",
    "representation",
    "operator",
    "search",
    "ecological",
    "evaluation",
)

PRIOR_LEVELS = ("P0", "P1", "P2", "P3", "P4")
MATURITY_LEVELS = tuple(f"M{i}" for i in range(7))
EVIDENCE_LEVELS = tuple(f"EV{i}" for i in range(6))
CLOSURE_STATES = (
    "OPEN",
    "LOCALLY_CLOSED",
    "HOSTILE_CLOSED",
    "REPLICATED_CLOSED",
    "REAL_SCALE_CLOSED",
)
SEVERITIES = ("CRITICAL", "HIGH", "MEDIUM", "LOW")


class FoundationError(ValueError):
    pass


def _fraction(value: int | Fraction) -> Fraction:
    if isinstance(value, bool):
        raise FoundationError("booleans are not numeric resource amounts")
    out = Fraction(value)
    return out


def validate_open_gap(gap: Mapping[str, object]) -> None:
    required = {
        "id",
        "claim_id",
        "premise",
        "inference",
        "unresolved_assumption",
        "possible_counterexample",
        "severity",
        "owner_role",
        "parent_result",
        "evidence_needed",
        "status",
        "materiality",
        "descendants",
    }
    missing = required - set(gap)
    if missing:
        raise FoundationError(f"OPEN_GAP missing fields: {sorted(missing)}")
    if gap["severity"] not in SEVERITIES:
        raise FoundationError("invalid OPEN_GAP severity")
    if gap["status"] not in CLOSURE_STATES:
        raise FoundationError("invalid OPEN_GAP status")
    if not isinstance(gap["descendants"], list):
        raise FoundationError("OPEN_GAP descendants must be a list")
    for key in required - {"descendants"}:
        if not isinstance(gap[key], str) or not gap[key].strip():
            raise FoundationError(f"OPEN_GAP field {key} must be a nonempty string")


def validate_prior_disclosure(record: Mapping[str, object]) -> None:
    required = {
        "claim_id",
        "declared_level",
        "named_architecture_visible",
        "family_property_vector_visible",
        "representation_operator_family_supplied",
        "generic_primitives_only",
        "recursive_primitive_invention",
        "priors",
        "encoding",
        "cost_model",
        "search_strategy",
        "ecology_generator",
        "evaluation_rule",
        "posthoc_family_mapping_only",
    }
    missing = required - set(record)
    if missing:
        raise FoundationError(f"prior disclosure missing fields: {sorted(missing)}")
    if record["declared_level"] not in PRIOR_LEVELS:
        raise FoundationError("unknown prior level")
    priors = record["priors"]
    if not isinstance(priors, Mapping):
        raise FoundationError("priors must be a mapping")
    if set(priors) != set(PRIOR_CATEGORIES):
        raise FoundationError("all six prior categories must be disclosed exactly")
    for category, items in priors.items():
        if not isinstance(items, list):
            raise FoundationError(f"prior category {category} must be a list")
        if any(not isinstance(item, str) or not item.strip() for item in items):
            raise FoundationError(f"prior category {category} contains an invalid item")
    for key in (
        "named_architecture_visible",
        "family_property_vector_visible",
        "representation_operator_family_supplied",
        "generic_primitives_only",
        "recursive_primitive_invention",
        "posthoc_family_mapping_only",
    ):
        if not isinstance(record[key], bool):
            raise FoundationError(f"{key} must be boolean")
    for key in ("encoding", "cost_model", "search_strategy", "ecology_generator", "evaluation_rule"):
        if not isinstance(record[key], str) or not record[key].strip():
            raise FoundationError(f"{key} must be disclosed")
    inferred = infer_prior_level(record)
    if inferred != record["declared_level"]:
        raise FoundationError(f"declared prior level {record['declared_level']} != inferred {inferred}")


def infer_prior_level(record: Mapping[str, object]) -> str:
    if record.get("named_architecture_visible"):
        return "P0"
    if record.get("family_property_vector_visible"):
        return "P1"
    if record.get("representation_operator_family_supplied"):
        return "P2"
    if record.get("generic_primitives_only"):
        if record.get("recursive_primitive_invention"):
            return "P4"
        return "P3"
    raise FoundationError("record does not satisfy any P0-P4 level")


def architecture_prior_free_relative(record: Mapping[str, object]) -> bool:
    """Return the #833 relative architecture-prior-free predicate.

    P3/P4 is necessary but not sufficient: family mapping must be post-hoc and
    all residual priors must be disclosed.  This predicate never means
    assumption-free or inductive-bias-free.
    """
    validate_prior_disclosure(record)
    return (
        record["declared_level"] in {"P3", "P4"}
        and bool(record["posthoc_family_mapping_only"])
        and not bool(record["named_architecture_visible"])
        and not bool(record["family_property_vector_visible"])
        and not bool(record["representation_operator_family_supplied"])
    )


def countable_equal_mass_witness(mass: int | Fraction) -> dict[str, object]:
    """Finite witness that equal mass cannot define a countable uniform prior.

    If c=0, the total mass is zero. If c>0, a finite prefix of sufficiently many
    atoms already has mass >1. Negative mass is invalid.  This is the executable
    witness for the analytic proof in PF-1.
    """
    c = _fraction(mass)
    if c < 0:
        raise FoundationError("probability mass cannot be negative")
    if c == 0:
        return {"possible": False, "reason": "equal_zero_mass_sums_to_zero"}
    n = int(Fraction(1, 1) // c) + 1
    while n * c <= 1:
        n += 1
    return {
        "possible": False,
        "reason": "finite_prefix_exceeds_one",
        "prefix_size": n,
        "prefix_mass": f"{(n*c).numerator}/{(n*c).denominator}",
    }


def common_fixed_points_under_all_renamings(n: int) -> tuple[int, ...]:
    """Points fixed by every permutation of an n-element hypothesis set."""
    if n < 1 or n > 8:
        raise FoundationError("finite renaming hostile supports 1 <= n <= 8")
    points = set(range(n))
    fixed = set(points)
    for perm in permutations(range(n)):
        fixed &= {i for i in points if perm[i] == i}
    return tuple(sorted(fixed))


def deterministic_prior_free_unique_selector_exists(n: int) -> bool:
    """Renaming-invariant unique selector on a fully symmetric finite set."""
    return bool(common_fixed_points_under_all_renamings(n))


def pareto_strictly_dominates(a: Sequence[int | Fraction], b: Sequence[int | Fraction]) -> bool:
    if len(a) != len(b) or not a:
        raise FoundationError("resource vectors must have equal nonzero dimension")
    aa = tuple(_fraction(v) for v in a)
    bb = tuple(_fraction(v) for v in b)
    if any(v < 0 for v in aa + bb):
        raise FoundationError("resource coordinates must be nonnegative")
    return all(x <= y for x, y in zip(aa, bb)) and any(x < y for x, y in zip(aa, bb))


def scalar_cost(vector: Sequence[int | Fraction], weights: Sequence[int | Fraction], *, strict_positive: bool = True) -> Fraction:
    if len(vector) != len(weights) or not vector:
        raise FoundationError("vector and weights must have equal nonzero dimension")
    vv = tuple(_fraction(v) for v in vector)
    ww = tuple(_fraction(w) for w in weights)
    if any(v < 0 for v in vv):
        raise FoundationError("resource coordinates must be nonnegative")
    if strict_positive:
        if any(w <= 0 for w in ww):
            raise FoundationError("registered scalarization requires strictly positive weights")
    elif any(w < 0 for w in ww):
        raise FoundationError("monotone scalarization requires nonnegative weights")
    return sum((v * w for v, w in zip(vv, ww)), Fraction(0))


def incomparable(a: Sequence[int | Fraction], b: Sequence[int | Fraction]) -> bool:
    return not pareto_strictly_dominates(a, b) and not pareto_strictly_dominates(b, a) and tuple(a) != tuple(b)


def reversal_weights(a: Sequence[int | Fraction], b: Sequence[int | Fraction]) -> tuple[tuple[Fraction, ...], tuple[Fraction, ...]]:
    """Construct strictly-positive weights ranking either side of an incomparable pair."""
    if len(a) != len(b) or not a:
        raise FoundationError("resource vectors must have equal nonzero dimension")
    aa = tuple(_fraction(v) for v in a)
    bb = tuple(_fraction(v) for v in b)
    d = tuple(y - x for x, y in zip(aa, bb))
    pos = [i for i, x in enumerate(d) if x > 0]
    neg = [i for i, x in enumerate(d) if x < 0]
    if not pos or not neg:
        raise FoundationError("pair is not Pareto-incomparable")

    def favor(sign_index: int, target_positive: bool) -> tuple[Fraction, ...]:
        weights = [Fraction(1) for _ in d]
        if target_positive:
            adverse = sum((-x for x in d if x < 0), Fraction(0))
            weights[sign_index] = adverse / d[sign_index] + 2
        else:
            adverse = sum((x for x in d if x > 0), Fraction(0))
            weights[sign_index] = adverse / (-d[sign_index]) + 2
        return tuple(weights)

    favor_a = favor(pos[0], True)
    favor_b = favor(neg[0], False)
    if not scalar_cost(aa, favor_a) < scalar_cost(bb, favor_a):
        raise AssertionError("failed to construct a-favoring positive weights")
    if not scalar_cost(bb, favor_b) < scalar_cost(aa, favor_b):
        raise AssertionError("failed to construct b-favoring positive weights")
    return favor_a, favor_b


@dataclass(frozen=True)
class BehavioralSpecification:
    instances: tuple[str, ...]
    acceptable_traces: Mapping[str, frozenset[str]]

    def __post_init__(self) -> None:
        if not self.instances:
            raise FoundationError("behavioral specification needs at least one instance")
        if set(self.instances) != set(self.acceptable_traces):
            raise FoundationError("acceptable traces must be defined for every and only registered instance")
        if any(not values for values in self.acceptable_traces.values()):
            raise FoundationError("every registered instance needs at least one acceptable trace")

    def accepts(self, instance: str, trace: str) -> bool:
        return trace in self.acceptable_traces[instance]


def legacy_obligation_to_behavioral_spec(
    instances: Iterable[str],
    legal_traces: Mapping[str, Iterable[str]],
    legacy_accepts,
) -> BehavioralSpecification:
    """Conservative semantics map Phi(Omega) for a registered obligation.

    `legacy_accepts(i, trace)` is the existing obligation acceptance predicate.
    The map adds no new acceptance semantics: it extensionalizes the same predicate.
    """
    inst = tuple(instances)
    acc: dict[str, frozenset[str]] = {}
    for i in inst:
        if i not in legal_traces:
            raise FoundationError(f"missing legal trace universe for {i}")
        accepted = frozenset(t for t in legal_traces[i] if legacy_accepts(i, t))
        if not accepted:
            raise FoundationError(f"legacy obligation has no acceptable legal trace for {i}")
        acc[i] = accepted
    return BehavioralSpecification(inst, acc)


def quotient_by_protected_responses(histories: Sequence[str], continuations: Sequence[str], response) -> tuple[tuple[str, ...], ...]:
    """Finite exact future-response quotient used only as an executable certificate."""
    if len(set(histories)) != len(histories):
        raise FoundationError("histories must be unique")
    signatures: dict[tuple[object, ...], list[str]] = {}
    for h in histories:
        sig = tuple(response(h, c) for c in continuations)
        signatures.setdefault(sig, []).append(h)
    blocks = [tuple(sorted(block)) for block in signatures.values()]
    return tuple(sorted(blocks))


def encoding_refines_response_quotient(histories: Sequence[str], continuations: Sequence[str], response, encoding) -> bool:
    by_code: dict[object, list[str]] = {}
    for h in histories:
        by_code.setdefault(encoding(h), []).append(h)
    for block in by_code.values():
        first = block[0]
        sig0 = tuple(response(first, c) for c in continuations)
        for h in block[1:]:
            if tuple(response(h, c) for c in continuations) != sig0:
                return False
    return True


def exhaustive_pareto_certificate() -> dict[str, int]:
    vectors = list(product(range(3), repeat=3))
    pairs = 0
    dominance = 0
    incomparable_count = 0
    reversals = 0
    positive_weights = (
        (Fraction(1), Fraction(1), Fraction(1)),
        (Fraction(100), Fraction(1), Fraction(1)),
        (Fraction(1), Fraction(100), Fraction(1)),
        (Fraction(1), Fraction(1), Fraction(100)),
    )
    for i, a in enumerate(vectors):
        for b in vectors[i + 1 :]:
            pairs += 1
            if pareto_strictly_dominates(a, b):
                dominance += 1
                if not all(scalar_cost(a, w) < scalar_cost(b, w) for w in positive_weights):
                    raise AssertionError("positive weights reversed Pareto dominance")
            elif pareto_strictly_dominates(b, a):
                dominance += 1
                if not all(scalar_cost(b, w) < scalar_cost(a, w) for w in positive_weights):
                    raise AssertionError("positive weights reversed Pareto dominance")
            elif a != b:
                incomparable_count += 1
                wa, wb = reversal_weights(a, b)
                if scalar_cost(a, wa) < scalar_cost(b, wa) and scalar_cost(b, wb) < scalar_cost(a, wb):
                    reversals += 1
    return {
        "vectors": len(vectors),
        "unordered_pairs": pairs,
        "dominance_pairs": dominance,
        "incomparable_pairs": incomparable_count,
        "incomparable_reversals_constructed": reversals,
    }


def build_receipt() -> dict[str, object]:
    pareto = exhaustive_pareto_certificate()
    fixed = {str(n): list(common_fixed_points_under_all_renamings(n)) for n in range(2, 7)}
    if any(fixed[str(n)] for n in range(2, 7)):
        raise AssertionError("a nontrivial symmetric hypothesis set unexpectedly has a universal fixed point")

    quotient = quotient_by_protected_responses(
        ("u0", "u1", "s", "l"),
        ("query", "teach_then_query"),
        lambda h, c: {
            ("u0", "query"): "0",
            ("u1", "query"): "0",
            ("s", "query"): "0",
            ("l", "query"): "1",
            ("u0", "teach_then_query"): "1",
            ("u1", "teach_then_query"): "1",
            ("s", "teach_then_query"): "0",
            ("l", "teach_then_query"): "1",
        }[(h, c)],
    )

    countable = [countable_equal_mass_witness(Fraction(0)), countable_equal_mass_witness(Fraction(1, 10))]
    return {
        "schema": "GMI_833_FOUNDATION_RECEIPT_V1",
        "terminal": "GMI_833_FOUNDATION_V1_FORMALIZED_AT_DECLARED_SCOPE",
        "prior_levels": list(PRIOR_LEVELS),
        "evidence_levels": list(EVIDENCE_LEVELS),
        "maturity_levels": list(MATURITY_LEVELS),
        "closure_states": list(CLOSURE_STATES),
        "renaming_fixed_points_n2_to_n6": fixed,
        "countable_uniform_prior_witnesses": countable,
        "protected_response_quotient": [list(block) for block in quotient],
        "pareto_certificate": pareto,
        "forbidden_promotions": [
            "COMPLETE_GMI",
            "ONTOLOGICAL_COMPLETENESS",
            "UNIVERSAL_ARCHITECTURE_PRIOR_FREEDOM",
            "ALL_EXISTING_RESULTS_AUDITED",
            "KNOWN_FAMILIES_DERIVED_AT_P3",
            "UNSEEN_FORMS_DISCOVERED",
            "REAL_SCALE_VALIDATION_COMPLETE",
        ],
    }


def main() -> None:
    print(json.dumps(build_receipt(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
