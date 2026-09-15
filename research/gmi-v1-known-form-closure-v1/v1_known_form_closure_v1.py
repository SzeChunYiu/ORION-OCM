#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Executable audit for #602 V1 known-form closure + #431/#433 P0 rows."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]

Z_ORDER = {"Z2": 2, "Z3": 3, "Z4": 4}


def _load(name: str) -> Dict[str, Any]:
    path = HERE / name
    with path.open("r", encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, dict):
        raise TypeError("%s must be object" % name)
    return data


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _exists_repo_path(rel: str) -> bool:
    return (REPO / rel).is_file()


def _z_at_least(earned: str, need: str) -> bool:
    if earned not in Z_ORDER or need not in Z_ORDER:
        return False
    return Z_ORDER[earned] >= Z_ORDER[need]


def audit_ledger(ledger: Dict[str, Any]) -> List[str]:
    errors = []  # type: List[str]
    checklist = ledger.get("ml_practice_checklist") or []
    families = ledger.get("families") or []
    by_id = {}  # type: Dict[str, Dict[str, Any]]
    for fam in families:
        fid = fam.get("family_id")
        if not fid:
            errors.append("family missing family_id")
            continue
        if fid in by_id:
            errors.append("duplicate family_id %s" % fid)
        by_id[fid] = fam
        pv = fam.get("property_vector") or []
        if len(pv) < 2:
            errors.append("%s property_vector too short" % fid)
        if not _z_at_least(str(fam.get("z_earned")), "Z2"):
            errors.append("%s below Z2" % fid)
        ev = fam.get("evidence") or []
        if not ev:
            errors.append("%s missing evidence" % fid)
        for rel in ev:
            if not _exists_repo_path(rel):
                errors.append("%s missing evidence path %s" % (fid, rel))
        if not fam.get("negative_twin"):
            errors.append("%s missing negative_twin" % fid)
        if not fam.get("falsifier"):
            errors.append("%s missing falsifier" % fid)
        gap = fam.get("gap")
        if gap is not None:
            for key in ("gap_type", "detail", "next_experiment"):
                if not gap.get(key):
                    errors.append("%s gap missing %s" % (fid, key))
    for need in checklist:
        if need not in by_id:
            errors.append("ml_practice_checklist missing family %s" % need)
    for fid in ledger.get("frontier_z3_required") or []:
        if fid not in by_id:
            errors.append("frontier family missing %s" % fid)
    return errors


def audit_frontier_z3(
    ledger: Dict[str, Any], repairs: Dict[str, Any]
) -> Tuple[List[str], Dict[str, Any]]:
    errors = []  # type: List[str]
    repair_ids = {r.get("family_id") for r in repairs.get("repairs") or []}
    summary = {"z3_earned": [], "z3_repair": []}  # type: Dict[str, List[str]]
    by_id = {f["family_id"]: f for f in ledger.get("families") or []}
    for fid in ledger.get("frontier_z3_required") or []:
        fam = by_id[fid]
        if _z_at_least(str(fam.get("z_earned")), "Z3"):
            summary["z3_earned"].append(fid)
        else:
            summary["z3_repair"].append(fid)
            if fid not in repair_ids:
                errors.append("frontier %s lacks Z3 and has no repair row" % fid)
            gap = fam.get("gap") or {}
            if gap.get("gap_type") not in (
                "z3_recovery",
                "scale",
                "theory",
                "estimator",
                "z4_held_family",
                "z4_selection",
            ):
                errors.append("frontier %s gap_type not typed for remainder" % fid)
    if len(summary["z3_earned"]) < 4:
        errors.append(
            "expected at least 4 frontier families at Z3, got %d" % len(summary["z3_earned"])
        )
    return errors, summary


def audit_z4_where_possible(
    ledger: Dict[str, Any]
) -> Tuple[List[str], Dict[str, Any]]:
    errors = []  # type: List[str]
    partial = []  # type: List[str]
    typed_open = []  # type: List[str]
    for fam in ledger.get("families") or []:
        st = str(fam.get("z4_status"))
        fid = fam["family_id"]
        if st in ("EXACT_FINITE_PARTIAL", "MEASURED_PROFILE_PARTIAL"):
            partial.append(fid)
        elif st == "TYPED_OPEN":
            typed_open.append(fid)
            gap = fam.get("gap")
            if gap is None:
                errors.append("%s TYPED_OPEN z4 without gap row" % fid)
        else:
            errors.append("%s unknown z4_status %s" % (fid, st))
    if len(partial) < 8:
        errors.append(
            "expected >=8 families with Z4-partial evidence, got %d" % len(partial)
        )
    return errors, {"z4_partial": partial, "z4_typed_open": typed_open}


def audit_p0(rows_doc: Dict[str, Any]) -> Tuple[List[str], Dict[str, Any]]:
    errors = []  # type: List[str]
    closed = 0
    typed = 0
    for row in rows_doc.get("rows") or []:
        rid = row.get("row_id")
        status = row.get("status")
        if not row.get("falsifier") or not row.get("next_experiment"):
            errors.append("%s missing falsifier/next_experiment" % rid)
        for rel in row.get("evidence") or []:
            if not _exists_repo_path(rel):
                errors.append("%s missing evidence %s" % (rid, rel))
        term = row.get("terminal")
        if term:
            found = False
            for rel in row.get("evidence") or []:
                if not rel.endswith(".json"):
                    continue
                try:
                    with (REPO / rel).open("r", encoding="utf-8") as fh:
                        payload = json.load(fh)
                except Exception as exc:  # noqa: BLE001
                    errors.append("%s cannot read %s: %s" % (rid, rel, exc))
                    continue
                if payload.get("terminal") == term or payload.get("status") == term:
                    found = True
            json_ev = [e for e in (row.get("evidence") or []) if e.endswith(".json")]
            if json_ev and not found:
                errors.append("%s terminal %s not found in evidence receipts" % (rid, term))
        if status == "CLOSED_EXACT_LAYER":
            closed += 1
        elif status in ("TYPED_OPEN_PARTIAL", "REGISTERED_PROTOCOL_PRESENT"):
            typed += 1
        else:
            errors.append("%s unknown status %s" % (rid, status))
    if closed < 6:
        errors.append("expected >=6 CLOSED_EXACT_LAYER P0 rows, got %d" % closed)
    return errors, {"closed_exact_layer": closed, "typed_open_or_protocol": typed}


def audit_boxes(boxes: Dict[str, Any]) -> List[str]:
    errors = []  # type: List[str]
    rows = boxes.get("boxes") or []
    if len(rows) != 6:
        errors.append("expected 6 disposition rows (5 V1 + P0), got %d" % len(rows))
    for row in rows:
        if not row.get("tick"):
            errors.append("%s not tickable under registered-scope policy" % row.get("box_id"))
        if not row.get("disposition"):
            errors.append("%s missing disposition" % row.get("box_id"))
    if boxes.get("terminal") != "KNOWN_FORM_ZERO_PRIOR_DERIVATION_GREEN_AT_REGISTERED_SCOPE":
        errors.append("unexpected terminal")
    return errors


def audit_repairs(repairs: Dict[str, Any]) -> List[str]:
    errors = []  # type: List[str]
    for row in repairs.get("repairs") or []:
        for key in (
            "family_id",
            "missing_rung",
            "negative",
            "repair",
            "instrumentation",
            "kill_condition",
            "success_terminal",
        ):
            if key not in row or row[key] in (None, "", []):
                errors.append("repair missing %s" % key)
        inst = row.get("instrumentation") or []
        if len(inst) < 2:
            errors.append("%s instrumentation too thin" % row.get("family_id"))
    return errors


def run_audit() -> Dict[str, Any]:
    ledger = _load("FAMILY_LEDGER_V1.json")
    p0 = _load("P0_ZERO_PRIOR_ROWS_V1.json")
    repairs = _load("NEGATIVE_REPAIR_PLAN_V1.json")
    boxes = _load("V1_BOX_DISPOSITION_V1.json")

    errors = []  # type: List[str]
    errors.extend(audit_ledger(ledger))
    e2, frontier = audit_frontier_z3(ledger, repairs)
    errors.extend(e2)
    e3, z4 = audit_z4_where_possible(ledger)
    errors.extend(e3)
    e4, p0_sum = audit_p0(p0)
    errors.extend(e4)
    errors.extend(audit_boxes(boxes))
    errors.extend(audit_repairs(repairs))

    required_terminals = {
        "research/machine-intelligence-morphogenesis-v1/GMI_KNOWN_FORM_DERIVATION_EXACT_RECEIPT_V1.json": "KNOWN_FORM_DERIVATION_EXACT_FINITE_GREEN",
        "research/machine-intelligence-morphogenesis-v1/GMI_P0_ZERO_PRIOR_RESPONSE_EXACT_RECEIPT_V1.json": "P0_ZERO_PRIOR_RESPONSE_LAWS_EXACT_LAYER_GREEN",
        "research/machine-intelligence-morphogenesis-v1/GMI_ZERO_PRIOR_EXACT_REDISCOVERY_RECEIPT_V2.json": "ZERO_PRIOR_EXACT_PROPERTY_REDISCOVERY_V2_GREEN",
    }
    receipt_checks = {}  # type: Dict[str, Any]
    for rel, term in required_terminals.items():
        path = REPO / rel
        if not path.is_file():
            errors.append("missing required receipt %s" % rel)
            continue
        with path.open("r", encoding="utf-8") as fh:
            payload = json.load(fh)
        got = payload.get("terminal") or payload.get("status")
        ok = got == term
        receipt_checks[rel] = {
            "expected": term,
            "got": got,
            "ok": ok,
            "sha256": _sha256_file(path),
        }
        if not ok:
            errors.append("receipt %s terminal mismatch %s != %s" % (rel, got, term))

    cg = REPO / "research/gmi-cross-grammar-four-family-v1/RESULT_V1.json"
    cross_grammar = None  # type: Optional[Dict[str, Any]]
    if cg.is_file():
        with cg.open("r", encoding="utf-8") as fh:
            cross_grammar = json.load(fh)
    else:
        errors.append("missing cross-grammar RESULT_V1.json")

    family_count = len(ledger.get("families") or [])
    untyped = 0
    for fam in ledger.get("families") or []:
        gap = fam.get("gap")
        if gap is None:
            continue
        if not gap.get("gap_type"):
            untyped += 1
    if untyped:
        errors.append("untyped gaps: %d" % untyped)

    status = "GREEN" if not errors else "RED"
    receipt = {
        "artifact": "GMI_V1_KNOWN_FORM_CLOSURE_RECEIPT_V1",
        "status": status,
        "terminal": "KNOWN_FORM_ZERO_PRIOR_DERIVATION_GREEN_AT_REGISTERED_SCOPE"
        if status == "GREEN"
        else "KNOWN_FORM_ZERO_PRIOR_DERIVATION_RED",
        "claim_ceiling": ledger.get("claim_ceiling"),
        "scope_id": ledger.get("scope_id"),
        "family_count": family_count,
        "ml_practice_checklist_count": len(ledger.get("ml_practice_checklist") or []),
        "frontier_z3": frontier,
        "z4": z4,
        "p0": p0_sum,
        "required_receipts": receipt_checks,
        "cross_grammar_present": cross_grammar is not None,
        "box_terminal": boxes.get("terminal"),
        "errors": errors,
        "package_files_sha256": {
            name: _sha256_file(HERE / name)
            for name in (
                "FAMILY_LEDGER_V1.json",
                "P0_ZERO_PRIOR_ROWS_V1.json",
                "NEGATIVE_REPAIR_PLAN_V1.json",
                "V1_BOX_DISPOSITION_V1.json",
                "CORE.md",
            )
            if (HERE / name).is_file()
        },
    }
    return receipt


def write_receipt(path: Optional[Path] = None) -> Dict[str, Any]:
    receipt = run_audit()
    out = path or (HERE / "RECEIPT_V1.json")
    with out.open("w", encoding="utf-8") as fh:
        json.dump(receipt, fh, indent=2, sort_keys=True)
        fh.write("\n")
    return receipt


def main() -> int:
    receipt = write_receipt()
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0 if receipt.get("status") == "GREEN" else 1


if __name__ == "__main__":
    raise SystemExit(main())
