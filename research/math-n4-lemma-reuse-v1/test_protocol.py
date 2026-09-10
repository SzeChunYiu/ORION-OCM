"""Protocol tests for the MATH-1 miniature Hilbert lemma-reuse microscope."""
from __future__ import annotations

from pathlib import Path
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import experiment as E
import kernel as K


class TestHilbertKernel(unittest.TestCase):
    def test_kernel_accepts_k_and_rejects_bad_mp(self):
        k_formula = K.instantiate_schema(K.K_SCHEMA, {"A": "p", "B": "q"})
        proof = K.HilbertProof((K.HilbertStep(formula=k_formula, rule="K"),))
        self.assertEqual(K.check_proof(proof), k_formula)
        bad = K.HilbertProof((
            K.HilbertStep(formula=k_formula, rule="K"),
            K.HilbertStep(formula="p", rule="MP", premises=(0, 0)),
        ))
        with self.assertRaises(K.KernelReject):
            K.check_proof(bad)

    def test_b_and_i_are_kernel_checked_sk_proofs(self):
        b_goal = K.instantiate_schema(K.PREFIX_SCHEMA, {"A": "p", "B": "q", "C": "r"})
        i_goal = K.instantiate_schema(K.IDENTITY_SCHEMA, {"A": "p"})
        b_proof = K.reconstruct_proof(K.B_TERM, b_goal)
        i_proof = K.reconstruct_proof(K.I_TERM, i_goal)
        self.assertEqual(K.check_proof(b_proof), b_goal)
        self.assertEqual(K.check_proof(i_proof), i_goal)
        self.assertEqual(b_proof.lemmas_invoked(), ())

    def test_revoked_lemma_is_rejected(self):
        goal = K.instantiate_schema(K.PREFIX_SCHEMA, {"A": "p", "B": "q", "C": "r"})
        lemma = K.Lemma("PREFIX", K.PREFIX_SCHEMA, K.B_TERM, ("task:x",), authorized=False)
        proof = K.HilbertProof((K.HilbertStep(formula=goal, rule="LEMMA", lemma_id="PREFIX"),))
        with self.assertRaises(K.KernelReject):
            K.check_proof(proof, {"PREFIX": lemma})


class TestOneStepVersusMultiStep(unittest.TestCase):
    def lemmas(self):
        return {
            "PREFIX": K.Lemma("PREFIX", K.PREFIX_SCHEMA, K.B_TERM, ("a",), True),
            "SWAP": K.Lemma("SWAP", K.SWAP_SCHEMA, K.C_TERM, ("b",), True),
        }

    def test_one_step_cannot_consume_suffix_composition(self):
        goal = K.instantiate_schema(K.SUFFIX_SCHEMA, {"A": "p", "B": "q", "C": "r"})
        self.assertEqual(K.one_step_screen(goal, self.lemmas()), ())

    def test_goal_only_mp_invokes_both_lemmas_on_fresh_suffix(self):
        goal = K.instantiate_schema(K.SUFFIX_SCHEMA, {"A": "p", "B": "q", "C": "r"})
        row = K.goal_only_mp_search(goal, self.lemmas(), max_mp=4000)
        self.assertEqual(row.status, "FOUND")
        self.assertEqual(set(row.lemmas_used), {"PREFIX", "SWAP"})
        self.assertEqual(row.one_step_hits, ())
        self.assertTrue(row.subgoals)
        self.assertEqual(K.check_proof(row.proof, self.lemmas()), goal)

    def test_ablation_of_either_lemma_loses_the_selected_proof(self):
        goal = K.instantiate_schema(K.SUFFIX_SCHEMA, {"A": "p", "B": "q", "C": "r"})
        lemmas = self.lemmas()
        both = K.goal_only_mp_search(goal, lemmas, max_mp=4000)
        prefix_only = K.goal_only_mp_search(goal, {"PREFIX": lemmas["PREFIX"]}, max_mp=4000)
        swap_only = K.goal_only_mp_search(goal, {"SWAP": lemmas["SWAP"]}, max_mp=4000)
        primitive = K.goal_only_mp_search(goal, {}, max_mp=4000)
        self.assertEqual(both.status, "FOUND")
        self.assertNotEqual(prefix_only.status, "FOUND")
        self.assertNotEqual(swap_only.status, "FOUND")
        self.assertNotEqual(primitive.status, "FOUND")
        self.assertGreater(prefix_only.costs.mp_attempts, both.costs.mp_attempts)
        self.assertGreater(swap_only.costs.mp_attempts, both.costs.mp_attempts)


class TestFailureMemory(unittest.TestCase):
    def test_shape_memory_skips_renamed_dead_end_without_task_ids(self):
        study = E.failure_attempt_study()
        self.assertEqual(study["first_status"], "NOT_FOUND")
        self.assertEqual(study["second_status"], "NOT_FOUND")
        self.assertGreater(study["skipped_on_second"], 0)
        self.assertTrue(study["not_task_id_blacklist"])
        self.assertTrue(study["success_outside_failure_scope"])
        self.assertFalse(study["memory_contains_first_task_id"])


class TestRetrievalAndNeural(unittest.TestCase):
    def test_bag_of_symbols_ranks_same_shape_lemmas(self):
        goal = K.instantiate_schema(K.SUFFIX_SCHEMA, {"A": "p", "B": "q", "C": "r"})
        lemmas = {
            "PREFIX": K.Lemma("PREFIX", K.PREFIX_SCHEMA, K.B_TERM, ("a",), True),
            "SWAP": K.Lemma("SWAP", K.SWAP_SCHEMA, K.C_TERM, ("b",), True),
        }
        top2 = K.retrieve_nearest_lemmas(goal, lemmas, 2)
        self.assertEqual(set(top2), {"PREFIX", "SWAP"})
        self.assertEqual(K.bag_jaccard(goal, K.PREFIX_SCHEMA), 1.0)

    def test_neural_and_transformer_are_cannot_check(self):
        status = E.neural_status()
        self.assertEqual(status, "CANNOT_CHECK_NO_NEURAL_PROVER_IN_THIS_ENVIRONMENT")


class TestExperimentProtocol(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = E.run()

    def test_terminal_is_scoped_miniature_positive(self):
        self.assertEqual(
            self.result["terminal"],
            "CAUSAL_PROOF_METHOD_REUSE_SUPPORTED_AT_MINIATURE_SCOPE",
        )
        self.assertNotEqual(self.result["terminal"], "CAUSAL_PROOF_METHOD_REUSE_SUPPORTED")
        self.assertTrue(self.result["unscoped_causal_reuse_not_claimed"])
        self.assertEqual(self.result["n4_metamath_status"], "OPEN")
        self.assertTrue(self.result["do_not_expand_flt"])

    def test_fresh_theorem_held_out_and_both_lemmas_invoked(self):
        self.assertTrue(self.result["partition"]["fresh_atoms_disjoint_from_acquisition"])
        self.assertEqual(self.result["fresh"]["one_step_invocations"], 0)
        self.assertEqual(set(self.result["fresh"]["both"]["lemmas_used"]), {"PREFIX", "SWAP"})
        self.assertEqual(self.result["fresh"]["both"]["status"], "FOUND")
        self.assertEqual(self.result["fresh"]["primitive"]["status"], "NOT_FOUND")

    def test_ablation_restart_revocation_and_costs(self):
        fresh = self.result["fresh"]
        self.assertEqual(fresh["prefix_only"]["status"], "NOT_FOUND")
        self.assertEqual(fresh["swap_only"]["status"], "NOT_FOUND")
        self.assertGreater(fresh["prefix_only"]["costs"]["mp_attempts"], fresh["both"]["costs"]["mp_attempts"])
        self.assertGreater(fresh["swap_only"]["costs"]["mp_attempts"], fresh["both"]["costs"]["mp_attempts"])
        self.assertEqual(self.result["restart"]["status"], "FOUND")
        self.assertEqual(set(self.result["restart"]["lemmas_used"]), {"PREFIX", "SWAP"})
        self.assertNotEqual(self.result["restart"]["pid"], self.result["process"]["pid"])
        self.assertEqual(self.result["revocation"]["revoke_both"]["status"], "NOT_FOUND")
        self.assertEqual(self.result["revocation"]["restore"]["status"], "FOUND")
        costs = self.result["costs"]
        for key in ("search", "check", "storage", "acquisition"):
            self.assertTrue(costs[key])
        self.assertEqual(
            self.result["neural_guided_prover"],
            "CANNOT_CHECK_NO_NEURAL_PROVER_IN_THIS_ENVIRONMENT",
        )
        self.assertEqual(
            self.result["transformer_proof_reference"],
            "CANNOT_CHECK_NO_NEURAL_PROVER_IN_THIS_ENVIRONMENT",
        )
        self.assertTrue(all(self.result["criteria"].values()))

    def test_library_artifact_is_not_silently_treated_as_runtime(self):
        note = self.result["metamath_library"]
        self.assertTrue(note["present"])
        self.assertEqual(note["disposition"], "MINIATURE_HILBERT_MICROSCOPE")
        self.assertFalse(note["runtime_available"])

    def test_persist_round_trip(self):
        lemmas = {
            "PREFIX": K.Lemma("PREFIX", K.PREFIX_SCHEMA, K.B_TERM, ("task:a",), True),
        }
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "library.json"
            E.persist_library(path, lemmas)
            loaded = E.load_library(path)
        self.assertEqual(loaded["PREFIX"].lemma_id, "PREFIX")
        self.assertEqual(loaded["PREFIX"].support_ids, ("task:a",))


class TestResultFileContract(unittest.TestCase):
    def test_result_schema_constant(self):
        self.assertEqual(E.SCHEMA, "math-n4-lemma-reuse.result.v1")
        self.assertNotIn("CAUSAL_PROOF_METHOD_REUSE_SUPPORTED\n", (HERE / "experiment.py").read_text())


if __name__ == "__main__":
    unittest.main()
