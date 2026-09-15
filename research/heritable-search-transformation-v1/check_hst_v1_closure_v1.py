#!/usr/bin/env python3
"""Aggregate fail-closed HST v1 closure audit for issue #233.

This does not replace mathematical proofs with execution.  It verifies that the frozen
P1/P5 proof artifacts, P2 certificates, P3 specialization, empirical bridge, hostile
counterexamples, and the additive proof-class normalization needed by #233's v1
Definition of Done are all present and internally terminal.
"""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent

REGISTRY = ROOT / "HST_THEOREM_REGISTRY_V1.json"
OVERLAY = ROOT / "HST_FORMALIZATION_CLOSURE_V1.json"
BRIDGE = ROOT / "HST_EMPIRICAL_BRIDGE_V1.json"

EXPECTED = {f"HST-T{i:02d}" for i in range(1, 19)}
TERMINAL = {
    "PROVED",
    "FINITE_CERTIFIED",
    "PARENT_SUFFICIENT",
    "BOUND_DERIVED",
    "BOUND_DERIVED_VACUOUS_AT_SCOPE",
}

REQUIRED_FILES = [
    "HST_DEFINITIONS_V1.md",
    "HST_THEOREM_REGISTRY_V1.json",
    "HST_FORMALIZATION_CLOSURE_V1.json",
    "HST_EMPIRICAL_BRIDGE_V1.json",
    "proofs/PROOFS_CORE_V1.md",
    "proofs/LIMITS_V1.md",
    "proofs/T17_TOY.md",
    "bounds/HST_TRANSFER_BOUND_V1.md",
    "bounds/NEGATIVE_TRANSFER_COUNTEREXAMPLE_V1.md",
    "exact/T02_REACH_WITNESS_V1.json",
    "exact/PARENT_WITNESSES_T04_T08_V1.json",
    "exact/T10_EV_ORACLE_V1.json",
    "exact/T11_MODULE_PROMOTION_V1.json",
    "exact/check_t12_v1.cert.json",
    "exact/check_t13_v1.cert.json",
    "hostiles/T17_TAMPER_WITNESS.json",
    "hostiles/W_T01_mandatory_overhead.json",
    "hostiles/W_T03_aliasing.json",
    "hostiles/W_T05_macro_never_pays.json",
    "hostiles/W_T06_missing_edge_false_locality.json",
    "hostiles/W_T07_ratchet_no_transfer.json",
    "hostiles/W_T18_fixed_epsilon_saturation.json",
    "hostiles/W_QD_syntactic_one_phenotype.json",
]

CHECKERS = [
    "check_hst_formalization_closure_v1.py",
    "exact/check_core_v1.py",
    "exact/check_t12_v1.py",
    "exact/check_t13_v1.py",
    "exact/check_t17_v1.py",
    "bounds/check_bound_v1.py",
    "hostiles/check_qd_syntactic_hostile_v1.py",
]


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def run_checker(relative: str) -> dict:
    path = ROOT / relative
    process = subprocess.run(
        [sys.executable, str(path)],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    return {
        "checker": relative,
        "exit_code": process.returncode,
        "output_tail": process.stdout[-4000:],
    }


def main() -> int:
    failures: list[str] = []

    for relative in REQUIRED_FILES:
        if not (ROOT / relative).is_file():
            failures.append(f"missing required artifact: {relative}")
    for relative in CHECKERS:
        if not (ROOT / relative).is_file():
            failures.append(f"missing checker: {relative}")

    if failures:
        print(json.dumps({"schema": "HST_V1_CLOSURE_RECEIPT_V1", "verdict": "FAIL", "failures": failures}, indent=2))
        return 1

    registry = load(REGISTRY)
    overlay = load(OVERLAY)
    bridge = load(BRIDGE)

    registry_rows = registry.get("rows", [])
    overlay_rows = overlay.get("rows", [])
    registry_by_id = {row.get("theorem_id"): row for row in registry_rows}
    overlay_by_id = {row.get("theorem_id"): row for row in overlay_rows}

    if set(registry_by_id) != EXPECTED:
        failures.append(f"registry theorem census mismatch: {sorted(set(registry_by_id) ^ EXPECTED)}")
    if set(overlay_by_id) != EXPECTED:
        failures.append(f"overlay theorem census mismatch: {sorted(set(overlay_by_id) ^ EXPECTED)}")

    for theorem_id in sorted(EXPECTED):
        row = registry_by_id.get(theorem_id, {})
        normalized = overlay_by_id.get(theorem_id, {})
        if row.get("status") not in TERMINAL:
            failures.append(f"{theorem_id}: nonterminal status {row.get('status')!r}")
        if not row.get("assumptions"):
            failures.append(f"{theorem_id}: assumptions absent")
        if not row.get("parent_theorem"):
            failures.append(f"{theorem_id}: strongest parent absent")
        if not row.get("ocm_residual"):
            failures.append(f"{theorem_id}: empirical residual absent")
        for field in ("primary_proof_class", "domain", "quantifiers", "proof_artifact", "counterexample_or_escape", "claim_ceiling"):
            if not str(normalized.get(field, "")).strip():
                failures.append(f"{theorem_id}: normalized {field} absent")

    bridge_rows = bridge.get("rows", {})
    expected_bridge = {f"T{i:02d}" for i in range(1, 19)}
    if set(bridge_rows) != expected_bridge:
        failures.append(f"bridge census mismatch: {sorted(set(bridge_rows) ^ expected_bridge)}")
    for key in sorted(expected_bridge):
        row = bridge_rows.get(key, {})
        if not row.get("issue") or not row.get("hook"):
            failures.append(f"{key}: empirical bridge lacks issue/hook")

    # Definition-of-done-specific sentinels.
    t09 = registry_by_id.get("HST-T09", {})
    t10 = registry_by_id.get("HST-T10", {})
    if t09.get("status") != "BOUND_DERIVED":
        failures.append("T09 OCM finite-class P3 specialization not terminal BOUND_DERIVED")
    t10_text = json.dumps(t10, sort_keys=True)
    for needle in ("Hoeffding", "T10_EV_ORACLE_V1.json", "continued-vs-reset"):
        if needle not in t10_text and needle not in json.dumps(bridge_rows.get("T10", {}), sort_keys=True):
            failures.append(f"T10 missing required v1 closure evidence: {needle}")

    master = overlay.get("master_statement", "")
    if not master.strip():
        failures.append("master surviving conditional statement absent")
    forbidden_master = ("UNIVERSAL_THEORY_OF_INTELLIGENCE_PROVEN", "OPEN_ENDED_INTELLIGENCE_PROVEN", "RECURSIVE_SELF_IMPROVEMENT_PROVEN_IN_REALITY")
    if any(token in master for token in forbidden_master):
        failures.append("master statement contains forbidden universal terminal")

    checker_receipts = [run_checker(relative) for relative in CHECKERS]
    for receipt in checker_receipts:
        if receipt["exit_code"] != 0:
            failures.append(f"checker failed: {receipt['checker']}")

    result = {
        "schema": "HST_V1_CLOSURE_RECEIPT_V1",
        "verdict": "PASS" if not failures else "FAIL",
        "theorems_checked": len(EXPECTED),
        "terminal_statuses": {key: registry_by_id[key].get("status") for key in sorted(EXPECTED)},
        "empirical_bridge_rows": len(bridge_rows),
        "required_artifacts": len(REQUIRED_FILES),
        "checker_receipts": checker_receipts,
        "master_statement_present": bool(master.strip()),
        "failures": failures,
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
