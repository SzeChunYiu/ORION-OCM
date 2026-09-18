from __future__ import annotations
import importlib.util,sys,unittest,json
from fractions import Fraction
from pathlib import Path
HERE=Path(__file__).resolve().parent
sp=importlib.util.spec_from_file_location('af5',HERE/'af5_verification_barriers_v1.py');af5=importlib.util.module_from_spec(sp);sys.modules['af5']=af5;sp.loader.exec_module(af5)

class T(unittest.TestCase):
 def safe(self):return af5.System(('bad','s0','s1','s2'),'s0',(('s0','s1'),('s1','s2')),'bad')
 def bug4(self):return af5.System(('bad','s0','s1','s2','s3'),'s0',(('s0','s1'),('s1','s2'),('s2','s3'),('s3','bad')),'bad')
 def test_01_parent_no_go_not_executor_proof(self):self.assertEqual(af5.certificate()['parent_no_go']['ownership'],'PARENT_OWNED_NOT_PROVED_BY_EXECUTOR')
 def test_02_lattice_named_points(self):self.assertEqual(af5.lattice_meet(af5.STATUS_POINTS['CERTIFIABLE'],af5.STATUS_POINTS['SOUND_INCOMPLETE_APPROXIMATION']),frozenset({'SOUND_ACCEPT','TERMINATES'}))
 def test_03_finite_exact_safe(self):self.assertEqual(af5.exact_safety(self.safe())['status'],'ACCEPT_SAFE')
 def test_04_cert_missing_init(self):
  with self.assertRaisesRegex(ValueError,'MISSING_INITIAL'):af5.validate_certificate(self.safe(),('s1','s2'))
 def test_05_cert_not_inductive(self):
  with self.assertRaisesRegex(ValueError,'NOT_INDUCTIVE'):af5.validate_certificate(self.safe(),('s0',))
 def test_06_cert_contains_bad(self):
  with self.assertRaisesRegex(ValueError,'CONTAINS_BAD'):af5.validate_certificate(self.safe(),('s0','s1','s2','bad'))
 def test_07_valid_cert_has_separate_costs(self):
  r=af5.validate_certificate(self.safe(),('s0','s1','s2'));self.assertGreater(r['proof_construct_cost'],0);self.assertGreater(r['proof_check_cost'],0)
 def test_08_coarse_false_alarm_not_bug(self):
  r=af5.abstract_system(self.safe(),{'s0':'A','s1':'B','s2':'C','bad':'C'});self.assertEqual(r['status'],'UNKNOWN_FALSE_ALARM_POSSIBLE')
 def test_09_unsound_missing_map_rejected(self):
  with self.assertRaisesRegex(ValueError,'NOT_TOTAL'):af5.abstract_system(self.safe(),{'s0':'A'})
 def test_10_cegar_spurious_then_proves(self):self.assertEqual(af5.cegar_safe_fixture(self.safe(),{'s0':'A','s1':'B','s2':'C','bad':'C'})['refinements'],1)
 def test_11_cegar_always_terminates_forbidden(self):
  with self.assertRaisesRegex(ValueError,'FORBIDDEN_PROMOTION'):af5.validate_terminal('CEGAR_ALWAYS_TERMINATES')
 def test_12_bmc_three_not_unbounded_proof(self):self.assertFalse(af5.bmc(self.bug4(),3)['unbounded_safety_proved'])
 def test_13_bmc_four_finds_bug(self):self.assertEqual(af5.bmc(self.bug4(),4)['status'],'BUG_WITNESS_WITHIN_BOUND')
 def test_14_property_test_exact_contract(self):
  r=af5.property_test((1,1,1,1,0,0,0,0),3);self.assertEqual(r['exact_reject_probability'],'13/14');self.assertEqual(r['delta'],'1/14');self.assertFalse(r['exact_decider'])
 def test_15_property_test_wrong_promise_rejected(self):
  with self.assertRaisesRegex(ValueError,'FROZEN_PROMISE'):af5.property_test((1,0,0,0,0,0,0,0),3)
 def test_16_semidecision_safe_unknown(self):self.assertTrue(af5.semidecision(self.safe())['status'].startswith('UNKNOWN'))
 def test_17_selection_tie_preserved(self):self.assertEqual(af5.selection(Fraction(1))['argmin'],['DIRECT_REPLAY','CERTIFICATE_EMITTER'])
 def test_18_selection_reprices(self):self.assertEqual(af5.selection(Fraction(2))['argmin'],['CERTIFICATE_EMITTER'])
 def test_19_forbidden_unrestricted_solution(self):
  with self.assertRaisesRegex(ValueError,'FORBIDDEN_PROMOTION'):af5.validate_terminal('UNRESTRICTED_SEMANTIC_VERIFICATION_SOLVED')
 def test_20_parent_ledger(self):
  o=json.loads((HERE/'PARENT_LEDGER_V1.json').read_text());self.assertGreaterEqual(len(o['rows']),6);self.assertTrue(any('Proof-Carrying' in r.get('owner','') for r in o['rows']))
if __name__=='__main__':unittest.main()
