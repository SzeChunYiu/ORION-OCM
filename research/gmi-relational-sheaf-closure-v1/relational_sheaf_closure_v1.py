#!/usr/bin/env python3
"""Fail-closed reconciliation of Issue #602 relational/sheaf tasks."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
RECEIPT = REPO / "research/machine-intelligence-morphogenesis-v1/microscopes/results/STAGE_DN_V26_N3_SHEAF.json"


def receipt_digest(receipt: dict[str, Any]) -> str:
    payload = {key: value for key, value in receipt.items() if key != "receipt_sha256"}
    return hashlib.sha256(json.dumps(payload, sort_keys=True, default=str).encode()).hexdigest()


def reduction_disposition(*, preserves_answers: bool, status: str, burden_witness: str | None) -> str:
    """A failed reduction cannot become novelty without a material burden witness."""
    if preserves_answers:
        return "REDUCED_TO_PARENT"
    if status == "REDUCTION_FAILED" and not burden_witness:
        return "CANNOT_IDENTIFY"
    if status == "REDUCTION_FAILED":
        return "RESIDUAL_WITH_BURDEN_WITNESS"
    raise ValueError("unknown reduction status")


def validate_receipt() -> dict[str, Any]:
    receipt = json.loads(RECEIPT.read_text(encoding="utf-8"))
    if receipt["schema"] != "StageDNN3SheafV1" or receipt["status"] != "EXECUTED_EXACT_AT_SCOPE":
        raise ValueError("sheaf receipt schema/status drifted")
    if receipt_digest(receipt) != receipt["receipt_sha256"]:
        raise ValueError("sheaf receipt digest mismatch")
    equality = receipt["developmental_equality"]
    table = [value for key, value in equality.items() if key.endswith("SHEAF_vs_TABLE_MAT")]
    search = [value for key, value in equality.items() if key.endswith("SHEAF_vs_PROG_SEARCH")]
    twin = [value for key, value in equality.items() if key.endswith("SHEAF_vs_SHEAF_NOGLUE")]
    if len(table) != 22 or len(search) != 22 or not all(table + search):
        raise ValueError("parent answer equality no longer holds in 22/22 pairs")
    if len(twin) != 22 or any(twin):
        raise ValueError("no-glue negative twin no longer separates")
    niche = {
        key: value
        for key, value in receipt["frontier"].items()
        if key.startswith("n10_d3_late") and value == ["SHEAF"]
    }
    if not niche or not any("|reduced|H=1024" in key for key in niche):
        raise ValueError("predicted late-failure frontier niche disappeared")
    if len(receipt["cells"]) != 110 or len(receipt["frontier"]) != 508:
        raise ValueError("executed receipt coverage drifted")
    return {
        "receipt_sha256": receipt["receipt_sha256"],
        "cells": len(receipt["cells"]),
        "frontier_cells": len(receipt["frontier"]),
        "table_equalities": len(table),
        "search_equalities": len(search),
        "negative_twin_separations": sum(not value for value in twin),
        "late_niche_cells": len(niche),
    }


def validate_closure() -> dict[str, Any]:
    ledger = json.loads((HERE / "RELATIONAL_SHEAF_CLOSURE_LEDGER_V1.json").read_text(encoding="utf-8"))
    expected = {
        "Build local-section/gluing/obstruction families.",
        "Reduce against CSP/SAT.",
        "Reduce against factor graphs/probabilistic graphical models.",
        "Reduce against GNN/message passing.",
        "Reduce against distributed D7.",
        "Require burden-separation witness if reduction fails.",
        "Predict ecology where it enters the frontier.",
    }
    if len(ledger["rows"]) != 7 or {row["task"] for row in ledger["rows"]} != expected:
        raise ValueError("relational/sheaf task inventory drifted")
    if any(row["status"] != "GREEN" for row in ledger["rows"]):
        raise ValueError("relational/sheaf ledger contains a non-green row")
    for row in ledger["rows"]:
        if not (REPO / row["evidence"].split("#", 1)[0]).is_file():
            raise ValueError(f"missing evidence: {row['evidence']}")
    receipt = validate_receipt()
    if reduction_disposition(preserves_answers=False, status="REDUCTION_FAILED", burden_witness=None) != "CANNOT_IDENTIFY":
        raise ValueError("burden witness gate is not fail-closed")
    if reduction_disposition(preserves_answers=True, status="REDUCTION_FAILED", burden_witness=None) != "REDUCED_TO_PARENT":
        raise ValueError("successful parent equality was not respected")
    return {"ledger_rows": 7, **{key: receipt[key] for key in (
        "cells", "frontier_cells", "table_equalities", "search_equalities",
        "negative_twin_separations", "late_niche_cells",
    )}}


if __name__ == "__main__":
    result = validate_closure()
    print("GMI_RELATIONAL_SHEAF_CLOSURE_V1_VALID")
    for key, value in result.items():
        print(f"{key}={value}")
