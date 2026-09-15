from __future__ import print_function

import os
import sys
import unittest
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import transport_v1 as tv1


class TransportTests(unittest.TestCase):
    def test_frozen_five_kind_chain(self):
        campaign = tv1.frozen_five_kind_campaign()
        states = campaign.propagate_all()
        expected = [
            ("v0", {-1, 0, 1}),
            ("v1", {0, 1, 2}),
            ("v2", {0, 1, 2}),
            ("v3", {0, 1, 2, 3}),
            ("v4", {-1, 0, 1, 2, 3, 4}),
            ("v5", {0, 1, 4, 9, 16}),
        ]
        self.assertEqual(len(states), len(expected))
        for state, (version, values) in zip(states, expected):
            self.assertEqual(state.version, version)
            self.assertEqual(state.uncertainty, frozenset(Fraction(x) for x in values))
            self.assertEqual(state.failure_budget, Fraction(1, 20))
            self.assertEqual(state.raw_visits, 0)
            self.assertEqual(state.raw_sum, Fraction(0))
            self.assertEqual(state.inherited_tokens, ())
            self.assertEqual(state.inherited_origins, ())

    def test_all_change_kinds_present(self):
        campaign = tv1.frozen_five_kind_campaign()
        self.assertEqual(tuple(c.change_kind for c in campaign.contracts), tv1.ALLOWED_KINDS)

    def test_post_activation_registration_rejected(self):
        F = Fraction
        c = tv1.TransportCampaign("v0", (F(0),), F(0))
        c.activate_source((F(0),))
        with self.assertRaises(RuntimeError):
            c.register_contract("x", "v0", "v1", "INFO", (F(0),), (F(0),), ((F(0), F(0)),))

    def test_incomplete_relation_rejected(self):
        F = Fraction
        c = tv1.TransportCampaign("v0", (F(0), F(1)), F(0))
        with self.assertRaises(ValueError):
            c.register_contract("x", "v0", "v1", "INFO", (F(0), F(1)), (F(0), F(1)), ((F(0), F(0)),))

    def test_out_of_domain_endpoint_rejected(self):
        F = Fraction
        c = tv1.TransportCampaign("v0", (F(0),), F(0))
        with self.assertRaises(ValueError):
            c.register_contract("x", "v0", "v1", "INFO", (F(0),), (F(0),), ((F(0), F(1)),))

    def test_version_skip_rejected(self):
        F = Fraction
        c = tv1.TransportCampaign("v0", (F(0),), F(0))
        with self.assertRaises(ValueError):
            c.register_contract("x", "v0", "v2", "INFO", (F(0),), (F(0),), ((F(0), F(0)),))

    def test_version_back_edge_rejected(self):
        F = Fraction
        c = tv1.TransportCampaign("v1", (F(0),), F(0))
        with self.assertRaises(ValueError):
            c.register_contract("x", "v1", "v0", "INFO", (F(0),), (F(0),), ((F(0), F(0)),))

    def test_malformed_budgets_rejected(self):
        F = Fraction
        for value in (-0.01, 0.1, 1.01):
            with self.assertRaises(TypeError):
                tv1.TransportCampaign("v0", (F(0),), value)
        for value in (F(-1, 10), F(11, 10)):
            with self.assertRaises(ValueError):
                tv1.TransportCampaign("v0", (F(0),), value)

    def test_relation_budget_type_and_range_rejected(self):
        F = Fraction
        for value, exc in ((0.1, TypeError), (F(-1, 10), ValueError), (F(11, 10), ValueError)):
            c = tv1.TransportCampaign("v0", (F(0),), F(0))
            with self.assertRaises(exc):
                c.register_contract("x", "v0", "v1", "INFO", (F(0),), (F(0),), ((F(0), F(0)),), value)

    def test_source_uncertainty_outside_domain_rejected(self):
        F = Fraction
        c = tv1.TransportCampaign("v0", (F(0),), F(0))
        with self.assertRaises(ValueError):
            c.activate_source((F(1),))

    def test_zero_beta_preserves_failure_budget(self):
        states = tv1.frozen_five_kind_campaign().propagate_all()
        self.assertTrue(all(s.failure_budget == Fraction(1, 20) for s in states))

    def test_uncertain_budgets_add_without_independence(self):
        F = Fraction
        self.assertEqual(F(1, 20) + F(1, 100) + F(1, 200), F(13, 200))
        self.assertEqual(F(1) - F(13, 200), F(187, 200))
        control = tv1._tight_union_bound_control()
        self.assertTrue(control["bound_is_tight"])
        self.assertFalse(control["independence_used"])

    def test_countable_budget_identity(self):
        F = Fraction
        beta = F(1, 20)
        for n in (1, 2, 5, 1000):
            observed = sum((beta / F(t * (t + 1)) for t in range(1, n + 1)), F(0))
            self.assertEqual(observed, beta * F(n, n + 1))
            self.assertLess(observed, beta)
        self.assertEqual(F(1) - F(1, 20) - beta, F(9, 10))

    def test_missing_relation_returns_full_target(self):
        F = Fraction
        c = tv1.TransportCampaign("v0", (F(0),), F(0))
        c.activate_source((F(0),))
        state = c.propagate_missing_relation("v1", (F(0), F(1), F(2)))
        self.assertEqual(state.uncertainty, frozenset((F(0), F(1), F(2))))
        self.assertEqual(state.terminal, "CANNOT_IDENTIFY_NO_RELATION")

    def test_missing_relation_query_identifiability(self):
        F = Fraction
        c = tv1.TransportCampaign("v0", (F(0),), F(0))
        c.activate_source((F(0),))
        state = c.propagate_missing_relation("v1", (F(0), F(1), F(2)))
        self.assertEqual(tv1.identify_boolean(state, lambda x: x > 0), "CANNOT_IDENTIFY")
        self.assertEqual(tv1.identify_boolean(state, lambda x: True), "IDENTIFIED_TRUE")

    def test_copy_source_set_counterexample(self):
        source_set = {0}
        target_domain = {0, 1}
        actual_target = 1
        self.assertNotIn(actual_target, source_set)
        self.assertIn(actual_target, target_domain)

    def test_relational_image_matches_independent_comprehension(self):
        F = Fraction
        source_domain = tuple(F(x, 2) for x in range(-4, 5))
        relation = tuple((x, y) for x in source_domain for y in (x - F(1, 2), x + F(1, 2)))
        for left in range(0, 5):
            source = frozenset(source_domain[left:left + 3])
            direct = frozenset(y for x, y in relation if x in source)
            self.assertEqual(tv1.relational_image(source, relation), direct)

    def test_affine_interval_frozen_hull(self):
        F = Fraction
        lo, hi = tv1.affine_interval_hull(F(1, 4), F(3, 4), F(-2), F(3), F(-1, 10), F(1, 10))
        self.assertEqual((lo, hi), (F(7, 5), F(13, 5)))

    def test_affine_interval_matches_corners(self):
        F = Fraction
        lo, hi = tv1.affine_interval_hull(F(1, 4), F(3, 4), F(-2), F(3), F(-1, 10), F(1, 10))
        corners = [F(-2) * x + F(3) + e for x in (F(1, 4), F(3, 4)) for e in (F(-1, 10), F(1, 10))]
        self.assertEqual(lo, min(corners))
        self.assertEqual(hi, max(corners))

    def test_nonlinear_finite_relation(self):
        F = Fraction
        source = frozenset((F(-1), F(0), F(1)))
        relation = tuple((x, y) for x in source for y in (x * x - 1, x * x, x * x + 1))
        self.assertEqual(tv1.relational_image(source, relation), frozenset(F(x) for x in (-1, 0, 1, 2)))

    def test_transport_state_has_zero_raw_evidence(self):
        for state in tv1.frozen_five_kind_campaign().propagate_all()[1:]:
            self.assertEqual((state.raw_visits, state.raw_sum, state.inherited_tokens, state.inherited_origins),
                             (0, Fraction(0), (), ()))

    def test_failure_budget_capped_at_one(self):
        F = Fraction
        c = tv1.TransportCampaign("v0", (F(0),), F(9, 10))
        c.register_contract("x", "v0", "v1", "INFO", (F(0),), (F(0),), ((F(0), F(0)),), F(3, 10))
        c.activate_source((F(0),))
        self.assertEqual(c.propagate_contract(0).failure_budget, F(1))

    def test_duplicate_relation_pair_rejected(self):
        F = Fraction
        c = tv1.TransportCampaign("v0", (F(0),), F(0))
        with self.assertRaises(ValueError):
            c.register_contract("x", "v0", "v1", "INFO", (F(0),), (F(0),), ((F(0), F(0)), (F(0), F(0))))

    def test_receipt_is_deterministic(self):
        self.assertEqual(tv1.build_receipt(), tv1.build_receipt())


if __name__ == "__main__":
    unittest.main(verbosity=2)
