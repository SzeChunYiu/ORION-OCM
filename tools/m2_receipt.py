#!/usr/bin/env python3
"""Verify the active runtime successor; preserve historical M2_RECEIPT_V1.json.

    python tools/m2_receipt.py --write-current  # create declared successor; never overwrite history
    python tools/m2_receipt.py --verify         # verify active successor; no historical fallback

Binds: the M2 source modules, the runtime obligation registry, the vendored-source manifest, the
M2.1 revival and scaling receipts; records the deterministic checker outputs (nogoods, procedure
algebra, surprise lemma/hub theorem, historical replay counts) and the inherited authority.
Timing rows of the scaling receipt are bound by digest only (they are host measurements).
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RECEIPT = ROOT / "docs" / "provenance" / "M2_RECEIPT_V1.json"
BOUND = (
    "src/ocm/kso/nogoods.py", "src/ocm/kso/procedures.py", "src/ocm/kso/surprise.py", "src/ocm/kso/navigation_sparse.py",
    "src/ocm/store/event.py", "src/ocm/store/evidence.py", "src/ocm/store/ledger.py", "src/ocm/store/canonical.py",
    "src/ocm/runtime/solve.py", "src/ocm/runtime/ocm_runtime.py", "src/ocm/runtime/trace.py", "src/ocm/runtime/transition.py",
    "src/ocm/operators/registry.py", "src/ocm/learning/learner.py",
    "src/ocm/constitution/action.py", "src/ocm/constitution/boundary.py", "src/ocm/constitution/hard_gates.py",
    "src/ocm/evaluation/historical.py", "src/ocm/evaluation/m21_surprise_revival.py", "src/ocm/evaluation/scaling.py",
    "docs/theorems/OCM_RUNTIME_OBLIGATION_REGISTRY_V1.json", "docs/provenance/VENDORED_SOURCE_MANIFEST_V1.json",
    "research/ocm-m2/M2_1_SURPRISE_REVIVAL_RECEIPT_V1.json", "research/ocm-m2/M2_SCALING_BASELINE_V1.json",
)


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def fresh() -> dict:
    from fractions import Fraction

    from ocm.evaluation.historical import replay_all
    from ocm.kso import nogoods, procedures, surprise
    from ocm.store.event import EventType

    hist = replay_all()
    result = {
        "nogoods": nogoods.check_nogoods(3),
        "procedure_algebra": procedures.check_procedure_algebra(3),
        "hub_theorem_under_models": {m.value: surprise.check_hub_theorem_under_model(m) for m in surprise.SurpriseModel},
        "historical_replay": {"counts": hist["counts"], "terminals": {a["name"]: a["terminal"] for a in hist["adapters"]}},
        "event_families": [e.value for e in EventType],
    }
    revival = json.loads((ROOT / "research/ocm-m2/M2_1_SURPRISE_REVIVAL_RECEIPT_V1.json").read_text(encoding="utf-8"))
    try:
        head = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()
    except Exception:  # noqa: BLE001
        head = "UNKNOWN"
    return {
        "receipt": "M2_RECEIPT_V1",
        "terminal": "M2_UNIFIED_RUNTIME_GREEN",
        "milestone_issue": 4,
        "bound_files": {p: sha(ROOT / p) for p in BOUND if (ROOT / p).exists()},
        "missing_bound_files": [p for p in BOUND if not (ROOT / p).exists()],
        "git_head_at_generation": head,
        "commands": ["python -m pytest -q tests/m2", "python tools/m2_vendor_check.py", "python tools/m2_receipt.py --verify"],
        "result": result,
        "m2_1_revival": {"verdict": revival["verdict"], "uniform": revival["uniform"]["FOUND_BY_NAVIGATION"], "propagated": revival["propagated"]["FOUND_BY_NAVIGATION"], "guards": revival["guards"], "default_model_changed": False},
        "authority": {
            "M2_SOLVE_HISTORICAL": "PARENT_SUFFICIENT",
            "GENERAL_NOVELTY": "NOT_ESTABLISHED",
            "M2_PROTECTED_SPLIT": "NOT_RUN",
            "note": "one canonical runtime replays the inherited controlled results without upgrading any claim; the surprise-model comparison is a dev-split design-choice study.",
        },
    }


def main(argv: list[str]) -> int:
    from runtime_revision_receipts_v4 import revision_main

    return revision_main(ROOT, argv, 2)

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
