"""Tests for the #203 soft-wall diagnosis."""
from __future__ import annotations

import json
from pathlib import Path
import unittest

D = json.loads((Path(__file__).resolve().parent
                / "G203_SOFT_WALL_DIAGNOSIS_V1.json").read_text())


class Vacuity(unittest.TestCase):
    def test_every_row_terminated_at_the_soft_wall(self):
        self.assertEqual(D["finding"]["rows_terminating_at_soft_wall"],
                         D["finding"]["rows_total"])
        for mode, arm in D["arms"].items():
            self.assertEqual(set(arm["terminals"]), {"UNKNOWN"}, mode)
            for reason in arm["error_reasons"]:
                self.assertIn("REGISTERED_SOFT_WALL_BOUND", reason, mode)

    def test_no_proof_decision_was_ever_made(self):
        """The load-bearing fact: the mechanism under test never acted."""
        self.assertEqual(D["finding"]["proof_decisions_ever_made"], 0)
        for mode, arm in D["arms"].items():
            self.assertTrue(all(c in (None, 0) for c in arm["decision_counts"]), mode)
            self.assertTrue(all(s is False for s in arm["parent_scope_complete"]), mode)

    def test_exactly_one_budget_is_saturated_and_it_is_the_wall(self):
        sat = D["saturation"]
        self.assertEqual(sat["solver_soft_wall_s"]["fraction"], 1.0)
        others = [k for k in sat if k != "solver_soft_wall_s"]
        for k in others:
            self.assertLess(sat[k]["fraction"], 0.2,
                            f"{k} is also near its budget, so the wall would not be "
                            "the single binding constraint")

    def test_the_diagnosis_declares_itself_unscored(self):
        self.assertEqual(D["analysis_status"], "DIAGNOSTIC_RERUN_NOT_SCORED_EVIDENCE")
        self.assertIn("makes no architectural, lifetime or OCM claim", D["authority"])

    def test_the_verdict_is_cannot_check_shaped_not_a_negative(self):
        self.assertEqual(D["finding"]["verdict"],
                         "VACUOUS_RUN_RESOURCE_BOUND_NOT_RESULT")
        self.assertEqual(D["upstream"]["reported_causal_decision_witnesses"], 0)

    def test_the_syntax_path_is_identified_as_the_cost(self):
        for mode, arm in D["arms"].items():
            self.assertGreater(arm["syntax_not_derivable_fraction"], 0.9, mode)
            self.assertGreater(arm["syntax_requests_total"], 100_000, mode)


if __name__ == "__main__":
    unittest.main(verbosity=2)
