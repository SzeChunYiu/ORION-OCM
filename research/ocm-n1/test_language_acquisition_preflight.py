from __future__ import annotations

import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(HERE))

from language_acquisition_preflight import run, transitive_aligned_demo_floor  # noqa: E402


class LanguageAcquisitionPreflightTests(unittest.TestCase):
    def test_frozen_m5_transitive_family_is_one_demo_at_cold_start(self):
        floor = transitive_aligned_demo_floor()
        self.assertEqual(floor.hypothesis_count, 6)
        self.assertEqual(floor.first_pass_demos, 1)
        self.assertEqual(floor.statuses[0], (1, "PASS"))

    def test_one_demo_floor_blocks_meta_learning_headline(self):
        result = run()
        self.assertFalse(result["protected_claim_authority"])
        self.assertEqual(result["terminal"], "CURRENT_ALIGNED_CONSTRUCTION_TASK_HAS_ONE_DEMO_FLOOR")
        self.assertIn("non-trivial multi-observation range", result["registered_n1_primary_endpoint_requirements"][0])


if __name__ == "__main__":
    unittest.main()
