"""12 exact controls for reachability refinement (E). Sibling-compiled; -I safe."""

from pathlib import Path
import importlib.util
import unittest
from fractions import Fraction as F

path = Path(__file__).with_name("reachability_refinement_v1.py")
spec = importlib.util.spec_from_loader("reach_checked", loader=None)
mod = importlib.util.module_from_spec(spec)
mod.__file__ = str(path)
exec(compile(path.read_bytes(), str(path), "exec"), mod.__dict__)


class ReachabilityBasic(unittest.TestCase):
    def test_reachable_sets(self):
        self.assertEqual(mod.reachable(mod.L_A, 0), frozenset((0, 1, 2, 3)))
        self.assertEqual(mod.reachable(mod.L_B, 0), frozenset((0, 1, 3)))
        self.assertEqual(mod.reachable(mod.L_A_PLUS, 0), frozenset((0, 1, 2, 3)))

    def test_representable_same_laws_different_reach(self):
        self.assertEqual(mod.R, mod.M)
        self.assertEqual(mod.R, frozenset((0, 1, 2, 3)))
        self.assertNotEqual(mod.reachable(mod.L_A, 0), mod.reachable(mod.L_B, 0))

    def test_burden_is_bfs_distance(self):
        self.assertEqual(mod.burden(mod.L_A, 0, 2), 2)
        self.assertIsNone(mod.burden(mod.L_B, 0, 2))
        self.assertEqual(mod.burden(mod.L_A, 0, 0), 0)
        self.assertEqual(mod.burden(mod.L_A_SC, 2, 0), 1)

    def test_optimum_reachability_witness(self):
        self.assertTrue(mod.burden(mod.L_A, mod.SEED, mod.OPTIMUM) is not None)
        self.assertTrue(mod.is_globally_impossible(mod.SEED, mod.OPTIMUM, mod.L_B))
        self.assertTrue(mod.burden(mod.L_A_PLUS, mod.SEED, mod.OPTIMUM) is not None)

    def test_local_basin_vs_global_impossibility(self):
        # 3 under L_B is reachable but dead-end not leading to 2
        self.assertEqual(mod.burden(mod.L_B, 0, 3), 2)
        self.assertTrue(mod.is_local_basin(3, mod.L_B))
        # 2 under L_B is globally impossible from 0
        self.assertTrue(mod.is_globally_impossible(0, 2, mod.L_B))
        self.assertFalse(mod.is_local_basin(2, mod.L_B))


class SufficientAndGreedy(unittest.TestCase):
    def test_strong_connectivity_sufficient(self):
        self.assertTrue(mod.is_strongly_connected(mod.L_A_SC, mod.R))
        for u in mod.R:
            self.assertEqual(mod.reachable(mod.L_A_SC, u), mod.R)
        self.assertFalse(mod.is_strongly_connected(mod.L_A, mod.R))

    def test_greedy_succeeds_where_monotone(self):
        self.assertTrue(mod.greedy_reaches(mod.L_A, 0, 2))
        # L_A burden along greedy path 0->1->2 is 2,1,0 monotone

    def test_greedy_trap_fails(self):
        self.assertFalse(mod.greedy_reaches(mod.L_GREEDY_TRAP, 0, 2))
        # 2 is representable but greedy cycles between 1 and 3

    def test_cross_search_agreement_on_L_A_and_L_B(self):
        for L in (mod.L_A, mod.L_B):
            c = mod.cross_search_agreement(L, 0, 2)
            self.assertTrue(c["bfs_dfs_agree"])

    def test_encoding_bound(self):
        holds, diff = mod.encoding_bound_holds(mod.L_A)
        self.assertTrue(holds)
        self.assertLessEqual(diff, 1)
        holds_b, diff_b = mod.encoding_bound_holds(mod.L_B)
        self.assertTrue(holds_b)
        self.assertLessEqual(diff_b, 1)

    def test_summary_counts(self):
        s = mod.summary()
        self.assertEqual(s["morphologies"], 4)
        self.assertEqual(s["laws"], 5)
        self.assertTrue(s["L_A_reaches_opt"])
        self.assertFalse(s["L_B_reaches_opt"])
        self.assertTrue(s["L_A_plus_reaches_opt"])

    def test_interfaces_refuse_bad_inputs(self):
        with self.assertRaises(ValueError):
            mod.reachable({0: frozenset((1,))}, 0)
        with self.assertRaises(ValueError):
            mod.reachable(mod.L_A, 99)
        with self.assertRaises(ValueError):
            mod.burden(mod.L_A, 0, 99)


if __name__ == "__main__":
    unittest.main()
