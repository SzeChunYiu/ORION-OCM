from __future__ import annotations

import json
import math
import tempfile
import unittest
from pathlib import Path

import experiment as E
from ocm.kso.warrant import CannotCheck
from ocm.language.meaning import MAX_EXACT_CANONICAL, canonical, isomorphic
from ocm.language.meaning_tree import canonical_any, is_tree


V1_RESULT = Path(__file__).resolve().parents[1] / "l1-linguistic-g2-v1" / "RESULT.json"
V2_RESULT = Path(__file__).resolve().parents[1] / "l1-linguistic-g2-v2" / "RESULT.json"
V3_RESULT = Path(__file__).resolve().parents[1] / "l1-linguistic-g2-v3" / "RESULT.json"
V4_RESULT = Path(__file__).resolve().parents[1] / "l1-linguistic-g2-v4" / "RESULT.json"


class TestL1MeaningGraphBound(unittest.TestCase):
    def test_planted_adjectives_are_new_salt_not_v1_v2_v3_content(self):
        planted = set(E.PLANTED_ADJS)
        self.assertTrue(planted.isdisjoint(E.V1_SURFACES))
        self.assertTrue(planted.isdisjoint(E.V2_CONTENT_SURFACES))
        self.assertTrue(planted.isdisjoint(E.V3_CONTENT_SURFACES))
        self.assertIn("meaning-graph-bound", E.SALT)
        self.assertNotIn("v2", E.SALT)
        self.assertNotIn("v3", E.SALT)
        self.assertNotIn("green", E.PLANTED_ADJS)
        self.assertNotIn("red", E.PLANTED_ADJS)

    def test_historical_bound_is_production_seven_not_invented(self):
        self.assertEqual(MAX_EXACT_CANONICAL, 7)
        rec = E.historical_bound_record()
        self.assertTrue(rec["independent"])
        self.assertEqual(rec["value"], 7)
        self.assertEqual(rec["kind"], "max_nodes")
        self.assertFalse(rec["edge_bound_invented"])
        self.assertEqual(rec["l0_max_exact_canonical"], 7)
        self.assertIn("MAX_EXACT_CANONICAL = 7", rec["ks_t34_limitation"])

    def test_production_canonical_at_and_beyond_bound(self):
        at = E.identical_colour_graph(MAX_EXACT_CANONICAL)
        over = E.identical_colour_graph(MAX_EXACT_CANONICAL + 1)
        canonical(at)
        self.assertTrue(isomorphic(at, at.relabel({f"e{i}": f"z{i}" for i in range(MAX_EXACT_CANONICAL)})))
        with self.assertRaises(CannotCheck):
            canonical(over)
        self.assertEqual(E.colour_perm_count(over), math.factorial(8))
        self.assertGreater(E.colour_perm_count(over), E.PERM_BUDGET)
        with self.assertRaises(CannotCheck):
            E.canonical_under_perm_budget(over)

    def test_perm_budget_raises_bound_for_distinct_colours_not_salt(self):
        small = E.distinct_colour_graph(MAX_EXACT_CANONICAL)
        self.assertEqual(canonical(small)[1], E.canonical_under_perm_budget(small)[1])
        big = E.distinct_colour_graph(E.DISTINCT_MEASURED_NODES)
        with self.assertRaises(CannotCheck):
            canonical(big)
        _, digest = E.canonical_under_perm_budget(big)
        relabelled = big.relabel({f"e{i}": f"z{i}" for i in range(E.DISTINCT_MEASURED_NODES)})
        self.assertEqual(digest, E.canonical_under_perm_budget(relabelled)[1])
        self.assertEqual(E.PERM_BUDGET, math.factorial(MAX_EXACT_CANONICAL))

    def test_tree_ahu_raises_finite_measured_bound(self):
        tree = E.modifier_chain_tree(E.TREE_MEASURED_NODES)
        self.assertTrue(is_tree(tree))
        with self.assertRaises(CannotCheck):
            canonical(tree)
        digest = canonical_any(tree)
        self.assertTrue(digest.startswith("tree:"))
        relabelled = tree.relabel(
            {f"n{i}": f"m{(i * 3 + 1) % E.TREE_MEASURED_NODES}" for i in range(E.TREE_MEASURED_NODES)}
        )
        self.assertEqual(digest, canonical_any(relabelled))

    def test_planted_recursive_np_exceeds_through_production_interpret(self):
        meanings = E.planted_clause_meanings()
        self.assertTrue(meanings)
        n = max(len(g.nodes) for g in meanings)
        self.assertGreater(n, MAX_EXACT_CANONICAL)
        sample = max(meanings, key=lambda g: len(g.nodes))
        self.assertFalse(is_tree(sample))
        with self.assertRaises(CannotCheck):
            canonical(sample)
        with self.assertRaises(CannotCheck):
            canonical_any(sample)
        _, digest = E.canonical_under_perm_budget(sample)
        self.assertEqual(len(digest), 64)
        with self.assertRaises(CannotCheck):
            E.interpret(
                E.PLANTED_UTTERANCE,
                E.planted_lexicon(),
                list(E.seed_constructions()) + [E.stacked_adj_construction()],
            )

    def test_seed_inventory_stays_inside_historical_bound(self):
        examples = E.measure_examples()
        micro = E.measure_microworld()
        seed = E.measure_seed_interpret()
        self.assertLessEqual(examples["max_nodes"], MAX_EXACT_CANONICAL)
        self.assertLessEqual(micro["max_nodes"], MAX_EXACT_CANONICAL)
        self.assertLessEqual(seed["max_nodes"], MAX_EXACT_CANONICAL)
        self.assertEqual(seed["verdict"], "INTERPRETED")

    def test_protocol_terminal_and_locks(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = E.main(Path(tmp) / "RESULT.json")
        self.assertEqual(result["schema"], E.SCHEMA)
        self.assertEqual(result["issue"], 165)
        self.assertIn(result["terminal"], E.LEGAL_TERMINALS)
        self.assertEqual(result["terminal"], "GRAPH_BOUND_EXCEEDED_AT_SCOPE")
        self.assertEqual(result["historical_bound"]["value"], 7)
        self.assertTrue(result["historical_bound"]["independent"])
        self.assertGreater(result["planted_recursive_np"]["max_nodes"], 7)
        self.assertTrue(result["planted_recursive_np"]["interpret_cannot_check"])
        self.assertLessEqual(result["seed_inventory_max_nodes"], 7)
        self.assertEqual(result["raised_bounds"]["colour_class_permutation_budget"]["value"], 5040)
        self.assertTrue(result["raised_bounds"]["colour_class_permutation_budget"]["production_node_cutoff_unchanged"])
        self.assertEqual(result["raised_bounds"]["tree_ahu"]["value"], 16)
        self.assertFalse(result["l2_started"])
        self.assertFalse(result["l3_started"])
        self.assertFalse(result["neural_net"])
        self.assertFalse(result["corpus_n1"])
        self.assertFalse(result["production_src_edited"])
        self.assertTrue(result["v1_result_intact"])
        self.assertTrue(result["v2_result_intact"])
        self.assertTrue(result["v3_result_intact"])
        cl = result["checklist"]
        self.assertEqual(cl["meaning_graphs_beyond_bound"], "GRAPH_BOUND_EXCEEDED_AT_SCOPE")
        self.assertEqual(cl["exact_canonicalization"], "EARNED_AT_SCOPE")
        self.assertEqual(cl["exact_canonicalization_fail_closed_beyond_bound"], "EARNED_AT_SCOPE")
        self.assertEqual(cl["tree_ahu_bound_raised"], "EARNED_AT_SCOPE")
        self.assertEqual(cl["perm_budget_restatement"], "EARNED_AT_SCOPE")
        self.assertEqual(cl["l2"], "LOCKED")
        self.assertEqual(cl["l3"], "LOCKED")
        self.assertTrue(cl["ud_alignment"].startswith("CANNOT_CHECK"))
        self.assertNotIn("EARNED", cl["acquire_corpus_scale_lexicon"])

    def test_capsule_does_not_patch_production_src_or_use_nn(self):
        text = Path(E.__file__).read_text()
        self.assertNotIn("monkeypatch", text)
        self.assertNotIn("torch", text)
        self.assertNotIn("tensorflow", text)
        self.assertIn("from ocm.language.meaning import", text)
        self.assertIn("MAX_EXACT_CANONICAL", text)

    def test_v1_v2_v3_results_not_overwritten(self):
        v1 = json.loads(V1_RESULT.read_text())
        v2 = json.loads(V2_RESULT.read_text())
        v3 = json.loads(V3_RESULT.read_text())
        self.assertEqual(v1["schema"], "ocm.l1.linguistic-g2.v1")
        self.assertEqual(v1["checklist"]["meaning_graphs_beyond_bound"], "CANNOT_CHECK_MICROWORLD_SMALL")
        self.assertEqual(v2["schema"], "ocm.l1.linguistic-g2.v2")
        self.assertEqual(v2["checklist"]["meaning_graphs_beyond_bound"], "CANNOT_CHECK_MICROWORLD_SMALL")
        self.assertEqual(v3["schema"], "ocm.l1.linguistic-g2.v3")
        self.assertEqual(v3["checklist"]["meaning_graphs_beyond_bound"], "CANNOT_CHECK_MICROWORLD_SMALL")
        self.assertEqual(v3["terminal"], "COMPOSITIONAL_LANGUAGE_LEARNING_ONLY")
        if V4_RESULT.exists():
            v4 = json.loads(V4_RESULT.read_text())
            self.assertTrue(str(v4.get("schema", "")).startswith("ocm.l1.linguistic-g2"))


class TestWrittenResultFreeze(unittest.TestCase):
    def test_written_result_matches_protocol_if_present(self):
        path = Path(__file__).resolve().parent / "RESULT.json"
        if not path.exists():
            self.skipTest("RESULT.json not yet written")
        data = json.loads(path.read_text())
        self.assertEqual(data["schema"], E.SCHEMA)
        self.assertIn(data["terminal"], E.LEGAL_TERMINALS)
        self.assertFalse(data["l2_started"])
        self.assertFalse(data["l3_started"])
        self.assertEqual(data["historical_bound"]["value"], 7)


if __name__ == "__main__":
    unittest.main()
