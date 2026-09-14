import importlib.util
import json
import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("phase", ROOT / "section_d_phase_winners_witness.py")
phase = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = phase
SPEC.loader.exec_module(phase)


class PhaseWinnerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.r = phase.build_results()

    def test_v2_failure_is_preserved(self):
        self.assertEqual(self.r["authority"]["v2_overall_status"], "FAILED_PREREGISTRATION")
        self.assertFalse(self.r["N_v2_failure"]["prediction_passed"])
        self.assertEqual(self.r["N_v2_failure"]["observed_best_residual"], 70)

    def test_probabilistic_frozen_subtest(self):
        p = self.r["P_probabilistic"]
        self.assertFalse(p["point_only_valid"])
        self.assertEqual(p["registered_exhibit"]["n1_6"], "safe")
        self.assertEqual(p["registered_exhibit"]["n1_7"], "guess_1")
        self.assertTrue(p["q1_count_belief_tie"])
        self.assertTrue(p["belief_strictly_dominates_count_q2_to_12"])
        self.assertEqual(p["heldout_pareto"], ["belief_weights"])
        self.assertTrue(p["negative_twin_MAP_sufficient"])
        self.assertTrue(p["remint_ok"])

    def test_clean_neural_v3(self):
        n = self.r["N_v3_neural_replication"]
        self.assertEqual(n["shell_size"], 126)
        self.assertEqual(n["best_cutoff_residual"], 126)
        self.assertEqual(n["cutoff_plus_exceptions_cells"], 128)
        self.assertFalse(n["affine_exact_exists"])
        self.assertFalse(n["one_cutoff_exact_exists"])
        self.assertTrue(n["weighted_local_composition_exact"])
        self.assertEqual(n["weighted_local_composition_cells"], 23)
        self.assertEqual(n["heldout_pareto"], ["weighted_local_composition"])
        self.assertTrue(n["negative_twin_cutoff_dominates_weighted"])
        self.assertTrue(n["remint_ok"])

    def test_online_planning_frozen_subtest(self):
        s = self.r["S_online_planning"]
        self.assertGreater(s["token_greedy_failure_count"], 0)
        self.assertEqual(s["bfs_failure_count"], 0)
        self.assertEqual(s["compiled_failure_count"], 0)
        self.assertEqual(s["heldout_pareto"], ["online_bfs"])
        self.assertTrue(s["online_dominates_compiled_Q_1_to_8"])
        self.assertTrue(s["q9_to_16_tradeoff"])
        self.assertTrue(s["remint_ok"])

    def test_stochastic_replication(self):
        sr = self.r["stochastic_search_replication"]
        self.assertFalse(sr["candidate_labels_visible_to_search"])
        for key in ("P", "N_v3", "S"):
            self.assertGreaterEqual(sr[key]["success_count"], 95)
            self.assertTrue(sr[key]["criterion_at_least_95"])

    def test_committed_result_reproduces(self):
        committed = json.loads((ROOT / "RESULT_V2_V3.json").read_text(encoding="utf-8"))
        self.assertEqual(committed, self.r)


if __name__ == "__main__":
    unittest.main()
