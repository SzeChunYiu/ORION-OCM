from __future__ import annotations
import importlib.util
from pathlib import Path
from fractions import Fraction as F
import sys, unittest

ROOT=Path(__file__).resolve().parent
SPEC=importlib.util.spec_from_file_location('history_switching_hysteresis_v1',ROOT/'history_switching_hysteresis_v1.py')
m=importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name]=m
SPEC.loader.exec_module(m)

class TestHistorySwitching(unittest.TestCase):
    def test_certificate_green(self):
        r=m.finite_certificate(); self.assertEqual(r['verdict'],'GREEN'); self.assertTrue(all(r['checks'].values()))
    def test_equal_cost_history(self):
        sw=m.symmetric_two_switch(1); dep,s=m.history_dependent(('A','B'),{'A':0,'B':0},sw)
        self.assertTrue(dep); self.assertEqual(s,{'A':('A',),'B':('B',)})
    def test_hysteresis_interior(self):
        sw=m.symmetric_two_switch(2)
        self.assertEqual(m.selection(('A','B'),{'A':3,'B':4},sw,'A'),('A',))
        self.assertEqual(m.selection(('A','B'),{'A':3,'B':4},sw,'B'),('B',))
    def test_hysteresis_outside(self):
        self.assertEqual(m.symmetric_expected(-2,1),(('B',),('B',)))
        self.assertEqual(m.symmetric_expected(2,1),(('A',),('A',)))
    def test_boundaries(self):
        self.assertEqual(m.affine_thresholds(-1,2,F(1,2)),(F(1,4),F(3,4)))
    def test_origin_additive(self):
        ms=('A','B','C'); b={'A':0,'B':1,'C':2}; u={'A':0,'B':1,'C':2}; v={'A':2,'B':0,'C':1}
        inv,s=m.origin_additive_invariant(ms,b,u,v); self.assertTrue(inv); self.assertEqual(len(set(s.values())),1)
    def test_margin(self):
        ms=('A','B'); b={'A':0,'B':3}; sw={('A','A'):0,('A','B'):1,('B','A'):1,('B','B'):0}
        self.assertTrue(m.uniform_winner_margin(ms,b,sw,'A'))
        self.assertEqual(m.selection(ms,b,sw,'A'),('A',)); self.assertEqual(m.selection(ms,b,sw,'B'),('A',))
    def test_reset(self):
        ms=('A','B'); b={'A':0,'B':0}; sw=m.symmetric_two_switch(1)
        self.assertEqual(m.reset_selection(ms,b,sw,'A'),{'A':('A',),'B':('A',)})
    def test_negative_switch_rejected(self):
        with self.assertRaises(m.SwitchingError): m.symmetric_two_switch(-1)
    def test_unknown_previous(self):
        with self.assertRaises(m.SwitchingError): m.selection(('A','B'),{'A':0,'B':1},m.symmetric_two_switch(1),'X')

if __name__=='__main__': unittest.main()
