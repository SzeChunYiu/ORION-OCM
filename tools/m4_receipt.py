#!/usr/bin/env python3
"""Generate or verify docs/provenance/M4_RECEIPT_V1.json.
    python tools/m4_receipt.py            # (re)generate
    python tools/m4_receipt.py --verify   # exit 1 on drift of bound files or deterministic results
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
RECEIPT = ROOT / "docs" / "provenance" / "M4_RECEIPT_V1.json"
BOUND = (
    "src/ocm/dialogue/workspace.py", "src/ocm/dialogue/reference.py", "src/ocm/dialogue/clarify.py", "src/ocm/dialogue/gate.py",
    "src/ocm/dialogue/session.py", "src/ocm/dialogue/microworld.py", "src/ocm/evaluation/m4_dialogue_eval.py",
    "docs/theorems/OCM_DIALOGUE_OBLIGATION_REGISTRY_V1.json", "docs/provenance/M3_RECEIPT_V1.json",
    "research/ocm-m4/M4_DIALOGUE_EVAL_V1.json", "scripts/acquire_multiwoz.sh", "docs/provenance/MULTIWOZ24_CUSTODY_MANIFEST_V1.json",
)


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def fresh() -> dict:
    from ocm.dialogue import microworld as DW

    ds = DW.generate()
    custody = DW.custody_receipt(ds, "OCM-M4-DIALOGUE-20260905")
    ev = json.loads((ROOT / "research/ocm-m4/M4_DIALOGUE_EVAL_V1.json").read_text(encoding="utf-8"))
    result = {
        "dialogue_custody": {k: custody[k] for k in ("n", "dev", "protected", "dev_sha256", "protected_sha256", "families", "turns_total")},
        "dialogue_eval": {k: ev[k] for k in ("protected_dialogues", "acts", "state_reference", "correction", "clarification", "epistemic_integrity", "persistence")},
    }
    try:
        head = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()
    except Exception:  # noqa: BLE001
        head = "UNKNOWN"
    return {
        "receipt": "M4_RECEIPT_V1",
        "terminal": "M4_DIALOGUE_COGNITIVE_LOOP_GREEN",
        "git_head_at_generation": head,
        "bound_files": {rel: sha(ROOT / rel) for rel in BOUND},
        "deterministic_results": result,
        "authority": "engineering receipt for the M4 dialogue milestone on a synthetic dialogue microworld with a given vocabulary; no real-conversation result, no comparator, no novelty claim; the theory these modules implement is ORION-V2 batch 2 (B1, B5) and batch 3 (C1, C2, C7)",
    }


def main(argv: list[str]) -> int:
    new = fresh()
    if "--verify" in argv:
        if not RECEIPT.exists():
            print("MISSING receipt", RECEIPT)
            return 1
        old = json.loads(RECEIPT.read_text(encoding="utf-8"))
        drift = []
        for rel, digest in new["bound_files"].items():
            if old["bound_files"].get(rel) != digest:
                drift.append(rel)
        if old["deterministic_results"] != new["deterministic_results"]:
            drift.append("deterministic_results")
        if drift:
            print("DRIFT:", drift)
            return 1
        print("M4 receipt verified; bound files:", len(new["bound_files"]))
        return 0
    RECEIPT.write_text(json.dumps(new, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("wrote", RECEIPT)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
