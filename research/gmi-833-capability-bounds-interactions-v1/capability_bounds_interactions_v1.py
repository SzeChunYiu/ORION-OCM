#!/usr/bin/env python3
"""Exact finite capability-bound and interaction witnesses for issue #906."""

from __future__ import annotations

from fractions import Fraction
from hashlib import sha1
from itertools import product
import json
from pathlib import Path
from typing import Hashable, Mapping, Sequence


HERE = Path(__file__).resolve().parent
CLAIM_CEILING = "GMI_833_FINITE_CAPABILITY_BOUNDS_SYNERGY_AND_INTERFERENCE_AT_REGISTERED_SCOPE"
NO_FEASIBLE = "NO_FEASIBLE_REALIZATION"
FORBIDDEN_PROMOTIONS = (
    "ALL_CAPABILITY_DEFINITIONS_REAUDITED",
    "ALL_ELEVEN_CAPABILITY_CEILINGS_REPROVED",
    "CAPABILITY_PREDICTOR_VALIDATED",
    "OVERLAP_IMPLIES_SYNERGY",
    "ALL_CAPABILITY_INTERACTIONS_CLASSIFIED",
    "REAL_SYSTEM_INTERACTION_EFFECT",
    "UNIVERSAL_SCALAR_RESOURCE_LAW",
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
        "morphcap",
        "research/gmi-833-morphcap-v1/RESULT_V1.json",
        "bdc5c3cd42e312d8c7af52f7ba84220631a25f8a",
        "claim_ceiling",
        "GMI_MORPHOLOGY_AND_CAPABILITY_OBJECTS_AT_REGISTERED_FINITE_SCOPE",
    ),
    (
        "axiom_core",
        "research/gmi-833-axiom-core-v1/RESULT_V1.json",
        "3366a3bc7236d286f8d123bf53e4e3b2d22ad7b9",
        "claim_ceiling",
        "GMI_REGISTERED_FINITE_AXIOM_CORE_SATISFIABLE_AND_COMPACT_AT_SCOPE",
    ),
    (
        "historical_interaction_tranche",
        "research/gmi-capability-interactions-v3/INTERACTIONS_TRANCHE3_V1.json",
        "40b24f58069777bcc3a3ccb3c68497d1e1e04d18",
        "claim_ceiling",
        "G2",
    ),
    (
        "historical_unified_theorem",
        "research/gmi-capability-interactions-unified-v1/CAPABILITY_INTERACTIONS_UNIFIED_THEOREM_V1.md",
        "294898059082ee55377bb0b73c1e55bd6a749847",
        None,
        None,
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
            rows.append(
                {
                    "name": name,
                    "path": path,
                    "actual_blob": None,
                    "blob_ok": False,
                    "claim_ok": False,
                }
            )
            continue
        data = target.read_bytes()
        claim_ok = True
        if field is not None:
            try:
                claim_ok = json.loads(data).get(field) == expected_claim
            except (UnicodeDecodeError, json.JSONDecodeError):
                claim_ok = False
        rows.append(
            {
                "name": name,
                "path": path,
                "actual_blob": git_blob_sha(data),
                "blob_ok": git_blob_sha(data) == expected_blob,
                "claim_ok": claim_ok,
            }
        )
    return {"rows": rows, "all_ok": all(row["blob_ok"] and row["claim_ok"] for row in rows)}


def finite_capability_bounds(scores: Mapping[Hashable, int | Fraction]) -> dict[str, object]:
    """Return the uniform floor and ceiling of exactly the feasible class supplied."""
    normalized = {member: exact(score) for member, score in scores.items()}
    if not normalized:
        return {"status": NO_FEASIBLE, "floor": None, "ceiling": None}
    values = tuple(normalized.values())
    return {
        "status": "BOUNDED",
        "floor": min(values),
        "ceiling": max(values),
        "floor_witnesses": tuple(member for member, score in normalized.items() if score == min(values)),
        "ceiling_witnesses": tuple(member for member, score in normalized.items() if score == max(values)),
    }


def witness_ceiling_lower_certificate(
    scores: Mapping[Hashable, int | Fraction], witness: Hashable
) -> dict[str, object]:
    bounds = finite_capability_bounds(scores)
    if bounds["status"] != "BOUNDED" or witness not in scores:
        raise ValueError("certificate requires a registered witness in a nonempty feasible class")
    witness_score = exact(scores[witness])
    floor = bounds["floor"]
    ceiling = bounds["ceiling"]
    assert isinstance(floor, Fraction) and isinstance(ceiling, Fraction)
    return {
        "witness_score": witness_score,
        "ceiling": ceiling,
        "is_ceiling_lower_certificate": witness_score <= ceiling,
        "is_uniform_class_lower_bound": witness_score <= floor,
    }


def inclusion_bounds(
    smaller: Mapping[Hashable, int | Fraction], larger: Mapping[Hashable, int | Fraction]
) -> dict[str, object]:
    if not smaller:
        raise ValueError("inclusion theorem requires a nonempty smaller feasible class")
    small = {member: exact(score) for member, score in smaller.items()}
    large = {member: exact(score) for member, score in larger.items()}
    if not set(small).issubset(large) or any(large[member] != score for member, score in small.items()):
        raise ValueError("larger class must preserve every smaller-class member and score")
    sb = finite_capability_bounds(small)
    lb = finite_capability_bounds(large)
    return {
        "smaller_floor": sb["floor"],
        "larger_floor": lb["floor"],
        "smaller_ceiling": sb["ceiling"],
        "larger_ceiling": lb["ceiling"],
        "floor_nonincreasing": lb["floor"] <= sb["floor"],
        "ceiling_nondecreasing": sb["ceiling"] <= lb["ceiling"],
    }


CELL_FACTORS = {"00": (False, False), "10": (True, False), "01": (False, True), "11": (True, True)}
CELL_FIELDS = {"factor_a", "factor_b", "score", "contract_id", "ecology_id", "budget"}


def registered_interaction(design: Mapping[str, Mapping[str, object]]) -> dict[str, object]:
    """Evaluate a frozen two-factor/four-cell capability design."""
    if set(design) != set(CELL_FACTORS):
        raise ValueError("registered interaction requires exactly cells 00, 10, 01, and 11")
    normalized: dict[str, Fraction] = {}
    context = None
    for cell, expected_factors in CELL_FACTORS.items():
        row = design[cell]
        if set(row) != CELL_FIELDS:
            raise ValueError("four-cell rows must contain exactly the registered fields")
        if (row["factor_a"], row["factor_b"]) != expected_factors:
            raise ValueError("cell label and factor flags disagree")
        budget = tuple(exact(value) for value in row["budget"])
        if not budget or any(value < 0 for value in budget):
            raise ValueError("registered budget must be a nonempty nonnegative exact vector")
        row_context = (row["contract_id"], row["ecology_id"], budget)
        if context is None:
            context = row_context
        elif row_context != context:
            raise ValueError("contract, ecology, and budget must be frozen across all four cells")
        normalized[cell] = exact(row["score"])
    delta = normalized["11"] - normalized["10"] - normalized["01"] + normalized["00"]
    classification = (
        "POSITIVE_SYNERGY" if delta > 0 else "ADDITIVE_AT_REGISTERED_DESIGN" if delta == 0 else "NEGATIVE_INTERACTION"
    )
    return {"scores": normalized, "mixed_difference": delta, "classification": classification}


def make_design(scores: Sequence[int | Fraction], *, contract_id="c", ecology_id="e", budget=(1,)):
    if len(scores) != 4:
        raise ValueError("scores must be ordered as 00,10,01,11")
    return {
        cell: {
            "factor_a": factors[0],
            "factor_b": factors[1],
            "score": score,
            "contract_id": contract_id,
            "ecology_id": ecology_id,
            "budget": budget,
        }
        for cell, factors, score in zip(("00", "10", "01", "11"), CELL_FACTORS.values(), scores, strict=True)
    }


def joint_threshold_interaction(a0: int, a1: int, b0: int, b1: int, threshold: int) -> dict[str, object]:
    values = (a0, a1, b0, b1, threshold)
    if any(isinstance(value, bool) or type(value) is not int or value <= 0 for value in values):
        raise ValueError("capacities and threshold must be positive integers")
    if a1 < a0 or b1 < b0:
        raise ValueError("registered upgrades may not reduce capacity")
    products = (a0 * b0, a1 * b0, a0 * b1, a1 * b1)
    scores = tuple(int(value >= threshold) for value in products)
    interaction = registered_interaction(make_design(scores, contract_id="joint-threshold", ecology_id="product-code"))
    joint_only = products[0] < threshold and products[1] < threshold and products[2] < threshold <= products[3]
    return {
        "products": products,
        "scores": scores,
        "joint_only_condition": joint_only,
        "mixed_difference": interaction["mixed_difference"],
        "strict_positive_synergy": interaction["mixed_difference"] > 0,
        "iff_holds": joint_only == (interaction["mixed_difference"] > 0),
    }


def shared_budget_interference(
    total_budget: int | Fraction, requirement: int | Fraction, mandatory_charge: int | Fraction
) -> dict[str, object]:
    total = exact(total_budget)
    required = exact(requirement)
    charge = exact(mandatory_charge)
    if total < 0 or required <= 0 or charge < 0:
        raise ValueError("budget/charge must be nonnegative and requirement strictly positive")
    remaining = max(Fraction(0), total - charge)
    capable_before = total >= required
    capable_after = remaining >= required
    interferes = capable_before and not capable_after
    iff_condition = total >= required and total - charge < required
    return {
        "remaining": remaining,
        "capable_before": capable_before,
        "capable_after": capable_after,
        "interferes": interferes,
        "iff_condition": iff_condition,
        "iff_holds": interferes == iff_condition,
    }


def free_option_monotonicity(
    old_scores: Mapping[Hashable, int | Fraction], new_scores: Mapping[Hashable, int | Fraction]
) -> dict[str, object]:
    if not old_scores:
        raise ValueError("free-option theorem requires a nonempty old feasible set")
    old = {item: exact(score) for item, score in old_scores.items()}
    new = {item: exact(score) for item, score in new_scores.items()}
    if not set(old).issubset(new) or any(new[item] != score for item, score in old.items()):
        raise ValueError("new feasible set must retain old configurations under the unchanged objective")
    old_optimum, new_optimum = max(old.values()), max(new.values())
    return {
        "old_optimum": old_optimum,
        "new_optimum": new_optimum,
        "cannot_harm_optimum": new_optimum >= old_optimum,
    }


def overlap_nonidentification_hostile() -> dict[str, object]:
    tables = {
        "positive_synergy": (0, 0, 0, 1),
        "additive": (0, 1, 1, 2),
        "negative_interaction": (0, 1, 1, 1),
    }
    observed = {
        name: registered_interaction(
            make_design(scores, contract_id="same-contract", ecology_id="same-ecology", budget=(2,))
        )["classification"]
        for name, scores in tables.items()
    }
    return {
        "shared_resource_channel_signature": ("compute",),
        "classifications": observed,
        "overlap_determines_sign": len(set(observed.values())) == 1,
    }


def exhaustive_census() -> dict[str, int]:
    bound_cases = 0
    for width in range(1, 5):
        for values in product(range(4), repeat=width):
            bounds = finite_capability_bounds(dict(enumerate(values)))
            if bounds["floor"] != min(values) or bounds["ceiling"] != max(values):
                raise ValueError("finite bound census mismatch")
            bound_cases += 1

    inclusion_cases = 0
    for values in product(range(4), repeat=4):
        larger = dict(enumerate(values))
        for mask in range(1, 16):
            smaller = {index: value for index, value in larger.items() if mask & (1 << index)}
            theorem = inclusion_bounds(smaller, larger)
            if not theorem["floor_nonincreasing"] or not theorem["ceiling_nondecreasing"]:
                raise ValueError("bound inclusion monotonicity failed")
            inclusion_cases += 1

    four_cell_cases = 0
    for scores in product(range(3), repeat=4):
        result = registered_interaction(make_design(scores))
        expected = Fraction(scores[3] - scores[1] - scores[2] + scores[0])
        if result["mixed_difference"] != expected:
            raise ValueError("four-cell interaction identity failed")
        four_cell_cases += 1

    joint_threshold_cases = 0
    for a0 in range(1, 4):
        for a1 in range(a0, 5):
            for b0 in range(1, 4):
                for b1 in range(b0, 5):
                    for threshold in range(1, 18):
                        result = joint_threshold_interaction(a0, a1, b0, b1, threshold)
                        if not result["iff_holds"]:
                            raise ValueError("joint-threshold iff failed")
                        joint_threshold_cases += 1

    shared_budget_cases = 0
    for total, required, charge in product(range(11), range(1, 11), range(11)):
        if not shared_budget_interference(total, required, charge)["iff_holds"]:
            raise ValueError("shared-budget iff failed")
        shared_budget_cases += 1

    free_option_cases = 0
    for old_a, old_b, added in product(range(3), repeat=3):
        result = free_option_monotonicity({"a": old_a, "b": old_b}, {"a": old_a, "b": old_b, "x": added})
        if not result["cannot_harm_optimum"]:
            raise ValueError("free-option monotonicity failed")
        free_option_cases += 1

    return {
        "finite_bound_cases": bound_cases,
        "class_inclusion_cases": inclusion_cases,
        "four_cell_interaction_cases": four_cell_cases,
        "joint_threshold_iff_cases": joint_threshold_cases,
        "shared_budget_iff_cases": shared_budget_cases,
        "free_option_cases": free_option_cases,
    }


def validate_ledgers() -> dict[str, object]:
    data = json.loads((HERE / "SCIENTIFIC_LEDGER_V1.json").read_text())
    required = {"id", "assumptions", "dependencies", "falsifiers", "strongest_parent", "counterexample_methods", "limits"}
    claims = data["claims"]
    if len(claims) != 4 or any(set(row) != required for row in claims):
        raise ValueError("scientific ledger schema/count drifted")
    if any(not row["assumptions"] or not row["falsifiers"] or not row["limits"] for row in claims):
        raise ValueError("scientific ledger is incomplete")
    gaps = data["open_gaps"]
    if len(gaps) != 1 or gaps[0]["status"] != "OPEN":
        raise ValueError("independent-review gap must remain open")
    return {"claim_ledgers": 4, "open_review_gaps": 1, "closure_level": "LOCALLY_CLOSED"}


def validate_package_contracts() -> dict[str, object]:
    manifest = json.loads((HERE / "MANIFEST_V1.json").read_text())
    reconciliation = json.loads((HERE / "ISSUE_833_RECONCILIATION_CAPABILITY_INTERACTIONS_V1.json").read_text())
    expected_rows = {
        "- [ ] Derive capability lower bounds as well as ceilings.",
        "- [ ] Derive capability interactions/synergies.",
        "- [ ] Derive capability interference under shared budgets.",
    }
    replacements = reconciliation.get("replacements", [])
    manifest_ok = (
        manifest.get("issue") == 906
        and manifest.get("source_pr") == 907
        and manifest.get("parent_issue") == 833
        and manifest.get("freeze_commit") == "964a77c3accbf51b64a4b2af355dec751dfeec92"
        and manifest.get("frozen_main") == "9f90fc4ef961b7e9adccf7438488d1a64b9e68be"
        and manifest.get("claim_ceiling") == CLAIM_CEILING
        and manifest.get("target_rows") == 3
        and manifest.get("total_exhaustive_cases") == 6875
        and tuple(manifest.get("forbidden_promotions", ())) == FORBIDDEN_PROMOTIONS
    )
    reconciliation_ok = (
        reconciliation.get("schema") == "GMI_ISSUE_RECONCILIATION_V2"
        and reconciliation.get("issue") == 833
        and reconciliation.get("source_issue") == 906
        and reconciliation.get("source_pr") == 907
        and reconciliation.get("claim_ceiling") == CLAIM_CEILING
        and tuple(reconciliation.get("forbidden_promotions", ())) == FORBIDDEN_PROMOTIONS
        and len(replacements) == 3
        and {row.get("old") for row in replacements} == expected_rows
        and all(row.get("anchor") == "# K. Capability theory upgrade" for row in replacements)
        and all(row.get("new", "").startswith("- [x]") and "PR #907 / #906" in row.get("new", "") for row in replacements)
    )
    return {
        "manifest_ok": manifest_ok,
        "reconciliation_ok": reconciliation_ok,
        "reconciliation_rows": len(replacements),
        "source_pr": reconciliation.get("source_pr"),
    }


def build_receipt(parent_audit: dict[str, object] | None = None) -> dict[str, object]:
    parent_audit = parent_audit or {"all_ok": True, "rows": []}
    bounds = finite_capability_bounds({"low": 1, "middle": 2, "high": 3})
    empty = finite_capability_bounds({})
    witness = witness_ceiling_lower_certificate({"low": 1, "high": 3}, "high")
    inclusion = inclusion_bounds({"middle": 2}, {"low": 1, "middle": 2, "high": 3})
    synergy = joint_threshold_interaction(1, 2, 1, 2, 4)
    single_upgrade_twin = joint_threshold_interaction(1, 2, 1, 2, 2)
    additive = registered_interaction(make_design((0, 1, 1, 2)))
    interference = shared_budget_interference(2, 2, 1)
    restored = shared_budget_interference(3, 2, 1)
    free_option = free_option_monotonicity({"old": 2}, {"old": 2, "optional": 1})
    overlap = overlap_nonidentification_hostile()
    census = exhaustive_census()
    ledgers = validate_ledgers()
    package_contracts = validate_package_contracts()
    expected_census = {
        "finite_bound_cases": 340,
        "class_inclusion_cases": 3840,
        "four_cell_interaction_cases": 81,
        "joint_threshold_iff_cases": 1377,
        "shared_budget_iff_cases": 1210,
        "free_option_cases": 27,
    }
    checks = {
        "parents_exactly_pinned": bool(parent_audit["all_ok"]),
        "finite_floor_and_ceiling_exact": bounds["floor"] == 1 and bounds["ceiling"] == 3,
        "empty_class_is_typed_nonnumeric": empty == {"status": NO_FEASIBLE, "floor": None, "ceiling": None},
        "witness_lower_bounds_ceiling_not_class": witness["is_ceiling_lower_certificate"] and not witness["is_uniform_class_lower_bound"],
        "class_inclusion_opposite_monotonicities": inclusion["floor_nonincreasing"] and inclusion["ceiling_nondecreasing"],
        "joint_threshold_synergy_iff": synergy["joint_only_condition"] and synergy["strict_positive_synergy"] and synergy["iff_holds"],
        "single_upgrade_twin_removes_positive_synergy": not single_upgrade_twin["strict_positive_synergy"],
        "additive_control_zero_interaction": additive["mixed_difference"] == 0,
        "shared_budget_interference_iff": interference["interferes"] and interference["iff_holds"],
        "budget_restoration_removes_interference": not restored["interferes"] and restored["iff_holds"],
        "free_option_cannot_harm": free_option["cannot_harm_optimum"],
        "overlap_does_not_determine_sign": not overlap["overlap_determines_sign"] and len(set(overlap["classifications"].values())) == 3,
        "bounded_censuses_complete": census == expected_census,
        "scientific_ledgers_complete": ledgers == {"claim_ledgers": 4, "open_review_gaps": 1, "closure_level": "LOCALLY_CLOSED"},
        "manifest_and_reconciliation_exact": package_contracts == {
            "manifest_ok": True,
            "reconciliation_ok": True,
            "reconciliation_rows": 3,
            "source_pr": 907,
        },
    }
    return {
        "schema": "GMI833CapabilityBoundsInteractionsResultV1",
        "issue": 906,
        "parent_issue": 833,
        "claim_ceiling": CLAIM_CEILING,
        "forbidden_promotions": FORBIDDEN_PROMOTIONS,
        "parent_audit": parent_audit,
        "census": census,
        "witness": {
            "bounds": bounds,
            "empty": empty,
            "witness_certificate": witness,
            "inclusion": inclusion,
            "joint_threshold_synergy": synergy,
            "single_upgrade_twin": single_upgrade_twin,
            "additive_control": additive,
            "shared_budget_interference": interference,
            "budget_restoration_twin": restored,
            "free_option_control": free_option,
            "overlap_nonidentification": overlap,
        },
        "scientific_ledger": ledgers,
        "package_contracts": package_contracts,
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
