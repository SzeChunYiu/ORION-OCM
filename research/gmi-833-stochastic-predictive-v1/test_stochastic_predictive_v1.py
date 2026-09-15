#!/usr/bin/env python3
from fractions import Fraction as F
import importlib.util, pathlib, unittest, sys
P=pathlib.Path(__file__).with_name('stochastic_predictive_v1.py')
s=importlib.util.spec_from_file_location('sp',P);M=importlib.util.module_from_spec(s);sys.modules[s.name]=M;s.loader.exec_module(M)
class Tests(unittest.TestCase):
 def test_sep(self):
  p=M.separation_process();hs,ts,D=p.block(1,1);self.assertEqual(len(hs),3);self.assertEqual(len(set(D)),3);self.assertEqual(M.rank(D),2);self.assertEqual(M.rank_by_minors(D),2)
  f=M.factor(D);self.assertEqual(f['reconstructed'],D);self.assertEqual(len(f['core_columns']),2)
 def test_sep_relation(self):
  _,ts,D=M.separation_process().block(1,1);x=ts.index((('a','X'),));y=ts.index((('a','Y'),));self.assertEqual((D[0][x],D[0][y]),(F(1),F(0)));self.assertEqual((D[1][x],D[1][y]),(F(1,2),F(1,2)));self.assertEqual((D[2][x],D[2][y]),(F(0),F(1)))
 def test_rank_lower_bound_hostile(self):self.assertFalse(M.build_receipt()['SEP_1']['under_dimension_claim_accepted'])
 def test_illegal_merge(self):
  D=M.separation_process().block(1,1)[2];ok,w=M.exact_statistic(D,('x','x','y'));self.assertFalse(ok);self.assertIsNotNone(w)
 def test_legal_quotient(self):
  D=M.duplicate_row_process().block(1,1)[2];ok,w=M.exact_statistic(D,('x','x'));self.assertTrue(ok);self.assertIsNone(w);self.assertEqual(len(set(D)),1)
 def test_horizon(self):
  p=M.horizon_process();s=p.block(1,1)[2];l=p.block(1,2)[2];self.assertEqual(s[0],s[1]);self.assertNotEqual(l[0],l[1])
 def test_zero_history(self):
  p=M.separation_process();self.assertEqual(p.likelihood((('a','X'),)),0)
  with self.assertRaises(M.ContractError):p.ptest((('a','X'),),())
 def test_det(self):self.assertEqual(M.det(((F(1),F(2)),(F(3),F(5)))),-1)
 def test_ranks(self):
  self.assertEqual(M.rank(((F(0),F(0)),(F(0),F(0)))),0);self.assertEqual(M.rank_by_minors(((F(1),F(0)),(F(0),F(1)))),2)
 def test_singular_solve(self):
  with self.assertRaises(M.ContractError):M.solve(((F(1),F(1)),(F(2),F(2))),(F(1),F(2)))
 def test_census(self):
  c=M.small_census();self.assertEqual(c,{'blocks':81,'statistic_assignments':20736,'rank_class_failures':0,'factorization_failures':0,'statistic_minimality_failures':0,'class_count_strictly_above_rank_blocks':36})
 def test_latent_count(self):
  c=M.latent_census(5);self.assertEqual(c['observable_words_checked_including_empty'],63);self.assertEqual(c['nonempty_words_checked'],62);self.assertEqual(c['failures'],0);self.assertFalse(c['latent_cardinality_identified'])
 def test_receipt(self):
  r=M.build_receipt();self.assertEqual(r['terminal'],'GMI_833_FINITE_PREDICTIVE_RANK_V1_ALL_GREEN');self.assertEqual(r['claim_ceiling'],M.CLAIM_CEILING);self.assertIn('COMPLETE_GMI',r['forbidden_promotions']);self.assertEqual(len(r['gap_descendants_required_open']),4)
if __name__=='__main__':unittest.main()
