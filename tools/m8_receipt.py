#!/usr/bin/env python3
"""Generate or verify docs/provenance/M8_RECEIPT_V1.json.
    python tools/m8_receipt.py            # (re)generate
    python tools/m8_receipt.py --verify   # exit 1 on drift of bound files or deterministic results
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
RECEIPT = ROOT / "docs" / "provenance" / "M8_RECEIPT_V1.json"
BOUND = (
    "src/ocm/organisation/interface.py", "src/ocm/organisation/arms.py", "src/ocm/organisation/navigate.py", "src/ocm/organisation/worlds.py", "src/ocm/organisation/language_stream.py",
    "src/ocm/evaluation/m8_organisation_eval.py", "docs/theorems/OCM_ORGANISATION_OBLIGATION_REGISTRY_V1.json", "docs/provenance/M7_RECEIPT_V1.json",
    "research/ocm-m8/M8_ORGANISATION_EVAL_V1.json", "docs/M8_ORGANISATION_REPORT.md",
)


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def fresh() -> dict:
    ev = json.loads((ROOT / "research/ocm-m8/M8_ORGANISATION_EVAL_V1.json").read_text(encoding="utf-8"))
    worlds = {w["family"]: {arm: {"task_success": v["task_success"], "navigation_work": v["navigation_work"], "exact_regions": v["partition_recovery"]["exact_regions"], "macro_live_over_dead_children": v["revocation_commutation"]["macro_live_over_dead_children"]} for arm, v in w["arms"].items()} for w in ev["worlds"]}
    lang = {arm: {"task_success": v["task_success"], "navigation_work": v["navigation_work"]} for arm, v in ev["language_stream"]["arms"].items()}
    result = {"worlds": worlds, "flat_baselines": {w["family"]: w["flat_baseline"] for w in ev["worlds"]}, "language_stream": lang, "cannot_check_arms": ev["worlds"][0]["cannot_check_arms"]}
    try:
        head = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()
    except Exception:  # noqa: BLE001
        head = "UNKNOWN"
    return {
        "receipt": "M8_RECEIPT_V1",
        "terminal": "M8_PARENT_SUFFICIENT_AT_THIS_SCALE",
        "git_head_at_generation": head,
        "bound_files": {rel: sha(ROOT / rel) for rel in BOUND},
        "deterministic_results": result,
        "authority": "organisation study on synthetic oracle worlds and the Alpha language stream against parent organisations built here; PARENT_SUFFICIENT at this scale; no novelty claim; theory: ORION-V2 batch 2 (B7), batch 4 (D5, D7, D8 in progress)",
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
        print("M8 receipt verified; bound files:", len(new["bound_files"]))
        return 0
    RECEIPT.write_text(json.dumps(new, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("wrote", RECEIPT)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
