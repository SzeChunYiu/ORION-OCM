#!/usr/bin/env python3
"""Exact, dependency-free infrastructure for issue #602 Section J1."""

from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from dataclasses import dataclass
from itertools import combinations
from pathlib import Path
from typing import Any, Iterable

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[1]
PROTECTED_METADATA_KEYS = {
    "candidate_id",
    "ecology_digest",
    "resource_digest",
    "grammar_digest",
    "split_digest",
    "prediction",
    "negative_twin_digest",
    "falsifier",
    "evaluator",
}


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def load_json(name: str) -> Any:
    with (HERE / name).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _leaf_items(value: Any, prefix: tuple[str, ...] = ()) -> dict[tuple[str, ...], Any]:
    if isinstance(value, dict):
        result: dict[tuple[str, ...], Any] = {}
        for key in sorted(value):
            result.update(_leaf_items(value[key], prefix + (str(key),)))
        return result
    return {prefix: value}


def negative_twin(base_ecology: dict[str, Any], path: tuple[str, ...], replacement: Any) -> dict[str, Any]:
    """Change exactly one registered leaf and return a hash-bound certificate."""
    if not path:
        raise ValueError("negative-twin path must name one leaf")
    twin = deepcopy(base_ecology)
    cursor: Any = twin
    for key in path[:-1]:
        if not isinstance(cursor, dict) or key not in cursor:
            raise KeyError("negative-twin path is absent")
        cursor = cursor[key]
    leaf = path[-1]
    if not isinstance(cursor, dict) or leaf not in cursor:
        raise KeyError("negative-twin leaf is absent")
    if cursor[leaf] == replacement:
        raise ValueError("negative twin must change the selected leaf")
    cursor[leaf] = replacement

    before = _leaf_items(base_ecology)
    after = _leaf_items(twin)
    changed = sorted(".".join(key) for key in before.keys() | after.keys() if before.get(key) != after.get(key))
    if changed != [".".join(path)]:
        raise AssertionError(f"negative twin changed unexpected leaves: {changed}")
    return {
        "schema": "GMI_DOMAIN_NEGATIVE_TWIN_V1",
        "base_digest": digest(base_ecology),
        "twin_digest": digest(twin),
        "changed_coordinate": changed[0],
        "base": base_ecology,
        "twin": twin,
    }


def collision_pairs(
    records: Iterable[dict[str, Any]],
    present_keys: tuple[str, ...] = ("present_output", "ordinary_score"),
    future_key: str = "future_response",
) -> dict[str, Any]:
    """Enumerate every same-present/different-future pair exactly."""
    rows = deepcopy(tuple(records))
    collisions = []
    for left, right in combinations(range(len(rows)), 2):
        a, b = rows[left], rows[right]
        if all(a.get(key) == b.get(key) for key in present_keys) and a.get(future_key) != b.get(future_key):
            collisions.append(
                {
                    "left": a["id"],
                    "right": b["id"],
                    "shared_present": {key: a.get(key) for key in present_keys},
                    "left_future": a.get(future_key),
                    "right_future": b.get(future_key),
                }
            )
    return {
        "schema": "GMI_DOMAIN_COLLISION_CERTIFICATE_V1",
        "record_count": len(rows),
        "pair_count": len(rows) * (len(rows) - 1) // 2,
        "present_keys": list(present_keys),
        "future_key": future_key,
        "records_digest": digest(rows),
        "collision_count": len(collisions),
        "collisions": collisions,
    }


@dataclass(frozen=True)
class ParentAttempt:
    parent_id: str
    priority: int
    status: str
    semantic_result: str
    burden_class: str
    evidence: str


def parent_reduction_tournament(attempts: Iterable[ParentAttempt]) -> dict[str, Any]:
    """Apply strongest-parent-first refusal with a fail-closed terminal."""
    ordered = sorted(tuple(attempts), key=lambda attempt: (attempt.priority, attempt.parent_id))
    if not ordered:
        raise ValueError("at least one registered parent is required")
    allowed = {"ABSORBS", "REFUTES", "OPEN"}
    if any(attempt.status not in allowed for attempt in ordered):
        raise ValueError("unknown parent-attempt status")
    if len({attempt.parent_id for attempt in ordered}) != len(ordered):
        raise ValueError("parent ids must be unique")

    first_absorber = next((attempt for attempt in ordered if attempt.status == "ABSORBS"), None)
    if first_absorber is not None:
        verdict = "PARENT_SUFFICIENT"
        owner = first_absorber.parent_id
    elif any(attempt.status == "OPEN" for attempt in ordered):
        verdict = "CANNOT_IDENTIFY"
        owner = None
    else:
        verdict = "RESIDUAL_SURVIVES_REGISTERED_PARENT_SET"
        owner = None
    return {
        "schema": "GMI_PARENT_REDUCTION_TOURNAMENT_V1",
        "verdict": verdict,
        "owner": owner,
        "attempts": [attempt.__dict__ for attempt in ordered],
        "all_parents_disposed": all(attempt.status != "OPEN" for attempt in ordered),
    }


def freeze_receipt(metadata: dict[str, Any], outcome: Any, salt: str) -> dict[str, Any]:
    """Create a public freeze with no outcome or salt field."""
    if not salt:
        raise ValueError("receipt salt must be nonempty")
    missing = PROTECTED_METADATA_KEYS - metadata.keys()
    if missing:
        raise ValueError(f"protected receipt metadata missing: {sorted(missing)}")
    commitment = hashlib.sha256(salt.encode("utf-8") + b"\0" + canonical_bytes(outcome)).hexdigest()
    return {
        "schema": "GMI_PROTECTED_DOMAIN_FREEZE_V1",
        "metadata": deepcopy(metadata),
        "outcome_commitment_sha256": commitment,
        "outcome_present": False,
        "salt_present": False,
    }


def reveal_receipt(freeze: dict[str, Any], outcome: Any, salt: str) -> dict[str, Any]:
    expected = hashlib.sha256(salt.encode("utf-8") + b"\0" + canonical_bytes(outcome)).hexdigest()
    if freeze.get("schema") != "GMI_PROTECTED_DOMAIN_FREEZE_V1":
        raise ValueError("wrong freeze schema")
    if freeze.get("outcome_present") is not False or freeze.get("salt_present") is not False:
        raise ValueError("freeze claims protected fields were exposed")
    if expected != freeze.get("outcome_commitment_sha256"):
        raise ValueError("held-out reveal does not match the frozen commitment")
    return {
        "schema": "GMI_PROTECTED_DOMAIN_REVEAL_V1",
        "freeze_digest": digest(freeze),
        "metadata": deepcopy(freeze["metadata"]),
        "outcome": deepcopy(outcome),
        "salt": salt,
        "commitment_verified": True,
    }


def validate_reduction_matrix(registry: dict[str, Any], matrix: dict[str, Any]) -> None:
    domain_ids = {row["id"] for row in registry["domains"]}
    expected = {(source, target) for source in domain_ids for target in domain_ids}
    cells = matrix["cells"]
    actual = {(row["source"], row["target"]) for row in cells}
    if actual != expected or len(cells) != len(expected):
        raise ValueError("reduction matrix must contain every ordered domain pair exactly once")
    for row in cells:
        diagonal = row["source"] == row["target"]
        if diagonal != (row["status"] == "IDENTITY"):
            raise ValueError("identity status must occur exactly on the diagonal")
        if not diagonal and row["status"] == "OPEN_SCOPE_DEPENDENT" and not row["blockers"]:
            raise ValueError("open reduction cells must state their blockers")
        for key in (
            "state_compiler",
            "operator_compiler",
            "semantic_preservation",
            "burden_disposition",
            "evidence",
            "blockers",
        ):
            if key not in row:
                raise ValueError(f"reduction cell missing {key}")


def _validate_component(instance: dict[str, Any], definition: dict[str, Any], label: str) -> None:
    required = set(definition["required"])
    allowed = set(definition["properties"])
    keys = set(instance)
    if not required <= keys:
        raise ValueError(f"{label}: missing required keys {sorted(required - keys)}")
    if keys - allowed:
        raise ValueError(f"{label}: unexpected keys {sorted(keys - allowed)}")
    for key, rule in definition["properties"].items():
        if "enum" in rule and instance[key] not in rule["enum"]:
            raise ValueError(f"{label}: {key} is outside its enum")
        if rule.get("type") == "string" and not instance[key]:
            raise ValueError(f"{label}: {key} is empty")
        if rule.get("type") == "array":
            if rule.get("minItems", 0) and not instance[key]:
                raise ValueError(f"{label}: {key} is empty")
            if not all(isinstance(value, str) and value for value in instance[key]):
                raise ValueError(f"{label}: {key} must contain nonempty strings")


def _evidence_path(reference: str) -> Path:
    file_part = reference.split("#", 1)[0]
    candidate = Path(file_part)
    if candidate.parts and candidate.parts[0] == "research":
        return REPO_ROOT / candidate
    return HERE / candidate


def validate_registry() -> dict[str, int]:
    schema = load_json("DOMAIN_COMPONENT_SCHEMA_V1.json")
    registry = load_json("DOMAIN_REGISTRY_V1.json")
    matrix = load_json("REDUCTION_MATRIX_V1.json")
    grammar = load_json("NEUTRAL_DOMAIN_GRAMMAR_V1.json")
    receipt_schema = load_json("PROTECTED_DOMAIN_RECEIPT_SCHEMA_V1.json")
    ledger = load_json("J1_INFRASTRUCTURE_LEDGER_V1.json")

    if schema["$schema"] != "https://json-schema.org/draft/2020-12/schema":
        raise ValueError("component schema draft drifted")
    if set(schema["$defs"]) != {"state_carrier", "native_operator", "development_law", "burden_equivalence"}:
        raise ValueError("component schema definitions drifted")
    domains = registry["domains"]
    if [row["id"] for row in domains] != [f"D{i}" for i in range(1, 9)]:
        raise ValueError("registry must contain exactly ordered D1-D8")
    for row in domains:
        if not row["carriers"] or not row["native_operators"] or not row["development_laws"]:
            raise ValueError(f"{row['id']}: component inventory is empty")
        if not row["strongest_parents"] or not row["falsifier"] or not row["claim_ceiling"]:
            raise ValueError(f"{row['id']}: scientific boundary is incomplete")
        for carrier in row["carriers"]:
            _validate_component(carrier, schema["$defs"]["state_carrier"], f"{row['id']} carrier")
        for operator in row["native_operators"]:
            _validate_component(operator, schema["$defs"]["native_operator"], f"{row['id']} operator")
        for law in row["development_laws"]:
            _validate_component(law, schema["$defs"]["development_law"], f"{row['id']} development law")
        for evidence in row["evidence"]:
            if not _evidence_path(evidence).is_file():
                raise ValueError(f"{row['id']}: missing evidence file {evidence}")

    validate_reduction_matrix(registry, matrix)
    classes = registry["accepted_burden_equivalence_classes"]
    for burden_class in classes:
        _validate_component(burden_class, schema["$defs"]["burden_equivalence"], "burden class")
    accepted = {row["id"] for row in classes if row["accepted_for_domain_equivalence"]}
    rejected = {row["id"] for row in classes if not row["accepted_for_domain_equivalence"]}
    if accepted != {"E0_EXACT_ISOMETRY", "E1_CONSTANT_FACTOR", "E2_POLYNOMIAL"}:
        raise ValueError("accepted burden classes drifted")
    if rejected != {"E3_APPROXIMATE_OR_EMPIRICAL"}:
        raise ValueError("approximate evidence must not establish exact domain equivalence")

    symbols = [row["symbol"] for row in grammar["carrier_constructors"] + grammar["operator_constructors"]]
    forbidden = tuple(grammar["forbidden_symbol_substrings"])
    if len(symbols) != len(set(symbols)):
        raise ValueError("neutral grammar symbols must be unique")
    if any(token.lower() in symbol.lower() for symbol in symbols for token in forbidden):
        raise ValueError("neutral grammar contains a forbidden domain/family macro")
    if receipt_schema["freeze_schema"]["required"][-2:] != ["outcome_present", "salt_present"]:
        raise ValueError("protected freeze guards drifted")
    if set(receipt_schema["freeze_schema"]["properties"]["metadata"]["required"]) != PROTECTED_METADATA_KEYS:
        raise ValueError("protected metadata requirements drifted")
    if len(ledger["rows"]) != 11 or any(row["status"] != "GREEN" for row in ledger["rows"]):
        raise ValueError("J1 infrastructure ledger must contain exactly eleven green rows")
    for row in ledger["rows"]:
        if not _evidence_path(row["evidence"]).is_file():
            raise ValueError(f"J1 ledger evidence is missing: {row['evidence']}")

    return {
        "domains": len(domains),
        "matrix_cells": len(matrix["cells"]),
        "burden_classes": len(classes),
        "grammar_symbols": len(symbols),
    }


if __name__ == "__main__":
    counts = validate_registry()
    print("GMI_DOMAIN_REGISTRY_V1_VALID")
    for key, value in counts.items():
        print(f"{key}={value}")
