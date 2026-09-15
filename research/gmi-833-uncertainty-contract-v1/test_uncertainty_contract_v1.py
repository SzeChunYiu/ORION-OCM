#!/usr/bin/env python3
from __future__ import annotations

from fractions import Fraction
import importlib.util
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("uncertainty_contract_v1", HERE / "uncertainty_contract_v1.py")
mod = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name] = mod
SPEC.loader.exec_module(mod)


class GlobalUncertaintyContractV1Tests(unittest.TestCase):
    def parent_audit(self):
        return mod.audit_parent_files(mod.repo_root())

    def receipt(self):
        return mod.build_receipt(self.parent_audit())

    def test_parent_evidence_exactly_pinned(self):
        audit = self.parent_audit()
        self.assertTrue(audit["all_ok"])
        self.assertEqual(len(audit["rows"]), 4)
        self.assertTrue(all(row["blob_ok"] for row in audit["rows"]))
        self.assertTrue(all(row["claim_ceiling_ok"] for row in audit["rows"]))
        self.assertTrue(all(row["semantic_ok"] for row in audit["rows"]))

    def test_parent_pin_mutation_fails_closed(self):
        root = mod.repo_root()
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            for pin in mod.PARENT_PINS:
                src = root / pin["path"]
                dst = tmp / pin["path"]
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(src, dst)
            victim = tmp / mod.PARENT_PINS[0]["path"]
            victim.write_bytes(victim.read_bytes() + b"\n")
            audit = mod.audit_parent_files(tmp)
            self.assertFalse(audit["all_ok"])
            self.assertFalse(audit["rows"][0]["blob_ok"])
            self.assertEqual(mod.build_receipt(audit)["verdict"], "RED")

    def test_receipt_green_and_byte_reproducible(self):
        receipt = self.receipt()
        expected = json.loads((HERE / "RESULT_V1.json").read_text())
        self.assertEqual(receipt["verdict"], "GREEN")
        self.assertTrue(all(receipt["checks"].values()))
        self.assertEqual(receipt, expected)
        self.assertEqual(mod.canonical_json(receipt), (HERE / "RESULT_V1.json").read_text())

    def test_feasible_set_is_not_confidence_set(self):
        feasible = mod.FeasibleSet(domain={0, 1}, candidates={0, 1}, version=0, provenance="F")
        confidence = mod.ConfidenceSet(domain={0, 1}, candidates={0, 1}, alpha=0, target="theta", version=0, provenance="C")
        self.assertIsInstance(feasible, mod.FeasibleSet)
        self.assertNotIsInstance(feasible, mod.ConfidenceSet)
        self.assertFalse(hasattr(feasible, "alpha"))
        self.assertEqual(confidence.coverage_lower_bound, Fraction(1))

    def test_set_objects_are_immutable_and_domain_checked(self):
        domain = {0, 1}
        candidates = {0}
        obj = mod.FeasibleSet(domain=domain, candidates=candidates, version=0, provenance="F")
        domain.add(2)
        candidates.add(1)
        self.assertEqual(obj.domain, frozenset({0, 1}))
        self.assertEqual(obj.candidates, frozenset({0}))
        with self.assertRaisesRegex(ValueError, "subset"):
            mod.FeasibleSet(domain={0}, candidates={0, 1}, version=0, provenance="bad")
        with self.assertRaisesRegex(ValueError, "nonempty"):
            mod.FeasibleSet(domain=set(), candidates=set(), version=0, provenance="bad")

    def test_confidence_budget_validation(self):
        with self.assertRaisesRegex(ValueError, "alpha"):
            mod.ConfidenceSet(domain={0}, candidates={0}, alpha=Fraction(6, 5), target="x", version=0, provenance="bad")
        with self.assertRaisesRegex(ValueError, "evidence count"):
            mod.ConfidenceSet(domain={0}, candidates={0}, alpha=0, target="x", version=0, provenance="bad", raw_evidence_count=-1)

    def test_predictive_law_requires_normalized_unique_outcomes(self):
        good = mod.PredictiveLaw(probabilities=((1, Fraction(1, 2)), (-1, Fraction(1, 2))), version=0, provenance="P")
        self.assertEqual(good.probabilities, ((-1, Fraction(1, 2)), (1, Fraction(1, 2))))
        with self.assertRaisesRegex(ValueError, "normalized"):
            mod.PredictiveLaw(probabilities=((0, Fraction(1, 4)),), version=0, provenance="bad")
        with self.assertRaisesRegex(ValueError, "unique"):
            mod.PredictiveLaw(probabilities=((0, Fraction(1, 2)), (0, Fraction(1, 2))), version=0, provenance="bad")

    def test_latent_model_duplicate_ids_and_outcomes_fail_closed(self):
        with self.assertRaisesRegex(ValueError, "weights must be unique"):
            mod.LatentPredictiveModel(
                weights=(("x", Fraction(1, 2)), ("x", Fraction(1, 2))),
                kernels=(("x", ((0, 1),)),),
                version=0,
                provenance="bad",
            )
        with self.assertRaisesRegex(ValueError, "kernel identifiers must be unique"):
            mod.LatentPredictiveModel(
                weights=(("x", 1),),
                kernels=(("x", ((0, 1),)), ("x", ((0, 1),))),
                version=0,
                provenance="bad",
            )
        with self.assertRaisesRegex(ValueError, "outcomes must be unique"):
            mod.LatentPredictiveModel(
                weights=(("x", 1),),
                kernels=(("x", ((0, Fraction(1, 2)), (0, Fraction(1, 2)))),),
                version=0,
                provenance="bad",
            )

    def test_chain_composition_budget_and_version_are_exact(self):
        source, result, terminals = mod.source_chain_witness()
        self.assertEqual(terminals, ("TRANSPORTED", "TRANSPORTED"))
        self.assertEqual(result.terminal, "TRANSPORTED_CHAIN")
        self.assertEqual(result.confidence.alpha, Fraction(13, 200))
        self.assertEqual(result.confidence.coverage_lower_bound, Fraction(187, 200))
        self.assertEqual(result.confidence.candidates, frozenset({10, 20}))
        self.assertEqual(source.raw_evidence_count, 2048)
        self.assertEqual(result.confidence.raw_evidence_count, 0)
        self.assertEqual(result.confidence.version, 2)

    def test_relation_outside_registered_domain_is_rejected(self):
        source = mod.ConfidenceSet(domain={0, 1}, candidates={0}, alpha=0, target="x", version=0, provenance="s")
        with self.assertRaisesRegex(ValueError, "leaves declared"):
            mod.transport_confidence(source, {"a"}, {(2, "a")}, 0, 1, "bad")
        with self.assertRaisesRegex(ValueError, "beta"):
            mod.transport_confidence(source, {"a"}, {(0, "a")}, Fraction(2), 1, "bad")

    def test_dependence_hostile_refutes_independence_product(self):
        d = mod.dependence_hostile()
        self.assertEqual(d["true_joint_good"], Fraction(1, 2))
        self.assertEqual(d["union_lower"], Fraction(1, 2))
        self.assertEqual(d["independence_product"], Fraction(9, 16))
        self.assertTrue(d["product_unsound"])
        self.assertTrue(d["union_attained"])

    def test_shared_ancestor_global_relation_is_stricter(self):
        h = mod.shared_ancestor_hostile()
        self.assertEqual(h["global_y"], frozenset({0}))
        self.assertEqual(h["local_y"], frozenset({-2, 0, 2}))
        self.assertTrue(h["strict"])

    def test_missing_relation_is_unknown_not_source_copy(self):
        q = mod.missing_empty_query_witness()
        self.assertEqual(q["missing_terminal"], "TRANSPORTED_UNKNOWN_RELATION")
        self.assertTrue(q["missing_unknown"])
        self.assertEqual(q["missing_candidates"], frozenset({0, 1, 2}))

    def test_unknown_nonconstant_query_abstains(self):
        q = mod.missing_empty_query_witness()
        self.assertEqual(q["identity_query"].terminal, "CANNOT_IDENTIFY")
        self.assertEqual(q["identity_query"].values, (0, 1, 2))

    def test_unknown_constant_query_can_still_be_identified(self):
        q = mod.missing_empty_query_witness()
        self.assertEqual(q["constant_query"].terminal, "IDENTIFIED")
        self.assertEqual(q["constant_query"].values, ("same",))

    def test_empty_relation_is_inconsistency_with_zero_guaranteed_coverage(self):
        q = mod.missing_empty_query_witness()
        self.assertEqual(q["empty_relation_transport_terminal"], "INCONSISTENT_REGISTERED_ASSUMPTIONS")
        self.assertEqual(q["empty_relation_coverage_lower"], Fraction(0))
        self.assertEqual(q["empty_relation_query"].terminal, "INCONSISTENT_REGISTERED_ASSUMPTIONS")

    def test_cannot_identify_cannot_check_and_inconsistency_are_distinct(self):
        q = mod.missing_empty_query_witness()
        terminals = {
            q["identity_query"].terminal,
            q["empty_relation_query"].terminal,
            q["no_query"].terminal,
        }
        self.assertEqual(terminals, {"CANNOT_IDENTIFY", "INCONSISTENT_REGISTERED_ASSUMPTIONS", "CANNOT_CHECK"})
        self.assertEqual(q["no_domain_terminal"], "CANNOT_CHECK")
        self.assertEqual(q["no_domain_reason"], "TARGET_DOMAIN_NOT_REGISTERED")

    def test_non_set_uncertainty_object_cannot_be_queried_as_identified_set(self):
        law = mod.PredictiveLaw(probabilities=((0, 1),), version=0, provenance="P")
        result = mod.identified_set(law, lambda x: x)
        self.assertEqual(result.terminal, "CANNOT_CHECK")
        self.assertEqual(result.reason, "QUERY_REQUIRES_SET_VALUED_OBJECT")

    def test_same_marginal_can_have_opposite_uncertainty_decomposition(self):
        h = mod.epistemic_aleatoric_hostile()
        self.assertTrue(h["same_marginal"])
        self.assertTrue(h["different_decomposition"])
        self.assertEqual(h["pure_aleatoric"], (Fraction(1), Fraction(0), Fraction(1)))
        self.assertEqual(h["pure_epistemic"], (Fraction(0), Fraction(1), Fraction(1)))
        self.assertEqual(h["marginal_only_terminal"], "CANNOT_DECOMPOSE_WITHOUT_LATENT_SEMANTICS")

    def test_selective_prediction_never_counts_abstention_as_success(self):
        good = mod.SelectivePrediction({1}, Fraction(1, 20), Fraction(1, 2), "scope", "prov")
        self.assertFalse(good.abstentions_counted_as_correct)
        with self.assertRaisesRegex(ValueError, "Abstentions|abstentions"):
            mod.SelectivePrediction({1}, Fraction(1, 20), Fraction(1, 2), "scope", "prov", True)

    def test_coverage_and_informativeness_are_separate(self):
        unknown = mod.ConfidenceSet(domain={0, 1}, candidates={0, 1}, alpha=0, target="theta", version=0, provenance="full")
        self.assertTrue(mod.is_unknown(unknown))
        self.assertEqual(unknown.coverage_lower_bound, Fraction(1))
        self.assertEqual(mod.identified_set(unknown, lambda x: x).terminal, "CANNOT_IDENTIFY")
        self.assertEqual(mod.identified_set(unknown, lambda x: 7).terminal, "IDENTIFIED")

    def test_claim_ceiling_is_bounded(self):
        receipt = self.receipt()
        self.assertEqual(receipt["claim_ceiling"], "GMI_GLOBAL_UNCERTAINTY_AND_ABSTENTION_CONTRACT_AT_REGISTERED_FINITE_SCOPE")
        self.assertIn("COMPLETE_GMI", receipt["forbidden_promotions"])
        self.assertIn("UNIVERSAL_UNCERTAINTY_CALIBRATION", receipt["forbidden_promotions"])

    def test_no_floats_in_receipt(self):
        def walk(x):
            if isinstance(x, float):
                self.fail("float found in exact receipt")
            if isinstance(x, dict):
                for v in x.values():
                    walk(v)
            elif isinstance(x, list):
                for v in x:
                    walk(v)
        walk(self.receipt())


if __name__ == "__main__":
    unittest.main()
