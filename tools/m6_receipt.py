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
RECEIPT = ROOT / "docs" / "provenance" / "M6_RECEIPT_V1.json"
BOUND = (
    "src/ocm/chat/session.py", "src/ocm/chat/__main__.py", "src/ocm/knowledge/world.py", "src/ocm/language/realize.py",
    "src/ocm/dialogue/planner.py", "src/ocm/evaluation/m6_alpha_eval.py",
    "docs/theorems/OCM_ALPHA_OBLIGATION_REGISTRY_V1.json", "docs/provenance/M5_RECEIPT_V1.json",
    "research/ocm-m6/KNOWLEDGE_MANIFEST_V1.json", "research/ocm-m6/M6_ALPHA_SCENARIO_EVAL_V1.json",
    "docs/provenance/SIMPLEWIKI_CUSTODY_MANIFEST_V1.json", "scripts/acquire_simple_wikipedia.sh",
    "docs/LANGUAGE_KSO_ALPHA_REPORT.md", "docs/spec/OCM_ALPHA_V1.md",
)


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def fresh() -> dict:
    ev = json.loads((ROOT / "research/ocm-m6/M6_ALPHA_SCENARIO_EVAL_V1.json").read_text(encoding="utf-8"))
    man = json.loads((ROOT / "research/ocm-m6/KNOWLEDGE_MANIFEST_V1.json").read_text(encoding="utf-8"))
    result = {"scenario_eval": {k: ev[k] for k in ("scenarios", "steps_total", "steps_expected", "hostiles", "incidents", "external_io")}, "knowledge": {"facts": len(man["facts"]), "verified": sum(1 for f in man["facts"] if f.get("verified_by")), "documents": len(man["documents"]), "families": man["families"]}}
    try:
        head = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()
    except Exception:  # noqa: BLE001
        head = "UNKNOWN"
    return {
        "receipt": "M6_RECEIPT_V1",
        "terminal": "LANGUAGE_KSO_ALPHA",
        "git_head_at_generation": head,
        "bound_files": {rel: sha(ROOT / rel) for rel in BOUND},
        "deterministic_results": result,
        "authority": "engineering receipt for the M6 Conversational OCM Alpha on a bounded controlled world; scripted protected scenarios; no human rating run, no comparator, no novelty claim; the theory these modules implement is ORION-V2 batch 2 (B1) and batch 3 (C2)",
    }


def main(argv: list[str]) -> int:
    from engineering_receipts import revision_main

    return revision_main(ROOT, argv, 6)

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
