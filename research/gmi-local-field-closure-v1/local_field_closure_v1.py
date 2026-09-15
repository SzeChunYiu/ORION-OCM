#!/usr/bin/env python3
"""Exact interventions and receipt reconciliation for Issue #602 local fields."""

from __future__ import annotations

import hashlib
import json
from itertools import product
from pathlib import Path
from typing import Any, Iterable


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
RECEIPT = REPO / (
    "research/machine-intelligence-morphogenesis-v1/microscopes/results/"
    "STAGE_DC_V30_DC2_FIELD.json"
)


def receipt_digest(receipt: dict[str, Any]) -> str:
    payload = {key: value for key, value in receipt.items() if key != "receipt_sha256"}
    return hashlib.sha256(json.dumps(payload, sort_keys=True, default=str).encode()).hexdigest()


def elementary_step(rule: int, state: Iterable[int], topology: str = "ring") -> tuple[int, ...]:
    values = tuple(state)
    if not 0 <= rule < 256 or len(values) < 3 or any(bit not in (0, 1) for bit in values):
        raise ValueError("rule/state outside binary elementary-automaton domain")
    if topology not in {"ring", "path"}:
        raise ValueError("topology must be ring or path")
    length = len(values)
    output = []
    for index, centre in enumerate(values):
        left = values[index - 1] if index > 0 else (values[-1] if topology == "ring" else 0)
        right = values[index + 1] if index + 1 < length else (values[0] if topology == "ring" else 0)
        neighbourhood = 4 * left + 2 * centre + right
        output.append((rule >> neighbourhood) & 1)
    return tuple(output)


def lesion_regeneration_certificate() -> dict[str, Any]:
    lengths = (4, 8, 16, 32)
    repaired: dict[int, int] = {}
    identity_repaired: dict[int, int] = {}
    for length in lengths:
        target = (1,) * length
        lesions = [target[:site] + (0,) + target[site + 1 :] for site in range(length)]
        repaired[length] = sum(elementary_step(232, lesion) == target for lesion in lesions)
        identity_repaired[length] = sum(elementary_step(204, lesion) == target for lesion in lesions)
    return {
        "rule": 232,
        "negative_control_rule": 204,
        "lesion_kind": "one zero in all-one fixed point",
        "repaired": repaired,
        "negative_control_repaired": identity_repaired,
    }


def topology_sensitivity_certificate() -> dict[str, Any]:
    lengths = (4, 8, 12)
    differing: dict[int, int] = {}
    expected: dict[int, int] = {}
    for length in lengths:
        differing[length] = sum(
            elementary_step(90, state, "ring") != elementary_step(90, state, "path")
            for state in product((0, 1), repeat=length)
        )
        expected[length] = 3 * 2 ** (length - 2)
    witness = (0, 0, 0, 1)
    return {
        "rule": 90,
        "boundary": "zero outside path",
        "differing": differing,
        "expected": expected,
        "fraction": "3/4",
        "witness": witness,
        "ring_output": elementary_step(90, witness, "ring"),
        "path_output": elementary_step(90, witness, "path"),
    }


def validate_receipt() -> dict[str, Any]:
    receipt = json.loads(RECEIPT.read_text(encoding="utf-8"))
    if receipt["schema"] != "StageDC2FieldV1" or receipt["status"] != "EXECUTED_EXACT_AT_SCOPE":
        raise ValueError("field receipt schema/status drifted")
    if receipt_digest(receipt) != receipt["receipt_sha256"]:
        raise ValueError("field receipt digest mismatch")
    if len(receipt["cells"]) != 576 or len(receipt["frontier"]) != 1152:
        raise ValueError("field receipt coverage drifted")
    separations = receipt["separation_by_L"]
    if len(separations) != 16:
        raise ValueError("field scaling-group count drifted")
    for key, row in separations.items():
        length = int(key.split("_", 1)[0][1:])
        if row["desc_field"] != 8 or row["desc_field_nonlocal"] != 8 * length:
            raise ValueError("linear description law drifted")
        if row["description_ratio"] != length:
            raise ValueError("description ratio drifted")
    equality = receipt["field_equals_field_nonlocal_answers"]
    if len(equality) != 144 or sum(equality.values()) != 60:
        raise ValueError("shared/unshared answer comparison drifted")
    return {
        "ecology_cells": 144,
        "machine_cells": 576,
        "frontier_cells": 1152,
        "answer_equalities": 60,
        "scaling_groups": 16,
    }


def validate_closure() -> dict[str, Any]:
    ledger = json.loads((HERE / "LOCAL_FIELD_CLOSURE_LEDGER_V1.json").read_text(encoding="utf-8"))
    expected = {
        "Local-radius execution microscope.",
        "Lesion/regeneration experiments.",
        "Topology sensitivity.",
        "Scaling law.",
        "Reduce against D6 dynamical systems.",
        "Reduce against D7 distributed systems.",
        "Reduce against GNN/NCA parents.",
    }
    if len(ledger["rows"]) != 7 or {row["task"] for row in ledger["rows"]} != expected:
        raise ValueError("local-field task inventory drifted")
    if any(row["status"] != "GREEN" for row in ledger["rows"]):
        raise ValueError("local-field closure contains a non-green row")
    for row in ledger["rows"]:
        if not (REPO / row["evidence"].split("#", 1)[0]).is_file():
            raise ValueError(f"missing evidence: {row['evidence']}")

    lesions = lesion_regeneration_certificate()
    if lesions["repaired"] != {4: 4, 8: 8, 16: 16, 32: 32}:
        raise ValueError("single-site regeneration law drifted")
    if any(lesions["negative_control_repaired"].values()):
        raise ValueError("identity negative control unexpectedly repaired a lesion")
    topology = topology_sensitivity_certificate()
    if topology["differing"] != topology["expected"]:
        raise ValueError("topology sensitivity law drifted")
    if topology["ring_output"] == topology["path_output"]:
        raise ValueError("topology witness no longer separates")
    return {"ledger_rows": 7, **validate_receipt(), "topology_fraction": "3/4"}


if __name__ == "__main__":
    result = validate_closure()
    print("GMI_LOCAL_FIELD_CLOSURE_V1_VALID")
    for key, value in result.items():
        print(f"{key}={value}")
