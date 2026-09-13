"""11 exact controls for CAU-5. Sibling sources compiled explicitly; -I safe."""

from fractions import Fraction as F
from pathlib import Path
import importlib.util
import unittest

path = Path(__file__).with_name("causal_rungs_v1.py")
spec = importlib.util.spec_from_loader("causal_rungs_checked", loader=None)
rungs = importlib.util.module_from_spec(spec)
exec(compile(path.read_bytes(), str(path), "exec"), rungs.__dict__)

HALF = F(1, 2)


class SeparatorNoSign(unittest.TestCase):
    def test_w4a_exaggerates(self):
        obs, cond, do = rungs.w4a()
        self.assertEqual(obs, {(0, 0): F(3, 8), (0, 1): F(1, 8),
                                 (1, 0): F(1, 8), (1, 1): F(3, 8)})
        self.assertEqual(cond, F(3, 4))
        self.assertEqual(do, HALF)

    def test_w4b_prevents(self):
        obs, cond, do = rungs.w4b()
        self.assertEqual(obs, {(0, 1): HALF, (1, 0): HALF})
        self.assertEqual(cond, F(0))
        self.assertEqual(do, HALF)

    def test_no_universal_sign(self):
        _, c_a, d_a = rungs.w4a()
        _, c_b, d_b = rungs.w4b()
        self.assertGreater(c_a - d_a, 0)
        self.assertLess(c_b - d_b, 0)


class RungThreeStrictlyAbove(unittest.TestCase):
    def test_rung1_identical(self):
        self.assertEqual(rungs.observed_w5(rungs.RA), rungs.observed_w5(rungs.RB))
        self.assertEqual(rungs.observed_w5(rungs.RA),
                         {(0, 0): F(1, 3), (1, 1): F(1, 3), (1, 0): F(1, 3)})

    def test_rung2_identical(self):
        for x in (0, 1):
            self.assertEqual(rungs.do_w5(rungs.RA, x), rungs.do_w5(rungs.RB, x))
        self.assertEqual(rungs.do_w5(rungs.RA, 1), F(1, 3))
        self.assertEqual(rungs.do_w5(rungs.RA, 0), F(1, 6))

    def test_pn_differs(self):
        self.assertEqual(rungs.pn_w5(rungs.RA), HALF)
        self.assertEqual(rungs.pn_w5(rungs.RB), F(1))

    def test_rung2_blind_estimator_misses_by_quarter(self):
        blind = rungs.rung2_blind_midpoint
        e = blind(rungs.do_w5(rungs.RA, 0), rungs.do_w5(rungs.RA, 1))
        self.assertEqual(e, blind(rungs.do_w5(rungs.RB, 0), rungs.do_w5(rungs.RB, 1)))
        self.assertEqual(e, F(1, 4))
        worst = max(abs(e - rungs.pn_w5(rungs.RA)), abs(e - rungs.pn_w5(rungs.RB)))
        self.assertGreaterEqual(worst, F(1, 4))


class DiscoveryBoundary(unittest.TestCase):
    def test_w1_identical_obs_different_targets(self):
        obs0, t0 = rungs.w1(0)
        obs1, t1 = rungs.w1(1)
        self.assertEqual(obs0, obs1)
        self.assertEqual(obs0, {(0, 0): HALF, (1, 1): HALF})
        self.assertNotEqual(t0, t1)

    def test_skeleton_returns_identically(self):
        self.assertEqual(rungs.skeleton_w1(rungs.w1(0)[0]),
                         rungs.skeleton_w1(rungs.w1(1)[0]))
        self.assertEqual(rungs.skeleton_w1(rungs.w1(0)[0]),
                         frozenset((("X", "Y"),)))

    def test_interfaces_refuse_outside_binary_domain(self):
        with self.assertRaises(ValueError):
            rungs.do_w5(rungs.RA, 2)
        with self.assertRaises(ValueError):
            rungs.w1(2)

    def test_tables_reject_bad_input(self):
        with self.assertRaises(ValueError):
            rungs.observed_w5({0: (0, 0)})
        bad = dict(rungs.RA)
        bad[2] = (1, 2)
        with self.assertRaises(ValueError):
            rungs.pn_w5(bad)


if __name__ == "__main__":
    unittest.main()
