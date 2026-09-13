import json
from fractions import Fraction as F
from pathlib import Path
import subprocess
import sys
import unittest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from relational_query_model_v1 import Problem, feasible, joint, synthesize
from relational_query_oracle_v1 import (equality_partition, execute_constructed,
                                      graph_gamma, oracle, pair_graph)
from grand_gmi_relational_query_checks_v1 import compare, run, witnesses


class RelationalQueryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.receipt = run()

    def test_full_census_matches_independent_oracle(self):
        self.assertEqual(self.receipt["census"]["instances"], 4168)
        self.assertEqual(self.receipt["census"]["syntax_obligation_checks"], 37000)
        self.assertEqual(self.receipt["census"]["infeasible_instances"], 1711)

    def test_equal_gamma_groups_have_identical_full_profiles(self):
        self.assertEqual(self.receipt["distinct_gamma_groups"], 55)

    def test_interval_positive_repair_census(self):
        self.assertEqual(self.receipt["interval_instances"], 1296)
        self.assertEqual(self.receipt["interval_pair_graph_groups"], 60)

    def test_combined_cheap_summaries_still_fail(self):
        r, s = (3, 6, 13, 3), (3, 5, 11, 3)
        self.assertEqual(pair_graph(r), pair_graph(s))
        self.assertEqual(equality_partition(r), equality_partition(s))
        self.assertEqual([a.bit_count() for a in r], [a.bit_count() for a in s])
        self.assertNotEqual(synthesize(Problem(r, 4, (1, 1)))["gamma"], graph_gamma(r, 2))
        self.assertEqual(witnesses()["summary_collision"],
                         {"R_mean_worst": ["1", "1"], "S_mean_worst": ["0", "0"]})

    def test_gamma_strictly_coarser_than_relation(self):
        a = synthesize(Problem((3, 5, 11, 3), 4, (1, 2)))
        b = synthesize(Problem((1, 1, 1, 1), 4, (1, 2)))
        self.assertEqual(a["gamma"], b["gamma"])
        self.assertEqual(set(a["profiles"]), set(b["profiles"]))

    def test_gratuitous_queries_are_in_complete_profile_set(self):
        result, _ = compare(Problem((3, 3), 2, (1,)))
        self.assertEqual(set(result["profiles"]), {(F(0), F(0)), (F(1), F(1))})

    def test_empty_row_prevents_all_input_success(self):
        result, _ = compare(Problem((1, 1, 1, 0), 1, (0, 0)))
        self.assertFalse(result["profiles"])
        self.assertFalse(feasible(result["profiles"], (1, 0, 0, 0), 0, 0))

    def test_zero_dimensional_boundary(self):
        yes, _ = compare(Problem((1,), 1, ()))
        no, _ = compare(Problem((0,), 1, ()))
        self.assertEqual(set(yes["profiles"]), {(F(0),)})
        self.assertFalse(no["profiles"])

    def test_zero_mass_does_not_erase_parity_obligations(self):
        result, _ = compare(Problem((1, 2, 2, 1), 2, (1, 1)))
        self.assertEqual(joint(result["profiles"], (1, 0, 0, 0)), {(F(2), F(2))})

    def test_zero_cost_does_not_mean_zero_query(self):
        result, _ = compare(Problem((1, 2), 2, (0,)))
        self.assertFalse(result["gamma"][0])
        self.assertEqual(set(result["profiles"]), {(F(0), F(0))})
        tree = next(iter(result["profiles"].values()))
        self.assertEqual(tree[0], "ask")

    def test_ambiguous_joint_frontier_and_shared_policy(self):
        self.assertEqual(self.receipt["witnesses"]["ambiguous_selector_frontier"],
                         [["19/5", "6"], ["64/15", "5"]])
        self.assertEqual(self.receipt["witnesses"]["selector_admitted_shapes"], 57)

    def test_private_output_identification_overcharges(self):
        relation = Problem(tuple(1 << (x+2) for x in range(8)), 10, (1, 2, 3))
        result, _ = compare(relation)
        self.assertEqual(set(result["profiles"]), {(F(6),)*8})

    def test_false_constant_action_is_executably_wrong(self):
        action, cost = execute_constructed(("emit", 0), 1, (1, 1))
        self.assertEqual(cost, 0)
        self.assertFalse((3, 6, 13, 3)[1] & (1 << action))

    def test_changed_query_costs_change_optima(self):
        for cost in (1, 3):
            result, _ = compare(Problem((3, 6, 13, 3), 4, (cost, cost)))
            self.assertEqual(joint(result["profiles"], (F(1, 4),)*4), {(F(cost), F(cost))})

    def test_no_infinite_resource_allowance(self):
        with self.assertRaises(ValueError):
            feasible({(F(0),)}, (1,), float("inf"), 0)
        with self.assertRaises(ValueError):
            Problem((1, 1), 1, (float("inf"),))

    def test_invalid_relation_and_prior_rejected(self):
        with self.assertRaises(ValueError):
            Problem((1, 4), 2, (1,))
        with self.assertRaises(ValueError):
            joint({(F(0), F(0))}, (1, 1))

    def test_receipt_matches_exact_current_run(self):
        self.assertEqual(self.receipt, json.loads((HERE / "GRAND_GMI_RELATIONAL_QUERY_RECEIPT_V1.json").read_text()))

    def test_standalone_isolated_checker_receipt(self):
        result = subprocess.run([sys.executable, "-I", "-B", str(HERE / "grand_gmi_relational_query_checks_v1.py")],
                                capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, (HERE / "GRAND_GMI_RELATIONAL_QUERY_RECEIPT_V1.json").read_text())


if __name__ == "__main__":
    unittest.main()
