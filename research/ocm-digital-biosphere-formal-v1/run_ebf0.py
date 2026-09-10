#!/usr/bin/env python3
"""Run parent reconstructions + BIO-T checkers + hostiles AFTER freeze."""
from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import hostiles  # noqa: E402
import lib  # noqa: E402
import parents  # noqa: E402
import theorems  # noqa: E402


def gate(parent_receipts, theorem_rows, hostile_rep):
    parent_fail = [r for r in parent_receipts if r.get("status") == "FAIL"]
    th_fail = [r for r in theorem_rows
               if r.get("status") in ("FAIL", "VACUOUS_PASS")]
    can_fail = hostile_rep.get("instruments_can_fail")
    holds = (not parent_fail) and (not th_fail) and bool(can_fail)
    missing = []
    if parent_fail:
        missing.append("parent_reconstruction")
    if th_fail:
        missing.append("theorem_fail_rows")
    if not can_fail:
        missing.append("required_hostiles")
    return {
        "schema": "EBF0_GATE_V1",
        "status": "GATE_HOLDS" if holds else "GATE_FAILS",
        "parent_fail": [r.get("parent") for r in parent_fail],
        "theorem_fail": [r.get("theorem_id") for r in th_fail],
        "instruments_can_fail": can_fail,
        "missing": missing,
        "long_earths": "REFUSED" if not holds else "PERMITTED_AFTER_THIS_GATE_ONLY_FOR_SCALING_NOT_TO_REDEFINE_MATH",
        "note": "GATE_HOLDS is bounded-scope: exact micro-Earths + reconstructed parents. It does not score long Earths or decide L*.",
    }


def main() -> int:
    root = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else HERE
    freeze = lib.require_freeze(root)
    freeze_sha = lib.sha256_file(os.path.join(root, lib.FREEZE_NAME))
    parent_receipts = parents.reconstruct_all()
    theorem_rows = theorems.run_all()
    hostile_rep = hostiles.run_all()
    g = gate(parent_receipts, theorem_rows, hostile_rep)
    obj = {
        "schema": "EBF0_CERTIFICATES_V1",
        "ts": lib.now(),
        "freeze_sha256": freeze_sha,
        "code_digest": freeze["code_digest"],
        "parents": parent_receipts,
        "theorems": theorem_rows,
        "hostiles": hostile_rep,
        "gate": g,
    }
    path = os.path.join(root, "results", "EBF0_CERTIFICATES_V1.json")
    sha = lib.write_json(path, obj)
    lib.write_json(os.path.join(root, "results", "EBF0_GATE_V1.json"), g)
    lib.event("ebf0_run", sha256=sha, gate=g["status"])
    print("GATE", g["status"], "cert", sha[:16])
    return 0 if g["status"] == "GATE_HOLDS" else 2


if __name__ == "__main__":
    sys.exit(main())
