"""Static archived-parent controls; no candidate or measurement execution."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import countercontrols_v2 as controls
from frozen_contract_v1 import AuditError

HERE = Path(__file__).resolve().parent


class CountercontrolV2Tests(unittest.TestCase):
    def test_exact_complete_v2_receipt(self):
        expected = json.loads((HERE / "raw/SYNTHETIC_COUNTERCONTROLS_V2.json").read_text())
        self.assertEqual(controls.run_controls(), expected)

    def test_changed_live_adjudicator_cannot_replace_historical_parent(self):
        with tempfile.TemporaryDirectory() as tmp:
            live = Path(tmp)
            (live / "parity3_cross_envelope_adjudicate_v5.py").write_text("raise RuntimeError('wrong parent')")
            with patch.object(controls, "GRAND", live):
                result = controls.run_controls()
        self.assertEqual(result["actual_measurement_function_invocations"], 0)
        self.assertTrue(result["repair"]["both_false_packets_rejected"])

    def test_corrupted_archived_parent_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            unit = Path(tmp)
            (unit / "raw").mkdir()
            (unit / "raw/HISTORICAL_CROSS_ADJUDICATOR_V5.py").write_text("raise RuntimeError('unbound parent')")
            with patch.object(controls, "HERE", unit), self.assertRaises(AuditError):
                controls.run_controls()


if __name__ == "__main__":
    unittest.main()
