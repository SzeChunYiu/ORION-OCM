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
RECEIPT = ROOT / "docs" / "provenance" / "M9_RECEIPT_V1.json"
BOUND = (
    "src/ocm/work/contracts.py", "src/ocm/work/envs.py", "src/ocm/work/methods.py", "src/ocm/evaluation/m9_transfer_eval.py",
    "docs/theorems/OCM_WORK_OBLIGATION_REGISTRY_V1.json", "docs/provenance/M8_RECEIPT_V1.json", "research/ocm-m9/M9_TRANSFER_EVAL_V2.json", "docs/M9_TRANSFER_REPORT.md",
)


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def fresh() -> dict:
    ev = json.loads((ROOT / "research/ocm-m9/M9_TRANSFER_EVAL_V2.json").read_text(encoding="utf-8"))
    result = {"summary": ev["summary"], "transfer_matrix": ev["transfer_matrix"], "transfer_precision": ev["transfer_precision"], "claims": {k: {"n": v["n"], "verdict": v["verdict"]} for k, v in ev.get("claims", {}).items()}, "external_benchmarks": ev["external_benchmarks"], "study_status": ev["study_status"]}
    try:
        head = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()
    except Exception:  # noqa: BLE001
        head = "UNKNOWN"
    return {
        "receipt": "M9_RECEIPT_V1",
        "terminal": "M9_CANNOT_CHECK_FOR_SUPPORTED_AT_THIS_N",
        "git_head_at_generation": head,
        "bound_files": {rel: sha(ROOT / rel) for rel in BOUND},
        "deterministic_results": result,
        "authority": "lifetime transfer study on OCM-authored environments with exact oracle state against matched parents built here; external benchmarks CANNOT_CHECK; no novelty claim",
    }


def main(argv: list[str]) -> int:
    from engineering_receipts import revision_main

    return revision_main(ROOT, argv, 9)

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
