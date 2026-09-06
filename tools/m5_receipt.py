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
RECEIPT = ROOT / "docs" / "provenance" / "M5_RECEIPT_V1.json"
BOUND = (
    "src/ocm/learning/language/lexical.py", "src/ocm/learning/language/morphology.py", "src/ocm/learning/language/corpus.py",
    "src/ocm/learning/language/interaction.py", "src/ocm/learning/language/active.py", "src/ocm/learning/language/transfer.py",
    "src/ocm/evaluation/m5_acquisition_eval.py", "docs/theorems/OCM_ACQUISITION_OBLIGATION_REGISTRY_V1.json",
    "docs/provenance/M4_RECEIPT_V1.json", "research/ocm-m5/M5_ACQUISITION_EVAL_V1.json",
    "scripts/acquire_gutenberg.sh", "scripts/acquire_babylm.sh", "docs/provenance/GUTENBERG_CUSTODY_MANIFEST_V1.json", "docs/provenance/BABYLM_CUSTODY_MANIFEST_V1.json",
)


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def fresh() -> dict:
    ev = json.loads((ROOT / "research/ocm-m5/M5_ACQUISITION_EVAL_V1.json").read_text(encoding="utf-8"))
    result = {"acquisition_eval": {k: ev[k] for k in ("frozen_system", "probes", "teacher_examples", "baseline_frozen", "regimes", "retention_after_E1", "negative_transfer")}}
    try:
        head = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()
    except Exception:  # noqa: BLE001
        head = "UNKNOWN"
    return {
        "receipt": "M5_RECEIPT_V1",
        "terminal": "M5_CONTINUAL_LANGUAGE_LEARNING_GREEN",
        "git_head_at_generation": head,
        "bound_files": {rel: sha(ROOT / rel) for rel in BOUND},
        "deterministic_results": result,
        "authority": "engineering receipt for the M5 acquisition milestone on the synthetic microworld with disclosed information channels per regime; BabyLM CANNOT_CHECK_BABYLM_DATA; no comparator, no novelty claim; the theory these modules implement is ORION-V2 batch 2 (B2, B3) and batch 3 (C6)",
    }


def main(argv: list[str]) -> int:
    from engineering_receipts import revision_main

    return revision_main(ROOT, argv, 5)

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
