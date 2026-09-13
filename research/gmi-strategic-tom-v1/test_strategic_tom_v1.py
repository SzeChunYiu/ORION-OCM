"""13 exact controls for TOM-1-3. Sibling source compiled explicitly; -I safe."""

from fractions import Fraction as F
from pathlib import Path
import importlib.util
import unittest

path = Path(__file__).with_name("strategic_tom_v1.py")
spec = importlib.util.spec_from_loader("strategic_tom_checked", loader=None)
tom = importlib.util.module_from_spec(spec)
exec(compile(path.read_bytes(), str(path), "exec"), tom.__dict__)


class OpponentModelForcing(unittest.TestCase):
    def test_round1_identical(self):
        # Both opponent types open D by construction: round 1 cannot separate
        # them, so no passive round-1 observation distinguishes the types.
        self.assertEqual(tom.opponent_first_move("copycat"), 1)
        self.assertEqual(tom.opponent_first_move("contrarian"), 1)

    def test_per_opponent_optimum_two(self):
        self.assertEqual(tom.tom1_best_vs("copycat"), 2)
        self.assertEqual(tom.tom1_best_vs("contrarian"), 2)

    def test_optimal_replies_are_opposite(self):
        # (a1=1, always-1) is optimal vs copycat and scores 1 vs contrarian;
        # (a1=1, always-0) is optimal vs contrarian and scores 1 vs copycat.
        self.assertEqual(tom.tom1_payoff(1, (1, 1), "copycat"), 2)
        self.assertEqual(tom.tom1_payoff(1, (1, 1), "contrarian"), 1)
        self.assertEqual(tom.tom1_payoff(1, (0, 0), "contrarian"), 2)
        self.assertEqual(tom.tom1_payoff(1, (0, 0), "copycat"), 1)

    def test_no_joint_optimum(self):
        self.assertEqual(tom.tom1_best_joint(), 1)

    def test_interfaces_refuse_bad_inputs(self):
        with self.assertRaises(ValueError):
            tom.tom1_payoff(2, (0, 0), "copycat")
        with self.assertRaises(ValueError):
            tom.tom1_payoff(0, (0, 0), "unknown")


class RecursiveBelief(unittest.TestCase):
    def test_ladder_chain(self):
        self.assertEqual(tom.beauty_ladder(), [5, 3, 2, 1, 1, 1])

    def test_each_level_beats_parent(self):
        ladder = tom.beauty_ladder()
        for child, parent in zip(ladder[1:4], ladder[:3]):
            self.assertGreater(tom.beauty_score(child, parent),
                               tom.beauty_score(parent, parent))

    def test_fixed_point_closure(self):
        self.assertEqual(tom.beauty_br(1), 1)
        self.assertEqual(tom.beauty_ladder()[-1], tom.beauty_ladder()[-2])

    def test_level_unbeatable_at_fixed_point(self):
        for n in range(6):
            self.assertLessEqual(tom.beauty_score(n, 1), tom.beauty_score(1, 1))
        self.assertEqual(tom.beauty_score(1, 1), F(-1, 3))

    def test_interfaces_refuse_bad_inputs(self):
        with self.assertRaises(ValueError):
            tom.beauty_br(6)
        with self.assertRaises(ValueError):
            tom.beauty_ladder(anchor=7)


class PartnerReliability(unittest.TestCase):
    def test_team_optimum(self):
        self.assertEqual(min(tom.TEAM_LOSS.values()), F(0))
        self.assertEqual(tom.TEAM_LOSS[(0, 0)], F(0))

    def test_two_nash_regret_cannot_select(self):
        for profile in ((0, 0), (1, 1)):
            self.assertTrue(tom.is_nash(profile))
        self.assertFalse(tom.is_nash((0, 1)))

    def test_minimax_plays_d_loses_two_on_reliable(self):
        action, worst = tom.minimax_without_signal()
        self.assertEqual((action, worst), (1, F(2)))
        self.assertEqual(tom.TEAM_LOSS[(1, 0)], F(1))
        self.assertNotEqual(tom.TEAM_LOSS[(1, 0)], tom.TEAM_LOSS[(0, 0)])

    def test_reliability_probe_value(self):
        self.assertEqual(tom.signal_branch_loss(True), F(0))
        self.assertEqual(tom.signal_branch_loss(False), F(2))
        unattended, _ = tom.minimax_without_signal()
        self.assertEqual(tom.TEAM_LOSS[(unattended, 0)], F(1))
        self.assertEqual(tom.TEAM_LOSS[(unattended, 0)] - tom.signal_branch_loss(True), F(1))

    def test_reliability_interfaces_refuse_bad_inputs(self):
        with self.assertRaises(ValueError):
            tom.signal_branch_loss("yes")
        with self.assertRaises(ValueError):
            tom.unilateral_regret((0, 0), 3)


if __name__ == "__main__":
    unittest.main()
