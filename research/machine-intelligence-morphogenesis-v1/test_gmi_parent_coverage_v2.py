"""Regression gates for #602 Section-Q parent coverage V2.

V1 remains the historical audit (7 solid / 3 suspect / 13 absent).  V2 must
reproduce the explicit extension transition to 23/23 without mutating V1 or
claiming universal literature completeness.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
RESULTS = HERE / "microscopes" / "results"
AUDIT = HERE / "gmi_microscope" / "parent_coverage_audit_v2.py"
BASE_RECEIPT = RESULTS / "STAGE_PARENT_COVERAGE_V1.json"
V2_RECEIPT = RESULTS / "STAGE_PARENT_COVERAGE_V2.json"
EXTENSION = HERE.parent / "parent-absorption-v1" / "GMI_602_PARENT_EXTENSION_V1.json"


def load(path: Path):
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def test_parent_coverage_v2_reproduces_committed_receipt():
    before = V2_RECEIPT.read_text(encoding="utf-8")
    try:
        proc = subprocess.run(
            [sys.executable, str(AUDIT)],
            cwd=HERE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=60,
            check=False,
        )
        assert proc.returncode == 0, proc.stdout[-4000:]
        assert load(V2_RECEIPT) == json.loads(before)
        assert "GMI_PARENT_COVERAGE_V2_VALID" in proc.stdout
    finally:
        V2_RECEIPT.write_text(before, encoding="utf-8")


def test_v1_history_is_preserved_and_v2_transition_is_exact():
    v1 = load(BASE_RECEIPT)
    v2 = load(V2_RECEIPT)
    assert v1["traditions_total"] == 23
    assert v1["traditions_covered_solid"] == 7
    assert v1["traditions_covered_suspect"] == 3
    assert v1["traditions_uncovered"] == 13

    assert v2["v1_base_solid"] == 7
    assert v2["v1_base_suspect"] == 3
    assert v2["v1_base_uncovered"] == 13
    assert v2["extension_entries"] == 16
    assert v2["extension_explicit_traditions"] == 16
    assert len(v2["resolved_v1_suspects"]) == 3
    assert len(v2["newly_covered_v1_absences"]) == 13
    assert v2["traditions_covered_solid"] == 23
    assert v2["traditions_uncovered"] == 0
    assert v2["uncovered"] == []


def test_extension_is_explicit_one_tradition_per_record_not_token_inference():
    ext = load(EXTENSION)
    entries = ext["entries"]
    assert len(entries) == 16
    ids = [e["id"] for e in entries]
    assert len(ids) == len(set(ids))

    traditions = []
    for entry in entries:
        rows = entry["section_q_traditions"]
        assert isinstance(rows, list) and len(rows) == 1
        traditions.extend(rows)
        assert entry["parents"]
        assert all(p.get("name") and p.get("citation") for p in entry["parents"])
        assert entry["what_parent_explained"]
        assert entry["higher_order_question_remaining"]
        assert entry["parent_sufficient_at_scope"]
        assert entry["sources"]
    assert len(traditions) == len(set(traditions)) == 16


def test_coverage_does_not_promote_adequacy_or_universal_parent_completeness():
    v2 = load(V2_RECEIPT)
    ext = load(EXTENSION)
    assert v2["coverage_is_adequacy"] is False
    assert v2["all_relevant_parents_known"] is False
    assert v2["mechanism_rediscovery_is_novelty"] is False
    assert ext["claim_boundary"]["coverage_is_adequacy"] is False
    assert ext["claim_boundary"]["all_relevant_parents_known"] is False
    assert ext["claim_boundary"]["mechanism_rediscovery_is_novelty"] is False
    assert v2["v1_promiscuous_entries_retained_as_historical_signal"], (
        "V2 must not erase the V1 promiscuity finding simply because dedicated records now resolve it")


def test_parent_subtraction_keeps_more_than_one_disposition():
    ext = load(EXTENSION)
    dispositions = {entry["disposition"] for entry in ext["entries"]}
    assert "ADOPT" in dispositions
    assert "ADAPT" in dispositions
    assert len(dispositions) >= 2
