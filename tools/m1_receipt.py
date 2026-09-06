#!/usr/bin/env python3
"""Verify the selected immutable engineering run; preserve all historical receipts.

Use tools/record_engineering_revision.py to execute and record the current gates.
This wrapper accepts --verify only and never executes a historical recipe.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RECEIPT = ROOT / "docs" / "provenance" / "M1_RECEIPT_V1.json"
BOUND_FILES = (
    "src/ocm/kso/warrant.py", "src/ocm/kso/ids.py", "src/ocm/kso/types.py", "src/ocm/kso/space.py",
    "src/ocm/kso/navigation.py", "src/ocm/kso/firing.py", "src/ocm/kso/revocation.py", "src/ocm/kso/extraction.py",
    "src/ocm/kso/admission.py", "src/ocm/kso/abstraction.py", "src/ocm/kso/resources.py", "src/ocm/kso/jump.py",
    "src/ocm/kso/obligations.py", "src/ocm/kso/checks.py", "docs/theorems/KSO_OBLIGATION_REGISTRY_V1.json",
    "docs/provenance/ORION_V2_FAILURE_LEDGER_42b1b0d.md",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fresh() -> dict:
    from ocm.kso.checks import run_all

    result = run_all()
    # drop non-deterministic floats to strings with fixed precision
    def norm(x):
        if isinstance(x, float):
            return f"{x:.12g}"
        if isinstance(x, dict):
            return {k: norm(v) for k, v in x.items()}
        if isinstance(x, (list, tuple)):
            return [norm(v) for v in x]
        return x
    result = norm(result)
    try:
        head = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()
    except Exception:  # noqa: BLE001
        head = "UNKNOWN"
    return {
        "receipt": "M1_RECEIPT_V1",
        "terminal": "M1_KSO_CORE_GREEN",
        "milestone_issue": 3,
        "bound_files": {p: sha256(ROOT / p) for p in BOUND_FILES},
        "git_head_at_generation": head,
        "commands": ["python -m ocm.kso.checks --json", "python -m pytest -q tests/m1", "python tools/m1_receipt.py --verify"],
        "result": result,
        "authority": {
            "M2_SOLVE_HISTORICAL": "PARENT_SUFFICIENT",
            "GENERAL_NOVELTY": "NOT_ESTABLISHED",
            "KS-P1_RETRACTION_LAW": "PARENT_PRODUCT_OWNED",
            "KS-T12_CONSOLIDATION": "OPEN",
            "KS-T10_TRANSLATOR_INVARIANCE": "OPEN_M5",
            "note": "M1 consolidates inherited mathematics; no lower milestone row is implied.",
        },
    }


def main(argv: list[str]) -> int:
    from engineering_receipts import revision_main

    return revision_main(ROOT, argv, 1)

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
