import unittest
from copy import deepcopy
from unittest.mock import patch
import record_audit_v1 as audit
from record_audit_v1 import RAW, DOC_HASH, deferred, load, module, run


class RecordTests(unittest.TestCase):
    def test_actual_complete_three_prediction_payload_no_alarm(self):
        r = run()
        self.assertEqual(r["deferred_complete_payload"]["held"], 3)
        self.assertEqual(r["deferred_complete_payload"]["frozen_digest"], DOC_HASH)

    def test_original_empty_registration_reproduces_false_pass(self):
        m = module("gmi-learning-law-selection-v1/learning_law_selection_v1.py")
        old = module("gmi-learning-law-selection-v1/execute_deferred_v1.py", m)
        empty = "## Frozen ecologies\n\n## Predictions not evaluated here\n"
        old.execute.__globals__["frozen_text"] = lambda: empty
        result = old.execute()
        self.assertEqual((result["held"], result["total"]), (0, 0))
        self.assertEqual(result["terminal"], "ALL_DEFERRED_PREDICTIONS_HELD")
        with self.assertRaises(ValueError):
            deferred(empty)

    def test_missing_or_changed_real_row_rejected(self):
        text = (RAW / "gmi-learning-law-selection-v1/DEFERRED_PREDICTIONS_V1.md").read_text()
        for variant in (text.replace("D-P2", "missing"), text + "\n"):
            with self.assertRaises(ValueError):
                deferred(variant)

    def test_actual_aggregate_bad_denominator_is_refused(self):
        real = audit.load
        def bad(rel):
            value = deepcopy(real(rel))
            if "K2_ACQUISITION_RECEIPT" in rel:
                value["confirmatory_heldout"]["results"]["orig"]["reuse_targets"] += 1
            return value
        with patch.object(audit, "load", bad):
            with self.assertRaisesRegex(ValueError, "denominator"):
                audit.run()

    def test_original_full_aggregate_preserved(self):
        r = run()
        self.assertEqual(r["k2_original_complete_aggregate"],
                         load("gmi-k2-acquisition-experiment-v1/K2_ACQUISITION_RECEIPT_V1.json"))
        self.assertEqual(sum(r["exploratory_no_shortening_ties"]), 10)
        self.assertEqual(r["corrected_minimum_sufficiency"], "113/287")


if __name__ == "__main__":
    unittest.main()
