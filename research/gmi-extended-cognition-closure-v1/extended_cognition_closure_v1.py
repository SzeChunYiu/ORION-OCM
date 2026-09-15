#!/usr/bin/env python3
"""Exact body-environment state-boundary witness for Issue #602."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]


def canonical_digest(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def extended_episode(bit: int, *, erase_write: bool = False) -> dict[str, Any]:
    """Zero-bit agent writes/reads a one-bit environmental mark."""
    if bit not in (0, 1):
        raise ValueError("episode bit must be binary")
    agent_state = "unit"
    environment = 0 if erase_write else bit
    # DISTRACT equalizes current agent state and non-mark observation.
    distract_observation = "unit"
    output = environment
    return {
        "input": bit,
        "agent_state_at_query": agent_state,
        "ordinary_observation_at_query": distract_observation,
        "environment_state_at_query": environment,
        "output": output,
        "correct": output == bit,
        "resources": {"internal_bits": 0, "external_bits": 1, "write_ops": 1, "read_ops": 1},
    }


def agent_only_episode(bit: int) -> dict[str, Any]:
    """Canonical deterministic zero-bit arm; both histories reach one state."""
    return {
        "input": bit,
        "agent_state_at_query": "unit",
        "ordinary_observation_at_query": "unit",
        "output": 0,
        "correct": bit == 0,
        "resources": {"internal_bits": 0, "external_bits": 0, "write_ops": 0, "read_ops": 0},
    }


def memory_parent_episode(bit: int) -> dict[str, Any]:
    """Matched D2 parent moves the same bit across the declared boundary."""
    internal_memory = bit
    return {
        "input": bit,
        "agent_state_at_query": ("unit", internal_memory),
        "ordinary_observation_at_query": "unit",
        "output": internal_memory,
        "correct": internal_memory == bit,
        "resources": {"internal_bits": 1, "external_bits": 0, "write_ops": 1, "read_ops": 1},
    }


def capability(rows: list[dict[str, Any]]) -> float:
    return sum(row["correct"] for row in rows) / len(rows)


def minimality_certificate() -> dict[str, Any]:
    rows = [extended_episode(bit) for bit in (0, 1)]
    same_agent_projection = len(
        {(row["agent_state_at_query"], row["ordinary_observation_at_query"]) for row in rows}
    ) == 1
    different_future = len({row["output"] for row in rows}) == 2
    if not same_agent_projection or not different_future:
        raise AssertionError("external-state collision was not constructed")
    return {
        "schema": "GMI_EXTERNAL_STATE_MINIMALITY_CERTIFICATE_V1",
        "same_agent_projection": same_agent_projection,
        "different_external_states": len({row["environment_state_at_query"] for row in rows}) == 2,
        "different_required_future_outputs": different_future,
        "histories": rows,
        "conclusion": "NO_FUNCTION_OF_AGENT_PROJECTION_ALONE_IS_OBLIGATION_SUFFICIENT",
        "certificate_sha256": canonical_digest(rows),
    }


def reduction_certificate() -> dict[str, Any]:
    extended = [extended_episode(bit) for bit in (0, 1)]
    parent = [memory_parent_episode(bit) for bit in (0, 1)]
    answers_equal = [row["output"] for row in extended] == [row["output"] for row in parent]
    joint_state_bits = [
        row["resources"]["internal_bits"] + row["resources"]["external_bits"] for row in extended
    ]
    parent_state_bits = [row["resources"]["internal_bits"] for row in parent]
    if not answers_equal or joint_state_bits != parent_state_bits:
        raise AssertionError("matched D2/D6 reduction failed")
    return {
        "schema": "GMI_EXTERNAL_TO_MEMORY_REDUCTION_CERTIFICATE_V1",
        "state_compiler": "(agent_state, environment_bit) -> (agent_state, internal_memory_bit)",
        "operator_compiler": "external WRITE/READ -> internal D2 WRITE/READ; joint step -> D6 transition",
        "protected_answers_equal": answers_equal,
        "joint_state_bits": joint_state_bits,
        "parent_state_bits": parent_state_bits,
        "burden_class": "E0 on total state bits and read/write counts; location/custody coordinate changes",
        "conclusion": "REDUCED_TO_PARENT_D2_D6_AT_MATCHED_FINITE_SCOPE",
    }


def validate_prediction() -> dict[str, Any]:
    freeze = json.loads((HERE / "EXTENDED_COGNITION_PREDICTION_V1.json").read_text(encoding="utf-8"))
    extended = [extended_episode(bit) for bit in (0, 1)]
    agent_only = [agent_only_episode(bit) for bit in (0, 1)]
    erased = [extended_episode(bit, erase_write=True) for bit in (0, 1)]
    parent = [memory_parent_episode(bit) for bit in (0, 1)]
    observed = {
        "extended_capability": capability(extended),
        "agent_only_zero_bit_upper_bound": capability(agent_only),
        "erase_write_negative_twin_capability": capability(erased),
        "one_bit_internal_memory_parent_capability": capability(parent),
    }
    for key, value in observed.items():
        if value != freeze["predictions"][key]:
            raise ValueError(f"prediction failed: {key}: {value}")
    # There is exactly one deterministic output function on a singleton state
    # up to its selected constant; either constant is correct on one of two bits.
    zero_bit_functions = [{bit: constant == bit for bit in (0, 1)} for constant in (0, 1)]
    if any(sum(result.values()) / 2 > 0.5 for result in zero_bit_functions):
        raise ValueError("zero-bit upper bound violated")
    minimality_certificate()
    reduction_certificate()
    return {
        **observed,
        "zero_bit_functions_exhausted": len(zero_bit_functions),
        "prediction_digest": canonical_digest(freeze),
    }


def validate_closure() -> dict[str, Any]:
    schema = json.loads((HERE / "STATE_BOUNDARY_SCHEMA_V1.json").read_text(encoding="utf-8"))
    freeze = json.loads((HERE / "EXTENDED_COGNITION_PREDICTION_V1.json").read_text(encoding="utf-8"))
    ledger = json.loads((HERE / "EXTENDED_COGNITION_CLOSURE_LEDGER_V1.json").read_text(encoding="utf-8"))
    boundary = freeze["boundary"]
    if set(boundary) != set(schema["required"]):
        raise ValueError("state boundary does not instantiate every required coordinate exactly")
    expected = {
        "Define boundary between machine state and environmental state.",
        "Derive conditions where external state is part of the minimal sufficient cognitive carrier.",
        "Reduce against ordinary memory/tool-use formulations.",
        "Predict ecology where embodiment becomes irreducible.",
    }
    if len(ledger["rows"]) != 4 or {row["task"] for row in ledger["rows"]} != expected:
        raise ValueError("extended cognition ledger inventory drifted")
    if any(row["status"] != "GREEN" for row in ledger["rows"]):
        raise ValueError("extended cognition ledger contains a non-green row")
    for row in ledger["rows"]:
        if not (REPO / row["evidence"].split("#", 1)[0]).is_file():
            raise ValueError(f"missing evidence: {row['evidence']}")
    result = validate_prediction()
    return {
        "ledger_rows": len(ledger["rows"]),
        "histories": 2,
        "zero_bit_functions_exhausted": result["zero_bit_functions_exhausted"],
        "extended_capability": result["extended_capability"],
        "agent_only_capability": result["agent_only_zero_bit_upper_bound"],
        "parent_capability": result["one_bit_internal_memory_parent_capability"],
    }


if __name__ == "__main__":
    result = validate_closure()
    print("GMI_EXTENDED_COGNITION_CLOSURE_V1_VALID")
    for key, value in result.items():
        print(f"{key}={value}")
