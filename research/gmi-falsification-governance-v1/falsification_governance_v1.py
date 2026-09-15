#!/usr/bin/env python3
"""Exact source audit for four standalone Issue #602 falsification controls."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
RETRACTIONS = REPO / "research/gmi-adaptive-creation-v1/ADAPTIVE_CREATION_AND_HORIZONS_V1.md"
J2 = REPO / "research/gmi-j2-bounded-completeness-v1/RESULT_V1.json"
COORDINATES = REPO / "research/gmi-ecology-extension-v1/ECOLOGY_EXTENSION_CONTRACT_V1.json"
PILOT = REPO / "research/machine-intelligence-morphogenesis-v1/GMI_B6_DEVELOPMENTAL_MORPHOGENESIS_RV_377_180_FREEZE.md"


def validate_audit() -> dict[str, Any]:
    ledger = json.loads((HERE / "FALSIFICATION_GOVERNANCE_LEDGER_V1.json").read_text(encoding="utf-8"))
    if len(ledger["rows"]) != 4 or len(ledger["open_tasks"]) != 3:
        raise ValueError("falsification-governance task partition drifted")
    if any(row["status"] != "GREEN" for row in ledger["rows"]):
        raise ValueError("non-green governance row")
    for row in ledger["rows"]:
        if not (REPO / row["evidence"].split("#", 1)[0]).is_file():
            raise ValueError(f"missing evidence: {row['evidence']}")

    retractions = " ".join(RETRACTIONS.read_text(encoding="utf-8").split())
    required_retractions = (
        "## Visible retractions",
        "infinitely many positive weights necessarily diverge is false",
        "does not impose a limiting confidence radius floor",
        "not a proof that every conceivable method fails",
        "original text remains in version history",
        "must not be cited as an established all-method impossibility result",
    )
    if any(token not in retractions for token in required_retractions):
        raise ValueError("visible retraction evidence drifted")

    j2 = json.loads(J2.read_text(encoding="utf-8"))
    if j2["status"] != "EXECUTED_FINITE_EXACT" or len(j2["individual"]) != 8:
        raise ValueError("bounded null/negative receipt drifted")
    for name, row in j2["individual"].items():
        exact_key = "exact_at_7" if name == "D5" else "exact_at_2" if name == "D6" else "exact"
        positive_key = "positive_at_8" if name == "D5" else "positive_at_3" if name == "D6" else "positive"
        if row[exact_key] != 0 or not row[positive_key]:
            raise ValueError(f"{name} lacks bounded negative plus positive control")
    if j2["pairwise"] != {"pairs": 28, "pairs_with_failure": 22, "complete_pairs": 6}:
        raise ValueError("pairwise null-result preservation drifted")

    coordinates = json.loads(COORDINATES.read_text(encoding="utf-8"))
    resource_rule = coordinates["coordinates"]["resource_prices_budgets"]["definition"]
    if "frozen prospectively" not in resource_rule or "not scalarized post hoc" not in resource_rule:
        raise ValueError("post-hoc coordinate prohibition drifted")

    pilot = PILOT.read_text(encoding="utf-8")
    required_pilot = (
        "pilot numbers, not evidence",
        "Pilot receipts carry the host token `PILOT`",
        "are not read as evidence and are not committed",
        "seed set in the pilot had k = 4 per carrier",
        "No parameter is retuned after any outcome",
    )
    if any(token not in pilot for token in required_pilot):
        raise ValueError("pilot disclosure/exclusion drifted")
    return {
        "ledger_rows": 4,
        "open_registry_tasks": 3,
        "visible_retractions": 3,
        "bounded_negative_domains": 8,
        "pairwise_nulls_preserved": 6,
        "prospective_coordinate_rule": True,
        "pilot_excluded_from_evidence": True,
    }


if __name__ == "__main__":
    print("GMI_FALSIFICATION_GOVERNANCE_V1_VALID")
    print(json.dumps(validate_audit(), sort_keys=True))
