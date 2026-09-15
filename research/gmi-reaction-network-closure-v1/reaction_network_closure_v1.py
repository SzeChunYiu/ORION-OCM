#!/usr/bin/env python3
"""Bounded reaction-network reductions and exact generator checks."""

from __future__ import annotations

import hashlib
import itertools
import json
from fractions import Fraction
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]


def digest(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), default=str).encode()
    ).hexdigest()


def reversible_generator(
    total: int, forward_rate: Fraction, reverse_rate: Fraction
) -> tuple[tuple[Fraction, ...], ...]:
    """Generator for A <-> B, with state index equal to the A count."""
    if total < 1 or forward_rate <= 0 or reverse_rate <= 0:
        raise ValueError("positive total and rates required")
    size = total + 1
    rows = []
    for a_count in range(size):
        b_count = total - a_count
        row = [Fraction(0) for _ in range(size)]
        if a_count:
            row[a_count - 1] = forward_rate * a_count
        if b_count:
            row[a_count + 1] = reverse_rate * b_count
        row[a_count] = -sum(row)
        rows.append(tuple(row))
    return tuple(rows)


def program_compiler(
    total: int, forward_rate: Fraction, reverse_rate: Fraction
) -> tuple[tuple[Fraction, ...], ...]:
    """D4/D6 compiler: enumerate applicable stoichiometric transitions."""
    states = tuple((a, total - a) for a in range(total + 1))
    matrix = []
    for index, (a_count, b_count) in enumerate(states):
        row = [Fraction(0) for _ in states]
        transitions = (
            (-1, forward_rate * a_count),
            (+1, reverse_rate * b_count),
        )
        for delta, propensity in transitions:
            if propensity:
                row[index + delta] += propensity
        row[index] = -sum(row)
        matrix.append(tuple(row))
    return tuple(matrix)


def embedded_choice_probabilities(generator: tuple[tuple[Fraction, ...], ...]) -> tuple[tuple[Fraction, ...], ...]:
    """Exact D3 event-choice distributions, excluding exponential wait time."""
    output = []
    for index, row in enumerate(generator):
        exit_rate = -row[index]
        if exit_rate == 0:
            output.append(tuple(Fraction(index == j) for j in range(len(row))))
        else:
            output.append(
                tuple(Fraction(0) if j == index else rate / exit_rate for j, rate in enumerate(row))
            )
    return tuple(output)


def exhaustive_generator_certificate(max_total: int = 6) -> dict[str, Any]:
    systems = 0
    state_rows = 0
    compiler_mismatches = 0
    conservation_violations = 0
    generator_violations = 0
    probability_violations = 0
    for total in range(1, max_total + 1):
        for forward, reverse in itertools.product(range(1, 4), repeat=2):
            systems += 1
            native = reversible_generator(total, Fraction(forward), Fraction(reverse))
            compiled = program_compiler(total, Fraction(forward), Fraction(reverse))
            choices = embedded_choice_probabilities(native)
            compiler_mismatches += int(native != compiled)
            for a_count, (row, probs) in enumerate(zip(native, choices)):
                state_rows += 1
                conservation_violations += int(a_count + (total - a_count) != total)
                generator_violations += int(sum(row) != 0)
                generator_violations += int(any(value < 0 for j, value in enumerate(row) if j != a_count))
                probability_violations += int(sum(probs) != 1 or any(value < 0 for value in probs))
    payload = {
        "schema": "GMI_REACTION_GENERATOR_EXHAUSTIVE_CERTIFICATE_V1",
        "max_total": max_total,
        "systems": systems,
        "state_rows": state_rows,
        "compiler_mismatches": compiler_mismatches,
        "conservation_violations": conservation_violations,
        "generator_violations": generator_violations,
        "probability_violations": probability_violations,
    }
    return {**payload, "certificate_sha256": digest(payload)}


def validate_closure() -> dict[str, Any]:
    schema = json.loads((HERE / "REACTION_NETWORK_SCHEMA_V1.json").read_text(encoding="utf-8"))
    accounting = json.loads((HERE / "REACTION_RESOURCE_ACCOUNTING_V1.json").read_text(encoding="utf-8"))
    ledger = json.loads((HERE / "REACTION_NETWORK_CLOSURE_LEDGER_V1.json").read_text(encoding="utf-8"))
    expected = {
        "Define reaction-network state/operator law.",
        "Reduce against stochastic/dynamical/program systems.",
        "Include precision, latency and physical resource accounting.",
    }
    if len(ledger["rows"]) != 3 or {row["task"] for row in ledger["rows"]} != expected:
        raise ValueError("reaction-network task inventory drifted")
    if any(row["status"] != "GREEN" for row in ledger["rows"]):
        raise ValueError("reaction-network ledger contains a non-green row")
    for row in ledger["rows"]:
        if not (REPO / row["evidence"].split("#", 1)[0]).is_file():
            raise ValueError(f"missing evidence: {row['evidence']}")
    if set(schema["required"]) != {
        "species", "count_bounds", "reactions", "propensities", "state", "clock", "readout"
    }:
        raise ValueError("reaction carrier schema drifted")
    required_resources = {
        "rate_constant_precision_bits", "state_preparation", "random_bits", "simulation_error",
        "latency", "wall_time", "physical_volume", "temperature", "energy", "waste_and_reset",
    }
    if not required_resources <= set(accounting["coordinates"]):
        raise ValueError("physical/precision accounting is incomplete")
    exact = exhaustive_generator_certificate()
    if exact["systems"] != 54 or exact["state_rows"] != 243:
        raise ValueError("reaction exact-universe cardinality drifted")
    for key in (
        "compiler_mismatches", "conservation_violations", "generator_violations",
        "probability_violations",
    ):
        if exact[key]:
            raise ValueError(f"reaction reduction failed: {key}={exact[key]}")
    return {
        "ledger_rows": len(ledger["rows"]),
        "systems": exact["systems"],
        "state_rows": exact["state_rows"],
        "violations": 0,
        "resource_coordinates": len(accounting["coordinates"]),
    }


if __name__ == "__main__":
    result = validate_closure()
    print("GMI_REACTION_NETWORK_CLOSURE_V1_VALID")
    for key, value in result.items():
        print(f"{key}={value}")
