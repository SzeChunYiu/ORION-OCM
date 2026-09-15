#!/usr/bin/env python3
from __future__ import annotations

from fractions import Fraction as F
import importlib.util
import sys
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("global_uncertainty_v1", HERE / "global_uncertainty_v1.py")
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("cannot load global_uncertainty_v1.py")
M = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = M
SPEC.loader.exec_module(M)


class TypedObjectTests(unittest.TestCase):
    def test_five_kinds_are_distinct(self):
        self.assertEqual(len(set(M.UncertaintyKind)), 5)

    def test_feasible_full_domain_is_unknown(self):
        obj = M.FeasibleSet((0, 1), (0, 1), 0, ("p",))
        self.assertEqual(obj.knowledge, M.SetKnowledge.UNKNOWN)

    def test_feasible_empty_is_inconsistent(self):
        obj = M.FeasibleSet((0, 1), (), 0, ("p",))
        self.assertEqual(obj.knowledge, M.SetKnowledge.INCONSISTENT_REGISTERED_ASSUMPTIONS)

    def test_confidence_is_exact_fraction(self):
        with self.assertRaises(ValueError):
            M.ConfidenceSet((0, 1), (0,), 0.05, "theta", 0, ("p",))

    def test_confidence_rejects_bad_budget(self):
        with self.assertRaises(ValueError):
            M.ConfidenceSet((0, 1), (0,), F(5, 4), "theta", 0, ("p",))

    def test_predictive_law_normalizes(self):
        law = M.PredictiveLaw((0, 1), (F(1, 3), F(2, 3)), 0, ("p",))
        self.assertEqual(sum(law.probabilities, F(0)), 1)

    def test_predictive_law_rejects_bad_mass(self):
        with self.assertRaises(ValueError):
            M.PredictiveLaw((0, 1), (F(1, 3), F(1, 3)), 0, ("p",))

    def test_marginal_only_decomposition_fails_closed(self):
        law = M.PredictiveLaw((F(0), F(1)), (F(1, 2), F(1, 2)), 0, ("p",))
        with self.assertRaisesRegex(M.CannotCheckError, "LATENT_SEMANTICS"):
            law.epistemic_aleatoric_decomposition()

    def test_selective_prediction_validates_certificate(self):
        obj = M.SelectivePrediction(("yes",), F(1, 20), F(3, 4), 0, ("audit",))
        self.assertEqual(obj.kind, M.UncertaintyKind.SELECTIVE_PREDICTION)


class QuerySemanticsTests(unittest.TestCase):
    def setUp(self):
        self.unknown = M.FeasibleSet((0, 1), (0, 1), 0, ("q",))

    def test_unknown_identity_query_cannot_identify(self):
        result = M.query_identified_set(self.unknown, {0: 0, 1: 1})
        self.assertEqual(result.disposition, M.QueryDisposition.CANNOT_IDENTIFY)
        self.assertEqual(result.candidates, (0, 1))

    def test_unknown_constant_query_identifies(self):
        result = M.query_identified_set(self.unknown, {0: 7, 1: 7})
        self.assertEqual(result.disposition, M.QueryDisposition.IDENTIFIED)
        self.assertEqual(result.candidates, (7,))

    def test_empty_set_is_inconsistency(self):
        empty = M.FeasibleSet((0, 1), (), 0, ("q",))
        result = M.query_identified_set(empty, {0: 0, 1: 1})
        self.assertEqual(result.disposition, M.QueryDisposition.INCONSISTENT_REGISTERED_ASSUMPTIONS)

    def test_missing_query_is_cannot_check(self):
        result = M.query_identified_set(self.unknown, None)
        self.assertEqual(result.disposition, M.QueryDisposition.CANNOT_CHECK)

    def test_query_domain_mismatch_is_cannot_check(self):
        result = M.query_identified_set(self.unknown, {0: 0})
        self.assertEqual(result.disposition, M.QueryDisposition.CANNOT_CHECK)

    def test_predictive_law_not_query_set(self):
        law = M.PredictiveLaw((0, 1), (F(1, 2), F(1, 2)), 0, ("p",))
        result = M.query_identified_set(law, {0: 0, 1: 1})
        self.assertEqual(result.disposition, M.QueryDisposition.CANNOT_CHECK)

    def test_confidence_query_preserves_failure_budget(self):
        obj = M.ConfidenceSet((0, 1), (0, 1), F(1, 20), "theta", 0, ("q",))
        result = M.query_identified_set(obj, {0: 7, 1: 7})
        self.assertEqual(result.disposition, M.QueryDisposition.IDENTIFIED)
        self.assertEqual(result.failure_budget, F(1, 20))
        self.assertEqual(result.coverage_lower_bound, F(19, 20))

    def test_query_census_exhaustive(self):
        census = M.query_identification_census()
        self.assertEqual(census["cases"], 64)
        self.assertEqual(census["failures"], 0)
        self.assertGreater(census["identified_cases"], 0)
        self.assertGreater(census["cannot_identify_cases"], 0)
        self.assertGreater(census["empty_cases"], 0)


class RelationTests(unittest.TestCase):
    def test_relational_image(self):
        rel = M.FiniteRelation((0, 1), ("a", "b"), ((0, "a"), (1, "b")), ("r",))
        self.assertEqual(M.relational_image((0,), rel), ("a",))

    def test_empty_relation_is_registered(self):
        rel = M.FiniteRelation((0, 1), ("a", "b"), (), ("empty",))
        self.assertEqual(M.relational_image((0, 1), rel), ())

    def test_relation_rejects_out_of_domain_pair(self):
        with self.assertRaises(ValueError):
            M.FiniteRelation((0,), (1,), ((0, 2),), ("bad",))

    def test_exact_composition_identity_1024_cases(self):
        census = M.relation_composition_census()
        self.assertEqual(census, {"cases": 1024, "failures": 0})

    def test_boole_union_exhaustive_4096_cases(self):
        census = M.boole_union_census()
        self.assertEqual(census["cases"], 4096)
        self.assertEqual(census["failures"], 0)
        self.assertGreater(census["equality_cases"], 0)

    def test_union_bound_exact_budget(self):
        self.assertEqual(M.coverage_lower_bound(F(1, 20), (F(1, 100), F(1, 200))), F(187, 200))

    def test_union_bound_clips_at_zero(self):
        self.assertEqual(M.coverage_lower_bound(F(3, 4), (F(1, 2),)), F(0))

    def test_product_requires_independence_registration(self):
        with self.assertRaisesRegex(M.CannotCheckError, "INDEPENDENCE"):
            M.product_good_probability((F(1, 4), F(1, 4)))

    def test_product_when_independence_is_registered(self):
        self.assertEqual(
            M.product_good_probability((F(1, 4), F(1, 4)), independence_registered=True),
            F(9, 16),
        )

    def test_disjoint_failure_hostile(self):
        row = M.anti_product_witness()
        self.assertEqual(row["true_joint_good"], F(1, 2))
        self.assertEqual(row["independence_product"], F(9, 16))
        self.assertGreater(row["independence_product"], row["true_joint_good"])
        self.assertEqual(row["union_bound_lower"], row["true_joint_good"])


class DependenceTests(unittest.TestCase):
    def test_shared_ancestor_global_exact(self):
        row = M.shared_ancestor_witness()
        self.assertEqual(row["global_y"], (0,))
        self.assertEqual(row["local_y"], (-2, 0, 2))
        self.assertTrue(row["strict_overapproximation"])

    def test_dependent_root_global_exact(self):
        row = M.dependent_root_witness()
        self.assertEqual(row["global_y"], (0,))
        self.assertEqual(row["local_y"], (0, 1))
        self.assertTrue(row["strict_overapproximation"])

    def test_dag_relation_parent_outside_registered_domain_rejected(self):
        spec = M.DAGNodeRelation("y", ("x",), (0, 1), (((2,), 0),))
        with self.assertRaisesRegex(ValueError, "parent tuple outside"):
            M.global_feasible_assignments(("x",), {"x": (0, 1)}, ((0,),), (spec,))

    def test_bad_topological_order_rejected(self):
        spec = M.DAGNodeRelation("y", ("missing",), (0, 1), (((0,), 0),))
        with self.assertRaises(ValueError):
            M.global_feasible_assignments(("x",), {"x": (0, 1)}, ((0,),), (spec,))


class MissingEmptyVersionTests(unittest.TestCase):
    def setUp(self):
        self.source = M.ConfidenceSet((0, 1), (0,), F(1, 20), "theta", 2, ("src",), raw_evidence_count=99)
        self.target = ("u", "v")

    def test_missing_relation_returns_full_domain_feasible_unknown(self):
        out = M.propagate_confidence(
            self.source, None, F(0), target_domain=self.target, target_version=3, provenance=("m",)
        )
        self.assertIsInstance(out, M.FeasibleSet)
        self.assertEqual(out.values, self.target)
        self.assertEqual(out.knowledge, M.SetKnowledge.UNKNOWN)

    def test_empty_relation_returns_inconsistency(self):
        rel = M.FiniteRelation((0, 1), self.target, (), ("empty",))
        out = M.propagate_confidence(
            self.source, rel, F(0), target_domain=self.target, target_version=3, provenance=("e",)
        )
        self.assertIsInstance(out, M.FeasibleSet)
        self.assertEqual(out.values, ())
        self.assertEqual(out.knowledge, M.SetKnowledge.INCONSISTENT_REGISTERED_ASSUMPTIONS)

    def test_missing_target_domain_cannot_check(self):
        out = M.propagate_confidence(
            self.source, None, F(0), target_domain=None, target_version=3, provenance=("n",)
        )
        self.assertIsInstance(out, M.CannotCheck)
        self.assertEqual(out.disposition, M.QueryDisposition.CANNOT_CHECK)

    def test_version_transport_does_not_migrate_raw_evidence(self):
        rel = M.FiniteRelation((0, 1), self.target, ((0, "u"), (1, "v")), ("r",))
        out = M.transport_developmental_confidence(
            self.source, rel, F(1, 100), target_domain=self.target, target_version=3, provenance=("t",)
        )
        self.assertIsInstance(out, M.ConfidenceSet)
        self.assertEqual(out.raw_evidence_count, 0)
        self.assertEqual(out.alpha, F(3, 50))
        self.assertEqual(out.values, ("u",))

    def test_missing_relation_does_not_launder_upstream_inconsistency(self):
        bad_source = M.ConfidenceSet((0, 1), (), F(1), "theta", 2, ("src",), raw_evidence_count=0)
        out = M.propagate_confidence(
            bad_source, None, F(0), target_domain=self.target, target_version=3, provenance=("m",)
        )
        self.assertIsInstance(out, M.FeasibleSet)
        self.assertEqual(out.knowledge, M.SetKnowledge.INCONSISTENT_REGISTERED_ASSUMPTIONS)
        self.assertEqual(out.values, ())

    def test_developmental_transport_requires_adjacent_version(self):
        rel = M.FiniteRelation((0, 1), self.target, ((0, "u"), (1, "v")), ("r",))
        out = M.transport_developmental_confidence(
            self.source, rel, F(0), target_domain=self.target, target_version=4, provenance=("bad-version",)
        )
        self.assertIsInstance(out, M.CannotCheck)
        self.assertEqual(out.reason, "DEVELOPMENTAL_TRANSPORT_REQUIRES_ADJACENT_VERSION")

    def test_relation_domain_mismatch_cannot_check(self):
        rel = M.FiniteRelation((2, 3), self.target, ((2, "u"),), ("r",))
        out = M.propagate_confidence(
            self.source, rel, F(0), target_domain=self.target, target_version=3, provenance=("t",)
        )
        self.assertIsInstance(out, M.CannotCheck)
        self.assertEqual(out.disposition, M.QueryDisposition.CANNOT_CHECK)


class LatentModelTests(unittest.TestCase):
    def test_same_marginal_opposite_decomposition(self):
        row = M.latent_nonidentifiability_witness()
        self.assertTrue(row["same_marginal"])
        self.assertEqual(row["marginal"], (F(1, 2), F(1, 2)))
        self.assertTrue(row["opposite_components"])
        self.assertEqual(row["pure_epistemic"]["aleatoric"], 0)
        self.assertEqual(row["pure_epistemic"]["epistemic_mean"], F(1, 4))
        self.assertEqual(row["pure_aleatoric"]["aleatoric"], F(1, 4))
        self.assertEqual(row["pure_aleatoric"]["epistemic_mean"], 0)

    def test_total_variance_identity(self):
        row = M.latent_nonidentifiability_witness()
        for key in ("pure_epistemic", "pure_aleatoric"):
            d = row[key]
            self.assertEqual(d["total"], d["aleatoric"] + d["epistemic_mean"])
            self.assertEqual(d["total"], F(1, 4))

    def test_latent_prior_must_normalize(self):
        with self.assertRaises(ValueError):
            M.LatentPredictiveModel(
                ("a", "b"), (F(1, 3), F(1, 3)), (F(0), F(1)),
                ((F(1), F(0)), (F(0), F(1))), 0, ("bad",),
            )


class ReceiptTests(unittest.TestCase):
    def test_receipt_terminal_green(self):
        receipt = M.build_receipt()
        self.assertEqual(receipt["terminal"], "GMI_833_GLOBAL_UNCERTAINTY_V1_ALL_GREEN")
        self.assertEqual(receipt["claim_ceiling"], M.CLAIM_CEILING)

    def test_receipt_pins_parent_ownership(self):
        receipt = M.build_receipt()
        self.assertEqual(receipt["parent_ownership"]["chain_composition"], "#757/#761")
        self.assertEqual(receipt["parent_ownership"]["dag_composition"], "#759/#765")
        self.assertEqual(receipt["parent_ownership"]["epistemic_aleatoric"], "#750/#751")

    def test_all_forbidden_promotions_stay_forbidden(self):
        receipt = M.build_receipt()
        self.assertIn("COMPLETE_GMI", receipt["forbidden_promotions"])
        self.assertIn("UNIVERSAL_UNCERTAINTY_CALIBRATION", receipt["forbidden_promotions"])


if __name__ == "__main__":
    unittest.main()
