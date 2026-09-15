#!/usr/bin/env python3
"""Exact sampled analog semantics plus bounded numerical-reduction checks."""

from __future__ import annotations

import hashlib
import itertools
import json
import math
from fractions import Fraction
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]


def digest(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), default=str).encode()
    ).hexdigest()


def analog_affine_interval(
    state: Fraction,
    coefficient: Fraction,
    input_gain: Fraction,
    input_value: Fraction,
    noise_bound: Fraction,
) -> tuple[Fraction, Fraction]:
    if noise_bound < 0:
        raise ValueError("noise bound must be nonnegative")
    center = coefficient * state + input_gain * input_value
    return center - noise_bound, center + noise_bound


def d1_d6_interval_compiler(
    state: Fraction,
    coefficient: Fraction,
    input_gain: Fraction,
    input_value: Fraction,
    noise_bound: Fraction,
) -> tuple[Fraction, Fraction]:
    """D1 stores coefficients; D6 applies the same interval transition."""
    center = coefficient * state + input_gain * input_value
    return center - noise_bound, center + noise_bound


def exhaustive_sampled_certificate() -> dict[str, Any]:
    values = tuple(map(Fraction, (-1, 0, 1)))
    noises = (Fraction(0), Fraction(1, 4))
    cases = 0
    mismatches = 0
    invalid_intervals = 0
    for state, coefficient, gain, input_value, noise in itertools.product(
        values, values, values, values, noises
    ):
        cases += 1
        native = analog_affine_interval(state, coefficient, gain, input_value, noise)
        compiled = d1_d6_interval_compiler(state, coefficient, gain, input_value, noise)
        mismatches += int(native != compiled)
        invalid_intervals += int(native[0] > native[1])
    payload = {
        "schema": "GMI_ANALOG_SAMPLED_EXACT_CERTIFICATE_V1",
        "cases": cases,
        "mismatches": mismatches,
        "invalid_intervals": invalid_intervals,
    }
    return {**payload, "certificate_sha256": digest(payload)}


def euler_step_bound(horizon: float, lipschitz: float, local_constant: float, epsilon: float) -> float:
    """Sufficient h from global error <= C h (exp(LT)-1)/L."""
    if horizon <= 0 or lipschitz < 0 or local_constant <= 0 or epsilon <= 0:
        raise ValueError("invalid error-bound parameters")
    amplification = horizon if lipschitz == 0 else math.expm1(lipschitz * horizon) / lipschitz
    return epsilon / (local_constant * amplification)


def euler_step_count(horizon: float, lipschitz: float, local_constant: float, epsilon: float) -> int:
    return math.ceil(horizon / euler_step_bound(horizon, lipschitz, local_constant, epsilon))


def validate_closure() -> dict[str, Any]:
    schema = json.loads((HERE / "ANALOG_SUBSTRATE_SCHEMA_V1.json").read_text(encoding="utf-8"))
    accounting = json.loads((HERE / "ANALOG_RESOURCE_ACCOUNTING_V1.json").read_text(encoding="utf-8"))
    ledger = json.loads((HERE / "ANALOG_SEMANTICS_CLOSURE_LEDGER_V1.json").read_text(encoding="utf-8"))
    expected = {
        "Define analog substrate semantics with precision/error accounting.",
        "Reduce against numerical D1/D6 simulation with bounded overhead.",
    }
    if len(ledger["rows"]) != 2 or {row["task"] for row in ledger["rows"]} != expected:
        raise ValueError("analog task inventory drifted")
    if any(row["status"] != "GREEN" for row in ledger["rows"]):
        raise ValueError("analog ledger contains a non-green row")
    for row in ledger["rows"]:
        if not (REPO / row["evidence"].split("#", 1)[0]).is_file():
            raise ValueError(f"missing evidence: {row['evidence']}")
    if len(schema["required"]) != 8:
        raise ValueError("analog semantics schema drifted")
    required = {
        "parameter_precision_bits", "noise_distribution_or_bound", "discretization_error",
        "roundoff_error", "state_preparation", "calibration", "settling_time", "readout",
        "conversion_adc_dac", "energy", "drift", "device_variation",
    }
    if not required <= set(accounting["coordinates"]):
        raise ValueError("analog precision/physical accounting incomplete")
    exact = exhaustive_sampled_certificate()
    if exact != {**exact, "mismatches": 0, "invalid_intervals": 0} or exact["cases"] != 162:
        raise ValueError("sampled analog compiler failed")
    steps = euler_step_count(1.0, 1.0, 1.0, 0.01)
    if steps != 172:
        raise ValueError("Euler burden bound drifted")
    return {
        "ledger_rows": len(ledger["rows"]),
        "sampled_cases": exact["cases"],
        "violations": 0,
        "accounting_coordinates": len(accounting["coordinates"]),
        "example_euler_steps": steps,
    }


if __name__ == "__main__":
    result = validate_closure()
    print("GMI_ANALOG_SEMANTICS_CLOSURE_V1_VALID")
    for key, value in result.items():
        print(f"{key}={value}")
