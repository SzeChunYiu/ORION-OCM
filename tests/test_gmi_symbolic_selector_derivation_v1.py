"""Repository gates for issue #602's B14/I5/B20 formal reconciliation."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BUNDLE = ROOT / "research/gmi-symbolic-selector-derivation-v1"
sys.path.insert(0, str(BUNDLE))

from selector_derivation_v1 import evaluate  # noqa: E402


def test_selector_family_order_reverses_on_matched_obligations() -> None:
    result = evaluate()["obligations"]
    xor = result["xor_01"]["families"]
    mux = result["mux_012"]["families"]
    assert xor["equality"]["rules"] < xor["positional"]["rules"]
    assert mux["positional"]["rules"] < mux["equality"]["rules"]


def test_arbitrary_predicates_pay_table_sized_selector_burden() -> None:
    result = evaluate()["obligations"]
    assert {
        row["families"]["arbitrary_subset"]["selector_description_atoms_or_bits"]
        for row in result.values()
    } == {16}


def test_cross_artifact_reconciliation_fails_closed() -> None:
    completed = subprocess.run(
        [sys.executable, str(BUNDLE / "validate_issue_602_reconciliation_v1.py")],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    assert "ISSUE_602_FORMAL_RECONCILIATION_V1_VALID" in completed.stdout
    assert "ISSUE_602_VERIFIED_ROWS=6" in completed.stdout
    assert "ISSUE_602_NEW_LIVE_CHECKBOX_AFTER_MERGE=P0_CAUSAL_COGNITION" in completed.stdout
