from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("heldout_transition_v1", ROOT / "heldout_transition_v1.py")
m = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = m
SPEC.loader.exec_module(m)


class TestHeldoutTransitions(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = m.run_certificate()

    def test_green(self):
        self.assertEqual(self.result["verdict"], "GREEN")
        self.assertTrue(all(self.result["checks"].values()))

    def test_temporal_freeze_and_case_count(self):
        self.assertEqual(self.result["freeze_commit"], "ddb3df7a44a6a4fb47fdc362a1fa02e34b7a3a75")
        self.assertEqual(len(self.result["cases"]), 20)

    def test_all_transitions(self):
        for case in self.result["cases"]:
            self.assertEqual(case["observed_low"], ["PERSISTENT_STATE"])
            self.assertEqual(case["observed_high"], ["STATELESS"])

    def test_two_searchers_agree(self):
        self.assertEqual(self.result["counts"]["independent_search_agreements"], 40)
        self.assertNotEqual(
            self.result["searchers"]["full"]["strategy_signature"],
            self.result["searchers"]["frontier"]["strategy_signature"],
        )
        self.assertEqual(self.result["searchers"]["full"]["declared_budget"], 65552)
        self.assertEqual(self.result["searchers"]["frontier"]["declared_budget"], 65552)

    def test_controls(self):
        self.assertEqual(self.result["counts"]["boundary_ties"], 20)
        self.assertEqual(self.result["counts"]["remint_agreements"], 40)
        self.assertEqual(self.result["counts"]["shifted_threshold_failures"], 20)
        self.assertGreater(self.result["counts"]["branch_pruned_points_total"], 0)

    def test_outcome_search_sources_do_not_cross_import(self):
        a = (ROOT / "full_enumeration_v1.py").read_text()
        b = (ROOT / "frontier_branch_bound_v1.py").read_text()
        self.assertNotIn("frontier_branch_bound_v1", a)
        self.assertNotIn("full_enumeration_v1", b)


if __name__ == "__main__":
    unittest.main()
