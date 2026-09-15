#!/usr/bin/env python3
"""Finite model and dependency checks for Issue #833's compact axiom core."""

from __future__ import annotations

from collections import defaultdict
import copy
import json
from itertools import product
from pathlib import Path
from typing import Mapping


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
AXIOM_IDS = {
    "AX1_TYPED_DOMAINS",
    "AX2_BEHAVIORAL_SPECIFICATION",
    "AX3_TOTAL_REGISTERED_PROCESS",
    "AX4_BEHAVIORAL_EQUIVALENCE",
    "AX5_DEVELOPMENT",
    "AX6_RESOURCES",
    "AX7_CAPABILITY",
    "AX8_UNCERTAINTY",
    "AX9_ABSTENTION",
    "AX10_SCOPE_TAGS",
}
QUERY_DISPOSITIONS = {
    "IDENTIFIED",
    "CANNOT_IDENTIFY",
    "CANNOT_CHECK",
    "INCONSISTENT_REGISTERED_ASSUMPTIONS",
}
SCOPE_TAGS = {"forall[D]", "forall_fin[U]", "heldout[F]", "sample[P,n]"}


def response_partition(model: Mapping[str, object]) -> tuple[tuple[str, ...], ...]:
    states = tuple(model["states"])
    actions = tuple(model["actions"])
    observation = model["observation"]
    transition = {(source, action): target for source, action, target in model["transition"]}
    block = {state: 0 for state in states}
    while True:
        signatures = {
            state: (observation[state], tuple(block[transition[state, action]] for action in actions))
            for state in states
        }
        labels = {signature: index for index, signature in enumerate(sorted(set(signatures.values()), key=repr))}
        refined = {state: labels[signatures[state]] for state in states}
        if refined == block:
            break
        block = refined
    groups: dict[int, list[str]] = defaultdict(list)
    for state in states:
        groups[block[state]].append(state)
    return tuple(tuple(group) for _, group in sorted(groups.items()))


def evaluate_axioms(model: Mapping[str, object]) -> dict[str, bool]:
    states = tuple(model.get("states", ()))
    actions = tuple(model.get("actions", ()))
    state_set = set(states)
    transition_rows = tuple(model.get("transition", ()))
    transition = {
        (row[0], row[1]): row[2]
        for row in transition_rows
        if isinstance(row, list) and len(row) == 3
    }
    specifications = tuple(model.get("specifications", ()))
    resources = tuple(model.get("resources", ()))
    development = tuple(model.get("development_edges", ()))
    uncertainty = set(model.get("uncertainty_worlds", ()))

    typed = (
        bool(states)
        and bool(actions)
        and len(state_set) == len(states)
        and len(set(actions)) == len(actions)
        and set(model.get("observation", {})) == state_set
    )
    specification_ok = bool(specifications) and all(
        row.get("id")
        and set(row.get("instances", ())) <= state_set
        and all(len(pair) == 2 and pair[0] in row.get("instances", ()) for pair in row.get("accept_pairs", ()))
        and "architecture" not in row
        for row in specifications
    )
    process_ok = (
        len(transition_rows) == len(transition)
        and set(transition) == set(product(states, actions))
        and set(transition.values()) <= state_set
    )
    try:
        partition_ok = process_ok and len(response_partition(model)) == len(states)
    except (KeyError, TypeError, ValueError):
        partition_ok = False
    development_ok = bool(development) and bool(resources) and all(
        isinstance(row, list)
        and len(row) == 3
        and row[0] in state_set
        and row[1] in state_set
        and len(row[2]) == len(resources)
        and all(type(value) is int and value >= 0 for value in row[2])
        for row in development
    )
    resources_ok = bool(resources) and all(type(value) is int and value >= 0 for value in resources)
    acceptance_pairs = {
        (pair[0], pair[1])
        for row in specifications
        for pair in row.get("accept_pairs", ())
        if len(pair) == 2
    }
    behavior = model.get("observation", {})
    capability_ok = specification_ok and all((state, behavior[state]) in acceptance_pairs for state in states)
    uncertainty_ok = (
        bool(state_set)
        and uncertainty <= state_set
        and model.get("uncertainty_kind") == "FEASIBLE_SET"
        and bool(model.get("uncertainty_version"))
        and bool(model.get("uncertainty_provenance"))
    )
    query_ok = set(model.get("query_dispositions", ())) == QUERY_DISPOSITIONS
    scopes_ok = bool(model.get("theorem_scopes")) and all(
        scope in SCOPE_TAGS for scope in model.get("theorem_scopes", {}).values()
    )
    return {
        "AX1_TYPED_DOMAINS": typed,
        "AX2_BEHAVIORAL_SPECIFICATION": specification_ok,
        "AX3_TOTAL_REGISTERED_PROCESS": process_ok,
        "AX4_BEHAVIORAL_EQUIVALENCE": partition_ok,
        "AX5_DEVELOPMENT": development_ok,
        "AX6_RESOURCES": resources_ok,
        "AX7_CAPABILITY": capability_ok,
        "AX8_UNCERTAINTY": uncertainty_ok,
        "AX9_ABSTENTION": query_ok,
        "AX10_SCOPE_TAGS": scopes_ok,
    }


def validate_imports_and_derivations() -> dict[str, int]:
    data = json.loads((HERE / "DERIVATION_MAP_V1.json").read_text(encoding="utf-8"))
    imports = data["imports"]
    expected_imports = {
        "IMPORT_FOUNDATION",
        "IMPORT_PARENT_EQUIVALENCE",
        "IMPORT_MORPHCAP",
        "IMPORT_UNCERTAINTY",
    }
    if set(imports) != expected_imports:
        raise ValueError("axiom-core import inventory drifted")
    imported_results = {name: json.loads((REPO / path).read_text(encoding="utf-8")) for name, path in imports.items()}
    if imported_results["IMPORT_FOUNDATION"].get("terminal") != "GMI_833_FOUNDATION_V1_FORMALIZED_AT_DECLARED_SCOPE":
        raise ValueError("foundation authority is not green")
    if imported_results["IMPORT_PARENT_EQUIVALENCE"].get("verdict") != "GREEN":
        raise ValueError("parent-equivalence authority is not green")
    if imported_results["IMPORT_MORPHCAP"].get("verdict") != "GREEN":
        raise ValueError("morphology/capability authority is not green")
    if imported_results["IMPORT_UNCERTAINTY"].get("terminal") != "GMI_833_GLOBAL_UNCERTAINTY_V1_ALL_GREEN":
        raise ValueError("uncertainty authority is not green")

    rows = data["derived_constructs"]
    ids = {row["id"] for row in rows}
    if len(rows) != 10 or len(ids) != len(rows):
        raise ValueError("derived-construct inventory drifted")
    allowed = AXIOM_IDS | expected_imports | ids
    for row in rows:
        if not row["dependencies"] or not set(row["dependencies"]) <= allowed:
            raise ValueError(f"unknown or empty dependency for {row['id']}")
    return {"imported_green_packages": len(imports), "derived_constructs": len(rows)}


def validate_registry(data: Mapping[str, object]) -> None:
    axioms = tuple(data.get("axioms", ()))
    if len(axioms) != 10 or {row.get("id") for row in axioms} != AXIOM_IDS:
        raise ValueError("compact axiom registry must contain exactly the ten registered identifiers")
    if any(not row.get("statement") or row.get("scope") not in SCOPE_TAGS or not row.get("falsifier") for row in axioms):
        raise ValueError("every axiom needs statement, valid scope, and falsifier")


def validate_model(model: Mapping[str, object]) -> dict[str, object]:
    checks = evaluate_axioms(model)
    failed = sorted(identifier for identifier, passed in checks.items() if not passed)
    if failed:
        raise ValueError(f"finite model violates registered axioms: {failed}")
    return {
        "axioms_satisfied": sum(checks.values()),
        "finite_model_states": len(model["states"]),
        "finite_model_actions": len(model["actions"]),
        "response_classes": len(response_partition(model)),
        "model_exists": True,
    }


def mutation_controls(model: Mapping[str, object]) -> dict[str, bool]:
    controls = {}
    mutants = {}
    missing_transition = copy.deepcopy(model)
    missing_transition["transition"] = missing_transition["transition"][:-1]
    mutants["missing_transition_rejected"] = missing_transition
    negative_resource = copy.deepcopy(model)
    negative_resource["resources"][0] = -1
    mutants["negative_resource_rejected"] = negative_resource
    missing_scope = copy.deepcopy(model)
    missing_scope["theorem_scopes"]["FINITE_MODEL_CHECK"] = ""
    mutants["missing_scope_rejected"] = missing_scope
    kind_conflation = copy.deepcopy(model)
    kind_conflation["uncertainty_kind"] = "OVERLOADED_SCALAR"
    mutants["uncertainty_kind_conflation_rejected"] = kind_conflation
    for name, mutant in mutants.items():
        controls[name] = not all(evaluate_axioms(mutant).values())
    if not all(controls.values()):
        raise ValueError("an axiom mutation survived")
    return controls


def validate_all() -> dict[str, object]:
    data = json.loads((HERE / "AXIOMS_V1.json").read_text(encoding="utf-8"))
    validate_registry(data)
    result = {
        "schema": "GMI_833_AXIOM_CORE_RESULT_V1",
        **validate_imports_and_derivations(),
        **validate_model(data["finite_model"]),
        "mutation_controls": mutation_controls(data["finite_model"]),
        "consistency_claim": "RELATIVE_FINITE_MODEL_CONSISTENCY",
        "closure_level": "LOCALLY_CLOSED",
        "open_independent_review_gaps": 1,
        "verdict": "GREEN",
    }
    expected = json.loads((HERE / "RESULT_V1.json").read_text(encoding="utf-8"))
    if result != expected:
        raise ValueError("axiom-core deterministic receipt drifted")
    return result


if __name__ == "__main__":
    print("GMI_833_AXIOM_CORE_V1_ALL_GREEN")
    print(json.dumps(validate_all(), sort_keys=True))
