"""Coverage direction, accounting and exact cohort completion countercontrols."""
import sys
import unittest
from fractions import Fraction as F
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import transport_v1 as T
import checks_v1 as C

class TransportTests(unittest.TestCase):
    def test_added_cheaper_allocation_rejects_old_bound(self):
        s={'s':2};t={'x':1,'y':2}
        rel,_=T.construct_relation(s,t,0)
        with self.assertRaises(ValueError):T.certify(s,t,2,0,rel,{'M':('y',2)})
        rel,_=T.construct_relation(s,t,1)
        self.assertEqual(T.certify(s,t,2,1,rel,{'M':('x',1)})['lower'],1)

    def test_target_total_not_source_total(self):
        with self.assertRaises(ValueError):
            T.certify({'s':0},{'x':1,'y':2},0,0,(('s','x'),),{'M':('x',1)})

    def test_false_source_bound_or_relation_refused(self):
        with self.assertRaises(ValueError):
            T.certify({'s':1},{'x':2},2,0,(('s','x'),),{'M':('x',2)})
        with self.assertRaises(ValueError):
            T.certify({'s':2},{'x':1},2,0,(('s','x'),),{'M':('x',1)})

    def test_accounting_direction_and_actual_membership(self):
        self.assertEqual(T.certify({'s':1},{'x':2},1,0,(('s','x'),),
                                  {'M':('x',3)})['lower'],1)
        for q,c in (('x',1),('missing',3)):
            with self.assertRaises(ValueError):
                T.certify({'s':1},{'x':2},1,0,(('s','x'),),{'M':(q,c)})

    def test_empty_and_unknown_or_inexact_contracts_refused(self):
        for s,t in (({}, {'t':1}),({'s':1},{})):
            with self.assertRaises(ValueError):T.construct_relation(s,t)
        with self.assertRaises(ValueError):T.construct_relation({'s':1},{'t':1},-1)
        with self.assertRaises(ValueError):T.construct_relation({'s':1.0},{'t':1})
        with self.assertRaises(ValueError):
            T.certify({'s':1},{'x':1},1,0,(('z','x'),),{'M':('x',1)})
        with self.assertRaises(ValueError):
            T.certify({'s':1},{'x':1},1,0,(('s','x'),),{})

    def test_two_way_zero_error_equality(self):
        s={'s':1,'u':3};t={'x':1,'y':2,'z':5}
        forward,_=T.construct_relation(s,t)
        reverse,_=T.construct_relation(t,s)
        a=T.certify(s,t,1,0,forward,{'M':('x',1)})
        b=T.certify(t,s,1,0,reverse,{'M':('s',1)})
        self.assertEqual(a['target_infimum'],b['target_infimum'])

    def test_five_of_nine_is_not_two_thirds(self):
        self.assertTrue(F(5,9)>F(1,2))
        self.assertEqual(T.threshold_completion(5,4,0)['status'],'FRACTION_FAIL')
        self.assertEqual(T.threshold_completion(6,3,0)['status'],'GUARANTEED_FRACTION_PASS')
        self.assertEqual(T.threshold_completion(2,7,0)['status'],'FRACTION_FAIL')

    def test_unknown_outcomes_are_not_default_failure_or_success(self):
        self.assertEqual(T.threshold_completion(5,3,1)['status'],'UNRESOLVED')
        self.assertEqual(T.threshold_completion(6,2,1)['status'],'GUARANTEED_FRACTION_PASS')
        self.assertEqual(T.threshold_completion(2,6,1)['status'],'FRACTION_FAIL')
        for counts in ((0,0,0),(True,0,0),(-1,3,1),(1,2,F(1))):
            with self.assertRaises(ValueError):T.threshold_completion(*counts)

    def test_independent_assignment_oracle(self):
        self.assertEqual(C.cover_census()['account_error_cases'],162)

    def test_independent_completion_oracle(self):
        self.assertEqual(C.gate_census()['registered_partial_cohorts'],219)

if __name__=="__main__":unittest.main()
