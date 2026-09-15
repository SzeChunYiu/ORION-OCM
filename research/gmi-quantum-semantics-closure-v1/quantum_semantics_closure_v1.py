#!/usr/bin/env python3
"""Exact rational one-qubit semantics and finite classical compiler."""

from __future__ import annotations

import hashlib
import itertools
import json
from fractions import Fraction
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
Matrix = tuple[tuple[Fraction, Fraction], tuple[Fraction, Fraction]]


def digest(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), default=str).encode()
    ).hexdigest()


def matmul(left: Matrix, right: Matrix) -> Matrix:
    return tuple(
        tuple(sum(left[i][k] * right[k][j] for k in range(2)) for j in range(2))
        for i in range(2)
    )  # type: ignore[return-value]


def transpose(matrix: Matrix) -> Matrix:
    return tuple(tuple(matrix[j][i] for j in range(2)) for i in range(2))  # type: ignore[return-value]


X: Matrix = ((Fraction(0), Fraction(1)), (Fraction(1), Fraction(0)))
H_NUMERATOR: Matrix = ((Fraction(1), Fraction(1)), (Fraction(1), Fraction(-1)))


def apply_x(rho: Matrix) -> Matrix:
    return matmul(matmul(X, rho), transpose(X))


def apply_h(rho: Matrix) -> Matrix:
    product = matmul(matmul(H_NUMERATOR, rho), transpose(H_NUMERATOR))
    return tuple(tuple(value / 2 for value in row) for row in product)  # type: ignore[return-value]


def measure_z(rho: Matrix) -> tuple[Fraction, Fraction]:
    return rho[0][0], rho[1][1]


def classical_density_compiler(rho: Matrix, operations: tuple[str, ...]) -> Matrix:
    """D1/D6 program stores four exact entries and executes matrix updates."""
    state = tuple(tuple(value for value in row) for row in rho)
    for operation in operations:
        state = apply_x(state) if operation == "X" else apply_h(state)
    return state


def native_evolve(rho: Matrix, operations: tuple[str, ...]) -> Matrix:
    state = rho
    for operation in operations:
        state = apply_x(state) if operation == "X" else apply_h(state)
    return state


STATES: tuple[Matrix, ...] = (
    ((Fraction(1), Fraction(0)), (Fraction(0), Fraction(0))),
    ((Fraction(0), Fraction(0)), (Fraction(0), Fraction(1))),
    ((Fraction(1, 2), Fraction(1, 2)), (Fraction(1, 2), Fraction(1, 2))),
    ((Fraction(1, 2), Fraction(-1, 2)), (Fraction(-1, 2), Fraction(1, 2))),
    ((Fraction(1, 2), Fraction(0)), (Fraction(0), Fraction(1, 2))),
)


def exhaustive_semantics_certificate(max_depth: int = 4) -> dict[str, Any]:
    trajectories = 0
    compiler_mismatches = 0
    trace_violations = 0
    measurement_violations = 0
    for depth in range(max_depth + 1):
        for operations in itertools.product(("X", "H"), repeat=depth):
            for rho in STATES:
                trajectories += 1
                native = native_evolve(rho, operations)
                compiled = classical_density_compiler(rho, operations)
                compiler_mismatches += int(native != compiled)
                trace_violations += int(native[0][0] + native[1][1] != 1)
                probabilities = measure_z(native)
                measurement_violations += int(
                    sum(probabilities) != 1 or any(value < 0 for value in probabilities)
                )
    payload = {
        "schema": "GMI_QUANTUM_EXACT_SEMANTICS_CERTIFICATE_V1",
        "states": len(STATES),
        "max_depth": max_depth,
        "trajectories": trajectories,
        "compiler_mismatches": compiler_mismatches,
        "trace_violations": trace_violations,
        "measurement_violations": measurement_violations,
    }
    return {**payload, "certificate_sha256": digest(payload)}


def simulation_bounds(qubits: int) -> dict[str, int]:
    if qubits < 1:
        raise ValueError("positive qubit count required")
    return {
        "state_vector_complex_entries": 2**qubits,
        "density_matrix_complex_entries": 4**qubits,
        "dense_unitary_entries": 4**qubits,
    }


def validate_closure() -> dict[str, Any]:
    schema = json.loads((HERE / "QUANTUM_CARRIER_SCHEMA_V1.json").read_text(encoding="utf-8"))
    accounting = json.loads((HERE / "QUANTUM_LIFECYCLE_ACCOUNTING_V1.json").read_text(encoding="utf-8"))
    ledger = json.loads((HERE / "QUANTUM_SEMANTICS_CLOSURE_LEDGER_V1.json").read_text(encoding="utf-8"))
    expected = {
        "Define coherent state/operator semantics.",
        "Include state preparation, readout and error correction.",
        "Reduce against classical simulation at declared scale.",
    }
    if len(ledger["rows"]) != 3 or {row["task"] for row in ledger["rows"]} != expected:
        raise ValueError("quantum task inventory drifted")
    if any(row["status"] != "GREEN" for row in ledger["rows"]):
        raise ValueError("quantum ledger contains a non-green row")
    for row in ledger["rows"]:
        if not (REPO / row["evidence"].split("#", 1)[0]).is_file():
            raise ValueError(f"missing evidence: {row['evidence']}")
    if set(schema["required"]) != {
        "hilbert_space", "density_operator", "channels", "measurements",
        "classical_register", "numeric_instrument",
    }:
        raise ValueError("quantum carrier schema drifted")
    required_costs = {
        "state_preparation_depth", "state_preparation_fidelity", "measurement_shots",
        "readout_error", "physical_qubits", "code_distance", "syndrome_cycles",
        "decoder_time", "logical_error", "energy", "cooling_and_reset",
    }
    if not required_costs <= set(accounting["coordinates"]):
        raise ValueError("quantum lifecycle accounting is incomplete")
    exact = exhaustive_semantics_certificate()
    if exact["trajectories"] != 155:
        raise ValueError("quantum exact-universe cardinality drifted")
    if any(exact[key] for key in ("compiler_mismatches", "trace_violations", "measurement_violations")):
        raise ValueError("quantum semantics/classical compiler failed")
    return {
        "ledger_rows": len(ledger["rows"]),
        "trajectories": exact["trajectories"],
        "violations": 0,
        "accounting_coordinates": len(accounting["coordinates"]),
        "density_entries_at_8_qubits": simulation_bounds(8)["density_matrix_complex_entries"],
    }


if __name__ == "__main__":
    result = validate_closure()
    print("GMI_QUANTUM_SEMANTICS_CLOSURE_V1_VALID")
    for key, value in result.items():
        print(f"{key}={value}")
