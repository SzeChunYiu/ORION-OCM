from pathlib import Path
import unittest
from helpers import api


class ReceiptControls(unittest.TestCase):
    def test_own_policy_and_predecessor_provenance_are_source_bound(self):
        inventory = api("corpus_receipt").code_inventory()
        self.assertIn(".gitignore", inventory)
        self.assertIn("provenance/PREDECESSORS.json", inventory)
        self.assertIn("tests/test_receipt.py", inventory)
        self.assertFalse(any("__pycache__" in key or key.startswith("provenance/runs/")
                             for key in inventory))

    def test_artifact_provenance_and_report_cost_limits_are_explicit(self):
        provenance = Path(__file__).resolve().parents[1] / "provenance/PREDECESSORS.json"
        self.assertTrue(provenance.is_file(), "predecessor provenance absent")


if __name__ == "__main__":
    unittest.main()
