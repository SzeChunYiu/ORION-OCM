import json
import tempfile
import unittest
from fractions import Fraction
from pathlib import Path

import section_e_searcher_comparison_witness as w

class E2Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.r=w.build_results()

    def test_all_frozen_predictions(self):
        self.assertTrue(self.r['all_frozen_predictions_pass'])
        self.assertTrue(all(self.r['assertions'].values()))

    def test_random_exact_rank_distribution(self):
        row=w.random_parent()
        self.assertEqual(row['success_prob_at_10'],'5/16')
        self.assertEqual(row['expected_rank'],'33/2')
        self.assertEqual(row['expected_truth_example_touches'],'528')

    def test_strict_evolution_is_plateau_blocked(self):
        row=w.strict_evolution()
        self.assertFalse(row['success_probability_or_exact_success'])
        self.assertEqual(row['terminal'],w.STRICT_TERMINAL)
        self.assertEqual(row['truth_example_touches'],192)
        self.assertEqual(set(row['cache_errors'].values()),{16})

    def test_neutral_drift_is_exact_not_monte_carlo(self):
        row=w.neutral_drift_exact(T=5)
        self.assertEqual(row['paths_enumerated'],3125)
        self.assertEqual(row['success_probability'],'12/125')
        self.assertEqual(row['expected_unique_discrete_candidates_verified'],'15622/3125')
        self.assertEqual(row['expected_proposal_or_mutation_attempts'],'613/125')
        self.assertEqual(w.neutral_hit_dp(T=10),Fraction(72696,390625))

    def test_nas_ablation_is_successful_but_over_primary_cap(self):
        row=w.ablation_nas()
        self.assertEqual(row['hard_mask'],w.TARGET)
        self.assertEqual(row['exact_error'],0)
        self.assertEqual(row['truth_example_touches'],352)
        self.assertEqual(row['arithmetic_update_ops'],8320)
        self.assertFalse(row['within_primary_touch_cap'])

    def test_darts_gradient_is_derived_and_charged(self):
        ys=w.target_y(); z=[Fraction(1,2)]*w.N
        loss,grad,ops=w.relaxed_loss_grad(z,ys)
        self.assertEqual(loss,Fraction(31,128))
        self.assertEqual(grad,[Fraction(-1,32),Fraction(1,32),Fraction(-1,32),Fraction(1,32),Fraction(-1,32)])
        self.assertEqual(ops,2112)
        row=w.darts()
        self.assertEqual(row['arithmetic_update_ops'],2122)
        self.assertEqual(row['hard_mask'],w.TARGET)
        self.assertEqual(row['exact_error'],0)

    def test_gradient_negative_twin_fails_closed(self):
        row=w.darts(singleton=True)
        self.assertFalse(row['grammar_has_exact_target'])
        self.assertFalse(row['success_probability_or_exact_success'])
        self.assertEqual(row['terminal'],w.MISSPEC_TERMINAL)
        self.assertGreater(row['exact_error'],0)

    def test_remint_preserves_search_classes(self):
        target,support=w.remint_target()
        self.assertEqual((target,support),(11,[0,1,3]))
        self.assertEqual(w.neutral_drift_exact(target,5)['success_probability'],'12/125')
        self.assertEqual(w.neutral_hit_dp(target,10),Fraction(72696,390625))
        self.assertEqual(w.ablation_nas(target)['hard_mask'],11)
        self.assertEqual(w.darts(target)['hard_mask'],11)

    def test_accounting_counter_is_not_hardcoded(self):
        z=[Fraction(1,2)]*w.N
        loss,ops=w.relaxed_loss(z,w.target_y())
        self.assertEqual(loss,Fraction(31,128))
        self.assertEqual(ops,832)
        _,_,grad_ops=w.relaxed_loss_grad(z,w.target_y())
        self.assertEqual(grad_ops,2112)

    def test_receipt_reproduction(self):
        here=Path(__file__).resolve().parent
        committed=json.loads((here/'RESULT_E2.json').read_text())
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'result.json'; p.write_text(json.dumps(w.receipt(w.build_results()),indent=2,sort_keys=True)+'\n')
            rerun=json.loads(p.read_text())
        self.assertEqual(committed,rerun)

if __name__=='__main__': unittest.main()
