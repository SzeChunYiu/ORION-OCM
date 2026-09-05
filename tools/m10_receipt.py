#!/usr/bin/env python3
"""Verify the active runtime successor; preserve historical M10_RECEIPT_V1.json.
    python tools/m10_receipt.py --write-current  # create declared successor; never overwrite history
    python tools/m10_receipt.py --verify         # verify active successor; no historical fallback
Binds: the M3 language modules, the language obligation registry, the microworld evaluation
receipt and the dataset custody manifests (UD EWT, BLiMP); records the deterministic checker
outputs (canonical-form exhaustive check, WL collision witness, the nine required meanings'
digests, the microworld protected-split numbers) and the inherited authority.  No claim.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RECEIPT = ROOT / "docs" / "provenance" / "M10_RECEIPT_V1.json"
BOUND = (
    "src/ocm/science/evidence.py", "src/ocm/science/causal.py", "src/ocm/science/selection.py", "src/ocm/science/analysis.py", "src/ocm/science/proof.py", "src/ocm/science/lifecycle.py",
    "src/ocm/evaluation/m10_science_eval.py", "docs/theorems/OCM_SCIENCE_OBLIGATION_REGISTRY_V1.json", "docs/provenance/M9_RECEIPT_V1.json",
    "research/ocm-m10/M10_SCIENCE_EVAL_V1.json", "docs/M10_SCIENCE_REPORT.md",
)


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def fresh() -> dict:
    ev = json.loads((ROOT / "research/ocm-m10/M10_SCIENCE_EVAL_V1.json").read_text(encoding="utf-8"))
    result = {k: ev[k] for k in ("causal", "experiment_selection", "analysis", "proof", "retraction", "cross_field_transfer", "communication", "external")}
    try:
        head = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()
    except Exception:  # noqa: BLE001
        head = "UNKNOWN"
    return {
        "receipt": "M10_RECEIPT_V1",
        "terminal": "M10_MIXED_CLAIM_BY_CLAIM",
        "git_head_at_generation": head,
        "bound_files": {rel: sha(ROOT / rel) for rel in BOUND},
        "deterministic_results": result,
        "authority": "scientific-lifecycle study on OCM-authored oracle worlds with registered parents built here; exact propositional kernel; external benchmarks CANNOT_CHECK; no novelty claim",
    }


def main(argv: list[str]) -> int:
    from runtime_revision_receipts_v4 import revision_main

    return revision_main(ROOT, argv, 10)

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
