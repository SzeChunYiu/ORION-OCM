from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / "research" / "gmi-833-morphology-selection-v1"
SPEC = importlib.util.spec_from_file_location("gmi_833_morphology_selection_v1", PACKAGE / "selection_v1.py")
M = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name] = M
SPEC.loader.exec_module(M)


def test_morphology_selection_receipt_is_exact_and_green():
    receipt = M.build_receipt(M.audit_parents(ROOT))
    assert receipt["verdict"] == "GREEN"
    assert all(receipt["checks"].values())
    assert M.canonical_json(receipt) == (PACKAGE / "RESULT_V1.json").read_text()


def test_morphology_selection_reconciliation_is_exactly_two_formal_rows():
    spec = json.loads((PACKAGE / "ISSUE_833_RECONCILIATION_SELECTION_V1.json").read_text())
    assert spec["source_issue"] == 892
    assert len(spec["replacements"]) == 2
    assert all(row["anchor"] == "# J. General morphology-selection theory" for row in spec["replacements"])
    assert all(row["old"].startswith("- [ ]") and row["new"].startswith("- [x]") for row in spec["replacements"])
    exact_targets = {
        "- [ ] Derive coexistence/niche partitioning laws.",
        "- [ ] Derive morphology transitions under resource repricing.",
    }
    assert {row["old"] for row in spec["replacements"]} == exact_targets
