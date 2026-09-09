"""Protocol tests for MATH-1 miniature family worlds (v3)."""
from __future__ import annotations

from pathlib import Path
import hashlib
import json
import sys
import unittest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import experiment as E
import kernel as K

V1_RESULT = HERE.parent / "math-n4-lemma-reuse-v1" / "RESULT.json"
V2_RESULT = HERE.parent / "math-n4-subgoal-v2" / "RESULT.json"


class TestFamilyKernel(unittest.TestCase):
    def test_cut_ids_are_never_prefix_or_swap(self):
        for schema in (K.SUCC_SCHEMA, K.COUNT_SCHEMA, K.EVEN_SCHEMA, K.ODD_SCHEMA, K.DISTRIB_SCHEMA):
            lemma_id = K.mint_cut_id(K.alpha_normalize(schema))
            self.assertTrue(lemma_id.startswith("CUT_"))
            self.assertNotIn(lemma_id, ("PREFIX", "SWAP"))
            self.assertNotIn(lemma_id, K.FROZEN_NAMES)

    def test_exact_checker_rejects_float(self):
        goal = K.closed_goal(K.EVEN_SCHEMA, {"A": "z"})
        with self.assertRaises(K.KernelReject):
            K.exact_check(2.0, goal)  # type: ignore[arg-type]
        with self.assertRaises(K.KernelReject):
            K.exact_answers_equal(1.0, 1.0)  # type: ignore[arg-type]

    def test_count_witness_inhabits_contraction_not_prefix(self):
        goal = K.closed_goal(K.COUNT_SCHEMA, {"A": "p", "B": "q"})
        proof = K.reconstruct_proof(K.COUNT_TERM, goal)
        self.assertEqual(K.exact_check(proof, goal), goal)
        prefix_goal = K.closed_goal(K.SUCC_SCHEMA, {"A": "u", "B": "v", "C": "w"})
        self.assertFalse(K.term_unifies_goal(K.COUNT_TERM, prefix_goal))

    def test_i_and_sbi_both_inhabit_iterator_and_are_not_weakly_equal(self):
        goal = K.closed_goal(K.ITER_SCHEMA, {"A": "it"})
        i_proof = K.reconstruct_proof(K.I_TERM, goal)
        sbi_proof = K.reconstruct_proof(K.SBI_TERM, goal)
        self.assertEqual(K.exact_check(i_proof, goal), goal)
        self.assertEqual(K.exact_check(sbi_proof, goal), goal)
        self.assertNotEqual(K.term_pretty(K.I_TERM), K.term_pretty(K.SBI_TERM))
        self.assertFalse(K.terms_weakly_equal(K.I_TERM, K.SBI_TERM))

    def test_v1_catalog_misses_distrib_and_counting(self):
        algebra = K.closed_goal(K.DISTRIB_SCHEMA, E.ALGEBRA_HOLDOUT)
        count = K.closed_goal(K.COUNT_SCHEMA, E.COUNT_HOLDOUT)
        self.assertEqual(K.catalog_rewrite_parent(algebra).status, "NOT_FOUND")
        self.assertEqual(K.catalog_rewrite_parent(count).status, "NOT_FOUND")
        arith = K.closed_goal(K.SUCC_SCHEMA, E.ARITH_HOLDOUT)
        self.assertEqual(K.catalog_rewrite_parent(arith).status, "FOUND")
        self.assertEqual(K.catalog_rewrite_parent(arith).hits, ("B",))


class TestExperimentProtocol(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = E.run()

    def test_terminal_is_scoped_miniature_positive(self):
        self.assertEqual(
            self.result["terminal"],
            "MINIATURE_FAMILY_METHOD_TRANSFER_SUPPORTED_AT_HILBERT_SCOPE",
        )
        self.assertNotEqual(self.result["terminal"], "CAUSAL_PROOF_METHOD_REUSE_SUPPORTED")
        self.assertTrue(self.result["unscoped_causal_reuse_not_claimed"])
        self.assertEqual(self.result["n4_metamath_status"], "OPEN")
        self.assertEqual(self.result["math2_n5_status"], "LOCKED")
        self.assertEqual(self.result["math3_n6_status"], "LOCKED")
        self.assertTrue(self.result["do_not_expand_flt"])
        self.assertTrue(all(self.result["criteria"].values()))

    def test_family_transfer_and_honest_failures(self):
        arith = self.result["families"]["arithmetic_successor"]
        algebra = self.result["families"]["algebra_distrib"]
        count = self.result["families"]["combinatorics_counting"]
        nthy = self.result["families"]["number_theory_mod2"]
        self.assertTrue(arith["lemma_id"].startswith("CUT_"))
        self.assertTrue(count["lemma_id"].startswith("CUT_"))
        self.assertNotIn(arith["lemma_id"], ("PREFIX", "SWAP"))
        self.assertEqual(arith["holdout"]["ocm"]["status"], "FOUND")
        self.assertIn(arith["lemma_id"], arith["holdout"]["ocm"]["lemmas_used"])
        self.assertEqual(algebra["holdout"]["ocm"]["status"], "FOUND")
        self.assertIn(arith["lemma_id"], algebra["holdout"]["ocm"]["lemmas_used"])
        self.assertEqual(
            algebra["holdout"]["parents"]["knuth_bendix_v1_catalog"]["status"],
            "NOT_FOUND",
        )
        self.assertEqual(
            algebra["holdout"]["parents"]["primitive_sk_size_4"]["status"],
            "NOT_FOUND",
        )
        self.assertEqual(count["holdout"]["ocm"]["status"], "FOUND")
        self.assertIn(count["lemma_id"], count["holdout"]["ocm"]["lemmas_used"])
        self.assertNotEqual(count["holdout"]["arithmetic_lemma_only"]["status"], "FOUND")
        self.assertNotEqual(nthy["odd_holdout"]["even_lemma_only"]["status"], "FOUND")
        self.assertEqual(nthy["odd_holdout"]["ocm"]["status"], "FOUND")
        self.assertTrue(nthy["odd"]["catalog_prior_information"])
        self.assertTrue(self.result["partition"]["fresh_atoms_disjoint_from_training"])

    def test_exact_checker_conjecture_and_parents(self):
        self.assertFalse(self.result["exact_symbolic_checker"]["float_licensed"])
        self.assertTrue(self.result["exact_symbolic_checker"]["float_rejected"])
        self.assertFalse(self.result["exact_symbolic_checker"]["I_weakly_equal_SBI"])
        conj = {row["conjecture_id"]: row["status"] for row in self.result["conjecture_tests"]}
        self.assertEqual(conj["prefix_solves_distrib"], "CONFIRMED")
        self.assertEqual(conj["prefix_solves_counting"], "REFUTED")
        self.assertEqual(conj["sbi_unique_iterator"], "REFUTED")
        dispositions = self.result["parent_dispositions"]
        self.assertEqual(dispositions["algebra_distrib"], "OCM_LEMMA_SERVES_PARENTS_MISS")
        self.assertEqual(dispositions["arithmetic_successor"], "PARENT_SUFFICIENT_FOR_SERVING")
        self.assertEqual(
            self.result["neural_guided_prover"],
            "CANNOT_CHECK_NO_NN_LIBRARY",
        )
        self.assertGreater(
            self.result["costs"]["search"]["algebra_sk6_terms"],
            self.result["costs"]["search"]["algebra_transfer_terms"],
        )
        self.assertTrue(
            self.result["amortized_algebra_note"]["transfer_cheaper_than_sk6_on_this_window"]
        )
        self.assertTrue(self.result["amortized_algebra_note"]["not_lifetime_payback"])

    def test_boxes_are_scoped_and_honest(self):
        boxes = self.result["math1_family_boxes_at_miniature_scope"]
        for key in (
            "arithmetic_families",
            "algebra_families",
            "number_theory_families",
            "combinatorics_families",
            "exact_symbolic_answer_checking",
            "method_acquisition",
            "method_transfer",
            "conjecture_testing",
            "discriminating_experiment_selection",
            "resource_accounting",
            "strongest_specialized_parents",
            "reference_model_on_same_tasks",
        ):
            self.assertTrue(boxes[key], key)
        self.assertFalse(boxes["math2_n5_close"])
        self.assertFalse(boxes["metamath_n4_close"])
        self.assertFalse(boxes["flt"])
        self.assertFalse(boxes["neural_guided_prover"])
        cannot_ids = {row["id"] for row in self.result["cannot_check"]}
        self.assertIn("math2_n5", cannot_ids)
        self.assertIn("flt_prs_129_132", cannot_ids)

    def test_v1_and_v2_results_not_overwritten(self):
        self.assertTrue(self.result["v1_result_custody"]["unchanged"])
        self.assertTrue(self.result["v2_result_custody"]["unchanged"])
        self.assertEqual(
            hashlib.sha256(V1_RESULT.read_bytes()).hexdigest(),
            E.V1_RESULT_SHA256,
        )
        self.assertEqual(
            hashlib.sha256(V2_RESULT.read_bytes()).hexdigest(),
            E.V2_RESULT_SHA256,
        )
        v1 = json.loads(V1_RESULT.read_text(encoding="utf-8"))
        v2 = json.loads(V2_RESULT.read_text(encoding="utf-8"))
        self.assertEqual(v1["terminal"], E.V1_TERMINAL)
        self.assertEqual(v2["terminal"], E.V2_TERMINAL)

    def test_discriminator_records_resource_vectors(self):
        rows = {row["goal_id"]: row for row in self.result["discriminating_experiments"]}
        self.assertIn("algebra_holdout", rows)
        self.assertEqual(rows["algebra_holdout"]["served_status"], "FOUND")
        self.assertTrue(rows["algebra_holdout"]["one_step_or_library_cheaper_than_sk4"])
        self.assertEqual(rows["odd_with_even_lemma"]["served_status"], "NOT_FOUND")


class TestResultFileContract(unittest.TestCase):
    def test_schema_and_unscoped_terminal_absent(self):
        self.assertEqual(E.SCHEMA, "math-n4-families.result.v3")
        text = (HERE / "experiment.py").read_text()
        self.assertNotIn("CAUSAL_PROOF_METHOD_REUSE_SUPPORTED\n", text)
        self.assertIn("CANNOT_CHECK_NO_NN_LIBRARY", text)
        self.assertIn("LOCKED", text)


if __name__ == "__main__":
    unittest.main()
