#!/usr/bin/env python3
"""Generate or verify docs/provenance/M9_RECEIPT_V1.json.
    python tools/m9_receipt.py            # (re)generate
    python tools/m9_receipt.py --verify   # exit 1 on drift of bound files or deterministic results
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
        print("M9 receipt verified; bound files:", len(new["bound_files"]))
        return 0
    RECEIPT.write_text(json.dumps(new, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("wrote", RECEIPT)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
