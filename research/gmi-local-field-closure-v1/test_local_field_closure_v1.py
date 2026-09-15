from __future__ import annotations

import unittest

from local_field_closure_v1 import (
    lesion_regeneration_certificate,
    topology_sensitivity_certificate,
    validate_closure,
    validate_receipt,
)


class LocalFieldClosureTests(unittest.TestCase):
    def test_every_single_site_lesion_repairs_and_identity_does_not(self):
        result = lesion_regeneration_certificate()
        self.assertEqual(result["repaired"], {4: 4, 8: 8, 16: 16, 32: 32})
        self.assertFalse(any(result["negative_control_repaired"].values()))

    def test_path_ring_difference_has_exact_three_quarters_measure(self):
        result = topology_sensitivity_certificate()
        self.assertEqual(result["differing"], result["expected"])
        self.assertNotEqual(result["ring_output"], result["path_output"])

    def test_committed_receipt_and_only_seven_earned_tasks(self):
        self.assertEqual(validate_receipt()["ecology_cells"], 144)
        self.assertEqual(validate_closure()["ledger_rows"], 7)


if __name__ == "__main__":
    unittest.main()
