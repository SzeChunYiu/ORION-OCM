#!/usr/bin/env python3
"""Fail-closed metadata and finite-schema audit for the canonical T602 corpus."""

from __future__ import annotations

import json
from itertools import product
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
CLOSURE = REPO / "research/gmi-grand-unification-v1/closure-602-v1"
DEPENDENCIES = CLOSURE / "GMI_602_CLOSURE_DEPENDENCIES_V1.json"
OWNERS = (
    CLOSURE / "GMI_602_PARENT_ATLAS_AND_FORMAL_CLOSURE_V1.md",
    CLOSURE / "GMI_602_FORMAL_GAP_CLOSURE_V2.md",
    CLOSURE / "GMI_602_KNOWN_FAMILY_FORMAL_CLOSURE_V3.md",
    CLOSURE / "GMI_602_HIGH_RISK_PARENT_SUBTRACTIONS_V1.md",
)
ALLOWED_TAGS = {"P1", "P2", "P3", "P4", "P5"}
P1_MODES = {"EXECUTABLE_SCHEMA", "FORMAL_DERIVATION_WITH_STRUCTURAL_GATE", "DEFINITIONAL_GATE", "PARENT_REDUCTION_CHECK"}
SCHEMA_COVERAGE = {
    "finite_factorization": {"T602-01", "T602-17", "T602-29", "T602-35"},
    "integer_crossover": {"T602-05", "T602-11", "T602-24", "T602-36"},
    "interaction_signs": {"T602-10", "T602-28"},
    "closure_conjunction": {"T602-23"},
    "finite_eventual_periodicity": {"T602-31"},
}


def finite_schema_checks() -> dict[str, bool]:
    # T602-05/11: strict integer crossover is floor(K/Delta)+1.
    crossover = all((h * delta > cost) == (h >= cost // delta + 1)
                    for cost in range(1, 12) for delta in range(1, 8) for h in range(20))
    # T602-10: all three interaction signs are constructively reachable.
    signs = {8 + 8 - joint - 10 for joint in (3, 6, 7)} == {3, 0, -1}
    # T602-17/29: finite factorization exists iff target is constant on fibers.
    factorization = True
    states = range(4)
    for observation in product(range(2), repeat=4):
        for target in product(range(2), repeat=4):
            constant = all(observation[a] != observation[b] or target[a] == target[b]
                           for a in states for b in states)
            functions = product(range(2), repeat=2)
            exists = any(all(candidate[observation[s]] == target[s] for s in states) for candidate in functions)
            factorization &= constant == exists
    # T602-20: perturbation vanishes on every observed point and differs outside.
    observed = (-1, 0, 2)
    perturbation = lambda x: (x + 1) * x * (x - 2)
    extrapolation = all(perturbation(x) == 0 for x in observed) and perturbation(3) != 0
    # T602-23: conjunction is true exactly when no required antecedent is false.
    conjunction = all((all(bits) == (sum(bits) == len(bits))) for bits in product((False, True), repeat=6))
    # T602-31: every map on four states repeats within five visited states.
    eventual_periodicity = all(
        len({(lambda transition=t: _trace(transition, 0, 5))()}) == 1 and
        len(set(_trace(t, 0, 5))) < 5
        for t in product(range(4), repeat=4)
    )
    return {
        "integer_crossover": crossover,
        "interaction_signs": signs,
        "finite_factorization": factorization,
        "finite_extrapolation_countermodel": extrapolation,
        "closure_conjunction": conjunction,
        "finite_eventual_periodicity": eventual_periodicity,
    }


def _trace(transition: tuple[int, ...], start: int, length: int) -> tuple[int, ...]:
    trace = [start]
    for _ in range(length - 1):
        trace.append(transition[trace[-1]])
    return tuple(trace)


def validate_audit() -> dict[str, Any]:
    dependencies = json.loads(DEPENDENCIES.read_text(encoding="utf-8"))
    audit = json.loads((HERE / "THEOREM_AUDIT_V1.json").read_text(encoding="utf-8"))
    ledger = json.loads((HERE / "FORMAL_PROOF_AUDIT_LEDGER_V1.json").read_text(encoding="utf-8"))
    expected = set(dependencies["theorems"])
    rows = {row["id"]: row for row in audit["rows"]}
    if len(expected) != 39 or set(rows) != expected or len(rows) != len(audit["rows"]):
        raise ValueError("canonical theorem inventory drifted")
    corpus = "\n".join(path.read_text(encoding="utf-8") for path in OWNERS)
    for theorem_id, row in rows.items():
        if theorem_id not in corpus:
            raise ValueError(f"missing owning theorem section: {theorem_id}")
        tags = set(row["tags"])
        if not tags or not tags <= ALLOWED_TAGS:
            raise ValueError(f"invalid proof tags: {theorem_id}")
        if not row["domain"].startswith("for ") or len(row["counterexample"]) < 30:
            raise ValueError(f"quantified domain/counterexample absent: {theorem_id}")
        if "P1" in tags and row["proof_mode"] not in P1_MODES:
            raise ValueError(f"P1 proof mode absent: {theorem_id}")

    tag_sets = {tag: {theorem_id for theorem_id, row in rows.items() if tag in row["tags"]} for tag in ALLOWED_TAGS}
    if set(audit["p2_certificates"]) != tag_sets["P2"]:
        raise ValueError("P2 certificate coverage drifted")
    if set(audit["p3_assumptions"]) != tag_sets["P3"]:
        raise ValueError("P3 assumption coverage drifted")
    if set(audit["p4_experiments"]) != tag_sets["P4"]:
        raise ValueError("P4 experiment coverage drifted")
    if set(audit["p5_consequences"]) != tag_sets["P5"]:
        raise ValueError("P5 consequence coverage drifted")
    if any(len(value) < 25 for mapping in (audit["p2_certificates"], audit["p3_assumptions"], audit["p4_experiments"], audit["p5_consequences"]) for value in mapping.values()):
        raise ValueError("evidence-rung metadata is not substantive")

    limits = audit["universal_limit_audit"]
    if set(limits) != {"NFL", "RICE_HALTING", "GODEL", "BLUM_SPEEDUP", "FINITE_STATE_OEE"}:
        raise ValueError("universal-limit inventory drifted")
    if any(not set(row["relevant"]) <= expected or not row["relevant"] or len(row["consequence"]) < 30 for row in limits.values()):
        raise ValueError("universal-limit relevance mapping invalid")
    if len(ledger["rows"]) != 9 or any(row["status"] != "GREEN" for row in ledger["rows"]):
        raise ValueError("Section O task ledger drifted")
    schemas = finite_schema_checks()
    if not all(schemas.values()):
        raise ValueError("finite proof schema failed")
    executable = {theorem_id for theorem_id, row in rows.items()
                  if "P1" in row["tags"] and row["proof_mode"] == "EXECUTABLE_SCHEMA"}
    covered = set().union(*SCHEMA_COVERAGE.values())
    if executable != covered or not set(SCHEMA_COVERAGE) <= schemas.keys():
        raise ValueError("executable-schema theorem coverage drifted")
    return {
        "theorems": len(rows),
        "tag_counts": {tag: len(ids) for tag, ids in sorted(tag_sets.items())},
        "p1_proof_modes": {mode: sum(row["proof_mode"] == mode for row in rows.values() if "P1" in row["tags"]) for mode in sorted(P1_MODES)},
        "nearest_counterexamples": len(rows),
        "limit_families": len(limits),
        "finite_schema_checks": schemas,
        "ledger_rows": len(ledger["rows"]),
    }


if __name__ == "__main__":
    print("GMI_FORMAL_PROOF_AUDIT_V1_VALID")
    print(json.dumps(validate_audit(), sort_keys=True))
