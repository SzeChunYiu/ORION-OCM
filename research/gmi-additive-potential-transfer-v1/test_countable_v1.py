import sys
import unittest
from pathlib import Path
from fractions import Fraction as F
sys.path.insert(0,str(Path(__file__).resolve().parent))
from countable_models_v1 import (polynomial_row,polynomial_slacks,polynomial_controls,
                                doubling_row,walk,envelope_controls)

class CountableTests(unittest.TestCase):
    def test_registered_polynomial_row_arithmetic(self):
        row=polynomial_controls()
        self.assertEqual(row["rational_rows"],28)
        self.assertEqual(row["minimum_slack"],0)
        self.assertEqual(row["exact_cost_intervals"][-1]["upper"],1)

    def test_prefix_survival_matches_independent_telescoping(self):
        for n in (1,2,7):
            for h in (0,1,4,12):
                out=walk(lambda k:polynomial_row(k,0),n,h)
                self.assertEqual(out["survival"],F(n*n,(n+h)**2))

    def test_certified_infinite_value_intervals_nest(self):
        for theta in (F(0),F(1,4),F(1)):
            intervals=[]
            for h in (2,8,16):
                out=walk(lambda n:polynomial_row(n,theta),1,h,lambda n:2*n)
                intervals.append((out["prefix_cost"],out["prefix_cost"]+out["envelope"]))
            for first,second in zip(intervals,intervals[1:]):
                self.assertLessEqual(first[0],second[0])
                self.assertGreaterEqual(first[1],second[1])
            self.assertGreaterEqual(intervals[-1][0],1)
            self.assertLessEqual(intervals[0][1],2)

    def test_countable_reserve_identity_not_only_sampled_inequality(self):
        for n,theta,e in ((1,F(0),F(1)),(7,F(1,4),F(1,2)),(32,F(1),F(1))):
            row=polynomial_slacks(n,theta,e)
            self.assertEqual(row["reserve"],2*e*(n+theta)/(n+1)**2)
            self.assertEqual(row["event_reserve"],e*(2*n+theta)/(n+1)**2)

    def test_positive_envelope_remainder_is_not_rejected(self):
        row=envelope_controls()
        self.assertEqual(row["nonvanishing_envelope_limit"],3)
        for out in row["finite_prefixes"]:
            self.assertEqual(out["prefix_cost"]+out["actual_cost_tail"],2)
            self.assertGreater(out["envelope"],3)

    def test_signed_value_falsifies_dropped_nonnegativity(self):
        for n in (1,2,4,8):
            continuation=sum(p*(0 if y==0 else 2-y) for y,p in doubling_row(n).items())
            self.assertEqual(1+continuation,2-n)
        actual=walk(doubling_row,2,4)
        self.assertEqual(actual["prefix_cost"],F(15,8))
        self.assertGreater(actual["prefix_cost"],0)

    def test_parameter_and_state_contracts_reject_invalid_inputs(self):
        for n,theta,e in ((0,0,1),(1,-1,1),(1,1,F(1,2)),(1,0,2)):
            with self.assertRaises(ValueError):
                polynomial_slacks(n,theta,e)
        with self.assertRaises(ValueError):
            polynomial_row(1,0.5)

if __name__=="__main__":
    unittest.main()
