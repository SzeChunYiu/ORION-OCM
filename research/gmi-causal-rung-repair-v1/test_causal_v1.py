from pathlib import Path
import sys,unittest
from fractions import Fraction as F
sys.path.insert(0,str(Path(__file__).resolve().parent))
from scm_v1 import model,from_units,law,complete_laws,evidence,necessity
from bounds_v1 import pn_bounds,endpoint_model,identified_or_bounds
from fiber_v1 import uniform_root_models,solve_fiber
from witnesses_v1 import rung_pairs,pair_results,orientation_result
from census_v1 import census

class CausalChecks(unittest.TestCase):
    def test_original_pair_all_nine_laws(self):
        r=pair_results()['six_original']
        self.assertTrue(r['all_nine_joint_laws_equal'])
        self.assertEqual((r['left_pn'],r['right_pn']),(F(1,2),F(1)))
        self.assertEqual(r['minimax_absolute_error'],F(1,4))
    def test_smaller_pair(self):
        r=pair_results()['two_smaller']
        self.assertTrue(r['all_nine_joint_laws_equal'])
        self.assertEqual((r['left_pn'],r['right_pn']),(F(0),F(1)))
    def test_smaller_with_both_treatments_observed(self):
        r=pair_results()['three_treatment_supported']
        self.assertTrue(r['all_nine_joint_laws_equal'])
        self.assertGreater(sum(r['observed'][:2]),0)
        self.assertGreater(sum(r['observed'][2:]),0)
    def test_faithfulness_does_not_orient(self):
        r=orientation_result()
        self.assertTrue(r['same_full_support_observed'] and r['dependent'])
        self.assertEqual((r['forward_do1'],r['reverse_do1']),(F(3,4),F(1,2)))
    def test_point_identification_control(self):
        w=from_units(((0,0,0),(1,0,1)))
        r=identified_or_bounds(*evidence(w))
        self.assertEqual((r['status'],r['lower'],r['upper']),('IDENTIFIED',F(1),F(1)))
    def test_general_rational_endpoint(self):
        p=(F(1,7),F(2,7),F(1,7),F(3,7)); q0,q1=F(4,7),F(5,7)
        self.assertEqual(pn_bounds(p,q0,q1),(F(1,3),F(2,3)))
        w=endpoint_model(p,q0,q1,F(1,2))
        self.assertEqual(evidence(w),(p,q0,q1)); self.assertEqual(necessity(w),F(1,2))
    def test_inconsistent_observation(self):
        with self.assertRaisesRegex(ValueError,'normalized'):
            pn_bounds((F(1),)*4,0,0)
    def test_empty_fiber_refusal(self):
        with self.assertRaisesRegex(ValueError,'empty compatible'):
            pn_bounds((F(1,4),)*4,F(0),F(1,2))
    def test_missing_conditioning_is_distinct(self):
        with self.assertRaisesRegex(ValueError,'undefined conditioning'):
            pn_bounds((1,0,0,0),0,0)
    def test_invalid_mass_not_coerced(self):
        for v in (-1,0.1,True):
            with self.assertRaises(ValueError): model((v,1,0,0,0,0,0,0))
    def test_invalid_interventions(self):
        w=from_units(((0,0,0),))
        for action in ((True,None),(2,None),[0,None],(0,)):
            with self.assertRaises(ValueError): law(w,action)
    def test_empty_units_refused(self):
        with self.assertRaises(ValueError): from_units(())
    def test_outside_interval_refused(self):
        with self.assertRaises(ValueError):
            endpoint_model((F(1,7),F(2,7),F(1,7),F(3,7)),F(4,7),F(5,7),F(1))
    def test_finite_solver_ambiguity_certificate(self):
        w=from_units(rung_pairs()['three_treatment_supported'][0])
        r=solve_fiber(uniform_root_models(3),complete_laws(w))
        self.assertEqual((r['status'],r['lower'],r['upper']),('PARTIALLY_IDENTIFIED',0,1))
        self.assertEqual(r['candidate_evaluations'],120)
        self.assertEqual(complete_laws(r['lower_model']),complete_laws(r['upper_model']))
    def test_finite_solver_no_alarm_identified(self):
        w=from_units(((1,0,1),))
        r=solve_fiber(uniform_root_models(1),complete_laws(w))
        self.assertEqual((r['status'],r['lower'],r['upper']),('IDENTIFIED',1,1))
    def test_same_laws_list_input_no_false_incompatibility(self):
        w=from_units(((1,0,1),))
        r=solve_fiber((w,),[list(p) for p in complete_laws(w)])
        self.assertEqual(r["status"],"IDENTIFIED")
    def test_undischarged_target_representation_refused(self):
        w=from_units(((1,0,1),))
        with self.assertRaisesRegex(ValueError,"exact rational"):
            solve_fiber((w,),complete_laws(w),target=lambda model:1.0)
    def test_original_prose_binding_drift_is_explicit(self):
        from source_evidence_v1 import original_results
        anchors=original_results()["original_receipt_anchors"]
        self.assertEqual([n for n,r in anchors.items() if not r["matches"]],
                         ["CAUSAL_COGNITION_SEPARATOR_THEOREM_V1.md"])
    def test_declared_class_empty_is_invalid(self):
        with self.assertRaises(ValueError): solve_fiber((),())
    def test_no_compatible_model_not_identified(self):
        a=from_units(((1,0,1),)); b=from_units(((1,1,1),))
        self.assertEqual(solve_fiber((a,),complete_laws(b))['status'],'INCOMPATIBLE')
    def test_exhaustive_real_model_census(self):
        rows=census()
        self.assertEqual([r['models'] for r in rows],[8,36,120,330,792,1716])
        self.assertEqual(rows[0]['ambiguous_fibers'],0)
        self.assertGreater(rows[1]['ambiguous_fibers'],0)
        self.assertEqual(rows[1]['treatment_supported_ambiguous_fibers'],0)
        self.assertGreater(rows[2]['treatment_supported_ambiguous_fibers'],0)

if __name__=='__main__': unittest.main()
