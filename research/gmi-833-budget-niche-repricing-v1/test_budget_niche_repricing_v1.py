from __future__ import annotations
import importlib.util, sys, unittest
from pathlib import Path
from fractions import Fraction as Q
ROOT=Path(__file__).resolve().parent
SPEC=importlib.util.spec_from_file_location('budget_niche_repricing_v1',ROOT/'budget_niche_repricing_v1.py')
m=importlib.util.module_from_spec(SPEC); assert SPEC.loader; sys.modules[SPEC.name]=m; SPEC.loader.exec_module(m)
class T(unittest.TestCase):
 def test_cert(self):
  r=m.finite_certificate(); self.assertEqual(r['verdict'],'GREEN'); self.assertTrue(all(r['checks'].values()))
 def test_budget(self):
  c=(m.make_search('a',2,1),m.make_search('b',0,2)); self.assertEqual(m.budget_winners(c,1),('a',)); self.assertEqual(m.budget_winners(c,2),('b',))
 def test_budget_stabilize(self):
  c=(m.make_search('a',2,1),m.make_search('b',0,2),m.make_search('c',1,3)); self.assertEqual(m.stabilization_budget(c),2); self.assertEqual(m.budget_winners(c,3),('b',))
 def test_niche(self):
  regs=(m.Regime('x',Q(1,2)),m.Regime('y',Q(1,2))); costs={('x','A'):0,('x','B'):1,('y','A'):1,('y','B'):0}; r=m.niche_summary(('A','B'),regs,costs); self.assertTrue(r['robust_coexistence'])
 def test_niche_tie(self):
  regs=(m.Regime('x',Q(1)),); costs={('x','A'):0,('x','B'):0}; r=m.niche_summary(('A','B'),regs,costs); self.assertEqual(r['lower'],{'A':Q(0),'B':Q(0)}); self.assertEqual(r['upper'],{'A':Q(1),'B':Q(1)})
 def test_reprice(self):
  c=(m.make_resource('A',(1,4)),m.make_resource('B',(4,1)),m.make_resource('C',(2,2))); self.assertEqual(m.repricing_boundaries(c,(0,1),(1,-1),Q(1,5),Q(4,5)),(Q(1,3),Q(1,2),Q(2,3)))
 def test_bad_price(self):
  c=(m.make_resource('A',(1,1)),)
  with self.assertRaises(m.LawError): m.price_winners(c,(0,1),(0,0),0)
 def test_bad_weights(self):
  with self.assertRaises(m.LawError): m.niche_summary(('A',),(m.Regime('x',Q(1,2)),),{('x','A'):0})
if __name__=='__main__': unittest.main()
