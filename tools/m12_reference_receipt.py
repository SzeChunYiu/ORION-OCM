#!/usr/bin/env python3
"""Generate or verify docs/provenance/M12_REFERENCE_RECEIPT_V1.json — the REFERENCE-arm receipt
(theory batch 6 F8): binds the reference-arm module and its result file and records the model tag,
content digest, information-binding label and the family summaries.  A reference arm never enters
the claim tiers or the D1 decision; this receipt is deliberately separate from M12_RECEIPT_V1."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RECEIPT = ROOT / "docs" / "provenance" / "M12_REFERENCE_RECEIPT_V1.json"
BOUND = ("src/ocm/lifetime/reference.py", "research/ocm-m12/M12_REFERENCE_ARM_V1.json", "docs/provenance/M12_RECEIPT_V1.json")


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def fresh() -> dict:
    ev = json.loads((ROOT / "research/ocm-m12/M12_REFERENCE_ARM_V1.json").read_text(encoding="utf-8"))
    return {"receipt": "M12_REFERENCE_RECEIPT_V1", "label": "REFERENCE (F8): pretraining exposure unbound; excluded from claim tiers and the D1 decision",
            "model": ev["info"].get("model"), "model_digest": ev["info"].get("digest"), "information_binding": ev["info"].get("information_binding"),
            "bound_files": {rel: sha(ROOT / rel) for rel in BOUND},
            "deterministic_results": {"summary": ev["summary"], "post_deployment": ev["post_deployment"], "always_attempts": ev["phase_A"]["always_attempts"], "conversations": ev["phase_A"]["conversations"]},
            "resources": ev["resources"], "host": "billy-laptop (local Ollama, no network)"}


def main(argv: list[str]) -> int:
    new = fresh()
    if "--verify" in argv:
        if not RECEIPT.exists():
            print("MISSING receipt", RECEIPT)
            return 1
        old = json.loads(RECEIPT.read_text(encoding="utf-8"))
        drift = [rel for rel, d in new["bound_files"].items() if old["bound_files"].get(rel) != d]
        if old["deterministic_results"] != new["deterministic_results"]:
            drift.append("deterministic_results")
        if drift:
            print("DRIFT:", drift)
            return 1
        print("M12 reference receipt verified")
        return 0
    RECEIPT.write_text(json.dumps(new, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("wrote", RECEIPT)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
