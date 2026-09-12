from fractions import Fraction as F
import unittest
import target_witness_gap as g

class TargetWitnessGap(unittest.TestCase):
    def test_one_witness_not_class_optimum(self):
        out = g.compare_target_bounds(5, 1, 10)
        self.assertTrue(out['beats_witness'])
        self.assertFalse(out['beats_target_class_if_lower_bound_valid'])

    def test_lower_bound_gives_sufficient_certificate(self):
        self.assertTrue(g.compare_target_bounds(3, 4, 10)['beats_target_class_if_lower_bound_valid'])

    def test_tie_is_not_strict_dominance(self):
        out = g.compare_target_bounds(4, 4, 10)
        self.assertFalse(out['beats_target_class_if_lower_bound_valid'])
        self.assertTrue(out['ties_lower_bound'])

    def test_reversed_bounds_rejected(self):
        with self.assertRaises(ValueError):
            g.compare_target_bounds(5, 12, 10)

    def test_finite_certificates(self):
        receipt = g.finite_bound_check()
        self.assertEqual(receipt['finite_class_bound_checks'], 216)
        self.assertGreater(receipt['beating_witness_without_beating_class'], 0)

    def test_source_projection_has_strict_cost_order(self):
        receipt = g.source_derived_receipt()
        self.assertTrue(receipt['strict_order_target_then_non_target_then_witness'])
        self.assertGreater(receipt['canonical_target_witness_cost'] - receipt['non_target_cost_between_them'], 10)

    def test_source_projection_preserves_target_coordinates(self):
        w = g.linear_candidate(False, False)
        t = g.linear_candidate(True, False)
        n = g.linear_candidate(True, True)
        self.assertEqual(w['vector'], t['vector'])
        self.assertNotEqual(w['vector'], n['vector'])
        self.assertEqual([x['positive_linear_surrogate_score'] for x in [w,t,n]], [F(1)]*3)
