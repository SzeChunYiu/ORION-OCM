"""Bounded G2.4 causal-reuse controls. Full P1×held-out screening lives in records/."""
import json
import sys
import unittest
from pathlib import Path

CAPSULE = Path(__file__).resolve().parent.parent
SUCCESSOR = CAPSULE / "successor"
CONSUMER = CAPSULE.parent / "ordinary-cut-source-evidence-v1" / "consumer-v3"
sys.path[:0] = [str(SUCCESSOR), str(CONSUMER), str(CONSUMER / "donor")]

import compile_lemmas as C
import load_inputs as L
import screen_heldout as S
import typed_context as TC


class FrozenInputs(unittest.TestCase):
    def test_unique_canonical_bodies(self):
        payload = L.load_negatives()
        self.assertEqual(payload["occurrences"], 24)
        unique = L.unique_negatives(payload)
        self.assertEqual(len(unique), 22)
        self.assertEqual(len({row["canonical_id"] for row in unique}), 22)

    def test_heldout_is_after_training(self):
        held = L.load_heldout()
        self.assertEqual(held["ordinals"], [4224, 4233])
        labels = [t["label"] for t in held["theorems"]]
        self.assertEqual(len(labels), 10)
        self.assertNotIn("ssind", labels)
        self.assertNotIn("inss", labels)
        self.assertNotIn("pssdif", labels)
        for theorem in held["theorems"]:
            self.assertGreater(theorem["ordinal"], 4223)
            self.assertTrue(theorem["statement"][0] == "|-")
            self.assertNotIn("proof_labels", theorem)

    def test_cut_bodies_exist_for_unique_negatives(self):
        unique = L.unique_negatives()
        bodies = L.cut_bodies(canonical_ids=[row["canonical_id"] for row in unique])
        self.assertEqual(len(bodies), 22)
        for row in unique:
            body = bodies[row["canonical_id"]]["body"]
            self.assertEqual(body["query"], row["query"])
            self.assertEqual(body["premises"], row["premises"])
            self.assertEqual(body["schema"], "native.typed-proper-chunk.v1")


class CompileDag(unittest.TestCase):
    def test_first_lemma_replays_two_semantic_steps(self):
        unique = L.unique_negatives()
        p1 = L.load_p1()
        bodies = L.cut_bodies(canonical_ids=[unique[0]["canonical_id"]])
        work = {}
        lemma = C.compile_one(bodies[unique[0]["canonical_id"]]["body"], p1, work, 0)
        self.assertEqual(lemma["semantic_applications"], 2)
        self.assertEqual(lemma["native_acceptance"], "UNKNOWN")
        self.assertIn("incom", lemma["proof"])
        self.assertEqual(lemma["proof"][-1], lemma["semantic_labels"][-1])
        self.assertEqual(work["body_nodes_validated"], 9)

    def test_compile_all_unique_are_two_p1_steps(self):
        unique = L.unique_negatives()
        p1 = L.load_p1()
        bodies = L.cut_bodies(canonical_ids=[row["canonical_id"] for row in unique])
        lemmas = C.compile_all(unique, bodies, p1, {})
        self.assertEqual(len(lemmas), 22)
        self.assertTrue(all(row["semantic_applications"] == 2 for row in lemmas))
        self.assertTrue(all(row["abstraction"] != "OTHER" for row in lemmas))
        self.assertEqual(len({row["label"] for row in lemmas}), 22)


class TinyScreen(unittest.TestCase):
    def test_lemma_does_not_one_step_alias_first_heldout(self):
        unique = L.unique_negatives()
        p1 = L.load_p1()
        bodies = L.cut_bodies(canonical_ids=[unique[0]["canonical_id"]])
        lemma = C.compile_one(bodies[unique[0]["canonical_id"]]["body"], p1, {}, 0)
        held = L.load_heldout()["theorems"][0]
        parent = C.ordinary_parent_rows([lemma])
        result = S.screen(held["statement"], [h["statement"] for h in held["essential"]],
                          held["floating"], parent, {})
        self.assertEqual(result["lemma_labels"], [])
        self.assertIn(result["status"], ("SCREENED_NEGATIVE_IN_DOMAIN", "UNKNOWN"))

    def test_context_ids_are_v0v1v2(self):
        self.assertEqual(TC.IDS, ("V0", "V1", "V2"))


class RecordedRun(unittest.TestCase):
    def test_replay_record_if_present(self):
        path = CAPSULE / "records" / "replay-01" / "RESULT.json"
        if not path.exists():
            self.skipTest("replay record not written yet")
        result = json.loads(path.read_text())
        self.assertEqual(result["native_calls"], 0)
        self.assertEqual(result["native_acceptance"], "UNKNOWN")
        self.assertEqual(result["unique_lemmas"], 22)
        self.assertEqual(result["heldout_n"], 10)
        self.assertFalse(result["lemma_consumed_on_fresh_task"])
        self.assertTrue(result["distinct_consumer_pids"])
        self.assertTrue(result["ablation_matches_reset"])
        self.assertIn(result["terminal"], (
            "NO_NEW_ABSTRACTION",
            "NO_CAUSAL_REUSE_IN_ONE_STEP_DOMAIN",
            "CAUSAL_METHOD_REUSE_SUPPORTED",
        ))
        if result["terminal"] == "CAUSAL_METHOD_REUSE_SUPPORTED":
            self.assertTrue(result["causal_method_reuse_supported"])
        else:
            self.assertFalse(result["causal_method_reuse_supported"])


if __name__ == "__main__":
    unittest.main()
