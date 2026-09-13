"""Actual successor countercontrols and independent joint-world comparisons."""
import sys
import unittest
from fractions import Fraction as F
from itertools import product
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from joint_comparison_v1 import compare_worlds,compare_box
from successor_controls_v1 import run
from sources_v1 import verify_sources

class JointComparisonTests(unittest.TestCase):
    def test_pinned_successor_countercontrols_and_no_alarm(self):
        got=run(verify_sources(Path(__file__).resolve().parent))
        self.assertEqual(got["original_valid_compare"],"CERTIFIED_STRICTLY_LOWER")
        self.assertEqual(got["original_reversed_interval_false_pass"],"CERTIFIED_STRICTLY_LOWER")
        self.assertTrue(got["repaired_reversed_interval_rejected"])
        self.assertEqual((got["atomic_retained_part_acquisition"],got["atomic_reset_acquisition"]),(0,1))
        self.assertTrue(got["altered_table_passed_original_digest_shape_tests"])
        self.assertEqual(got["generic_label_ties"],0)
        self.assertFalse(got["deferred_winners_evaluated"])

    def test_correlations_revive_strict_comparison(self):
        got=compare_worlds(((1,2),(2,3)))
        self.assertEqual(got["status"],"CERTIFIED_STRICTLY_LOWER")
        self.assertEqual(got["maximum_difference"],-1)
        self.assertEqual(compare_box((1,2),(2,3))["status"],"UNRESOLVED")

    def test_empty_and_malformed_worlds_refuse(self):
        for worlds in ((),((1,),),((1.0,2),),((-1,2),),((True,2),)):
            with self.assertRaises(ValueError):compare_worlds(worlds)

    def test_reversed_float_negative_intervals_refuse(self):
        for a in ((2,1),(1.0,2),(-1,2),(0,True),[0,1]):
            with self.assertRaises(ValueError):compare_box(a,(3,4))

    def test_mirror_and_unbounded_box_controls(self):
        self.assertEqual(compare_box((10,None),(1,4))["status"],"CERTIFIED_STRICTLY_HIGHER")
        self.assertEqual(compare_box((0,1),(2,None))["status"],"CERTIFIED_STRICTLY_LOWER")
        self.assertEqual(compare_box((0,None),(0,None))["status"],"UNRESOLVED")

    def test_all_closed_box_corners(self):
        intervals=[(a,b) for a in range(3) for b in range(a,3)]
        for a,b in product(intervals,repeat=2):
            worlds=tuple(product(a,b))
            self.assertEqual(compare_box(a,b)["status"],compare_worlds(worlds)["status"])

    def test_all_nonempty_small_joint_sets(self):
        points=tuple(product(range(3),repeat=2))
        for mask in range(1,1<<len(points)):
            worlds=tuple(p for i,p in enumerate(points) if mask&(1<<i))
            expected=("CERTIFIED_STRICTLY_LOWER" if all(a<b for a,b in worlds) else
                      "CERTIFIED_STRICTLY_HIGHER" if all(a>b for a,b in worlds) else "UNRESOLVED")
            self.assertEqual(compare_worlds(worlds)["status"],expected)

    def test_no_uniform_margin_in_infinite_limit_is_not_finite_test_claim(self):
        for n in (1,2,4,8):
            got=compare_worlds(tuple((0,F(1,k)) for k in range(1,n+1)))
            self.assertEqual(got["maximum_difference"],-F(1,n))
        # The analytic countable example, not this prefix check, proves sup=0.

if __name__=="__main__":unittest.main()
