"""Focused proof controls plus an independent occupancy-flow census."""
from fractions import Fraction as F
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from stopping_model_v1 import Model, action
from proper_policy_v1 import construct, evaluate, bellman_slacks, certify
from occupancy_oracle_v1 import independent_viable, flow_vertices
from stopping_checks_v1 import census, witnesses


class StochasticStoppingTests(unittest.TestCase):
    def test_zero_cycle_tie_requires_properness(self):
        model = Model(((action(0, 1, 0), action(1, 0, 1)),))
        result = construct(model)
        self.assertEqual(result["policy"], (1,))
        self.assertEqual(set(bellman_slacks(model, result).values()), {0})
        self.assertIsNone(evaluate(model, (0,), (0,)))

    def test_unreachable_goal_and_safe_action_filter(self):
        trap = Model(((action(0, 0, F(1,2), F(1,2)),), ()))
        self.assertEqual(construct(trap)["viable"], ())
        revived = Model(((action(0, 0, F(1,2), F(1,2)), action(3, 0, 0, 1)), ()))
        self.assertEqual(construct(revived)["cost"], (3, None))
        self.assertEqual(independent_viable(revived), (0,))

    def test_geometric_tail_is_not_pathwise_bound(self):
        result = witnesses()
        self.assertEqual(result["positive_geometric"]["steps"], (2,))
        self.assertTrue(all(x > 0 for x in result["geometric_tail_first_eight"]))
        self.assertEqual(sum(F(1,2**k) for k in range(8)), 2-F(1,128))

    def test_free_geometric_has_spurious_extended_fixed_point(self):
        m = Model(((action(0, F(1,2), F(1,2)),),))
        self.assertEqual(construct(m)["cost"], (0,))
        self.assertEqual(construct(m)["steps"], (2,))
        # Exact extended-real rule: positive multiple of +infinity is +infinity.
        infinity = float("inf")
        self.assertEqual(infinity/2, infinity)

    def test_one_common_policy_realizes_all_state_minima(self):
        m = Model(((action(0, 0, 1, 0), action(2, 0, 0, 1)),
                   (action(0, 1, 0, 0), action(1, 0, 0, 1))))
        r = construct(m)
        self.assertEqual((r["policy"], r["cost"], r["steps"]), ((0, 1), (1, 1), (2, 1)))
        self.assertEqual(evaluate(m, (0, 1), r["policy"]), ((1, 1), (2, 1)))

    def test_cost_ties_select_both_immediate_stops(self):
        m = Model(((action(0, 0, 1, 0), action(1, 0, 0, 1)),
                   (action(0, 1, 0, 0), action(1, 0, 0, 1))))
        r = construct(m)
        self.assertEqual(r["policy"], (1, 1))
        self.assertEqual(r["steps"], (1, 1))
        self.assertIsNone(evaluate(m, (0, 1), (0, 0)))

    def test_terminal_charge_and_count_are_included(self):
        m = Model(((action(0, 0, 1, 0),), (action(9, 0, 0, 1),)))
        r = construct(m)
        self.assertEqual((r["cost"], r["steps"]), ((9, 9), (2, 1)))

    def test_positive_pca_control(self):
        m = Model(((action(1, 0, F(1,2), F(1,2)), action(5, 0, 0, 1)),
                   (action(1, 1, 0, 0), action(5, 0, 0, 1))))
        r = construct(m)
        self.assertEqual(r["cost"], (3, 4))
        self.assertEqual(r["steps"], (3, 4))
        self.assertEqual(flow_vertices(m, (0, 1))[0], (7, 7))

    def test_finite_perturbation_not_exact_lexical_certificate(self):
        w = witnesses()
        self.assertEqual(w["lexical_cheap_trial"]["policy"], (0,))
        self.assertEqual(w["delta_one_higher_original_cost"]["policy"], (1,))

    def test_history_almost_sure_not_finite_mean(self):
        for k in range(1, 9):
            partial = sum(F(1, n*(n+1)) for n in range(1, k+1))
            self.assertEqual(partial, 1-F(1, k+1))
        self.assertEqual(sum(F(1, n) for n in range(1, 5)), F(25, 12))

    def test_empty_goal_only_and_no_actions(self):
        self.assertEqual(construct(Model(()))["viable"], ())
        self.assertEqual(construct(Model(((),)))["cost"], (None,))

    def test_malformed_probability_and_cost_contracts(self):
        for a in (action(-1, 0, 1), action(0, -1, 2), action(0, 0, 0),
                  action(0, 1), action(0, 0.0, 1), action(True, 0, 1)):
            with self.subTest(a=a), self.assertRaises(ValueError):
                Model(((a,),))

    def test_flow_requires_strictly_positive_initial_weights(self):
        m = Model(((action(0, 0, 1),),))
        with self.assertRaises(ValueError):
            flow_vertices(m, (0,), (0,))

    def test_certificate_rejects_scalar_fixed_point_without_progress(self):
        model = Model(((action(0, 1, 0), action(1, 0, 1)),))
        good = construct(model)
        self.assertTrue(certify(model, good))
        for changed in ({"policy": (0,)}, {"cost": (0,)}, {"steps": (0,)},
                        {"viable": ()}):
            with self.subTest(changed=changed), self.assertRaises(ValueError):
                certify(model, {**good, **changed})

    def test_certificate_geometric_drift_is_not_pathwise_descent(self):
        model = Model(((action(0, F(1,2), F(1,2)),),))
        good = construct(model)
        self.assertTrue(certify(model, good))
        self.assertEqual(good["steps"], (2,))
        for false_count in (1, 3):
            with self.assertRaises(ValueError):
                certify(model, {**good, "steps": (false_count,)})

    def test_full_independent_census(self):
        result = census()
        self.assertEqual((result["kernels"], result["models"]), (1296, 5184))
        self.assertGreater(result["flow_comparisons"], result["models"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
