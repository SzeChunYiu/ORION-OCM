"""Missing-evidence hostiles for the publication inventory gate."""
import copy
from pathlib import Path
import tempfile
import unittest

from assess_readiness import assess


class InventoryHostiles(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / "receipt.json").write_text('{"example":"software test only"}')
        self.doc = {"schema": "test", "scope": "software only", "gates": [
            {"id": "G1", "required": True, "status": "MET", "evidence": ["receipt.json"],
             "reason": "test receipt", "resolution_test": "independent scientific review"}]}

    def test_complete_inventory_never_implies_acceptance(self):
        r = assess(self.doc, self.root)
        self.assertEqual(r["disposition"], "INVENTORY_COMPLETE_REQUIRES_INDEPENDENT_SCIENTIFIC_REVIEW")
        self.assertEqual(r["scientific_acceptance"], "NOT_INFERRED_FROM_CHECKLIST_OR_FILE_EXISTENCE")

    def test_missing_and_empty_evidence_block_met(self):
        for evidence in ([], ["absent.json"]):
            d = copy.deepcopy(self.doc)
            d["gates"][0]["evidence"] = evidence
            self.assertEqual(assess(d, self.root)["disposition"], "DO_NOT_SUBMIT_YET")
        (self.root / "receipt.json").write_text("")
        self.assertEqual(assess(self.doc, self.root)["disposition"], "DO_NOT_SUBMIT_YET")

    def test_unknown_missing_and_partial_status_fail_closed(self):
        for status in ("GREEN", None, [], {}, "PARTIAL", "UNMET", "CANNOT_CHECK"):
            d = copy.deepcopy(self.doc)
            d["gates"][0]["status"] = status
            self.assertEqual(assess(d, self.root)["disposition"], "DO_NOT_SUBMIT_YET")

    def test_malformed_or_empty_registry_fails_closed(self):
        for document in ({}, [], {"schema": "x", "scope": "x", "gates": []}):
            self.assertEqual(assess(document, self.root)["disposition"], "DO_NOT_SUBMIT_YET")

    def test_duplicate_ids_and_missing_required_flag_block(self):
        d = copy.deepcopy(self.doc)
        d["gates"].append(copy.deepcopy(d["gates"][0]))
        self.assertEqual(assess(d, self.root)["disposition"], "DO_NOT_SUBMIT_YET")
        d = copy.deepcopy(self.doc)
        del d["gates"][0]["required"]
        self.assertEqual(assess(d, self.root)["disposition"], "DO_NOT_SUBMIT_YET")

    def test_receipt_content_change_changes_bound_digest(self):
        a = assess(self.doc, self.root)["gates"][0]["evidence_receipts"][0]["sha256"]
        (self.root / "receipt.json").write_text("different receipt")
        b = assess(self.doc, self.root)["gates"][0]["evidence_receipts"][0]["sha256"]
        self.assertNotEqual(a, b)


if __name__ == "__main__":
    unittest.main()
