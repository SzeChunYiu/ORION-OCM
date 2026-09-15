from __future__ import annotations

from fractions import Fraction
import json
import unittest

from dependency_aware_composition_v1 import (
    CLAIM_CEILING,
    DagCampaign,
    NodeSpec,
    budget_controls,
    build_receipt,
    canonical_receipt_bytes,
    exhaustive_local_soundness_certificate,
    joint_root_xor_control,
    marginal_dependence_hostile,
    missing_relation_control,
    nonlinear_setvalued_control,
    shared_ancestor_hostile,
)

F = Fraction


class DependencyAwareCompositionV1Tests(unittest.TestCase):
    def test_shared_ancestor_hostile_exact_global(self):
        receipt = shared_ancestor_hostile()
        self.assertEqual(receipt["global_y"], [0])

    def test_shared_ancestor_hostile_local_dependency_loss(self):
        receipt = shared_ancestor_hostile()
        self.assertEqual(receipt["local_y"], [-2, 0, 2])
        self.assertTrue(receipt["strict"])

    def test_joint_root_xor_preserves_joint_globally(self):
        receipt = joint_root_xor_control()
        self.assertEqual(receipt["global_y"], [0])

    def test_joint_root_xor_local_marginalization_is_looser(self):
        receipt = joint_root_xor_control()
        self.assertEqual(receipt["local_y"], [0, 1])
        self.assertTrue(receipt["strict"])

    def test_exhaustive_certificate_has_1024_cases(self):
        cert = exhaustive_local_soundness_certificate()
        self.assertEqual(cert["cases"], 1024)

    def test_exhaustive_local_propagation_is_sound(self):
        cert = exhaustive_local_soundness_certificate()
        self.assertEqual(cert["failures"], 0)
        self.assertTrue(cert["all_sound"])

    def test_exhaustive_certificate_exercises_strict_loss(self):
        cert = exhaustive_local_soundness_certificate()
        self.assertGreater(cert["strict_overapproximation_cases"], 0)
        self.assertTrue(cert["strict_dependency_loss_exercised"])

    def test_marginal_root_product_hostile(self):
        row = marginal_dependence_hostile()["disjoint"]
        self.assertEqual(row["true_joint_coverage"], "1/2")
        self.assertEqual(row["independence_product"], "9/16")
        self.assertEqual(row["union_lower"], "1/2")
        self.assertTrue(row["product_unsound"])
        self.assertTrue(row["union_attained"])

    def test_marginal_root_overlap_control(self):
        row = marginal_dependence_hostile()["overlap"]
        self.assertEqual(row["true_joint_coverage"], "3/4")
        self.assertEqual(row["union_lower"], "1/2")
        self.assertTrue(row["union_conservative"])

    def test_nonlinear_setvalued_control(self):
        row = nonlinear_setvalued_control()
        self.assertEqual(row["global_s"], [0, 1])
        self.assertEqual(row["global_q"], [-1, 0, 1, 2])
        self.assertEqual(row["local_s"], [0, 1])
        self.assertEqual(row["local_q"], [-1, 0, 1, 2])
        self.assertEqual(row["coverage_lower_bound"], "19/20")

    def test_missing_relation_is_full_domain(self):
        row = missing_relation_control()
        self.assertEqual(row["missing_nodes"], ["m"])
        self.assertEqual(row["global_m"], ["a", "b", "c"])
        self.assertEqual(row["local_m"], ["a", "b", "c"])

    def test_missing_relation_uncertainty_propagates_downstream(self):
        row = missing_relation_control()
        self.assertEqual(row["global_y"], [0, 1])
        self.assertEqual(row["local_y"], [0, 1])
        self.assertEqual(row["coverage_lower_bound"], "19/20")

    def test_registered_empty_relation_is_not_missing(self):
        c = DagCampaign()
        c.register_node(NodeSpec("x", (0, 1)))
        c.register_node(NodeSpec("y", ("a", "b"), ("x",), (), F(0)))
        c.set_outputs(("y",))
        c.set_joint_root_contract(("x",), ((0,),), F(0))
        c.activate()
        r = c.execute()
        self.assertEqual(r.global_output, ())
        self.assertEqual(r.local_output, ())
        self.assertEqual(r.missing_nodes, ())

    def test_cycle_rejected(self):
        c = DagCampaign()
        c.register_node(NodeSpec("a", (0, 1), ("b",), (((0,), 0),), F(0)))
        c.register_node(NodeSpec("b", (0, 1), ("a",), (((0,), 0),), F(0)))
        c.set_outputs(("a",))
        c.set_joint_root_contract(("a",), ((0,),), F(0))
        with self.assertRaises(ValueError):
            c.activate()

    def test_unknown_parent_rejected(self):
        c = DagCampaign()
        c.register_node(NodeSpec("x", (0, 1)))
        c.register_node(NodeSpec("y", (0, 1), ("missing",), (((0,), 0),), F(0)))
        c.set_outputs(("y",))
        c.set_joint_root_contract(("x",), ((0,),), F(0))
        with self.assertRaises(ValueError):
            c.activate()

    def test_duplicate_node_name_rejected(self):
        c = DagCampaign()
        c.register_node(NodeSpec("x", (0, 1)))
        with self.assertRaises(ValueError):
            c.register_node(NodeSpec("x", (0, 1)))

    def test_duplicate_parent_name_rejected(self):
        with self.assertRaises(ValueError):
            NodeSpec("y", (0, 1), ("x", "x"), (((0, 0), 0),), F(0))

    def test_self_parent_rejected(self):
        with self.assertRaises(ValueError):
            NodeSpec("x", (0, 1), ("x",), (((0,), 0),), F(0))

    def test_wrong_relation_parent_arity_rejected(self):
        c = DagCampaign()
        c.register_node(NodeSpec("x", (0, 1)))
        c.register_node(NodeSpec("y", (0, 1), ("x",), (((0, 1), 0),), F(0)))
        c.set_outputs(("y",))
        c.set_joint_root_contract(("x",), ((0,),), F(0))
        with self.assertRaises(ValueError):
            c.activate()

    def test_relation_parent_endpoint_rejected(self):
        c = DagCampaign()
        c.register_node(NodeSpec("x", (0, 1)))
        c.register_node(NodeSpec("y", (0, 1), ("x",), (((2,), 0),), F(0)))
        c.set_outputs(("y",))
        c.set_joint_root_contract(("x",), ((0,),), F(0))
        with self.assertRaises(ValueError):
            c.activate()

    def test_relation_output_endpoint_rejected(self):
        c = DagCampaign()
        c.register_node(NodeSpec("x", (0, 1)))
        c.register_node(NodeSpec("y", (0, 1), ("x",), (((0,), 2),), F(0)))
        c.set_outputs(("y",))
        c.set_joint_root_contract(("x",), ((0,),), F(0))
        with self.assertRaises(ValueError):
            c.activate()

    def test_duplicate_relation_row_rejected(self):
        c = DagCampaign()
        c.register_node(NodeSpec("x", (0, 1)))
        c.register_node(NodeSpec("y", (0, 1), ("x",), (((0,), 0), ((0,), 0)), F(0)))
        c.set_outputs(("y",))
        c.set_joint_root_contract(("x",), ((0,),), F(0))
        with self.assertRaises(ValueError):
            c.activate()

    def test_non_fraction_budget_rejected(self):
        with self.assertRaises(ValueError):
            NodeSpec("x", (0, 1), (), None, 0.0)

    def test_out_of_range_budget_rejected(self):
        with self.assertRaises(ValueError):
            NodeSpec("x", (0, 1), (), None, F(2))

    def test_missing_relation_nonzero_beta_rejected(self):
        with self.assertRaises(ValueError):
            NodeSpec("y", (0, 1), ("x",), None, F(1, 10))

    def test_root_local_relation_rejected(self):
        with self.assertRaises(ValueError):
            NodeSpec("x", (0, 1), (), (((0,), 0),), F(0))

    def test_unknown_output_rejected(self):
        c = DagCampaign()
        c.register_node(NodeSpec("x", (0, 1)))
        c.set_outputs(("unknown",))
        c.set_joint_root_contract(("x",), ((0,),), F(0))
        with self.assertRaises(ValueError):
            c.activate()

    def test_wrong_root_tuple_arity_rejected(self):
        c = DagCampaign()
        c.register_node(NodeSpec("x", (0, 1)))
        c.set_outputs(("x",))
        c.set_joint_root_contract(("x",), ((0, 1),), F(0))
        with self.assertRaises(ValueError):
            c.activate()

    def test_root_value_outside_domain_rejected(self):
        c = DagCampaign()
        c.register_node(NodeSpec("x", (0, 1)))
        c.set_outputs(("x",))
        c.set_joint_root_contract(("x",), ((2,),), F(0))
        with self.assertRaises(ValueError):
            c.activate()

    def test_duplicate_root_tuple_rejected(self):
        c = DagCampaign()
        c.register_node(NodeSpec("x", (0, 1)))
        c.set_outputs(("x",))
        c.set_joint_root_contract(("x",), ((0,), (0,)), F(0))
        with self.assertRaises(ValueError):
            c.activate()

    def test_root_order_must_match_graph_root_order(self):
        c = DagCampaign()
        c.register_node(NodeSpec("r1", (0, 1)))
        c.register_node(NodeSpec("r2", (0, 1)))
        c.set_outputs(("r1",))
        c.set_joint_root_contract(("r2", "r1"), ((0, 0),), F(0))
        with self.assertRaises(ValueError):
            c.activate()

    def test_post_activation_node_mutation_rejected(self):
        c = DagCampaign()
        c.register_node(NodeSpec("x", (0, 1)))
        c.set_outputs(("x",))
        c.set_joint_root_contract(("x",), ((0,),), F(0))
        c.activate()
        with self.assertRaises(RuntimeError):
            c.register_node(NodeSpec("y", (0, 1)))

    def test_post_activation_output_mutation_rejected(self):
        c = DagCampaign()
        c.register_node(NodeSpec("x", (0, 1)))
        c.set_outputs(("x",))
        c.set_joint_root_contract(("x",), ((0,),), F(0))
        c.activate()
        with self.assertRaises(RuntimeError):
            c.set_outputs(("x",))

    def test_post_activation_root_mutation_rejected(self):
        c = DagCampaign()
        c.register_node(NodeSpec("x", (0, 1)))
        c.set_outputs(("x",))
        c.set_joint_root_contract(("x",), ((0,),), F(0))
        c.activate()
        with self.assertRaises(RuntimeError):
            c.set_joint_root_contract(("x",), ((1,),), F(0))

    def test_marginal_root_contract_uses_union_budget(self):
        c = DagCampaign()
        c.register_node(NodeSpec("r1", (0, 1)))
        c.register_node(NodeSpec("r2", (0, 1)))
        relation = tuple(((a, b), a ^ b) for a in (0, 1) for b in (0, 1))
        c.register_node(NodeSpec("y", (0, 1), ("r1", "r2"), relation, F(1, 100)))
        c.set_outputs(("y",))
        c.set_marginal_root_contract(
            ("r1", "r2"), ((0, 1), (0, 1)), (F(1, 40), F(1, 40))
        )
        c.activate()
        self.assertEqual(c.coverage_lower_bound(), F(47, 50))

    def test_marginal_root_budget_caps_at_one(self):
        c = DagCampaign()
        c.register_node(NodeSpec("r1", (0, 1)))
        c.register_node(NodeSpec("r2", (0, 1)))
        c.set_outputs(("r1",))
        c.set_marginal_root_contract(
            ("r1", "r2"), ((0, 1), (0, 1)), (F(3, 4), F(3, 4))
        )
        c.activate()
        self.assertEqual(c.coverage_lower_bound(), F(0))

    def test_joint_budget_control_exact_373_over_400(self):
        self.assertEqual(budget_controls()["joint_source"]["lower"], "373/400")

    def test_marginal_budget_control_exact_373_over_400(self):
        self.assertEqual(budget_controls()["marginal_source"]["lower"], "373/400")

    def test_registered_beta_is_charged(self):
        c = DagCampaign()
        c.register_node(NodeSpec("x", (0, 1)))
        c.register_node(NodeSpec("y", (0, 1), ("x",), (((0,), 0), ((1,), 1)), F(1, 10)))
        c.set_outputs(("y",))
        c.set_joint_root_contract(("x",), ((0,), (1,)), F(1, 20))
        c.activate()
        self.assertEqual(c.coverage_lower_bound(), F(17, 20))

    def test_missing_relation_charges_no_beta(self):
        c = DagCampaign()
        c.register_node(NodeSpec("x", (0, 1)))
        c.register_node(NodeSpec("y", (0, 1), ("x",), None, F(0)))
        c.set_outputs(("y",))
        c.set_joint_root_contract(("x",), ((0,),), F(1, 20))
        c.activate()
        self.assertEqual(c.coverage_lower_bound(), F(19, 20))

    def test_empty_root_set_yields_empty_outputs(self):
        c = DagCampaign()
        c.register_node(NodeSpec("x", (0, 1)))
        c.register_node(NodeSpec("y", (0, 1), ("x",), None, F(0)))
        c.set_outputs(("y",))
        c.set_joint_root_contract(("x",), (), F(1))
        c.activate()
        r = c.execute()
        self.assertEqual(r.global_output, ())
        self.assertEqual(r.local_output, ())

    def test_receipt_claim_ceiling(self):
        self.assertEqual(build_receipt()["claim_ceiling"], CLAIM_CEILING)

    def test_receipt_contains_no_product_guarantee_field(self):
        encoded = json.dumps(build_receipt(), sort_keys=True)
        self.assertNotIn('"product_coverage_lower_bound"', encoded)
        self.assertNotIn('"independence_proved": true', encoded.lower())

    def test_receipt_is_deterministic(self):
        self.assertEqual(canonical_receipt_bytes(), canonical_receipt_bytes())


if __name__ == "__main__":
    unittest.main()
