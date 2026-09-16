import importlib.util,json,subprocess,sys,unittest
from pathlib import Path
from fractions import Fraction as F
R=Path(__file__).resolve().parent
sp=importlib.util.spec_from_file_location('cn',R/'cost_neutrality_v1.py');M=importlib.util.module_from_spec(sp);sys.modules[sp.name]=M;sp.loader.exec_module(M)
class T(unittest.TestCase):
 def test_freeze(self):self.assertEqual(M.FREEZE_COMMIT,'2460f0624410f639eac50f3464feedd67218857a')
 def test_presentations(self):self.assertEqual(len(M.presentations()),126)
 def test_dist(self):self.assertEqual(len(M.distances()),126)
 def test_label_checks(self):self.assertEqual(M.label_blind_certificate(),{'label_permutations':24,'weight_vectors':3,'checks':72,'failures':0})
 def test_iso_checks(self):self.assertEqual(M.isometric_certificate(),{'node_remints':24,'weight_vectors':3,'checks':72,'failures':0})
 def test_struct_all(self):
  for r in M.structural_pair().values():self.assertEqual((r['GA'],r['GB']),('A','B'))
 def test_dominance(self):self.assertEqual(M.g0_pareto_certificate()['dominance_violations'],0)
 def test_dom_count(self):self.assertEqual(M.g0_pareto_certificate()['ordered_strict_dominance_pairs'],1819)
 def test_incomp(self):self.assertTrue(M.g0_pareto_certificate()['incomparable_control_reverses'])
 def test_clean(self):self.assertEqual(M.hostiles()['clean'],'CLEAN_LABEL_BLIND_COST')
 def test_family_hostile(self):self.assertEqual(M.hostiles()['family_adjustment'],'FAMILY_LABEL_COST_PRIVILEGE')
 def test_target_hostile(self):self.assertEqual(M.hostiles()['target_adjustment'],'TARGET_SPECIFIC_COST_PRIVILEGE')
 def test_zero_hostile(self):self.assertEqual(M.hostiles()['zero_primitive'],'ZERO_OR_INVALID_PRIMITIVE_PRICE')
 def test_float_hostile(self):self.assertEqual(M.hostiles()['float_weight'],'INVALID_STRICTLY_POSITIVE_RATIONAL_WEIGHT')
 def test_scalar_bad(self):
  with self.assertRaises(ValueError):M.scalar((1,1),(1.0,F(1)))
 def test_row_disposition(self):self.assertEqual(M.build_receipt()['row_disposition'],'NO_UNIVERSAL_GRAMMAR_NEUTRALITY__STRUCTURAL_BIAS_COUNTEREXAMPLE')
 def test_narrow(self):self.assertEqual(M.build_receipt()['narrow_positive_terminal'],'LABEL_BLIND_AND_ISOMETRICALLY_INVARIANT_AT_REGISTERED_SCOPE')
 def test_green(self):self.assertEqual(M.build_receipt()['terminal'],'GMI_833_COST_NEUTRALITY_BOUNDARY_V1_ALL_GREEN')
 def test_committed(self):self.assertEqual(M.canonical_json(M.build_receipt()),(R/'RESULT_V1.json').read_text())
 def test_oracle(self):
  o=json.loads(subprocess.run([sys.executable,'-I','-B',str(R/'independent_oracle_v1.py')],check=True,text=True,capture_output=True).stdout);r=M.build_receipt()
  self.assertEqual(o['label_blind_checks'],r['label_blind_certificate']['checks']);self.assertEqual(o['isometric_checks'],r['isometric_remint_certificate']['checks'])
  for k in ('ordered_strict_dominance_pairs','dominance_weight_checks','dominance_violations','incomparable_control_reverses'):self.assertEqual(o[k],r['pareto_certificate'][k])
  self.assertEqual(o['terminal'],'GREEN')
if __name__=='__main__':unittest.main()
