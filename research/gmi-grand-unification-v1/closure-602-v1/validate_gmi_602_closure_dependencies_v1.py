#!/usr/bin/env python3
"""Fail-closed structural validator for the #602 formal closure spine."""

from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
DEP = HERE / "GMI_602_CLOSURE_DEPENDENCIES_V1.json"
SPINE = HERE / "GMI_602_PARENT_ATLAS_AND_FORMAL_CLOSURE_V1.md"
PARENT = ROOT.parent / "machine-intelligence-morphogenesis-v1" / "PARENT_LEDGER_V2.json"

EXPECTED_SECTIONS = tuple(chr(c) for c in range(ord("A"), ord("V") + 1))
EXPECTED_THEOREMS = {
    *(f"T602-{i:02d}" for i in range(1, 17)),
    "T602-17",
    "T602-17b",
    *(f"T602-{i:02d}" for i in range(18, 24)),
}


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def main() -> None:
    dep = load_json(DEP)
    parent = load_json(PARENT)
    spine = SPINE.read_text(encoding="utf-8")

    assert dep["schema"] == "GMI_602_CLOSURE_DEPENDENCIES_V1"
    assert isinstance(parent, dict) and parent, "specialist parent ledger must parse as a nonempty JSON object"
    assert PARENT.stat().st_size > 10_000, "specialist parent ledger unexpectedly collapsed"

    sections = dep["sections"]
    assert tuple(sections.keys()) == EXPECTED_SECTIONS, "A..V section ledger must be complete and ordered"
    for name, row in sections.items():
        assert row.get("formal_status"), f"{name}: missing formal_status"
        assert row.get("evidence_status"), f"{name}: missing evidence_status"
        assert isinstance(row.get("blockers"), list), f"{name}: blockers must be explicit"

    theorem_ids = set(dep["theorems"])
    assert theorem_ids == EXPECTED_THEOREMS, "formal theorem inventory drifted"
    for theorem_id in sorted(EXPECTED_THEOREMS):
        assert theorem_id in spine, f"{theorem_id}: declared but absent from formal spine"

    empirical = dep["empirical_claim"]
    if empirical["status"] == "EARNED":
        allowed = {"GREEN", "NOT_REQUIRED", "UPSTREAM_SPECIALIST_PARENT_LEDGER_PRESENT"}
        non_green = {
            name: row["evidence_status"]
            for name, row in sections.items()
            if row["evidence_status"] not in allowed
        }
        blockers = {name: row["blockers"] for name, row in sections.items() if row["blockers"]}
        assert not non_green, f"fail closed: empirical closure has non-green dependencies: {non_green}"
        assert not blockers, f"fail closed: empirical closure has blockers: {blockers}"

    assert empirical["status"] == "NOT_EARNED", "this branch must not silently promote empirical closure"
    assert sections["V"]["evidence_status"] == "NOT_GREEN"

    print("GMI_602_CLOSURE_DEPENDENCY_LEDGER_VALID")
    print(f"parent_ledger_bytes={PARENT.stat().st_size}")
    print(f"theorem_ids={len(theorem_ids)}")
    print(f"sections={len(sections)}")
    print("complete_empirical_closure=NOT_EARNED")


if __name__ == "__main__":
    main()
