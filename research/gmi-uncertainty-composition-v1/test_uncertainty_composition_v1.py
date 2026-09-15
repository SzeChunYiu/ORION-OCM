from __future__ import annotations

import sys
import unittest
from fractions import Fraction as F
from pathlib import Path

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import uncertainty_composition_v1 as uc


class CompositionTests(unittest.TestCase):
    def test_shared_ancestor_global_exact(self):
        c=uc._build_shared_ancestor()
        self.assertEqual(c.global_set("y"),frozenset((F(0),)))

    def test_shared_ancestor_local_is_strict_overapprox(self):
        c=uc._build_shared_ancestor()
        self.assertEqual(c.local_sets()["y"],frozenset((F(-2),F(0),F(2))))
        self.assertLess(c.global_set("y"),c.local_sets()["y"])

    def test_shared_ancestor_global_subset_local_all_nodes(self):
        c=uc._build_shared_ancestor(); local=c.local_sets()
        for n in c.specs:
            self.assertTrue(c.global_set(n).issubset(local[n]))

    def test_nonlinear_expected_output(self):
        c=uc._build_nonlinear(); expected=frozenset(F(x) for x in (0,2,3,5))
        self.assertEqual(c.global_set("out"),expected)
        self.assertEqual(c.local_sets()["out"],expected)

    def test_setvalued_expected_output(self):
        c=uc._build_setvalued()
        self.assertEqual(c.global_set("y"),frozenset(F(x) for x in (0,2,4)))
        self.assertTrue(c.global_set("y").issubset(c.local_sets()["y"]))

    def test_unknown_relation_full_domain(self):
        c=uc._build_unknown()
        self.assertEqual(c.global_set("q"),frozenset(F(x) for x in (0,1,2)))
        self.assertEqual(c.global_set("y"),frozenset(F(x) for x in (1,2,3)))
        self.assertEqual(c.output_terminal("y"),"CANNOT_IDENTIFY_UNKNOWN_RELATION")

    def test_unknown_can_still_collapse_to_identified(self):
        c=uc.CompositionCampaign(); c.register_node("x",(F(0),))
        c.register_node("q",(F(0),F(1),F(2)),("x",),unknown_relation=True)
        c.register_node("y",(F(7),),("q",),tuple(((q,),F(7)) for q in (F(0),F(1),F(2))))
        c.set_outputs(("y",)); c.activate(((F(0),),),F(0))
        self.assertEqual(c.global_set("y"),frozenset((F(7),)))
        self.assertEqual(c.output_terminal("y"),"IDENTIFIED")

    def test_failure_budget(self):
        self.assertEqual(uc._build_shared_ancestor().failure_budget(),(F(1,20),F(19,20)))

    def test_operator_failure_budget_adds(self):
        c=uc.CompositionCampaign(); c.register_node("x",(F(0),))
        c.register_node("a",(F(0),),("x",),(((F(0),),F(0)),),beta=F(1,100))
        c.register_node("b",(F(0),),("a",),(((F(0),),F(0)),),beta=F(1,200))
        c.set_outputs(("b",)); c.activate(((F(0),),),F(1,20))
        self.assertEqual(c.failure_budget(),(F(13,200),F(187,200)))

    def test_marginal_joint_union_bound(self):
        domains={"r1":(F(0),F(1)),"r2":(F(0),F(1))}
        sets={"r1":(F(0),F(1)),"r2":(F(0),)}
        alphas={"r1":F(1,20),"r2":F(1,20)}
        joint,total,cover=uc.joint_from_marginals(("r1","r2"),domains,sets,alphas)
        self.assertEqual(joint,frozenset(((F(0),F(0)),(F(1),F(0)))))
        self.assertEqual((total,cover),(F(1,10),F(9,10)))

    def test_marginal_dependence_counterexample(self):
        r=uc._marginal_dependence_control()
        self.assertEqual(r["actual_joint"],"9/10")
        self.assertEqual(r["union_bound_lower"],"9/10")
        self.assertEqual(r["independence_product"],"361/400")
        self.assertNotEqual(r["actual_joint"],r["independence_product"])
        self.assertFalse(r["independence_used"]); self.assertTrue(r["bound_tight"])

    def test_operator_dependence_counterexample(self):
        r=uc._operator_dependence_control()
        self.assertEqual(r["actual_joint_good"],"187/200")
        self.assertEqual(r["union_bound_lower"],"187/200")
        self.assertEqual(r["failure_sum"],"13/200")
        self.assertFalse(r["success_events_independent"])
        self.assertNotEqual(r["actual_joint_good"],r["independence_product"])
        self.assertTrue(r["bound_tight"])

    def test_affine_parent_regression(self):
        lo,hi,corners=uc.affine_interval_hull(F(1,4),F(3,4),F(-2),F(3),F(-1,10),F(1,10))
        self.assertEqual((lo,hi),(F(7,5),F(13,5)))
        self.assertEqual((lo,hi),(min(corners),max(corners)))

    def test_cycle_rejected(self):
        c=uc.CompositionCampaign()
        c.register_node("a",(F(0),),("b",),(((F(0),),F(0)),))
        c.register_node("b",(F(0),),("a",),(((F(0),),F(0)),))
        c.set_outputs(("b",))
        with self.assertRaises(ValueError): c.activate(((F(0),),),F(0))

    def test_self_cycle_rejected_early(self):
        c=uc.CompositionCampaign()
        with self.assertRaises(ValueError): c.register_node("a",(F(0),),("a",),(((F(0),),F(0)),))

    def test_unknown_parent_rejected(self):
        c=uc.CompositionCampaign(); c.register_node("a",(F(0),),("missing",),(((F(0),),F(0)),)); c.set_outputs(("a",))
        with self.assertRaises(ValueError): c.activate(((F(0),),),F(0))

    def test_duplicate_node_rejected(self):
        c=uc.CompositionCampaign(); c.register_node("x",(F(0),))
        with self.assertRaises(ValueError): c.register_node("x",(F(0),))

    def test_empty_domain_rejected(self):
        with self.assertRaises(ValueError): uc.CompositionCampaign().register_node("x",())

    def test_unsorted_domain_rejected(self):
        with self.assertRaises(ValueError): uc.CompositionCampaign().register_node("x",(F(1),F(0)))

    def test_duplicate_domain_rejected(self):
        with self.assertRaises(ValueError): uc.CompositionCampaign().register_node("x",(F(0),F(0)))

    def test_non_fraction_domain_rejected(self):
        with self.assertRaises(TypeError): uc.CompositionCampaign().register_node("x",(0,))

    def test_non_fraction_budget_rejected(self):
        with self.assertRaises(TypeError): uc.CompositionCampaign().register_node("x",(F(0),),beta=0)

    def test_out_of_range_budget_rejected(self):
        for beta in (F(-1,10),F(11,10)):
            with self.assertRaises(ValueError): uc.CompositionCampaign().register_node("x",(F(0),),beta=beta)

    def test_root_beta_rejected(self):
        with self.assertRaises(ValueError): uc.CompositionCampaign().register_node("x",(F(0),),beta=F(1,100))

    def test_unknown_relation_beta_rejected(self):
        c=uc.CompositionCampaign(); c.register_node("x",(F(0),))
        with self.assertRaises(ValueError): c.register_node("q",(F(0),),("x",),unknown_relation=True,beta=F(1,100))

    def test_explicit_relation_totality_required(self):
        c=uc.CompositionCampaign(); c.register_node("x",(F(0),F(1)))
        c.register_node("y",(F(0),),("x",),(((F(0),),F(0)),)); c.set_outputs(("y",))
        with self.assertRaises(ValueError): c.activate(((F(0),),),F(0))

    def test_relation_parent_endpoint_domain_checked(self):
        c=uc.CompositionCampaign(); c.register_node("x",(F(0),))
        c.register_node("y",(F(0),),("x",),(((F(1),),F(0)),)); c.set_outputs(("y",))
        with self.assertRaises(ValueError): c.activate(((F(0),),),F(0))

    def test_relation_output_domain_checked(self):
        c=uc.CompositionCampaign(); c.register_node("x",(F(0),))
        c.register_node("y",(F(0),),("x",),(((F(0),),F(1)),)); c.set_outputs(("y",))
        with self.assertRaises(ValueError): c.activate(((F(0),),),F(0))

    def test_duplicate_relation_entry_rejected(self):
        c=uc.CompositionCampaign(); c.register_node("x",(F(0),))
        with self.assertRaises(ValueError):
            c.register_node("y",(F(0),),("x",),(((F(0),),F(0)),((F(0),),F(0))))

    def test_relation_arity_rejected(self):
        c=uc.CompositionCampaign(); c.register_node("x",(F(0),))
        with self.assertRaises(ValueError): c.register_node("y",(F(0),),("x",),(((F(0),F(0)),F(0)),))

    def test_root_confidence_nonempty(self):
        c=uc.CompositionCampaign(); c.register_node("x",(F(0),)); c.set_outputs(("x",))
        with self.assertRaises(ValueError): c.activate((),F(0))

    def test_root_confidence_out_of_domain(self):
        c=uc.CompositionCampaign(); c.register_node("x",(F(0),)); c.set_outputs(("x",))
        with self.assertRaises(ValueError): c.activate(((F(1),),),F(0))

    def test_root_confidence_arity(self):
        c=uc.CompositionCampaign(); c.register_node("x",(F(0),)); c.set_outputs(("x",))
        with self.assertRaises(ValueError): c.activate(((F(0),F(0)),),F(0))

    def test_post_activation_node_mutation_rejected(self):
        c=uc.CompositionCampaign(); c.register_node("x",(F(0),)); c.set_outputs(("x",)); c.activate(((F(0),),),F(0))
        with self.assertRaises(RuntimeError): c.register_node("z",(F(0),))

    def test_post_activation_output_mutation_rejected(self):
        c=uc.CompositionCampaign(); c.register_node("x",(F(0),)); c.set_outputs(("x",)); c.activate(((F(0),),),F(0))
        with self.assertRaises(RuntimeError): c.set_outputs(("x",))

    def test_double_activation_rejected(self):
        c=uc.CompositionCampaign(); c.register_node("x",(F(0),)); c.set_outputs(("x",)); c.activate(((F(0),),),F(0))
        with self.assertRaises(RuntimeError): c.activate(((F(0),),),F(0))

    def test_propagation_before_activation_rejected(self):
        c=uc.CompositionCampaign(); c.register_node("x",(F(0),)); c.set_outputs(("x",))
        with self.assertRaises(RuntimeError): c.global_assignments()

    def test_missing_outputs_rejected(self):
        c=uc.CompositionCampaign(); c.register_node("x",(F(0),))
        with self.assertRaises(ValueError): c.activate(((F(0),),),F(0))

    def test_unknown_output_rejected(self):
        c=uc.CompositionCampaign(); c.register_node("x",(F(0),)); c.set_outputs(("missing",))
        with self.assertRaises(ValueError): c.activate(((F(0),),),F(0))

    def test_topological_order_deterministic(self):
        self.assertEqual(uc._build_shared_ancestor().topological_order(),("x","a","b","y"))

    def test_receipt_deterministic(self):
        self.assertEqual(uc.build_receipt(),uc.build_receipt())

    def test_receipt_matches_expected_core(self):
        r=uc.build_receipt()
        self.assertEqual(r["shared_ancestor"]["global_y"],["0"])
        self.assertEqual(r["shared_ancestor"]["local_y"],["-2","0","2"])
        self.assertEqual(r["nonlinear"]["global_out"],["0","2","3","5"])
        self.assertEqual(r["set_valued"]["global_y"],["0","2","4"])
        self.assertEqual(r["unknown_relation"]["global_y"],["1","2","3"])
        self.assertEqual(r["affine_parent_regression"]["hull"],["7/5","13/5"])


if __name__=="__main__":
    unittest.main(verbosity=2)
