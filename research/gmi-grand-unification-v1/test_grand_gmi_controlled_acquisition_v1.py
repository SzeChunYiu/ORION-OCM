import importlib.util
import json
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "controlled", HERE / "grand_gmi_controlled_acquisition_checks_v1.py")
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)


class TestControlledAcquisition(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = MOD.run_checks()

    def test_full_census_and_frozen_payload(self):
        self.assertTrue(self.result["all_checks_green"])
        self.assertEqual(self.result["census"], {
            "instances": 62208, "rank_oracle": 62208,
            "winning": 48744, "losing": 13464,
            "constructed_world_runs": 62064, "constructed_successes": 62064})
        frozen = json.loads((HERE / "GRAND_GMI_CONTROLLED_ACQUISITION_RECEIPT_V1.json").read_text())
        self.assertEqual(json.loads(json.dumps(self.result)), frozen)
        self.assertEqual(len(MOD.policy_trees(2)), 202)

    def test_uninformative_preparation_changes_current_state(self):
        t, obs, success = MOD.protection_instance()
        self.assertEqual(MOD.successors((0, 1), t, obs, 0), {0: (2, 3)})
        ranks, _ = MOD.synthesize(t, obs, success)
        self.assertEqual(ranks[(0, 1)], 2)
        self.assertEqual(ranks[(2, 3)], 1)
        self.assertIsNone(ranks[(4,)])
        self.assertIsNone(ranks[(5,)])

    def test_revealing_probe_destroys_terminal_feasibility(self):
        t, obs, success = MOD.protection_instance()
        probe = (1, ("stop", 0), ("stop", 1))
        outcomes = [MOD.execute_tree(probe, s, t, obs, (1, 1)) for s in (0, 1)]
        self.assertEqual(outcomes, [(4, 0, 1), (5, 1, 1)])
        self.assertEqual([a for _, a, _ in outcomes], [0, 1])
        self.assertTrue(all(a not in success[s] for s, a, _ in outcomes))

    def test_protection_revives_the_same_failure(self):
        t, obs, success = MOD.protection_instance()
        tree = (0, (1, ("stop", 0), ("stop", 1)), ("stop", 0))
        for initial in (0, 1):
            state, action, cost = MOD.execute_tree(tree, initial, t, obs, (1, 1))
            self.assertIn(action, success[state])
            self.assertEqual(cost, 2)
        self.assertEqual(self.result["protection_revival"], {
            "False": [None, None], "True": [2, 2]})

    def test_losing_loop_has_no_self_justifying_certificate(self):
        t, obs, success = ((0, 0),), ((0, 0),), (set(),)
        ranks, policy = MOD.synthesize(t, obs, success)
        self.assertEqual(ranks, {(0,): None})
        self.assertEqual(policy, {})
        self.assertEqual(MOD.successors((0,), t, obs, 0), {0: (0,)})
        for horizon in range(4):
            self.assertIsNone(MOD.bounded_cost((0,), t, obs, success, (0, 0), horizon))
        self.assertIsNone(MOD.oracle_cost(MOD.policy_profiles(t, obs, (0, 0), 2), (0,), success))

    def test_legality_is_universal_and_empty_branches_do_not_win(self):
        t, obs, success = ((1, 0), (None, 1)), ((0, 0), (0, 0)), (set(), {0})
        ranks, _ = MOD.synthesize(t, obs, success)
        self.assertEqual(ranks[(0,)], 1)
        self.assertEqual(ranks[(1,)], 0)
        self.assertIsNone(ranks[(0, 1)])
        self.assertIsNone(MOD.successors((0, 1), t, obs, 0))
        self.assertIsNone(MOD.execute_tree((0, ("stop", 0), ("stop", 0)), 1, t, obs, (1, 1)))

    def test_reset_can_solve_without_identifying_initial_world(self):
        t, obs, success = ((2, 0), (2, 1), (2, 2)), ((0, 0),) * 3, ({0}, {1}, {0})
        ranks, _ = MOD.synthesize(t, obs, success)
        self.assertEqual(MOD.successors((0, 1), t, obs, 0), {0: (2,)})
        self.assertEqual(ranks[(0, 1)], 1)
        self.assertEqual(MOD.oracle_cost(MOD.policy_profiles(t, obs, (1, 1), 1), (0, 1), success), 1)

    def test_bounded_cost_is_attained_without_zero_loop_shortcut(self):
        t, obs, success = ((0, 1), (1, 1)), ((0, 0), (0, 0)), (set(), {0})
        self.assertIsNone(MOD.bounded_cost((0,), t, obs, success, (0, 5), 0))
        for horizon in (1, 2, 3):
            self.assertEqual(MOD.bounded_cost((0,), t, obs, success, (0, 5), horizon), 5)
        self.assertEqual(len(self.result["bounded_cost_controls"]), 27)
        self.assertTrue(all(row[-1] == row[-2] for row in self.result["bounded_cost_controls"]))

    def test_stopping_is_allowed_before_the_horizon(self):
        t, obs, success = ((1, 1), (1, 1)), ((0, 0), (0, 0)), ({0}, set())
        ranks, policy = MOD.synthesize(t, obs, success)
        self.assertEqual(ranks[(0,)], 0)
        self.assertEqual(policy[(0,)], ("stop", 0))
        self.assertEqual(MOD.bounded_cost((0,), t, obs, success, (1, 1), 2), 0)


if __name__ == "__main__":
    unittest.main()
