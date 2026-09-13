import hashlib
import importlib.util
from itertools import product
import json
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("developmental_scope", HERE/"grand_gmi_developmental_underdetermination_checks_v1.py")
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)


class DevelopmentalUnderdeterminationTests(unittest.TestCase):
    def test_current_receipt_and_historical_preservation(self):
        actual = MOD.run()
        self.assertTrue(actual["all_checks_green"])
        self.assertEqual(actual, json.loads((HERE/"GRAND_GMI_DEVELOPMENTAL_UNDERDETERMINATION_RECEIPT_V2.json").read_text()))
        old = (HERE/"GRAND_GMI_DEVELOPMENTAL_UNDERDETERMINATION_RECEIPT_V1.json").read_bytes()
        self.assertEqual(hashlib.sha256(old).hexdigest(), "db68f7f5c96fddf90ba124a386421c9dd4e602e2b79537374df2e7534b397e01")

    def test_static_summaries_do_not_choose_the_development_law(self):
        rows = MOD.check_static_underdetermination()["laws"]
        self.assertEqual(rows["D1"]["support"], ["A"])
        self.assertEqual(rows["D2"]["support"], ["B"])

    def test_selected_policy_is_not_all_schedules_reachability(self):
        actual = MOD.check_schedule_scope()
        self.assertEqual(actual["all_admitted_schedules_at_most_two_steps"], [1, 2, 4, 5])
        self.assertEqual(actual["orders"]["add_three->double"], {"last_admitted": 4, "completed": False})

    def test_comparator_removal_and_positive_restoration(self):
        actual = MOD.check_retained_comparator()
        self.assertEqual(actual["B_excluded_before_removed_restored"], [True, False, True])
        self.assertEqual(actual["global_bests"], {"A": 2, "B": 5})
        self.assertEqual(actual["restricted_bests"], {"A": 9, "B": 5})

    def test_tied_or_same_family_comparator_is_insufficient(self):
        p, f = {"a": 5, "b": 5}, {"a": "A", "b": "B"}
        self.assertFalse(MOD.exclusion(p, f, set(p), "B", 5, "a"))
        self.assertFalse(MOD.exclusion(p, f, set(p), "B", 5, "b"))
        with self.assertRaises(ValueError):
            MOD.exclusion(p, f, set(p), "B", 6, "a")

    def test_finite_positive_closure_and_adverse_extension(self):
        row = MOD.check_prefix_and_closure()
        self.assertEqual(row["closed_limit_support"], ["A"])
        self.assertEqual(row["extended_limit_support"], ["B"])
        self.assertTrue(row["closed_certificate_accepted"])
        self.assertTrue(row["incomplete_certificate_rejected"])
        self.assertTrue(row["strict_improvement_and_family_change_do_not_force_branching_verdict_flip"])

    def test_certificate_rejects_nonpaths_and_missing_initial_or_successors(self):
        edges = {0: (1,), 1: (2,), 2: ()}
        valid = {0: (0,), 1: (0, 1), 2: (0, 1, 2)}
        self.assertTrue(MOD.closure_certificate(edges, 0, valid))
        for bad in ({}, {1: (0, 1), 2: (0, 1, 2)}, {0: (0,), 1: (0, 1)}):
            self.assertFalse(MOD.closure_certificate(edges, 0, bad))
        for path in ((), (1, 2), (0, 2), (0, 1)):
            bad = dict(valid)
            bad[2] = path
            self.assertFalse(MOD.closure_certificate(edges, 0, bad))
        self.assertFalse(MOD.closure_certificate(edges, 0, valid | {3: (0, 3)}))

    def test_all_512_three_state_graphs_against_independent_transitive_closure(self):
        states = tuple(range(3))
        for mask in range(1 << 9):
            edges = {i: tuple(j for j in states if mask >> (3*i+j) & 1) for i in states}
            matrix = [[i == j or j in edges[i] for j in states] for i in states]
            for middle in states:
                for i in states:
                    for j in states:
                        matrix[i][j] |= matrix[i][middle] and matrix[middle][j]
            expected = {j for j in states if matrix[0][j]}
            self.assertEqual(MOD.reach(edges, 0, 2), expected)
            paths = {}
            for length in range(3):
                for tail in product(states, repeat=length):
                    path = (0,)+tail
                    if all(v in edges[u] for u, v in zip(path, path[1:])):
                        paths.setdefault(path[-1], path)
            self.assertEqual(set(paths), expected)
            self.assertTrue(MOD.closure_certificate(edges, 0, paths))
            self.assertEqual(MOD.reach(edges, 0, 3), expected)

    def test_invalid_domains_and_empty_family_support(self):
        for budget in (-1, True, 1.5):
            with self.assertRaises(ValueError):
                MOD.reach({0: ()}, 0, budget)
        with self.assertRaises(ValueError):
            MOD.reach({0: ()}, 1, 0)
        for value in (-1, True, float("nan")):
            with self.assertRaises(ValueError):
                MOD.best_by_family({0: value}, {0: "A"}, {0})
        self.assertEqual(MOD.support({}), ())
        self.assertEqual(MOD.reach({0: ()}, 0, 0), {0})


if __name__ == "__main__":
    unittest.main()
