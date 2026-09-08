"""Authored controls, not new protected-population performance measurements."""
from __future__ import annotations

from copy import deepcopy
from fractions import Fraction
from itertools import product
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import audit_g2 as A


def rows_for(words, maximum=3, fragments=()):
    ids = list(dict.fromkeys(A.task_id(tuple(w)) for w in words))
    hits = A.first_hits(ids, maximum, fragments)
    return ids, [hits[fp] for fp in ids]


class ExactIdentityTests(unittest.TestCase):
    def test_canonical_hash_ignores_dict_order(self):
        self.assertEqual(A.digest({"a": 1, "b": 2}), A.digest({"b": 2, "a": 1}))

    def test_canonical_hash_preserves_types(self):
        self.assertNotEqual(A.digest({"slots": True}), A.digest({"slots": 1}))

    def test_integer_rejects_bool_float_negative_and_over_cap(self):
        for value in (True, 1.0, -1, 200001, "2", None):
            with self.subTest(value=value), self.assertRaises(A.AuditError):
                A.integer(value, "slots", 0, 200000)

    def test_expect_is_not_python_boolean_integer_equality(self):
        with self.assertRaises(A.AuditError):
            A.expect({"accepted": 1}, {"accepted": True}, "flag")

    def test_program_rejects_invalid_grammar(self):
        for value in ("inc", ["unknown"], [False], ["inc"] * 8, None):
            with self.subTest(value=value), self.assertRaises(A.AuditError):
                A.program(value)

    def test_polynomial_normal_forms(self):
        self.assertEqual(A.coefficients(("inc", "square")), (1, 2, 1))
        self.assertEqual(A.coefficients(("square", "inc")), (1, 0, 1))
        self.assertEqual(A.coefficients(("double", "square")), (0, 0, 4))
        self.assertEqual(A.coefficients(("inc", "dec")), (0, 1))

    def test_semantic_alias_has_same_task_identity(self):
        self.assertEqual(A.task_id(()), A.task_id(("inc", "dec")))
        self.assertNotEqual(A.task_id(("square", "inc")), A.task_id(("inc", "square")))

    def test_coefficients_match_direct_execution_exhaustively_at_degree_plus_one_points(self):
        # Independent rational execution, no protected tasks or performance outcomes.
        for length in range(4):
            for word in product(A.OPS, repeat=length):
                p = A.coefficients(word)
                for x in range(len(p)):
                    actual = Fraction(x)
                    for op in word:
                        if op == "inc": actual += 1
                        elif op == "dec": actual -= 1
                        elif op == "double": actual *= 2
                        else: actual *= actual
                    symbolic = sum(Fraction(a) * x ** i for i, a in enumerate(p))
                    self.assertEqual(actual, symbolic, (word, x))

    def test_method_identity_binds_library_and_lineage(self):
        a = A.method_id((("inc", "square"),), ["b", "a"])
        self.assertEqual(a, A.method_id((("inc", "square"),), ["a", "b"]))
        self.assertNotEqual(a, A.method_id((("square", "inc"),), ["a", "b"]))
        self.assertNotEqual(a, A.method_id((("inc", "square"),), ["a", "c"]))


class ScheduleTests(unittest.TestCase):
    def test_known_primitive_ranks(self):
        ids, rows = rows_for([(), ("inc",), ("dec",), ("double",), ("square",)], 1)
        self.assertEqual([r["slots"] for r in rows], [1, 2, 3, 4, 5])
        self.assertTrue(all(r["origin"] == "primitive" for r in rows))

    def test_known_guided_strict_win(self):
        ids, base = rows_for([("inc", "square")], 2)
        guided = A.first_hits(ids, 2, (("inc", "square"),))
        self.assertEqual(base[0]["slots"], 9)
        self.assertEqual(guided[ids[0]]["slots"], 1)
        self.assertEqual(guided[ids[0]]["origin"], "guided")

    def test_duplicate_and_too_long_candidates_still_charge_slots(self):
        ids, _ = rows_for([("dec",)], 1)
        hit = A.first_hits(ids, 1, (("inc", "square"),))[ids[0]]
        # Slot 1 is an overlength macro. Slot 2 is baseline identity.
        # Slot 3 is guided inc, slot 4 duplicate baseline inc, slot 5 guided dec.
        self.assertEqual(hit["slots"], 5)

    def test_fair_fallback_bound_on_small_complete_population(self):
        words = [w for n in range(4) for w in product(A.OPS, repeat=n)]
        ids, base = rows_for(words, 3)
        for fragment in (("inc", "square"), ("inc", "dec"), ("square", "double")):
            guided = A.first_hits(ids, 3, (fragment,))
            for row in base:
                self.assertLessEqual(guided[row["task"]]["slots"], 2 * row["slots"])

    def test_budget_boundary(self):
        fp = A.task_id(("inc",))
        with self.assertRaises(A.AuditError):
            A.first_hits([fp], 1, budget=1)
        self.assertEqual(A.first_hits([fp], 1, budget=2)[fp]["slots"], 2)

    def test_zero_budget_is_not_impossibility(self):
        with self.assertRaisesRegex(A.AuditError, "CANNOT_CHECK_UNSOLVED"):
            A.first_hits([A.task_id(())], 0, budget=0)

    def test_unknown_target_is_not_a_successful_empty_receipt(self):
        with self.assertRaisesRegex(A.AuditError, "CANNOT_CHECK_UNSOLVED"):
            A.first_hits(["no-such-polynomial"], 1)

    def test_duplicate_demand_rejected(self):
        fp = A.task_id(())
        with self.assertRaises(A.AuditError):
            A.first_hits([fp, fp], 1)

    def test_empty_demand_returns_no_evidence(self):
        self.assertEqual(A.first_hits([], 1), {})
        self.assertFalse(A.paired_equal([], [], []))

    def test_duplicate_and_singleton_fragments_rejected(self):
        for fs in ((("inc",),), (("inc", "square"),) * 2):
            with self.subTest(fs=fs), self.assertRaises(A.AuditError):
                A.first_hits([A.task_id(())], 2, fs)


class CoverageTests(unittest.TestCase):
    def setUp(self):
        self.ids, self.rows = rows_for([(), ("inc",), ("dec",)], 1)

    def test_complete_pairing(self):
        self.assertTrue(A.paired_equal(self.rows, deepcopy(self.rows), self.ids))

    def test_legacy_zip_prefix_counterexample(self):
        def legacy(a_rows, b_rows):
            return all(a["task"] == b["task"] and a["slots"] == b["slots"]
                       and tuple(a["program"]) == tuple(b["program"])
                       for a, b in zip(a_rows, b_rows))
        self.assertTrue(legacy(self.rows, self.rows[:-1]))
        self.assertTrue(legacy(self.rows, []))
        self.assertFalse(A.paired_equal(self.rows, self.rows[:-1], self.ids))
        self.assertFalse(A.paired_equal(self.rows, [], self.ids))

    def test_both_arms_truncated_are_rejected(self):
        self.assertFalse(A.paired_equal(self.rows[:-1], self.rows[:-1], self.ids))

    def test_reordered_or_duplicate_rows_rejected(self):
        for bad in (list(reversed(self.rows)), [self.rows[0]] * 3):
            with self.subTest(bad=bad):
                self.assertFalse(A.paired_equal(self.rows, bad, self.ids))
                with self.assertRaises(A.AuditError):
                    A.check_rows(bad, self.ids, 1)

    def test_boolean_slot_cannot_pass_pairing(self):
        bad = deepcopy(self.rows)
        bad[0]["slots"] = True
        self.assertFalse(A.paired_equal(bad, self.rows, self.ids))

    def test_missing_program_cannot_pass_pairing(self):
        bad = deepcopy(self.rows)
        del bad[0]["program"]
        self.assertFalse(A.paired_equal(bad, self.rows, self.ids))

    def test_exact_receipt_total(self):
        self.assertEqual(A.check_rows(self.rows, self.ids, 1), 6)

    def test_forged_slot_rejected_by_independent_schedule(self):
        bad = deepcopy(self.rows)
        bad[1]["slots"] = 1
        with self.assertRaises(A.AuditError):
            A.check_rows(bad, self.ids, 1)

    def test_false_guided_attribution_rejected(self):
        bad = deepcopy(self.rows)
        bad[1]["origin"] = "guided"
        with self.assertRaises(A.AuditError):
            A.check_rows(bad, self.ids, 1)

    def test_correct_but_not_first_solution_rejected(self):
        ids = [A.task_id(())]
        bad = [{"task": ids[0], "slots": 7, "program": ["inc", "dec"], "origin": "primitive"}]
        with self.assertRaises(A.AuditError):
            A.check_rows(bad, ids, 2)

    def test_wrong_mathematical_solution_rejected(self):
        bad = deepcopy(self.rows)
        bad[1]["program"] = ["dec"]
        with self.assertRaises(A.AuditError):
            A.check_rows(bad, self.ids, 1)

    def test_comparison_rejects_missing_or_duplicate_tasks(self):
        for a, b in ((self.rows, self.rows[:-1]), ([self.rows[0]] * 2, [self.rows[0]] * 2), ([], [])):
            with self.subTest(a=a, b=b), self.assertRaises(A.AuditError):
                A.comparison(a, b)

    def test_comparison_counts_guided_strict_use_not_just_presence(self):
        ids, base = rows_for([("inc", "square")], 2)
        guided = [A.first_hits(ids, 2, (("inc", "square"),))[ids[0]]]
        self.assertEqual(A.comparison(base, guided),
                         {"strict_improvement_tasks": 1, "harmful_tasks": 0, "guided_wins": 1})
        self.assertEqual(A.comparison(guided, guided)["guided_wins"], 0)


class CandidateAndParserTests(unittest.TestCase):
    def test_distinct_task_support(self):
        words = [("inc", "square", "inc"), ("inc", "square", "double")]
        rows = [{"task": A.task_id(w), "program": w} for w in words]
        pool, support = A.candidate_pool(rows)
        self.assertEqual(pool, [("inc", "square")])
        self.assertEqual(support[("inc", "square")], 2)

    def test_copied_training_episode_cannot_inflate_support(self):
        word = ("inc", "square", "inc")
        row = {"task": A.task_id(word), "program": word}
        with self.assertRaises(A.AuditError):
            A.candidate_pool([row, row])

    def test_relabelled_mathematical_task_cannot_inflate_support(self):
        word = ("inc", "square", "inc")
        with self.assertRaises(A.AuditError):
            A.candidate_pool([{"task": "invented-label", "program": word}])

    def test_no_whole_program_or_singleton_candidates(self):
        words = [("inc", "inc"), ("dec", "dec")]
        pool, support = A.candidate_pool([{"task": A.task_id(w), "program": w} for w in words])
        self.assertEqual(pool, [])
        self.assertEqual(support, {})

    def test_duplicate_json_keys_rejected(self):
        with self.assertRaises(A.AuditError):
            json.loads('{"slots":1,"slots":2}', object_pairs_hook=A.unique_object)

    def test_nonfinite_json_rejected(self):
        for literal in ("NaN", "Infinity", "-Infinity"):
            with self.subTest(literal=literal), self.assertRaises(A.AuditError):
                json.loads('{"slots":' + literal + '}', parse_constant=A.reject_constant)

    def test_unknown_schema_rejected_before_population_work(self):
        with self.assertRaises(A.AuditError):
            A.audit_result({"schema": "not-the-frozen-study"})

    def test_wrong_method_blob_rejected(self):
        with self.assertRaises(A.AuditError):
            A.audit_result({"schema": A.SCHEMA, "method_blob": "0" * 40})


class PopulationTests(unittest.TestCase):
    def test_partitions_have_full_disjoint_semantic_coverage(self):
        p = A.frozen_partition()
        groups = [p[f"{name}_ids"] for name, _, _ in A.PARTS]
        self.assertEqual([len(g) for g in groups], [48, 32, 64])
        self.assertEqual(len(set(sum(groups, []))), 144)

    def test_quotient_bfs_matches_complete_word_population(self):
        # A mathematical-identity census only, not a solve or a utility study.
        best = {}
        for length in range(8):
            for word in product(A.OPS, repeat=length):
                best.setdefault(A.task_id(word), length)
        p = A.frozen_partition()
        for name, length, n in A.PARTS:
            ids = [fp for fp, minimum in best.items() if minimum == length]
            ids.sort(key=lambda fp: (A.hashlib.sha256((p[f"{name}_salt"] + "\0" + fp).encode()).hexdigest(), fp))
            self.assertEqual(p[f"{name}_ids"], ids[:n])
            self.assertEqual(p["population_counts"][str(length)], len(ids))


if __name__ == "__main__":
    unittest.main()
