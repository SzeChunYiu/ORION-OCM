#!/usr/bin/env python3
"""Generate or verify docs/provenance/M12_RECEIPT_V1.json.
    python tools/m12_receipt.py            # (re)generate
    python tools/m12_receipt.py --verify   # exit 1 on drift of bound files or deterministic results
Binds: the lifetime modules, the evaluation, both pre-registrations, the V1 (DEV_CALIBRATION) and
V2 (PROTECTED) receipts, the replication receipt, the M11 receipt, the registry and the report;
records the V2 deterministic block.  No claim.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RECEIPT = ROOT / "docs" / "provenance" / "M12_RECEIPT_V1.json"
BOUND = (
    "src/ocm/lifetime/machine.py", "src/ocm/lifetime/phases.py", "src/ocm/evaluation/m12_lifetime_eval.py",
    "research/ocm-m12/M12_LIFETIME_PREREGISTRATION_V1.md", "research/ocm-m12/M12_LIFETIME_PREREGISTRATION_V2.md",
    "research/ocm-m12/M12_LIFETIME_EVAL_V1.json", "research/ocm-m12/M12_LIFETIME_EVAL_V2.json", "docs/provenance/M12_REPLICATION_RECEIPT_V1.json",
    "docs/provenance/M11_RECEIPT_V1.json", "docs/theorems/OCM_LIFETIME_OBLIGATION_REGISTRY_V1.json", "docs/M12_LIFETIME_REPORT.md", "research/ocm-m12/ORION_V2_FEEDBACK_PACKET_V1.md",
)


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def fresh() -> dict:
    ev = json.loads((ROOT / "research/ocm-m12/M12_LIFETIME_EVAL_V2.json").read_text(encoding="utf-8"))
    rep = json.loads((ROOT / "docs/provenance/M12_REPLICATION_RECEIPT_V1.json").read_text(encoding="utf-8"))
    try:
        head = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()
    except Exception:  # noqa: BLE001
        head = "UNKNOWN"
    return {
        "receipt": "M12_RECEIPT_V1",
        "terminal": ev.get("exit_gate_final", ev["exit_gate_before_replication"]),
        "git_head_at_generation": head,
        "bound_files": {rel: sha(ROOT / rel) for rel in BOUND},
        "deterministic_results": {"v2": ev["deterministic"], "replication": rep["verdict"], "exit_gate_before_replication": ev["exit_gate_before_replication"]},
        "authority": "one persistent OCM instance over OCM-authored bounded worlds and oracle environments with a matched whole-system parent; V1 DEV_CALIBRATION then V2 PROTECTED; replication on a second host; frontier reference, human rating and external benchmarks CANNOT_CHECK; no novelty claim",
    }


def main(argv: list[str]) -> int:
    new = fresh()
    if "--verify" in argv:
        if not RECEIPT.exists():
            print("MISSING receipt", RECEIPT)
            return 1
        old = json.loads(RECEIPT.read_text(encoding="utf-8"))
        drift = [rel for rel, digest in new["bound_files"].items() if old["bound_files"].get(rel) != digest]
        if old["deterministic_results"] != new["deterministic_results"]:
            drift.append("deterministic_results")
        if drift:
            print("DRIFT:", drift)
            return 1
        print("M12 receipt verified; bound files:", len(new["bound_files"]))
        return 0
    RECEIPT.write_text(json.dumps(new, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("wrote", RECEIPT)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
