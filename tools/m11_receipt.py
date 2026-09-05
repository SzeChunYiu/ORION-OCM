#!/usr/bin/env python3
"""Generate or verify docs/provenance/M11_RECEIPT_V1.json.
    python tools/m11_receipt.py            # (re)generate
    python tools/m11_receipt.py --verify   # exit 1 on drift of bound files or deterministic results
Binds: the M11 self-model modules, the self obligation registry, the M10 receipt, the
self-reorganisation evaluation and the report; records the deterministic summary, the per-scenario
verdicts and the recorded-replay summary.  No claim.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RECEIPT = ROOT / "docs" / "provenance" / "M11_RECEIPT_V1.json"
BOUND = (
    "src/ocm/selfmodel/model.py", "src/ocm/selfmodel/diagnose.py", "src/ocm/selfmodel/proposal.py", "src/ocm/selfmodel/govern.py", "src/ocm/selfmodel/benchmark.py", "src/ocm/selfmodel/replay.py", "src/ocm/selfmodel/intake.py",
    "src/ocm/evaluation/m11_self_eval.py", "docs/theorems/OCM_SELF_OBLIGATION_REGISTRY_V1.json", "docs/provenance/M10_RECEIPT_V1.json",
    "research/ocm-m11/M11_SELF_EVAL_V1.json", "docs/M11_SELF_REORGANISATION_REPORT.md",
)
KEYS = ("scenario", "true_layer", "diagnosed", "proposal_class", "escalation_allowed", "architecture_alarm", "assurance", "adopted", "target_before", "target_after", "preservation_before", "preservation_after", "rollback_exact", "broad_rewrite", "prediction_realised")


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def fresh() -> dict:
    ev = json.loads((ROOT / "research/ocm-m11/M11_SELF_EVAL_V1.json").read_text(encoding="utf-8"))
    result = {"summary": ev["summary"], "scenarios": [{k: r.get(k) for k in KEYS} for r in ev["scenarios"]], "parents": ev["parents"], "historical_replay_summary": ev["historical_replay"]["summary"]}
    try:
        head = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()
    except Exception:  # noqa: BLE001
        head = "UNKNOWN"
    return {
        "receipt": "M11_RECEIPT_V1",
        "terminal": "M11_MIXED_CLAIM_BY_CLAIM",
        "git_head_at_generation": head,
        "bound_files": {rel: sha(ROOT / rel) for rel in BOUND},
        "deterministic_results": result,
        "authority": "controlled self-reorganisation benchmark on OCM-authored planted causes with an oracle ablation channel; recorded replay of the self-application ledger; external adoption only; no novelty claim",
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
        print("M11 receipt verified; bound files:", len(new["bound_files"]))
        return 0
    RECEIPT.write_text(json.dumps(new, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("wrote", RECEIPT)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
