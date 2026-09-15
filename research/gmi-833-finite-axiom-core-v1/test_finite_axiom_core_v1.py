from __future__ import annotations
from copy import deepcopy
from fractions import Fraction as F
import importlib.util, json
from pathlib import Path
import sys, unittest

ROOT=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('core',ROOT/'finite_axiom_core_v1.py')
core=importlib.util.module_from_spec(spec); sys.modules[spec.name]=core; spec.loader.exec_module(core)
vspec=importlib.util.spec_from_file_location('spine',ROOT/'validate_axiom_spine_v1.py')
spine=importlib.util.module_from_spec(vspec); sys.modules[vspec.name]=spine; vspec.loader.exec_module(spine)

class TestFiniteAxiomCore(unittest.TestCase):
    def setUp(self): self.m=core.build_model()
    def test_base_axioms_green(self): self.assertTrue(core.check_model(self.m)['axioms_green'])
    def test_base_derived_green(self): self.assertTrue(core.check_model(self.m)['derived_green'])
    def test_behavioral_quotient_nontrivial(self): self.assertEqual(core.behavioral_partition(self.m),(('s0','s1'),('s2',)))
    def test_behavior_certificate_exact(self): self.assertEqual(core.check_behavior_certificate(self.m),(True,'GREEN'))
    def test_development_reachability(self): self.assertEqual(core.development_reachable(self.m),('s0','s1','s2'))
    def test_achievable_capability(self):
        ok,errs,d=core.check_capability_certificates(self.m); self.assertTrue(ok,errs); self.assertEqual(d['achievable']['ceiling'],F(1)); self.assertFalse(d['achievable']['impossible'])
    def test_impossible_capability(self):
        d=core.check_capability_certificates(self.m)[2]; self.assertEqual(d['impossible']['ceiling'],F(0)); self.assertTrue(d['impossible']['impossible'])
    def test_query_abstains(self): self.assertEqual(core.query_terminal(self.m),{'terminal':'CANNOT_IDENTIFY','values':(0,1)})
    def test_all_uncertainty_tags(self): self.assertEqual(set(o['tag'] for o in self.m['uncertainty_objects']),set(core.ALLOWED_UNCERTAINTY_TAGS))
    def test_morphology_renaming(self): self.assertTrue(core.mechanism_isomorphic(self.m,core.renamed_model(self.m),{'s0':'x','s1':'y','s2':'z'}))
    def test_ax1_independent(self): self.assertTrue(core.axiom_independence_witnesses()['AX-1']['only_target_false'])
    def test_ax2_independent(self): self.assertTrue(core.axiom_independence_witnesses()['AX-2']['only_target_false'])
    def test_ax3_independent(self): self.assertTrue(core.axiom_independence_witnesses()['AX-3']['only_target_false'])
    def test_ax4_independent(self): self.assertTrue(core.axiom_independence_witnesses()['AX-4']['only_target_false'])
    def test_ax5_independent(self): self.assertTrue(core.axiom_independence_witnesses()['AX-5']['only_target_false'])
    def test_empty_positive_confidence_hostile(self):
        r=core.targeted_hostiles()['empty_positive_confidence']; self.assertFalse(r['ok']); self.assertIn('ConfidenceSet:COVERAGE_PREMISE_FALSE',r['errors'])
    def test_capability_certificate_hostile(self):
        r=core.targeted_hostiles()['capability_ceiling_below_attained']; self.assertFalse(r['ok']); self.assertEqual(r['errors'],['DEF-CAP:CERTIFICATE:achievable'])
    def test_behavior_equivalence_hostile(self):
        r=core.targeted_hostiles()['malformed_behavior_equivalence']; self.assertFalse(r['ok']); self.assertEqual(r['errors'],['DEF-BEQ:CERTIFICATE_MISMATCH'])
    def test_finite_to_universal_hostile(self):
        m=deepcopy(self.m); claims=list(m['scope_claims']); claims[1]=dict(claims[1],claim_scope='UNIVERSAL'); m['scope_claims']=tuple(claims)
        r=core.check_axioms(m)['AX-5']; self.assertFalse(r['ok']); self.assertIn('scope:UNSUPPORTED:FINITE_EXHAUSTIVE->UNIVERSAL',r['errors'])
    def test_dev_outside_carrier_hostile(self):
        m=deepcopy(self.m); m['development_edges']+=(('OUT','s0'),); r=core.check_axioms(m)['AX-1']; self.assertFalse(r['ok']); self.assertIn('development:TYPED',r['errors'])
    def test_missing_transition_hostile(self):
        m=deepcopy(self.m); del m['transition'][('s0','stay')]; r=core.check_axioms(m)['AX-2']; self.assertFalse(r['ok']); self.assertIn('transition:TOTAL',r['errors'])
    def test_negative_resource_hostile(self):
        m=deepcopy(self.m); m['resources']=(F(-1),F(1)); r=core.check_axioms(m)['AX-3']; self.assertFalse(r['ok'])
    def test_confidence_outside_domain_hostile(self):
        m=deepcopy(self.m); objs=list(m['uncertainty_objects']); c=dict(objs[1],values=('s0','OUT')); objs[1]=c; m['uncertainty_objects']=tuple(objs); r=core.check_axioms(m)['AX-4']; self.assertFalse(r['ok']); self.assertIn('ConfidenceSet:SUBSET',r['errors'])
    def test_bounded_census(self):
        self.assertEqual(core.bounded_structural_census(),{'candidates':23328,'structurally_satisfying':1024,'ax1_failures':11664,'ax2_failures':18720,'ax3_failures':12960})
    def test_spine_valid(self): self.assertEqual(spine.validate_all(),{'axioms':5,'definitions':8,'nodes':18,'reduction_rows':10,'theorems':5})
    def test_cycle_hostile(self):
        s=json.loads((ROOT/'AXIOM_SPINE_V1.json').read_text()); s['nodes'][-1]['dependencies']=['CORE-5']
        with self.assertRaises(spine.ValidationError): spine.validate_graph(s)
    def test_reduction_targets_resolve(self):
        s=json.loads((ROOT/'AXIOM_SPINE_V1.json').read_text()); by=spine.validate_graph(s); r=json.loads((ROOT/'FOUNDATION_REDUCTION_V1.json').read_text()); spine.validate_reduction(r,by)
    def test_receipt_green(self):
        r=core.build_receipt(); self.assertEqual(r['terminal'],'GMI_833_FINITE_AXIOM_CORE_V1_ALL_GREEN'); self.assertEqual(r['axiom_count'],5); self.assertIn('COMPLETE_GMI',r['forbidden_promotions'])

if __name__=='__main__': unittest.main()
