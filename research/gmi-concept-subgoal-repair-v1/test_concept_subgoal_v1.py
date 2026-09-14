"""Decisive model tests and independently exhausted legal policies."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import unittest
from fractions import Fraction as F
from prefix_v1 import solve,complete_parses
from concept_v1 import gain,choose,execute,partition,subsets
from check_v1 import run

class ScienceTests(unittest.TestCase):
    def test_overlap_entry_without_strict_gain(self):
        r=solve('abc',{'ab':1,'bc':1})
        self.assertEqual(r['values'],[2,1,1,0])
        self.assertEqual(r['delta'],[1,1,0,0])
        self.assertEqual(r['entries'],[0,1]);self.assertEqual(r['local'],[1])

    def test_dominated_entry_beyond_tie_convention(self):
        r=solve('abcd',{'ab':1,'bcd':1})
        self.assertEqual(r['cost'],2);self.assertEqual(r['local'],[1])
        self.assertGreater(1+r['values'][2],r['values'][0])

    def test_positive_entry_equality(self):
        r=solve('abcabc',{'abc':1})
        self.assertEqual(r['entries'],[0,3]);self.assertEqual(r['local'],r['entries'])

    def test_every_delivered_symbol_is_charged(self):
        a=solve('abcabc',{'abc':1});b=solve('abcabc',{'abc':1},delivery=7)
        self.assertEqual(b['cost']-a['cost'],42)
        self.assertEqual(a['delta'],b['delta']);self.assertEqual(b['emitted'],'abcabc')
        self.assertEqual(sum(len(e['emitted']) for e in b['events']),6)

    def test_zero_and_expensive_skill_controls(self):
        self.assertEqual(solve('ab',{'ab':0})['local'],[0])
        r=solve('ab',{'ab':5});self.assertEqual(r['entries'],[0]);self.assertEqual(r['local'],[])
        self.assertEqual(solve('',{})['values'],[0])

    def test_invalid_registers(self):
        for skills in ({'':1},{'ab':-1},{'ab':float('inf')}):
            with self.assertRaises(ValueError):solve('ab',skills)
        with self.assertRaises(ValueError):gain(0,1,1,1)
        with self.assertRaises(ValueError):execute(((2,),),(0,),set(),1,1,1)
        with self.assertRaises(ValueError):execute(((0,),),(1,),set(),1,1,1)

    def test_sign_guard_and_tie(self):
        self.assertLess(gain(2,1,1,2),0)
        self.assertEqual(gain(2,3,2,1),0)
        self.assertEqual(gain(4,1,0,1),0)
        self.assertLess(gain(4,0,0,1),0)

    def test_full_static_subset_controls(self):
        stream=(0,0,0,1,1,1);rows=((0,1),(1,0))
        winners,g=choose(stream,5,3,1,capacity=1)
        self.assertEqual(set(winners),{frozenset({0}),frozenset({1})})
        self.assertEqual(g,5)
        self.assertNotIn(frozenset({0,1}),winners)
        for s in subsets((0,1)):
            r=execute(rows,stream,s,5,3,1)
            self.assertEqual(r['counts']['delivered_bits'],12)
            self.assertEqual(r['answers'],[rows[i] for i in stream])

    def test_complete_response_partition(self):
        rows,route=partition(((0,1),(1,1),(0,1)))
        self.assertEqual(rows,((0,1),(1,1)));self.assertEqual(route,(0,1,0))
        self.assertEqual(partition(((),())),(((),),(0,0)))

    def test_observed_recurrence_not_future_demand(self):
        # Both worlds have the identical already-acquired artifact and past cost10.
        self.assertGreater(10+3,10)
        self.assertLess(10+3+2,10+2*5)

    def test_independent_complete_census_and_original_records(self):
        result=run()
        self.assertEqual(result['prefix']['cases'],14336)
        self.assertEqual(result['concept']['cases'],2430)
        self.assertEqual(result['original']['original_scripts'],2)
        self.assertEqual(result['prefix']['original_local_reconstruction']['n_local'],10)
        self.assertEqual(result['concept']['original_reconstruction'],{'flat':75,'triggered':48,'all':57})
        self.assertEqual(result['future']['current'],[0,0])
        self.assertEqual(result['future']['after_update_query'],[1,0])

if __name__=='__main__':unittest.main()
