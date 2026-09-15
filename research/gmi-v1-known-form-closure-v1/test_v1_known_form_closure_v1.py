#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for gmi-v1-known-form-closure-v1."""
from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from v1_known_form_closure_v1 import REPO, Z_ORDER, run_audit, write_receipt  # noqa: E402


class V1KnownFormClosureTests(unittest.TestCase):
    def test_audit_green(self):
        receipt = run_audit()
        self.assertEqual(receipt["errors"], [], msg=receipt["errors"])
        self.assertEqual(receipt["status"], "GREEN")
        self.assertEqual(
            receipt["terminal"],
            "KNOWN_FORM_ZERO_PRIOR_DERIVATION_GREEN_AT_REGISTERED_SCOPE",
        )

    def test_every_family_at_least_z2(self):
        ledger = json.loads((HERE / "FAMILY_LEDGER_V1.json").read_text(encoding="utf-8"))
        for fam in ledger["families"]:
            self.assertGreaterEqual(
                Z_ORDER[fam["z_earned"]], Z_ORDER["Z2"], fam["family_id"]
            )

    def test_checklist_complete(self):
        ledger = json.loads((HERE / "FAMILY_LEDGER_V1.json").read_text(encoding="utf-8"))
        ids = {f["family_id"] for f in ledger["families"]}
        for need in ledger["ml_practice_checklist"]:
            self.assertIn(need, ids)

    def test_no_untyped_gaps(self):
        ledger = json.loads((HERE / "FAMILY_LEDGER_V1.json").read_text(encoding="utf-8"))
        for fam in ledger["families"]:
            gap = fam.get("gap")
            if gap is None:
                continue
            self.assertTrue(gap.get("gap_type"))
            self.assertTrue(gap.get("detail"))
            self.assertTrue(gap.get("next_experiment"))

    def test_frontier_z3_or_repair(self):
        ledger = json.loads((HERE / "FAMILY_LEDGER_V1.json").read_text(encoding="utf-8"))
        repairs = json.loads(
            (HERE / "NEGATIVE_REPAIR_PLAN_V1.json").read_text(encoding="utf-8")
        )
        repair_ids = {r["family_id"] for r in repairs["repairs"]}
        by_id = {f["family_id"]: f for f in ledger["families"]}
        earned = 0
        for fid in ledger["frontier_z3_required"]:
            if Z_ORDER[by_id[fid]["z_earned"]] >= Z_ORDER["Z3"]:
                earned += 1
            else:
                self.assertIn(fid, repair_ids)
        self.assertGreaterEqual(earned, 4)

    def test_p0_closed_layer_count(self):
        p0 = json.loads((HERE / "P0_ZERO_PRIOR_ROWS_V1.json").read_text(encoding="utf-8"))
        closed = sum(1 for r in p0["rows"] if r["status"] == "CLOSED_EXACT_LAYER")
        self.assertGreaterEqual(closed, 6)

    def test_evidence_paths_exist(self):
        ledger = json.loads((HERE / "FAMILY_LEDGER_V1.json").read_text(encoding="utf-8"))
        for fam in ledger["families"]:
            for rel in fam["evidence"]:
                self.assertTrue((REPO / rel).is_file(), rel)

    def test_receipt_roundtrip(self):
        receipt = write_receipt(HERE / "RECEIPT_V1.json")
        loaded = json.loads((HERE / "RECEIPT_V1.json").read_text(encoding="utf-8"))
        self.assertEqual(loaded["status"], receipt["status"])
        self.assertEqual(loaded["terminal"], receipt["terminal"])

    def test_boxes_tickable(self):
        boxes = json.loads(
            (HERE / "V1_BOX_DISPOSITION_V1.json").read_text(encoding="utf-8")
        )
        self.assertEqual(len(boxes["boxes"]), 6)
        self.assertTrue(all(b["tick"] for b in boxes["boxes"]))


if __name__ == "__main__":
    unittest.main()
