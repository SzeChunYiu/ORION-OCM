#!/usr/bin/env python3
"""Fail-closed structural validator for the #602 formal closure ledgers."""

from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEP = HERE / "GMI_602_CLOSURE_DEPENDENCIES_V1.json"
PARENT = HERE.parent / "machine-intelligence-morphogenesis-v1" / "PARENT_LEDGER_V2.json"

EXPECTED_SECTIONS = tuple(chr(c) for c in range(ord("A"), ord("V") + 1))
EXPECTED_THEOREMS = {
    *(f"T602-{i:02d}" for i in range(1, 17)),
    "T602-17",
    "T602-17b",
    *(f"T602-{i:02d}" for i in range(18, 24)),
}


def load(path: Path):
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def main() -> None:
    dep = load(DEP)
    parent = load(PARENT)

    assert dep["schema"] == "GMI_602_CLOSURE_DEPENDENCIES_V1"
    assert parent["schema"] == "GMI_PARENT_LEDGER_V2"
    assert len(parent["records"]) >= 40, "parent first-refusal coverage unexpectedly shrank"

    sections = dep["sections"]
    assert tuple(sections.keys()) == EXPECTED_SECTIONS, "A..V section ledger must be complete and ordered"
    for name, row in sections.items():
        assert row.get("formal_status"), f"{name}: missing formal_status"
        assert row.get("evidence_status"), f"{name}: missing evidence_status"
        assert isinstance(row.get("blockers"), list), f"{name}: blockers must be an explicit list"

    theorem_ids = set(dep["theorems"])
    assert theorem_ids == EXPECTED_THEOREMS, "formal spine theorem inventory drifted"

    empirical = dep["empirical_claim"]
    if empirical["status"] == "EARNED":
        non_green = {
            name: row["evidence_status"]
            for name, row in sections.items()
            if row["evidence_status"] not in {"GREEN", "NOT_REQUIRED"}
        }
        assert not non_green, f"fail closed: empirical closure has non-green dependencies: {non_green}"
        blockers = {name: row["blockers"] for name, row in sections.items() if row["blockers"]}
        assert not blockers, f"fail closed: empirical closure has blockers: {blockers}"

    assert empirical["status"] == "NOT_EARNED", "this branch must not silently promote empirical closure"
    assert sections["V"]["evidence_status"] == "NOT_GREEN"

    print("GMI_602_CLOSURE_DEPENDENCY_LEDGER_VALID")
    print(f"parent_records={len(parent['records'])}")
    print(f"theorem_ids={len(theorem_ids)}")
    print(f"sections={len(sections)}")
    print("complete_empirical_closure=NOT_EARNED")


if __name__ == "__main__":
    main()
