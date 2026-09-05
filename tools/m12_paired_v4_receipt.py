#!/usr/bin/env python3
"""Generate or verify docs/provenance/M12_PAIRED_RECEIPT_V1.json (the V4 paired-lifetimes study).
Binds the stream generator, the paired evaluation, the stream manifest, the V3 pre-registration,
the result, the replication receipt, the reference-arm result on the V3 streams and the report;
records the deterministic block.  No claim.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RECEIPT = ROOT / "docs" / "provenance" / "M12_PAIRED_RECEIPT_V4.json"
BOUND = ("src/ocm/lifetime/streams.py", "src/ocm/evaluation/m12_paired_eval.py", "src/ocm/lifetime/phases.py", "src/ocm/lifetime/machine.py",
         "research/ocm-m12/M12_V4_STREAM_MANIFEST_V1.json", "research/ocm-m12/M12_LIFETIME_PREREGISTRATION_V4.md", "research/ocm-m12/M12_PAIRED_LIFETIMES_EVAL_V4.json",
         "docs/provenance/M12_PAIRED_REPLICATION_RECEIPT_V4.json", "research/ocm-m12/M12_V4_REFERENCE_ARM_V1.json", "docs/M12_V4_PAIRED_LIFETIMES_REPORT.md", "docs/provenance/M12_PAIRED_RECEIPT_V1.json")


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def fresh() -> dict:
    ev = json.loads((ROOT / "research/ocm-m12/M12_PAIRED_LIFETIMES_EVAL_V4.json").read_text(encoding="utf-8"))
    rep = json.loads((ROOT / "docs/provenance/M12_PAIRED_REPLICATION_RECEIPT_V4.json").read_text(encoding="utf-8"))
    try:
        head = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()
    except Exception:  # noqa: BLE001
        head = "UNKNOWN"
    return {"receipt": "M12_PAIRED_RECEIPT_V4", "terminal": ev["deterministic"]["decision"] if rep["verdict"] == "MATCH" else "CANNOT_CHECK (replication mismatch)", "git_head_at_generation": head,
            "bound_files": {rel: sha(ROOT / rel) for rel in BOUND}, "deterministic_results": {"v4": ev["deterministic"], "replication": rep["verdict"], "preregistration_sha256": ev["preregistration_sha256"], "stream_manifest_sha256": ev["stream_manifest_sha256"]},
            "authority": "eight paired lifetimes on OCM-authored per-lifetime protected streams inside the bounded world; matched whole-system parent; sign test over lifetime differences; replication on a second host; reference arm separate (F8); no novelty claim"}


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
        print("M12 paired V4 receipt verified; bound files:", len(new["bound_files"]))
        return 0
    RECEIPT.write_text(json.dumps(new, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("wrote", RECEIPT)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
