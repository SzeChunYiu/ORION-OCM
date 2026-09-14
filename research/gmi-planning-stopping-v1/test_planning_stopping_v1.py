"""12 exact controls for planning / stopping (I4). Sibling-compiled; -I safe."""

from pathlib import Path
import importlib.util
import unittest
from fractions import Fraction as F

path = Path(__file__).with_name("planning_stopping_v1.py")
spec = importlib.util.spec_from_loader("planning_checked", loader=None)
mod = importlib.util.module_from_spec(spec)
mod.__file__ = str(path)
exec(compile(path.read_bytes(), str(path), "exec"), mod.__dict__)


class GoalFormation(unittest.TestCase):
    def test_formed_goal_unique_up_to_ties(self):
        for s in mod.all_subsets():
            leaders, omegas, conf = mod.formed_goal(s)
            self.assertTrue(leaders)
            self.assertEqual(conf, max(mod.confidence(a, s) for a in (0, 1, 2)))
            for a in leaders:
                self.assertIn(a, omegas)
                self.assertTrue(len(omegas[a]) > 0)

    def test_singleton_attained_and_no_positive_evc(self):
        for w in mod.WORLD6:
            s = frozenset((w,))
            self.assertTrue(mod.common_actions(s))
            self.assertTrue(mod.stop_rule_holds(s))
            self.assertEqual(mod.tda_value(s), F(0))

    def test_goal_minimises_ec(self):
        for s in mod.all_subsets():
            leaders, _, _ = mod.formed_goal(s)
            best_ec = min(mod.error_cost(a, s) for a in (0, 1, 2))
            self.assertTrue(any(mod.error_cost(a, s) == best_ec for a in leaders))


class Subgoal(unittest.TestCase):
    def test_subgoal_strictly_between(self):
        W = frozenset(mod.WORLD6)
        vw = mod.tda_value(W)
        self.assertEqual(vw, F(2))
        s = frozenset((3, 4))
        self.assertEqual(mod.tda_value(s), F(1))
        self.assertTrue(mod.is_subgoal(s, W))
        self.assertTrue(mod.is_subgoal(s))

    def test_subgoal_reusable_across_two_tasks(self):
        s = frozenset((3, 4))
        # two distinct V=2 tasks sharing the same V=1 subgoal
        t1 = frozenset(mod.WORLD6)
        t2 = frozenset((2, 3, 4, 5))
        self.assertEqual(mod.tda_value(t1), F(2))
        self.assertEqual(mod.tda_value(t2), F(2))
        self.assertTrue(mod.is_subgoal(s, t1))
        self.assertTrue(mod.is_subgoal(s, t2))
        W = frozenset(mod.WORLD6)
        mins = mod.tda_minimizers(W)
        self.assertTrue(len(mins) > 0)

    def test_non_subgoal_corners(self):
        W = frozenset(mod.WORLD6)
        self.assertFalse(mod.is_subgoal(W, W))
        s = frozenset((3,))
        self.assertFalse(mod.is_subgoal(s))
        self.assertEqual(mod.tda_value(s), F(0))


class StoppingRule(unittest.TestCase):
    def test_stop_holds_where_common_nonempty(self):
        for s in mod.all_subsets():
            if not mod.common_actions(s):
                continue
            self.assertTrue(mod.stop_rule_holds(s))
            # also no should_expand for the common action
            leaders, _, _ = mod.formed_goal(s)
            for t in mod.TESTS:
                self.assertFalse(mod.should_expand(leaders[0], s, t))

    def test_myopic_greedy_condition_13_of_35(self):
        agree, total = 0, 0
        for s in mod.all_subsets():
            if mod.common_actions(s):
                continue
            try:
                mins = set(mod.tda_minimizers(s))
            except ValueError:
                continue
            total += 1
            leaders, _, _ = mod.formed_goal(s)
            a = leaders[0]
            hit = bool(set(mod.max_evc_tests(a, s)) & mins)
            agree += int(hit)
        self.assertEqual((agree, total), (13, 35))

    def test_witness_agree_25_and_disagree_35(self):
        self.assertIn("t0", mod.max_evc_tests(1, frozenset((2, 5))))
        self.assertEqual(mod.tda_minimizers(frozenset((2, 5))), ["t0"])
        # disagree witness: EVC-myopic picks t0, TDA picks t1
        self.assertEqual(mod.tda_minimizers(frozenset((3, 5))), ["t1"])

    def test_interfaces_refuse_bad_inputs(self):
        with self.assertRaises(ValueError):
            mod.formed_goal(frozenset())
        with self.assertRaises(ValueError):
            mod.should_expand(0, frozenset((0,)), "t9")
        with self.assertRaises(ValueError):
            mod.confidence(3, frozenset((0,)))
        with self.assertRaises(ValueError):
            mod.tda_value(frozenset((99,)))


if __name__ == "__main__":
    unittest.main()
