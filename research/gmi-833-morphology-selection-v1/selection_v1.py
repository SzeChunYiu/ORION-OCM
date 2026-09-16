#!/usr/bin/env python3
"""Exact finite witnesses for #892 niche coexistence and resource repricing."""

from __future__ import annotations

from fractions import Fraction
from hashlib import sha1
from itertools import product
import json
from pathlib import Path
from typing import Hashable, Mapping, Sequence


HERE = Path(__file__).resolve().parent
CLAIM_CEILING = "GMI_833_FINITE_NICHE_AND_RESOURCE_REPRICING_LAWS_AT_REGISTERED_SCOPE"
FORBIDDEN_PROMOTIONS = (
    "PROSPECTIVE_20_TRANSITIONS",
    "INDEPENDENT_SEARCH_REPLICATION",
    "FIVE_REAL_SYSTEM_VALIDATIONS",
    "UNIVERSAL_SELECTION_LAW",
    "SEARCH_LAW_INVARIANCE",
    "UNCONDITIONAL_UNIQUE_MORPHOLOGY",
    "CONTINUOUS_OR_UNBOUNDED_SPACE_THEOREM",
    "COMPLETE_GMI",
)
PARENT_PINS = (
    (
        "foundation",
        "research/gmi-833-foundation-v1/RESULT_V1.json",
        "c0c574c4ec6e237d5fdafa694eac131399625a70",
        "terminal",
        "GMI_833_FOUNDATION_V1_FORMALIZED_AT_DECLARED_SCOPE",
    ),
    (
        "parent_equivalence",
        "research/gmi-833-parent-equivalence-v1/RESULT_V1.json",
        "7f6ee1c2d6e3e1bc24e66b192abffcc2d0a23ed3",
        "claim_ceiling",
        "GMI_PARENT_EQUIVALENCE_BOUNDARIES_AT_REGISTERED_FINITE_SCOPE",
    ),
    (
        "morphcap",
        "research/gmi-833-morphcap-v1/RESULT_V1.json",
        "bdc5c3cd42e312d8c7af52f7ba84220631a25f8a",
        "claim_ceiling",
        "GMI_MORPHOLOGY_AND_CAPABILITY_OBJECTS_AT_REGISTERED_FINITE_SCOPE",
    ),
    (
        "global_vs_reachable",
        "research/gmi-833-global-vs-reachable-morphology-v1/RESULT_V1.json",
        "37a0dda56649c02de1dd733b20a1266d481a3d30",
        "claim_ceiling",
        "GMI_FINITE_GLOBAL_VS_REACHABLE_MORPHOLOGY_SELECTION_SEPARATED_AT_REGISTERED_SCOPE",
    ),
    (
        "selection_phase_schema",
        "research/gmi-833-morphology-selection-schema-v1/RESULT_V1.json",
        "2adeddd201705e1583c2f4a858f679a3883a8227",
        "claim_ceiling",
        "GMI_FINITE_MORPHOLOGY_SELECTION_AND_AFFINE_PHASE_SCHEMA_AT_REGISTERED_SCOPE",
    ),
)


def exact(value: int | Fraction) -> Fraction:
    if isinstance(value, bool) or type(value) not in (int, Fraction):
        raise ValueError("registered numeric values must be exact integers or Fractions")
    return Fraction(value)


def repo_root(start: Path | None = None) -> Path:
    current = (start or HERE).resolve()
    while current.parent != current:
        if (current / ".git").exists() or (current / "research").is_dir():
            return current
        current = current.parent
    return HERE.parents[1]


def git_blob_sha(data: bytes) -> str:
    return sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def audit_parents(root: Path | None = None) -> dict[str, object]:
    root = root or repo_root()
    rows = []
    for name, path, expected_blob, field, expected_claim in PARENT_PINS:
        target = root / path
        if not target.is_file():
            rows.append({"name": name, "path": path, "actual_blob": None, "blob_ok": False, "claim_ok": False})
            continue
        data = target.read_bytes()
        parsed = json.loads(data)
        actual_blob = git_blob_sha(data)
        rows.append(
            {
                "name": name,
                "path": path,
                "actual_blob": actual_blob,
                "blob_ok": actual_blob == expected_blob,
                "claim_ok": parsed.get(field) == expected_claim,
            }
        )
    return {"rows": rows, "all_ok": all(row["blob_ok"] and row["claim_ok"] for row in rows)}


def maximizers(scores: Mapping[Hashable, int | Fraction]) -> tuple[Hashable, ...]:
    if not scores:
        raise ValueError("local score map must be nonempty")
    normalized = {item: exact(score) for item, score in scores.items()}
    best = max(normalized.values())
    return tuple(item for item, score in normalized.items() if score == best)


def niche_support(
    utilities: Mapping[Hashable, Mapping[Hashable, int | Fraction]],
    niche_mass: Mapping[Hashable, int | Fraction],
) -> frozenset[Hashable]:
    if not utilities or set(utilities) != set(niche_mass):
        raise ValueError("niche utilities and masses must share one nonempty niche carrier")
    candidate_sets = {frozenset(scores) for scores in utilities.values()}
    if len(candidate_sets) != 1 or not next(iter(candidate_sets)):
        raise ValueError("each niche must score the same nonempty morphology carrier")
    masses = {niche: exact(mass) for niche, mass in niche_mass.items()}
    if any(mass < 0 for mass in masses.values()) or sum(masses.values(), Fraction(0)) <= 0:
        raise ValueError("niche masses must be nonnegative with positive total mass")
    support: set[Hashable] = set()
    for niche, mass in masses.items():
        if mass > 0:
            support.update(maximizers(utilities[niche]))
    return frozenset(support)


def aggregate_scores(
    utilities: Mapping[Hashable, Mapping[Hashable, int | Fraction]],
    niche_mass: Mapping[Hashable, int | Fraction],
) -> dict[Hashable, Fraction]:
    # Validate the same domain/mass contract through niche_support first.
    niche_support(utilities, niche_mass)
    morphologies = tuple(next(iter(utilities.values())))
    masses = {niche: exact(mass) for niche, mass in niche_mass.items()}
    total = sum(masses.values(), Fraction(0))
    return {
        morphology: sum(
            (masses[niche] * exact(utilities[niche][morphology]) for niche in utilities),
            Fraction(0),
        ) / total
        for morphology in morphologies
    }


def repriced_scores(
    qualities: Mapping[Hashable, int | Fraction],
    resources: Mapping[Hashable, Sequence[int | Fraction]],
    prices: Sequence[int | Fraction],
) -> dict[Hashable, Fraction]:
    if not qualities or set(qualities) != set(resources) or not prices:
        raise ValueError("quality/resources must align with a nonempty price vector")
    normalized_prices = tuple(exact(price) for price in prices)
    if any(price < 0 for price in normalized_prices):
        raise ValueError("resource prices must be nonnegative")
    result = {}
    for item in qualities:
        vector = tuple(exact(value) for value in resources[item])
        if len(vector) != len(normalized_prices) or any(value < 0 for value in vector):
            raise ValueError("resource vectors must be aligned and nonnegative")
        result[item] = exact(qualities[item]) - sum(
            (price * value for price, value in zip(normalized_prices, vector, strict=True)),
            Fraction(0),
        )
    return result


def repricing_hyperplane(
    quality_left: int | Fraction,
    resources_left: Sequence[int | Fraction],
    quality_right: int | Fraction,
    resources_right: Sequence[int | Fraction],
) -> dict[str, object]:
    left = tuple(exact(value) for value in resources_left)
    right = tuple(exact(value) for value in resources_right)
    if not left or len(left) != len(right) or any(value < 0 for value in left + right):
        raise ValueError("paired raw resource vectors must align and be nonnegative")
    return {
        "quality_gap": exact(quality_left) - exact(quality_right),
        "resource_gap": tuple(x - y for x, y in zip(left, right, strict=True)),
    }


def pairwise_repriced_gap(
    quality_left: int | Fraction,
    resources_left: Sequence[int | Fraction],
    quality_right: int | Fraction,
    resources_right: Sequence[int | Fraction],
    prices: Sequence[int | Fraction],
) -> Fraction:
    scores = repriced_scores(
        {"left": quality_left, "right": quality_right},
        {"left": resources_left, "right": resources_right},
        prices,
    )
    return scores["left"] - scores["right"]


def one_dimensional_boundary(
    quality_left: int | Fraction,
    resource_left: int | Fraction,
    quality_right: int | Fraction,
    resource_right: int | Fraction,
) -> Fraction | str:
    quality_gap = exact(quality_left) - exact(quality_right)
    resource_gap = exact(resource_left) - exact(resource_right)
    if resource_gap == 0:
        return "TIED_EVERYWHERE" if quality_gap == 0 else "NO_CROSSING"
    return quality_gap / resource_gap


def dominance_no_flip(
    quality_left: int | Fraction,
    resources_left: Sequence[int | Fraction],
    quality_right: int | Fraction,
    resources_right: Sequence[int | Fraction],
    prices: Sequence[int | Fraction],
) -> bool:
    left = tuple(exact(value) for value in resources_left)
    right = tuple(exact(value) for value in resources_right)
    if len(left) != len(right):
        raise ValueError("dominance vectors must align")
    premise = exact(quality_left) >= exact(quality_right) and all(x <= y for x, y in zip(left, right, strict=True))
    if not premise:
        raise ValueError("dominance no-flip theorem requires its quality/resource premise")
    return pairwise_repriced_gap(quality_left, left, quality_right, right, prices) >= 0


def exhaustive_census() -> dict[str, int]:
    niche_cases = 0
    disjoint_unique_cases = 0
    for scores in product(range(3), repeat=4):
        utilities = {
            "left": {"A": scores[0], "B": scores[1]},
            "right": {"A": scores[2], "B": scores[3]},
        }
        for masses in ((1, 0), (0, 1), (1, 1)):
            observed = niche_support(utilities, {"left": masses[0], "right": masses[1]})
            expected: set[str] = set()
            for niche, mass in zip(("left", "right"), masses, strict=True):
                if mass:
                    expected.update(maximizers(utilities[niche]))
            if observed != frozenset(expected):
                raise ValueError("niche support census mismatch")
            if masses == (1, 1):
                left, right = maximizers(utilities["left"]), maximizers(utilities["right"])
                if len(left) == len(right) == 1 and left != right:
                    disjoint_unique_cases += 1
                    if observed != frozenset({left[0], right[0]}):
                        raise ValueError("disjoint unique niches failed to coexist")
            niche_cases += 1

    repricing_cases = 0
    dominance_cases = 0
    crossing_interval_cases = 0
    for ql, qr, rl, rr, price in product(range(4), repeat=5):
        gap = pairwise_repriced_gap(ql, (rl,), qr, (rr,), (price,))
        if gap != Fraction(ql - qr) - price * Fraction(rl - rr):
            raise ValueError("repricing identity failed")
        if ql >= qr and rl <= rr:
            dominance_cases += 1
            if not dominance_no_flip(ql, (rl,), qr, (rr,), (price,)):
                raise ValueError("dominance no-flip census failed")
        next_gap = pairwise_repriced_gap(ql, (rl,), qr, (rr,), (price + 1,))
        if gap * next_gap < 0:
            boundary = one_dimensional_boundary(ql, rl, qr, rr)
            if not isinstance(boundary, Fraction) or not Fraction(price) < boundary < Fraction(price + 1):
                raise ValueError("pair order changed outside its boundary")
            crossing_interval_cases += 1
        repricing_cases += 1
    return {
        "niche_allocation_cases": niche_cases,
        "disjoint_unique_coexistence_cases": disjoint_unique_cases,
        "repricing_cases": repricing_cases,
        "dominance_no_flip_cases": dominance_cases,
        "strict_crossing_interval_cases": crossing_interval_cases,
    }


def validate_ledgers() -> dict[str, object]:
    data = json.loads((HERE / "SCIENTIFIC_LEDGER_V1.json").read_text())
    required = {"id", "assumptions", "dependencies", "falsifiers", "strongest_parent", "counterexample_methods", "limits"}
    claims = data["claims"]
    if len(claims) != 3 or any(set(row) != required for row in claims):
        raise ValueError("scientific ledger schema/count drifted")
    if any(not row["assumptions"] or not row["falsifiers"] or not row["limits"] for row in claims):
        raise ValueError("scientific ledger is incomplete")
    gaps = data["open_gaps"]
    if len(gaps) != 1 or gaps[0]["status"] != "OPEN":
        raise ValueError("independent-review gap must remain open")
    return {"claim_ledgers": 3, "open_review_gaps": 1, "closure_level": "LOCALLY_CLOSED"}


def build_receipt(parent_audit: dict[str, object] | None = None) -> dict[str, object]:
    parent_audit = parent_audit or {"all_ok": True, "rows": []}
    utilities = {"left": {"A": 4, "B": 0}, "right": {"A": 0, "B": 4}}
    coexist = niche_support(utilities, {"left": 1, "right": 2})
    zero_mass = niche_support(utilities, {"left": 1, "right": 0})
    local_tie = niche_support({"one": {"A": 1, "B": 1}}, {"one": 1})
    aggregate = maximizers(aggregate_scores(utilities, {"left": 1, "right": 2}))
    cheap = maximizers(repriced_scores({"A": 5, "B": 4}, {"A": (3,), "B": (1,)}, (0,)))
    boundary = one_dimensional_boundary(5, 3, 4, 1)
    at_boundary = maximizers(
        repriced_scores({"A": 5, "B": 4}, {"A": (3,), "B": (1,)}, (boundary,))
    )
    expensive = maximizers(repriced_scores({"A": 5, "B": 4}, {"A": (3,), "B": (1,)}, (1,)))
    hyperplane = repricing_hyperplane(5, (3, 1), 4, (1, 2))
    census = exhaustive_census()
    ledgers = validate_ledgers()
    checks = {
        "parents_exactly_pinned": bool(parent_audit["all_ok"]),
        "positive_mass_niches_coexist": coexist == frozenset({"A", "B"}),
        "zero_mass_niche_excluded": zero_mass == frozenset({"A"}),
        "local_ties_preserved": local_tie == frozenset({"A", "B"}),
        "global_aggregation_is_distinct_problem": aggregate == ("B",) and coexist == frozenset({"A", "B"}),
        "repricing_transition_exact": (cheap, at_boundary, expensive) == (("A",), ("A", "B"), ("B",)),
        "repricing_hyperplane_exact": hyperplane == {"quality_gap": Fraction(1), "resource_gap": (Fraction(2), Fraction(-1))},
        "dominance_no_flip": dominance_no_flip(5, (1, 0), 4, (2, 0), (100, 3)),
        "bounded_censuses_complete": census == {
            "niche_allocation_cases": 243,
            "disjoint_unique_coexistence_cases": 18,
            "repricing_cases": 1024,
            "dominance_no_flip_cases": 400,
            "strict_crossing_interval_cases": 26,
        },
        "scientific_ledgers_complete": ledgers == {"claim_ledgers": 3, "open_review_gaps": 1, "closure_level": "LOCALLY_CLOSED"},
    }
    return {
        "schema": "GMI833NicheRepricingResultV1",
        "issue": 892,
        "parent_issue": 833,
        "claim_ceiling": CLAIM_CEILING,
        "forbidden_promotions": FORBIDDEN_PROMOTIONS,
        "parent_audit": parent_audit,
        "census": census,
        "witness": {
            "coexistence_support": tuple(sorted(coexist)),
            "zero_mass_support": tuple(sorted(zero_mass)),
            "local_tie_support": tuple(sorted(local_tie)),
            "aggregate_winners": aggregate,
            "repricing_winners": (cheap, at_boundary, expensive),
            "one_dimensional_boundary": boundary,
            "repricing_hyperplane": hyperplane,
        },
        "scientific_ledger": ledgers,
        "checks": checks,
        "verdict": "GREEN" if all(checks.values()) else "RED",
    }


def canonicalize(value):
    if isinstance(value, Fraction):
        return str(value)
    if isinstance(value, tuple):
        return [canonicalize(item) for item in value]
    if isinstance(value, frozenset):
        return [canonicalize(item) for item in sorted(value, key=repr)]
    if isinstance(value, list):
        return [canonicalize(item) for item in value]
    if isinstance(value, dict):
        return {str(key): canonicalize(item) for key, item in sorted(value.items(), key=lambda pair: repr(pair[0]))}
    return value


def canonical_json(value) -> str:
    return json.dumps(canonicalize(value), sort_keys=True, indent=2, ensure_ascii=False) + "\n"


if __name__ == "__main__":
    print(canonical_json(build_receipt(audit_parents())), end="")
