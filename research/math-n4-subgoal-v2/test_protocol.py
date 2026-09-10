"""Protocol tests for MATH-1 miniature subgoal discovery + lemma introduction."""
from __future__ import annotations

from pathlib import Path
import hashlib
import json
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import experiment as E
import kernel as K

V1_RESULT = HERE.parent / "math-n4-lemma-reuse-v1" / "RESULT.json"


class TestDiscoveryKernel(unittest.TestCase):
    def test_minted_id_is_never_prefix_or_swap(self):
        ident = K.collect_primitive_identities(4)
        ids = {row.lemma_id for row in ident}
        self.assertTrue(ids)
        self.assertTrue(ids.isdisjoint(K.FROZEN_TRAINING_LEMMA_NAMES))
        prefix_hits = [
            row for row in ident
            if K.unify_schema(K.PREFIX_SCHEMA, row.schema) is not None
        ]
        self.assertEqual(len(prefix_hits), 1)
        self.assertEqual(prefix_hits[0].lemma_id, K.mint_cut_id(prefix_hits[0].schema))
        self.assertNotEqual(prefix_hits[0].lemma_id, "PREFIX")

    def test_compose_second_needs_invented_cut_not_one_step(self):
        goal = K.instantiate_schema(K.COMPOSE_SECOND_SCHEMA, E.FRESH_ATOMS)
        self.assertEqual(K.one_step_screen(goal, {}), ())
        primitive = K.inhabit_well_typed(goal, ("S", "K"), {}, 2)
        self.assertNotEqual(primitive.status, "FOUND")
        row = K.subgoal_discover_and_finish(goal, ("task:test",), 4, 2)
        self.assertEqual(row.status, "FOUND")
        self.assertIsNotNone(row.invented_lemma)
        assert row.invented_lemma is not None
        self.assertNotIn(row.invented_lemma.lemma_id, K.FROZEN_TRAINING_LEMMA_NAMES)
        self.assertIn(row.invented_lemma.lemma_id, row.finish.lemmas_used)
        self.assertEqual(row.one_step_hits, ())
        self.assertNotEqual(
            K.pretty(K.alpha_normalize(row.invented_lemma.schema)),
            K.pretty(K.alpha_normalize(goal)),
        )
        self.assertEqual(K.check_proof(row.finish.proof, {
            row.invented_lemma.lemma_id: row.invented_lemma,
        }), goal)
        intermediates = K.intermediate_formulas(row.finish.proof, goal)
        self.assertTrue(intermediates)

    def test_revoked_cut_is_rejected_by_kernel(self):
        goal = K.instantiate_schema(K.COMPOSE_SECOND_SCHEMA, E.FRESH_ATOMS)
        row = K.subgoal_discover_and_finish(goal, ("task:test",), 4, 2)
        lemma = row.invented_lemma
        assert lemma is not None
        revoked = K.Lemma(
            lemma.lemma_id, lemma.schema, lemma.witness_term, lemma.support_ids, False,
        )
        proof = row.finish.proof
        with self.assertRaises(K.KernelReject):
            K.check_proof(proof, {lemma.lemma_id: revoked})


class TestRetrievalAndNeural(unittest.TestCase):
    def test_bag_of_symbols_ranks_invented_cut_over_identity(self):
        goal = K.instantiate_schema(K.COMPOSE_SECOND_SCHEMA, E.FRESH_ATOMS)
        row = K.subgoal_discover_and_finish(goal, ("task:test",), 4, 2)
        assert row.invented_lemma is not None
        distractor = E.identity_distractor()
        pool = {
            row.invented_lemma.lemma_id: row.invented_lemma,
            distractor.lemma_id: distractor,
        }
        top1 = K.retrieve_nearest_lemmas(goal, pool, 1)
        self.assertEqual(top1, (row.invented_lemma.lemma_id,))

    def test_neural_and_transformer_are_cannot_check_no_nn_library(self):
        self.assertEqual(E.neural_status(), "CANNOT_CHECK_NO_NN_LIBRARY")


class TestExperimentProtocol(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = E.run()

    def test_terminal_is_scoped_miniature_positive(self):
        self.assertEqual(
            self.result["terminal"],
            "CAUSAL_SUBGOAL_LEMMA_INTRODUCTION_SUPPORTED_AT_MINIATURE_SCOPE",
        )
        self.assertNotEqual(self.result["terminal"], "CAUSAL_PROOF_METHOD_REUSE_SUPPORTED")
        self.assertNotEqual(
            self.result["terminal"],
            "CAUSAL_PROOF_METHOD_REUSE_SUPPORTED_AT_MINIATURE_SCOPE",
        )
        self.assertTrue(self.result["unscoped_causal_reuse_not_claimed"])
        self.assertEqual(self.result["n4_metamath_status"], "OPEN")
        self.assertTrue(self.result["do_not_expand_flt"])

    def test_invented_lemma_is_cut_not_prefix_or_swap(self):
        invented = self.result["invented_lemma"]
        self.assertTrue(invented["lemma_id"].startswith("CUT_"))
        self.assertTrue(invented["name_is_not_prefix_or_swap"])
        self.assertFalse(invented["is_frozen_name"])
        self.assertTrue(invented["unifies_prefix_schema"])
        self.assertNotIn(invented["lemma_id"], ("PREFIX", "SWAP"))
        for row in self.result["discovery_tasks"]:
            self.assertEqual(row["discovery"]["invented_lemma_id"], invented["lemma_id"])
            self.assertTrue(row["intermediates"])
            self.assertEqual(row["one_step_hits"], [])

    def test_fresh_reuse_ablation_revocation_restart(self):
        fresh = self.result["fresh"]
        invented_id = self.result["invented_lemma"]["lemma_id"]
        self.assertEqual(fresh["one_step_invocations"], 0)
        self.assertEqual(fresh["with_cut"]["status"], "FOUND")
        self.assertIn(invented_id, fresh["with_cut"]["lemmas_used"])
        self.assertEqual(fresh["primitive"]["status"], "NOT_FOUND")
        self.assertEqual(fresh["ablation"]["status"], "NOT_FOUND")
        self.assertEqual(self.result["restart"]["status"], "FOUND")
        self.assertIn(invented_id, self.result["restart"]["lemmas_used"])
        self.assertNotEqual(self.result["restart"]["pid"], self.result["process"]["pid"])
        self.assertEqual(
            self.result["revocation"]["revoke_discovery_support"]["status"],
            "NOT_FOUND",
        )
        self.assertEqual(self.result["revocation"]["restore"]["status"], "FOUND")
        self.assertTrue(self.result["partition"]["fresh_atoms_disjoint_from_discovery"])
        self.assertTrue(all(self.result["criteria"].values()))
        self.assertEqual(
            self.result["neural_guided_prover"],
            "CANNOT_CHECK_NO_NN_LIBRARY",
        )
        self.assertEqual(
            self.result["transformer_proof_reference"],
            "CANNOT_CHECK_NO_NN_LIBRARY",
        )

    def test_math1_boxes_are_scoped_and_honest(self):
        boxes = self.result["math1_boxes_at_miniature_scope"]
        self.assertTrue(boxes["subgoal_discovery"])
        self.assertTrue(boxes["representation_lemma_introduction"])
        self.assertTrue(boxes["exact_support_revocation"])
        self.assertFalse(boxes["neural_guided_prover"])
        self.assertFalse(boxes["transformer_proof_reference_same_checker"])
        self.assertFalse(boxes["metamath_n4_close"])
        self.assertFalse(boxes["full_search_check_storage_acquisition_cost"])
        cannot_ids = {row["id"] for row in self.result["cannot_check"]}
        self.assertIn("neural_guided_prover", cannot_ids)
        self.assertIn("metamath_n4", cannot_ids)

    def test_v1_result_not_overwritten(self):
        custody = self.result["v1_result_custody"]
        self.assertTrue(custody["unchanged"])
        self.assertEqual(custody["sha256"], E.V1_RESULT_SHA256)
        digest = hashlib.sha256(V1_RESULT.read_bytes()).hexdigest()
        self.assertEqual(digest, E.V1_RESULT_SHA256)
        v1 = json.loads(V1_RESULT.read_text(encoding="utf-8"))
        self.assertEqual(v1["terminal"], E.V1_TERMINAL)

    def test_persist_round_trip(self):
        lemmas = {
            "CUT_test": K.Lemma("CUT_test", K.PREFIX_SCHEMA, K.B_TERM, ("task:a",), True),
        }
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "library.json"
            E.persist_library(path, lemmas)
            loaded = E.load_library(path)
        self.assertEqual(loaded["CUT_test"].support_ids, ("task:a",))


class TestResultFileContract(unittest.TestCase):
    def test_schema_and_unscoped_terminal_absent(self):
        self.assertEqual(E.SCHEMA, "math-n4-subgoal.result.v2")
        text = (HERE / "experiment.py").read_text()
        self.assertNotIn("CAUSAL_PROOF_METHOD_REUSE_SUPPORTED\n", text)
        self.assertIn("CANNOT_CHECK_NO_NN_LIBRARY", text)


if __name__ == "__main__":
    unittest.main()
