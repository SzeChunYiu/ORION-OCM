#!/usr/bin/env python3
"""Fail-closed validator for #602 Section-C formal specialization closure."""

from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
LEDGER = HERE / "SECTION_C_FORMAL_LEDGER_V1.json"
DOC = HERE / "GMI_SECTION_C_FORMAL_SPECIALIZATIONS_V1.md"

EXPECTED_GREEN = {f"C{i:02d}" for i in range(2, 13)}
EXPECTED_OPEN = {"C13", "C14"}
EXPECTED_SPECIALIZATIONS = {
    "gradient descent specialization",
    "reverse/local credit assignment specialization",
    "Bayesian updating specialization",
    "exemplar-memory update specialization",
    "symbolic rule induction specialization",
    "program/library learning specialization",
    "evolutionary population update specialization",
    "meta-learning / learned optimizer specialization",
    "self-modification / morphology-update specialization",
    "quantify when each law is cheaper",
    "negative ecology where each law loses",
}


def fail(msg: str) -> None:
    raise SystemExit(f"SECTION_C_FORMAL_V1_FAIL: {msg}")


def require(cond: bool, msg: str) -> None:
    if not cond:
        fail(msg)


def main() -> None:
    try:
        ledger = json.loads(LEDGER.read_text(encoding="utf-8"))
        doc = DOC.read_text(encoding="utf-8")
    except (OSError, json.JSONDecodeError) as exc:
        fail(str(exc))

    require(ledger.get("schema") == "GMI_602_SECTION_C_FORMAL_LEDGER_V1", "wrong ledger schema")
    require(ledger.get("common_update_authority", {}).get("pr") == 707, "common update object must remain owned by merged PR #707")
    require(ledger.get("common_update_authority", {}).get("status") == "MERGED", "#707 must be recorded as merged authority")
    require(ledger.get("universal_best_learning_law") is False, "cannot promote a universal best learning law")

    rows = ledger.get("rows")
    require(isinstance(rows, list) and len(rows) == 11, "expected exactly 11 formal specialization/comparison rows")
    ids = {row.get("id") for row in rows}
    require(ids == EXPECTED_GREEN, f"formal row inventory drifted: {ids}")
    names = {row.get("name") for row in rows}
    require(names == EXPECTED_SPECIALIZATIONS, "formal specialization names drifted")
    for row in rows:
        require(row.get("formal_status") == "GREEN", f"{row.get('id')}: formal status not green")
        require(bool(row.get("evidence_class")), f"{row.get('id')}: missing evidence class")
        require(bool(row.get("object")), f"{row.get('id')}: missing formal object")
        parents = row.get("parent_first")
        require(isinstance(parents, list) and parents, f"{row.get('id')}: missing strongest-parent set")
        require(bool(row.get("loses_when")), f"{row.get('id')}: missing losing/countercondition")
        require(row.get("prospective_complete") is False, f"{row.get('id')}: formal row illegally promoted prospective completion")
        require(row["id"] in doc, f"{row['id']}: theorem/section missing from formal document")

    prospective = ledger.get("prospective_rows")
    require(isinstance(prospective, list) and len(prospective) == 2, "expected exactly two prospective Section-C rows")
    require({row.get("id") for row in prospective} == EXPECTED_OPEN, "prospective row inventory drifted")
    for row in prospective:
        require(row.get("status") == "OPEN", f"{row.get('id')}: prospective row must remain open")
        require(bool(row.get("required_evidence")), f"{row.get('id')}: missing required evidence")

    counts = ledger.get("counts", {})
    require(counts.get("formal_specialization_or_comparison_rows_green") == 11, "formal green count drifted")
    require(counts.get("prospective_rows_open") == 2, "prospective open count drifted")

    forbidden = (
        "UNIVERSAL_BEST_LEARNING_LAW",
        "SECTION_C_NEUTRAL_RECOVERY_COMPLETE",
        "HELDOUT_LEARNING_LAW_PREDICTION_COMPLETE",
        "COMPLETE_GMI_LEARNING_LAW_CLOSURE",
    )
    for token in forbidden:
        require(token in doc, f"claim-boundary token missing: {token}")

    print("GMI_SECTION_C_FORMAL_V1_VALID")
    print("formal_rows_green=11")
    print("prospective_rows_open=2")
    print("common_update_authority_pr=707")
    print("complete_section_c_empirical_closure=NOT_EARNED")


if __name__ == "__main__":
    main()
