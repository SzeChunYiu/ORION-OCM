#!/usr/bin/env python3
"""Exact capability-query identification and abstention witnesses for #913."""

from __future__ import annotations

from fractions import Fraction
from hashlib import sha1
from itertools import product
import json
from pathlib import Path
from typing import Hashable, Iterable, Mapping


HERE = Path(__file__).resolve().parent
CLAIM_CEILING = "GMI_833_CAPABILITY_IDENTIFICATION_ABSTENTION_AT_REGISTERED_FINITE_SCOPE"
FORBIDDEN_PROMOTIONS = (
    "CAPABILITY_PREDICTOR_COMPLETED",
    "CALIBRATION_FROM_FEASIBILITY_ALONE",
    "REAL_SYSTEM_CAPABILITY_VALIDATION",
    "FULL_MODEL_IDENTITY_REQUIRED_FOR_EVERY_QUERY",
    "UNIVERSAL_CAPABILITY_IDENTIFICATION",
    "COMPLETE_GMI",
)
PARENT_PINS = (
    ("foundation", "research/gmi-833-foundation-v1/RESULT_V1.json", "c0c574c4ec6e237d5fdafa694eac131399625a70", "terminal", "GMI_833_FOUNDATION_V1_FORMALIZED_AT_DECLARED_SCOPE"),
    ("morphcap", "research/gmi-833-morphcap-v1/RESULT_V1.json", "bdc5c3cd42e312d8c7af52f7ba84220631a25f8a", "claim_ceiling", "GMI_MORPHOLOGY_AND_CAPABILITY_OBJECTS_AT_REGISTERED_FINITE_SCOPE"),
    ("global_uncertainty", "research/gmi-833-global-uncertainty-v1/RESULT_V1.json", "9ab16cf59087214e093ace3b18c6d08fc79ab871", "claim_ceiling", "GMI_GLOBAL_UNCERTAINTY_AND_ABSTENTION_CONTRACT_AT_REGISTERED_FINITE_SCOPE"),
    ("axiom_core", "research/gmi-833-axiom-core-v1/RESULT_V1.json", "3366a3bc7236d286f8d123bf53e4e3b2d22ad7b9", "claim_ceiling", "GMI_REGISTERED_FINITE_AXIOM_CORE_SATISFIABLE_AND_COMPACT_AT_SCOPE"),
    ("capability_bounds", "research/gmi-833-capability-bounds-interactions-v1/RESULT_V1.json", "7ff80bab4a0b9e967e02cc6943bbe8828e3acea0", "claim_ceiling", "GMI_833_FINITE_CAPABILITY_BOUNDS_SYNERGY_AND_INTERFERENCE_AT_REGISTERED_SCOPE"),
)


def exact(value: int | Fraction) -> Fraction:
    if isinstance(value, bool) or type(value) not in (int, Fraction):
        raise ValueError("capability scores and confidence budgets must be exact integers or Fractions")
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
        actual_blob = git_blob_sha(data)
        try:
            claim_ok = json.loads(data).get(field) == expected_claim
        except (UnicodeDecodeError, json.JSONDecodeError):
            claim_ok = False
        rows.append({"name": name, "path": path, "actual_blob": actual_blob, "blob_ok": actual_blob == expected_blob, "claim_ok": claim_ok})
    return {"rows": rows, "all_ok": all(row["blob_ok"] and row["claim_ok"] for row in rows)}


def capability_query_disposition(
    domain: Iterable[Hashable],
    survivors: Iterable[Hashable],
    query: Mapping[Hashable, int | Fraction] | None,
    *,
    uncertainty_kind: str = "FEASIBLE_SET",
    alpha: int | Fraction | None = None,
) -> dict[str, object]:
    carrier = tuple(domain)
    if not carrier or len(set(carrier)) != len(carrier):
        raise ValueError("candidate domain must be finite, nonempty, and duplicate-free")
    carrier_set = set(carrier)
    survivor_set = set(survivors)
    if not survivor_set.issubset(carrier_set):
        raise ValueError("survivors must be a subset of the registered domain")
    if uncertainty_kind not in {"FEASIBLE_SET", "CONFIDENCE_SET"}:
        raise ValueError("uncertainty kind must be FEASIBLE_SET or CONFIDENCE_SET")
    failure_budget = None
    coverage_lower_bound = None
    if uncertainty_kind == "CONFIDENCE_SET":
        if alpha is None:
            raise ValueError("confidence set requires an exact failure budget")
        failure_budget = exact(alpha)
        if failure_budget < 0 or failure_budget > 1:
            raise ValueError("confidence failure budget must lie in [0,1]")
        coverage_lower_bound = 1 - failure_budget
    elif alpha is not None:
        raise ValueError("bare feasible set cannot carry a fabricated confidence budget")

    common = {
        "uncertainty_kind": uncertainty_kind,
        "failure_budget": failure_budget,
        "coverage_lower_bound": coverage_lower_bound,
    }
    if not survivor_set:
        return {
            **common,
            "status": "INCONSISTENT_REGISTERED_ASSUMPTIONS",
            "identified_set": (),
            "point_prediction": None,
        }
    if query is None:
        return {
            **common,
            "status": "CANNOT_CHECK_QUERY_NOT_REGISTERED",
            "identified_set": None,
            "point_prediction": None,
        }
    if set(query) != carrier_set:
        return {
            **common,
            "status": "CANNOT_CHECK_QUERY_NOT_TOTAL_ON_DOMAIN",
            "identified_set": None,
            "point_prediction": None,
        }
    normalized_query = {candidate: exact(query[candidate]) for candidate in carrier}
    image = tuple(sorted({normalized_query[candidate] for candidate in survivor_set}))
    if len(image) == 1:
        return {
            **common,
            "status": "IDENTIFIED",
            "identified_set": image,
            "point_prediction": image[0],
        }
    return {
        **common,
        "status": "CANNOT_IDENTIFY",
        "identified_set": image,
        "point_prediction": None,
    }


def forced_point_counterexample(
    survivors: Iterable[Hashable],
    query: Mapping[Hashable, int | Fraction],
    chosen: int | Fraction,
) -> dict[str, object]:
    survivor_set = set(survivors)
    if not survivor_set or not survivor_set.issubset(query):
        raise ValueError("forced-point theorem requires nonempty registered survivors")
    normalized = {candidate: exact(query[candidate]) for candidate in survivor_set}
    image = set(normalized.values())
    point = exact(chosen)
    if len(image) < 2 or point not in image:
        raise ValueError("counterexample theorem requires a chosen member of a non-singleton image")
    witness = next(candidate for candidate in survivor_set if normalized[candidate] != point)
    return {
        "chosen_point": point,
        "counterexample_candidate": witness,
        "counterexample_value": normalized[witness],
        "uniformly_sound": False,
    }


def exhaustive_census() -> dict[str, int]:
    domain = ("a", "b", "c")
    subsets = [set(item for index, item in enumerate(domain) if mask & (1 << index)) for mask in range(8)]
    queries = [dict(zip(domain, values, strict=True)) for values in product((0, 1), repeat=3)]
    feasible_cases = 0
    confidence_cases = 0
    forced_counterexamples = 0
    for survivors in subsets:
        for query in queries:
            result = capability_query_disposition(domain, survivors, query)
            expected_image = tuple(sorted({Fraction(query[item]) for item in survivors}))
            if not survivors:
                if result["status"] != "INCONSISTENT_REGISTERED_ASSUMPTIONS":
                    raise ValueError("empty survivor set was not typed inconsistent")
            elif len(expected_image) == 1:
                if result["status"] != "IDENTIFIED" or result["point_prediction"] != expected_image[0]:
                    raise ValueError("singleton capability image was not identified")
            elif result["status"] != "CANNOT_IDENTIFY" or result["identified_set"] != expected_image or result["point_prediction"] is not None:
                raise ValueError("non-singleton capability image did not abstain exactly")
            if result["identified_set"] not in (None, expected_image):
                raise ValueError("identified set was incomplete")
            if len(expected_image) > 1:
                for chosen in expected_image:
                    if forced_point_counterexample(survivors, query, chosen)["uniformly_sound"]:
                        raise ValueError("forced point was incorrectly certified")
                    forced_counterexamples += 1
            feasible_cases += 1
            for alpha in (Fraction(0), Fraction(1, 4), Fraction(1)):
                confidence = capability_query_disposition(
                    domain, survivors, query, uncertainty_kind="CONFIDENCE_SET", alpha=alpha
                )
                if confidence["coverage_lower_bound"] != 1 - alpha or confidence["failure_budget"] != alpha:
                    raise ValueError("confidence budget was not transported exactly")
                if confidence["status"] != result["status"] or confidence["identified_set"] != result["identified_set"]:
                    raise ValueError("confidence typing changed exact identification")
                confidence_cases += 1
    missing_query_cases = 0
    for survivors in subsets:
        result = capability_query_disposition(domain, survivors, None)
        expected = "INCONSISTENT_REGISTERED_ASSUMPTIONS" if not survivors else "CANNOT_CHECK_QUERY_NOT_REGISTERED"
        if result["status"] != expected:
            raise ValueError("missing-query terminal mismatch")
        missing_query_cases += 1
    return {
        "feasible_query_cases": feasible_cases,
        "confidence_query_cases": confidence_cases,
        "forced_point_counterexamples": forced_counterexamples,
        "missing_query_cases": missing_query_cases,
    }


def validate_ledgers() -> dict[str, object]:
    data = json.loads((HERE / "SCIENTIFIC_LEDGER_V1.json").read_text())
    required = {"id", "assumptions", "dependencies", "falsifiers", "strongest_parent", "counterexample_methods", "limits"}
    claims = data["claims"]
    if len(claims) != 2 or any(set(row) != required for row in claims):
        raise ValueError("scientific ledger schema/count drifted")
    if any(not row["assumptions"] or not row["falsifiers"] or not row["limits"] for row in claims):
        raise ValueError("scientific ledger is incomplete")
    gaps = data["open_gaps"]
    if len(gaps) != 1 or gaps[0]["status"] != "OPEN":
        raise ValueError("independent-review gap must remain open")
    return {"claim_ledgers": 2, "open_review_gaps": 1, "closure_level": "LOCALLY_CLOSED"}


def build_receipt(parent_audit: dict[str, object] | None = None) -> dict[str, object]:
    parent_audit = parent_audit or {"all_ok": True, "rows": []}
    binary = capability_query_disposition(("m0", "m1"), ("m0", "m1"), {"m0": 0, "m1": 1})
    forced = forced_point_counterexample(("m0", "m1"), {"m0": 0, "m1": 1}, 0)
    coarse = capability_query_disposition(("m0", "m1"), ("m0", "m1"), {"m0": 7, "m1": 7})
    confidence = capability_query_disposition(
        ("m0", "m1"), ("m0", "m1"), {"m0": 0, "m1": 1},
        uncertainty_kind="CONFIDENCE_SET", alpha=Fraction(1, 20),
    )
    inconsistent = capability_query_disposition(("m0", "m1"), (), None)
    missing = capability_query_disposition(("m0", "m1"), ("m0",), None)
    nontotal = capability_query_disposition(("m0", "m1"), ("m0",), {"m0": 0})
    census = exhaustive_census()
    ledgers = validate_ledgers()
    expected_census = {
        "feasible_query_cases": 64,
        "confidence_query_cases": 192,
        "forced_point_counterexamples": 36,
        "missing_query_cases": 8,
    }
    checks = {
        "parents_exactly_pinned": bool(parent_audit["all_ok"]),
        "binary_nonidentification_abstains": binary["status"] == "CANNOT_IDENTIFY" and binary["identified_set"] == (0, 1) and binary["point_prediction"] is None,
        "forced_point_has_counterexample": forced["uniformly_sound"] is False and forced["counterexample_value"] == 1,
        "coarse_query_remains_identified": coarse["status"] == "IDENTIFIED" and coarse["point_prediction"] == 7,
        "confidence_preserved_not_certainty": confidence["status"] == "CANNOT_IDENTIFY" and confidence["failure_budget"] == Fraction(1, 20) and confidence["coverage_lower_bound"] == Fraction(19, 20),
        "inconsistency_and_cannot_check_distinct": inconsistent["status"] == "INCONSISTENT_REGISTERED_ASSUMPTIONS" and missing["status"] == "CANNOT_CHECK_QUERY_NOT_REGISTERED" and nontotal["status"] == "CANNOT_CHECK_QUERY_NOT_TOTAL_ON_DOMAIN",
        "bounded_census_complete": census == expected_census,
        "scientific_ledgers_complete": ledgers == {"claim_ledgers": 2, "open_review_gaps": 1, "closure_level": "LOCALLY_CLOSED"},
    }
    return {
        "schema": "GMI833CapabilityAbstentionResultV1",
        "issue": 913,
        "parent_issue": 833,
        "claim_ceiling": CLAIM_CEILING,
        "forbidden_promotions": FORBIDDEN_PROMOTIONS,
        "parent_audit": parent_audit,
        "census": census,
        "witness": {
            "binary_nonidentification": binary,
            "forced_point": forced,
            "coarse_query": coarse,
            "confidence_nonidentification": confidence,
            "empty_survivor": inconsistent,
            "missing_query": missing,
            "nontotal_query": nontotal,
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
    if isinstance(value, list):
        return [canonicalize(item) for item in value]
    if isinstance(value, dict):
        return {str(key): canonicalize(item) for key, item in sorted(value.items(), key=lambda pair: repr(pair[0]))}
    return value


def canonical_json(value) -> str:
    return json.dumps(canonicalize(value), sort_keys=True, indent=2, ensure_ascii=False) + "\n"


if __name__ == "__main__":
    print(canonical_json(build_receipt(audit_parents())), end="")
