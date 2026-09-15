#!/usr/bin/env python3
"""Finite-exact closure for Issue #602 energy-landscape tasks."""

from __future__ import annotations

import hashlib
import itertools
import json
import math
from pathlib import Path
from typing import Iterable


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
RECEIPT = (
    REPO
    / "research"
    / "machine-intelligence-morphogenesis-v1"
    / "microscopes"
    / "results"
    / "STAGE_DC_V25_DC3_ENERGY.json"
)


def neighbors_from_mask(n: int, mask: int) -> tuple[tuple[int, ...], ...]:
    """Decode one undirected simple graph on n labelled states."""
    rows = [set() for _ in range(n)]
    bit = 0
    for left in range(n):
        for right in range(left + 1, n):
            if mask & (1 << bit):
                rows[left].add(right)
                rows[right].add(left)
            bit += 1
    return tuple(tuple(sorted(row)) for row in rows)


def relax_state(
    state: int, energies: tuple[int, ...], neighbors: tuple[tuple[int, ...], ...]
) -> int:
    """Choose the lowest-energy strict improvement, breaking ties by state id."""
    improvements = [other for other in neighbors[state] if energies[other] < energies[state]]
    return min(improvements, key=lambda other: (energies[other], other)) if improvements else state


def compile_to_d6(
    energies: tuple[int, ...], neighbors: tuple[tuple[int, ...], ...]
) -> tuple[int, ...]:
    """The exact D6 transition-table compiler for a finite relaxation system."""
    return tuple(relax_state(state, energies, neighbors) for state in range(len(energies)))


def trajectory(start: int, transition: tuple[int, ...]) -> tuple[int, ...]:
    path = [start]
    while transition[path[-1]] != path[-1]:
        if len(path) > len(transition):
            raise AssertionError("strict relaxation failed to terminate")
        path.append(transition[path[-1]])
    return tuple(path)


def exhaustive_certificate(max_states: int = 4, energy_levels: int = 3) -> dict[str, int | str]:
    """Exhaust every labelled landscape through max_states over finite energy levels."""
    systems = 0
    state_cases = 0
    transition_mismatches = 0
    monotonicity_violations = 0
    termination_violations = 0
    for n in range(1, max_states + 1):
        graph_count = 1 << (n * (n - 1) // 2)
        for energies in itertools.product(range(energy_levels), repeat=n):
            for mask in range(graph_count):
                systems += 1
                neighbors = neighbors_from_mask(n, mask)
                compiled = compile_to_d6(energies, neighbors)
                for state in range(n):
                    state_cases += 1
                    native = relax_state(state, energies, neighbors)
                    transition_mismatches += int(native != compiled[state])
                    if native != state and not energies[native] < energies[state]:
                        monotonicity_violations += 1
                    path = trajectory(state, compiled)
                    distinct_levels = len(set(energies))
                    if len(path) - 1 > distinct_levels - 1:
                        termination_violations += 1
    payload = {
        "schema": "GMI_ENERGY_LANDSCAPE_EXHAUSTIVE_CERTIFICATE_V1",
        "max_states": max_states,
        "energy_levels": energy_levels,
        "systems": systems,
        "state_cases": state_cases,
        "transition_mismatches": transition_mismatches,
        "monotonicity_violations": monotonicity_violations,
        "termination_violations": termination_violations,
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    return {**payload, "certificate_sha256": hashlib.sha256(encoded).hexdigest()}


def description_crossover(n: int) -> int:
    """First P where an explicit P-by-n pattern store is no larger than couplings."""
    for patterns in itertools.count(1):
        coupling_bits = n * (n - 1) // 2 * max(1, math.ceil(math.log2(2 * patterns + 1)))
        if patterns * n >= coupling_bits:
            return patterns
    raise AssertionError("unreachable")


def lifecycle_cost(description: float, serve_per_query: float, reuse: int) -> float:
    return description + serve_per_query * reuse


def crossover(
    candidate_description: float,
    candidate_serve: float,
    parent_description: float,
    parent_serve: float,
) -> float:
    if candidate_serve >= parent_serve:
        raise ValueError("candidate has no high-reuse serve advantage")
    return (candidate_description - parent_description) / (parent_serve - candidate_serve)


def phase(
    reuse: int,
    candidate_description: float = 1984,
    candidate_serve: float = 3,
    parent_description: float = 128,
    parent_serve: float = 4,
) -> str:
    candidate = lifecycle_cost(candidate_description, candidate_serve, reuse)
    parent = lifecycle_cost(parent_description, parent_serve, reuse)
    if candidate < parent:
        return "ENERGY_RELAXATION"
    if parent < candidate:
        return "EXEMPLAR_PARENT"
    return "TIE"


def _receipt_digest(receipt: dict) -> str:
    payload = {key: value for key, value in receipt.items() if key != "receipt_sha256"}
    return hashlib.sha256(json.dumps(payload, sort_keys=True, default=str).encode()).hexdigest()


def validate_existing_receipt() -> dict[str, int | float | str]:
    receipt = json.loads(RECEIPT.read_text(encoding="utf-8"))
    if receipt["schema"] != "StageDC3EnergyV1" or receipt["status"] != "EXECUTED_EXACT_AT_SCOPE":
        raise ValueError("energy receipt schema/status drifted")
    if _receipt_digest(receipt) != receipt["receipt_sha256"]:
        raise ValueError("energy receipt digest mismatch")

    energy = receipt["cells"]["N32_P4_n1|HOPFIELD|wide"]
    parent = receipt["cells"]["N32_P4_n1|KNN_PAT|wide"]
    queries = receipt["ecology_facts"]["N32_P4_n1"]["n_cues"]
    if not energy["admissible"] or not parent["admissible"]:
        raise ValueError("corrected crossover cell is no longer jointly admissible")
    if energy["answer_signature"] != parent["answer_signature"]:
        raise ValueError("D6/D2 parent does not preserve the protected response")
    facts = (
        energy["desc_bits"],
        energy["native_ops"] / queries,
        parent["desc_bits"],
        parent["native_ops"] / queries,
    )
    if facts != (1984, 3.0, 128, 4.0):
        raise ValueError(f"energy crossover coordinates drifted: {facts}")
    threshold = crossover(*facts)
    if threshold != 1856 or description_crossover(32) != 124:
        raise ValueError("registered phase thresholds drifted")
    return {
        "receipt_sha256": receipt["receipt_sha256"],
        "description_crossover_patterns": description_crossover(32),
        "reuse_crossover": threshold,
        "candidate_native_serve": facts[1],
        "parent_native_serve": facts[3],
    }


def validate_closure() -> dict[str, int | float | str]:
    ledger = json.loads((HERE / "ENERGY_LANDSCAPE_CLOSURE_LEDGER_V1.json").read_text(encoding="utf-8"))
    expected_tasks = {
        "Define native energy state/operator law.",
        "Reduce against optimization/dynamical D6.",
        "Derive basin/relaxation burden laws.",
        "Predict phase regime.",
    }
    if {row["task"] for row in ledger["rows"]} != expected_tasks:
        raise ValueError("energy closure task inventory drifted")
    if len(ledger["rows"]) != 4 or any(row["status"] != "GREEN" for row in ledger["rows"]):
        raise ValueError("energy closure ledger is not exactly four green rows")
    for row in ledger["rows"]:
        path = REPO / row["evidence"].split("#", 1)[0]
        if not path.is_file():
            raise ValueError(f"missing evidence: {row['evidence']}")
    exact = exhaustive_certificate()
    if exact["systems"] != 5421 or exact["state_cases"] != 21423:
        raise ValueError("finite universe cardinality drifted")
    if any(exact[key] for key in (
        "transition_mismatches",
        "monotonicity_violations",
        "termination_violations",
    )):
        raise ValueError("finite relaxation theorem falsified")
    receipt = validate_existing_receipt()
    if (phase(1855), phase(1856), phase(1857)) != (
        "EXEMPLAR_PARENT",
        "TIE",
        "ENERGY_RELAXATION",
    ):
        raise ValueError("phase boundary is not exact")
    return {
        "ledger_rows": len(ledger["rows"]),
        "exact_systems": exact["systems"],
        "exact_state_cases": exact["state_cases"],
        "reuse_crossover": receipt["reuse_crossover"],
    }


if __name__ == "__main__":
    result = validate_closure()
    print("GMI_ENERGY_LANDSCAPE_CLOSURE_V1_VALID")
    for key, value in result.items():
        print(f"{key}={value}")
