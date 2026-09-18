#!/usr/bin/env python3
"""AE3 tests: two-route agreement, hostile potency and detection, nulls."""
import json
import os
import sys
import unittest
from fractions import Fraction as F

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import ae3_compression_learning_v1 as A       # noqa: E402
import independent_code_oracle_v1 as O        # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
RES = A.build_result()
R = RES["results"]
L1 = A.LANGS["L1"]


class TestVerdict(unittest.TestCase):
    def test_green(self):
        for name in sorted(RES["checks"]):
            self.assertTrue(RES["checks"][name], "check failed: " + name)
        self.assertEqual(RES["verdict"], "GREEN")
        self.assertEqual(RES["rows_closed"], 8)
        self.assertEqual(RES["issue_comment_id"], 5692689542)

    def test_no_float_anywhere(self):
        def walk(o):
            if isinstance(o, float):
                self.fail("float in receipt")
            if isinstance(o, dict):
                for v in o.values():
                    walk(v)
            elif isinstance(o, (list, tuple)):
                for v in o:
                    walk(v)
        walk(RES)

    def test_sources_never_use_floats_or_logs(self):
        for fn in ("ae3_compression_learning_v1.py",
                   "independent_code_oracle_v1.py"):
            with open(os.path.join(HERE, fn)) as fh:
                src = fh.read()
            for bad in ("float(", "math.log", "import math", "0.5"):
                self.assertNotIn(bad, src, fn + " uses " + bad)

    def test_deterministic(self):
        self.assertEqual(
            json.dumps(A.build_result(), sort_keys=True),
            json.dumps(RES, sort_keys=True),
        )


class TestTwoRoutes(unittest.TestCase):
    def test_code_lengths_agree_on_every_table_and_language(self):
        for name in sorted(A.LANGS):
            lengths = A.LANGS[name]
            for t in A.all_tables():
                self.assertEqual(
                    A.code_length(t, lengths),
                    O.code_length(t, lengths),
                    name + " " + str(t),
                )

    def test_kraft_agrees(self):
        for name in sorted(A.LANGS):
            self.assertEqual(A.kraft_sum(A.LANGS[name]), O.kraft(A.LANGS[name]))
            self.assertEqual(A.kraft_sum(A.LANGS[name]), F(1))

    def test_shortest_consistent_agrees(self):
        for t in A.all_tables():
            la, wa = A.shortest_consistent(t, A.S0, L1)
            lb, wb = O.shortest_consistent(t, A.S0, L1)
            self.assertEqual(la, lb)
            self.assertEqual(set(wa), set(wb))

    def test_notion_B_agrees(self):
        for t in A.all_tables():
            self.assertEqual(
                A.notion_B_task_lossy(t, A.TAU), O.min_junta_arity(t, A.TAU)
            )

    def test_out_of_sample_agrees(self):
        for t in A.all_tables()[:64]:
            for h in A.consistent_tables(t, A.S0):
                self.assertEqual(
                    A.out_of_sample_accuracy(h, t),
                    O.accuracy_on(h, t, A.HELD_OUT),
                )

    def test_rle_runs_agree(self):
        for t in A.all_tables():
            self.assertEqual(A.runs(t), O.runs(t))


class TestNamedResults(unittest.TestCase):
    def test_ae3_1_all_six_pairs_non_determining(self):
        pairs = R["AE3_1_three_notions"]["ordered_pair_census"]
        self.assertEqual(len(pairs), 6)
        for k in sorted(pairs):
            self.assertGreater(pairs[k]["conflicting_pairs"], 0, k)
            self.assertFalse(pairs[k]["determines"], k)

    def test_ae3_2_equal_compression_opposite_usefulness(self):
        s = R["AE3_2_compresses_but_useless"]
        self.assertTrue(s["code_lengths_equal"])
        self.assertTrue(s["both_strictly_compress"])
        self.assertEqual(s["usefulness_useless"], "1/2")
        self.assertEqual(s["usefulness_useful"], "1")
        target = tuple(O.b(x)[1] ^ O.b(x)[2] for x in range(8))
        obs = tuple(O.b(x)[0] for x in range(8))
        self.assertEqual(O.code_length(obs, L1), O.code_length(target, L1))
        self.assertLess(O.code_length(obs, L1), L1[3])
        self.assertEqual(O.representation_usefulness(obs, target), F(1, 2))
        self.assertEqual(O.representation_usefulness(target, target), F(1))

    def test_ae3_3_useful_predictor_is_longer(self):
        s = R["AE3_3_useful_predictor_not_shortest"]
        self.assertIsNotNone(s)
        self.assertGreater(s["length_excess"], 0)
        t = tuple(s["target"])
        ln, winners = O.shortest_consistent(t, A.S0, L1)
        self.assertEqual(ln, s["shortest_consistent_length"])
        best = max(O.accuracy_on(w, t, A.HELD_OUT) for w in winners)
        self.assertEqual(str(best), s["shortest_consistent_best_out_of_sample"])
        self.assertLess(best, F(1))
        perfect = [
            (x, O.code_length(x, L1))
            for x in O.TABLES
            if O.accuracy_on(x, t, A.HELD_OUT) == 1
        ]
        self.assertEqual(
            min(p[1] for p in perfect), s["shortest_perfect_generalizer_length"]
        )

    def test_ae3_4_memorization(self):
        s = R["AE3_4_memorization_vs_generalization"]
        self.assertFalse(s["train_accuracy_determines_out_of_sample"])
        self.assertGreater(s["census"]["conflicting_pairs"], 0)
        self.assertIn("1/2", s["distinct_out_of_sample_accuracies_among_them"])
        self.assertIn("1", s["distinct_out_of_sample_accuracies_among_them"])
        self.assertEqual(s["hypotheses_with_perfect_train_accuracy"], 16)

    def test_ae3_5_mdl(self):
        s = R["AE3_5_mdl_bayes_pacbayes"]
        self.assertTrue(s["mdl_can_select_a_strictly_worse_hypothesis"])
        self.assertGreaterEqual(s["mdl_argmin_size"], 2)
        self.assertEqual(s["mdl_worst_out_of_sample"], "1/2")
        self.assertEqual(s["risk_optimal_out_of_sample"], "1")
        self.assertEqual(len(s["crosswalk"]), 4)
        for entry in s["crosswalk"]:
            self.assertIn("citation", entry)
            self.assertTrue(len(entry["citation"]) > 20)

    def test_ae3_6_kolmogorov_guard(self):
        s = R["AE3_6_kolmogorov_boundary"]
        self.assertEqual(s["guard_alarms_on_this_receipt"], 0)
        self.assertEqual(s["guard_alarm_paths"], [])
        self.assertTrue(s["kolmogorov_complexity_not_computed"])
        planted = {"a": {"kolmogorov_complexity": 3},
                   "b": {"true_shortest_program": "P"}}
        self.assertEqual(len(A.uncomputable_quantity_guard(planted)), 2)
        self.assertEqual(
            A.uncomputable_quantity_guard(
                {"kolmogorov_complexity_not_computed": True}
            ),
            [],
        )
        for p in RES["forbidden_promotions"]:
            self.assertEqual(p, p.upper())
        self.assertIn("KOLMOGOROV_COMPLEXITY_COMPUTED",
                      RES["forbidden_promotions"])
        self.assertIn("GMI_COMPUTES_TRUE_SHORTEST_PROGRAM",
                      RES["forbidden_promotions"])

    def test_ae3_7_language_dependence(self):
        s = R["AE3_7_computable_surrogates"]
        self.assertTrue(s["language_dependence_is_nonzero"])
        self.assertGreater(s["max_abs_difference_L1_L2"], 0)
        self.assertEqual(len(s["surrogates"]), 3)
        gap = 0
        for t in O.TABLES:
            d = abs(O.code_length(t, A.LANGS["L1"]) - O.code_length(t, A.LANGS["L2"]))
            gap = max(gap, d)
        self.assertEqual(gap, s["max_abs_difference_L1_L2"])

    def test_ae3_8_remint_invariance_and_boundary(self):
        s = R["AE3_8_remint_invariance"]
        self.assertEqual(s["kraft_feasible_remints_tested"], 200)
        self.assertTrue(s["AE3_2_predicate_is_exact"])
        self.assertEqual(s["AE3_2_predicate_matches_observation"], 200)
        self.assertEqual(
            s["AE3_2_invariant_count"] + len(s["AE3_2_exceptions"]), 200
        )
        self.assertGreater(s["AE3_3_invariant_count"], 0)
        self.assertLess(s["AE3_3_invariant_count"], 200)
        self.assertEqual(
            s["AE3_3_invariant_count"] + len(s["AE3_3_exceptions"]), 200
        )
        self.assertFalse(s["universal_invariance_claimed"])
        self.assertEqual(s["verdict"], "INVARIANCE_IS_CONDITIONAL_NOT_UNIVERSAL")
        self.assertIn("UNIVERSAL_MACHINE_INVARIANCE_PROVED",
                      RES["forbidden_promotions"])
        # the AE3-2 predicate re-derived independently
        for tup in s["AE3_2_exceptions"]:
            a, _b, c, d = tup
            self.assertFalse(min(a, c) < d)
        b = R["AE3_8_boundary_counterexample"]
        self.assertTrue(b["flips_AE3_3"])
        self.assertFalse(b["kraft_feasible"])
        self.assertTrue(b["detected_by_kraft_guard"])
        self.assertGreater(F(b["kraft_sum"]), F(1))


class TestHostilesAndNull(unittest.TestCase):
    def test_hostiles(self):
        ids = set()
        for h in RES["hostiles"]:
            ids.add(h["id"])
            self.assertTrue(h["perturbation_moved_its_quantity"], h["id"])
            self.assertTrue(h["detected"], h["id"])
        self.assertEqual(len(ids), 5)

    def test_null(self):
        n = RES["null"]
        self.assertTrue(n["fires_on_planted_witness"])
        self.assertEqual(n["known_clean_flagged"], 0)
        self.assertEqual(n["known_clean_controls"], 2)
        self.assertEqual(n["random_corpora_trials"], 200)


class TestArtifacts(unittest.TestCase):
    def test_parent_pins(self):
        aud = RES["parent_audit"]
        self.assertTrue(aud["all_ok"])
        self.assertEqual(len(aud["rows"]), 5)
        for row in aud["rows"]:
            self.assertTrue(row["blob_ok"], row["path"])
            self.assertTrue(row["claim_ok"], row["path"])

    def test_reconciliation_spec(self):
        path = os.path.join(
            HERE, "ISSUE_833_RECONCILIATION_AE3_COMPRESSION_LEARNING_V1.json"
        )
        with open(path) as fh:
            spec = json.load(fh)
        self.assertEqual(spec["schema"], "GMI_ISSUE_RECONCILIATION_V2")
        self.assertEqual(spec["issue"], 833)
        self.assertEqual(spec["issue_comment_id"], 5692689542)
        self.assertEqual(spec["claim_ceiling"], RES["claim_ceiling"])
        self.assertEqual(len(spec["replacements"]), 8)
        seen = set()
        for rep in spec["replacements"]:
            self.assertTrue(rep["old"].startswith("- [ ] "))
            self.assertTrue(rep["new"].startswith("- [x] "))
            self.assertTrue(rep["new"][6:].startswith(rep["old"][6:]))
            self.assertNotIn(rep["old"], seen)
            seen.add(rep["old"])
            self.assertEqual(rep["anchor"],
                             "### AE3 — Compression is not automatically learning")

    def test_manifest(self):
        with open(os.path.join(HERE, "MANIFEST_V1.json")) as fh:
            m = json.load(fh)
        self.assertEqual(m["claim_ceiling"], RES["claim_ceiling"])
        self.assertEqual(m["source_main"], RES["source_main"])
        self.assertEqual(m["freeze_commit"], RES["freeze_commit"])
        self.assertEqual(m["rows_closed"], 8)
        self.assertEqual(len(m["parent_pins"]), 5)

    def test_receipt_matches_committed(self):
        with open(os.path.join(HERE, "RESULT_V1.json")) as fh:
            committed = json.load(fh)
        self.assertEqual(
            json.dumps(committed, sort_keys=True), json.dumps(RES, sort_keys=True)
        )


if __name__ == "__main__":
    unittest.main()
