from __future__ import annotations

from fractions import Fraction
import json
import unittest

from uncertainty_composition_v1 import (
    CANNOT_IDENTIFY,
    IDENTIFIED_FALSE,
    IDENTIFIED_TRUE,
    INCONSISTENT_EMPTY_IMAGE,
    MISSING_RELATION_FULL_DOMAIN,
    CompositionCampaign,
    Stage,
    build_receipt,
    canonical_receipt_bytes,
    complete_relation,
    compose_relations,
    coverage_lower_bound,
    exhaustive_uc1_certificate,
    frozen_chain,
    hostile_dependence_receipt,
    identify_boolean_query,
    relational_image,
)

F = Fraction


class UncertaintyCompositionV1Tests(unittest.TestCase):
    def test_uc1_exhaustive_1024_cases(self):
        cert = exhaustive_uc1_certificate()
        self.assertEqual(cert["cases"], 1024)
        self.assertEqual(cert["failures"], 0)
        self.assertTrue(cert["all_hold"])

    def test_frozen_heterogeneous_chain(self):
        x0, x1, x2, s0, r0, r1 = frozen_chain()
        s1 = relational_image(x0, x1, r0, s0)
        s2 = relational_image(x1, x2, r1, s1)
        self.assertEqual(s1, ("a", "b"))
        self.assertEqual(s2, (10, 20, 30, 40))

    def test_direct_composed_image_equals_sequential(self):
        x0, x1, x2, s0, r0, r1 = frozen_chain()
        s1 = relational_image(x0, x1, r0, s0)
        sequential = relational_image(x1, x2, r1, s1)
        composed = compose_relations(x0, x1, x2, r0, r1)
        direct = relational_image(x0, x2, composed, s0)
        self.assertEqual(sequential, direct)

    def test_functional_specialization(self):
        x = (0, 1, 2)
        y = (2, 3, 4)
        z = (4, 9, 16)
        r = ((0, 2), (1, 3), (2, 4))
        q = ((2, 4), (3, 9), (4, 16))
        s = (0, 2)
        sequential = relational_image(y, z, q, relational_image(x, y, r, s))
        direct = relational_image(x, z, compose_relations(x, y, z, r, q), s)
        self.assertEqual(sequential, (4, 16))
        self.assertEqual(sequential, direct)

    def test_empty_relation_gives_empty_image(self):
        self.assertEqual(relational_image((0, 1), ("a",), (), (0,)), ())

    def test_relation_endpoint_validation_fails_closed(self):
        with self.assertRaises(ValueError):
            relational_image((0, 1), ("a",), ((2, "a"),), (0,))

    def test_subset_endpoint_validation_fails_closed(self):
        with self.assertRaises(ValueError):
            relational_image((0, 1), ("a",), ((0, "a"),), (2,))

    def test_duplicate_domain_fails_closed(self):
        with self.assertRaises(ValueError):
            relational_image((0, 0), ("a",), (), ())

    def test_duplicate_relation_pair_fails_closed(self):
        with self.assertRaises(ValueError):
            relational_image((0,), ("a",), ((0, "a"), (0, "a")), (0,))

    def test_exact_coverage_187_over_200(self):
        lower = coverage_lower_bound(F(1, 20), (F(1, 100), F(1, 200)))
        self.assertEqual(lower, F(187, 200))

    def test_coverage_floor_is_zero(self):
        lower = coverage_lower_bound(F(3, 4), (F(1, 2),))
        self.assertEqual(lower, F(0))

    def test_non_fraction_budget_rejected(self):
        with self.assertRaises(ValueError):
            coverage_lower_bound(0.1, (F(1, 10),))

    def test_out_of_range_budget_rejected(self):
        with self.assertRaises(ValueError):
            coverage_lower_bound(F(1, 20), (F(6, 5),))

    def test_boolean_query_identified_true(self):
        self.assertEqual(
            identify_boolean_query((10, 20, 30), lambda x: x % 10 == 0),
            IDENTIFIED_TRUE,
        )

    def test_boolean_query_identified_false(self):
        self.assertEqual(
            identify_boolean_query((10, 20, 30), lambda x: x < 0),
            IDENTIFIED_FALSE,
        )

    def test_boolean_query_mixed_is_not_identified(self):
        self.assertEqual(
            identify_boolean_query((10, 20, 30, 40), lambda x: x > 25),
            CANNOT_IDENTIFY,
        )

    def test_empty_image_is_inconsistent_not_vacuously_identified(self):
        self.assertEqual(
            identify_boolean_query((), lambda _: True),
            INCONSISTENT_EMPTY_IMAGE,
        )

    def test_complete_relation_image_is_full_target_for_nonempty_source(self):
        x = (0, 1, 2)
        y = ("a", "b", "c")
        relation = complete_relation(x, y)
        self.assertEqual(relational_image(x, y, relation, (1,)), ("a", "b", "c"))

    def test_missing_relation_fails_closed_to_full_target(self):
        x0 = (0, 1)
        x1 = ("a", "b", "c")
        campaign = CompositionCampaign(x0, F(1, 20))
        campaign.register(Stage("missing", x0, x1, None, F(0)))
        campaign.activate()
        result = campaign.propagate((0,))
        self.assertEqual(result.target_set, ("a", "b", "c"))
        self.assertEqual(result.markers, (MISSING_RELATION_FULL_DOMAIN,))
        self.assertEqual(result.lower_coverage, F(19, 20))

    def test_missing_relation_cannot_claim_unregistered_beta(self):
        x0 = (0, 1)
        x1 = ("a", "b")
        with self.assertRaises(ValueError):
            Stage("missing", x0, x1, None, F(1, 2))

    def test_registered_stage_beta_is_charged(self):
        x0 = (0, 1)
        x1 = ("a", "b")
        campaign = CompositionCampaign(x0, F(1, 10))
        campaign.register(Stage("r", x0, x1, ((0, "a"), (1, "b")), F(1, 20)))
        campaign.activate()
        result = campaign.propagate((0,))
        self.assertEqual(result.target_set, ("a",))
        self.assertEqual(result.lower_coverage, F(17, 20))

    def test_mutation_after_activation_rejected(self):
        x0 = (0, 1)
        x1 = ("a", "b")
        campaign = CompositionCampaign(x0, F(0))
        campaign.activate()
        with self.assertRaises(RuntimeError):
            campaign.register(Stage("late", x0, x1, ((0, "a"),), F(0)))

    def test_propagation_before_activation_rejected(self):
        campaign = CompositionCampaign((0, 1), F(0))
        with self.assertRaises(RuntimeError):
            campaign.propagate((0,))

    def test_incompatible_stage_chain_rejected(self):
        campaign = CompositionCampaign((0, 1), F(0))
        campaign.register(Stage("r0", (0, 1), ("a",), ((0, "a"),), F(0)))
        with self.assertRaises(ValueError):
            campaign.register(Stage("bad", ("x",), (10,), (("x", 10),), F(0)))

    def test_hostile_disjoint_failures_refute_product_lower_bound(self):
        hostile = hostile_dependence_receipt()["disjoint_failures"]
        self.assertEqual(hostile["true_joint_good"], "1/2")
        self.assertEqual(hostile["independence_product"], "9/16")
        self.assertEqual(hostile["union_bound_lower"], "1/2")
        self.assertTrue(hostile["product_is_unsound_lower_bound"])
        self.assertTrue(hostile["union_bound_is_attained"])

    def test_overlap_control_shows_union_bound_can_be_conservative(self):
        hostile = hostile_dependence_receipt()["overlapping_failures"]
        self.assertEqual(hostile["true_joint_good"], "3/4")
        self.assertEqual(hostile["union_bound_lower"], "1/2")
        self.assertTrue(hostile["union_bound_is_conservative"])

    def test_receipt_has_frozen_query_outcomes(self):
        receipt = build_receipt()
        q = receipt["concrete_chain"]["query_outcomes"]
        self.assertEqual(q["q_even"], IDENTIFIED_TRUE)
        self.assertEqual(q["q_gt_25"], CANNOT_IDENTIFY)
        self.assertEqual(q["q_le_40"], IDENTIFIED_TRUE)

    def test_missing_relation_query_semantics_remain_set_based(self):
        receipt = build_receipt()
        q = receipt["missing_relation"]["query_outcomes"]
        self.assertEqual(q["q_even"], IDENTIFIED_TRUE)
        self.assertEqual(q["q_gt_25"], CANNOT_IDENTIFY)
        self.assertEqual(q["q_le_40"], IDENTIFIED_TRUE)
        self.assertEqual(
            receipt["missing_relation"]["markers"], [MISSING_RELATION_FULL_DOMAIN]
        )

    def test_receipt_forbids_product_coverage_field(self):
        receipt = build_receipt()
        encoded = json.dumps(receipt, sort_keys=True)
        self.assertNotIn('"product_coverage_lower_bound"', encoded)
        self.assertNotIn('"independent_stage_errors": true', encoded.lower())

    def test_receipt_is_deterministic(self):
        self.assertEqual(canonical_receipt_bytes(), canonical_receipt_bytes())

    def test_receipt_expected_coverage(self):
        receipt = build_receipt()
        self.assertEqual(receipt["concrete_chain"]["coverage_lower_bound"], "187/200")

    def test_receipt_expected_exhaustive_case_count(self):
        receipt = build_receipt()
        self.assertEqual(receipt["exhaustive_uc1"]["cases"], 1024)
        self.assertEqual(receipt["exhaustive_uc1"]["failures"], 0)


if __name__ == "__main__":
    unittest.main()
