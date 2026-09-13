"""Falsification controls for the labelled-partition reconstruction register."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from fractions import Fraction as F
import json
import math
import subprocess
import unittest
from grand_gmi_query_partition_model_v1 import canonical, optimize, pointwise_frontier, feasible, execute, pareto
from grand_gmi_query_partition_oracle_v1 import oracle, partitions, shapes
from grand_gmi_query_partition_checks_v1 import check_instance


class QueryPartitionTests(unittest.TestCase):
    def test_complete_partitions_and_syntax_have_independent_known_counts(self):
        self.assertEqual([sum(1 for _ in partitions(1 << n)) for n in range(4)], [1, 2, 15, 4140])
        self.assertEqual([len(shapes(tuple(range(n)))) for n in range(4)], [1, 2, 9, 244])

    def test_weighted_full_four_input_partition_oracle(self):
        for table in partitions(4):
            check_instance(table, (F(2, 3), F(7, 4)), (F(1, 10), F(2, 10), F(3, 10), F(4, 10)))

    def test_output_relabelling_transports_actual_leaf_outputs_and_work(self):
        table = (17, 17, 29, 29, 17, 29, 17, 29)
        result = optimize(table, (1, 2, 3))
        def rename(tree):
            return ("leaf", (17, 29)[tree[1]]) if tree[0] == "leaf" else (tree[0], rename(tree[1]), rename(tree[2]))
        transported = rename(result["mean_tree"])
        for x in range(8):
            before = execute(result["mean_tree"], x, 3, (1, 2, 3))
            after = execute(transported, x, 3, (1, 2, 3))
            self.assertEqual(after, (table[x], before[1]))

    def test_noninjective_relabelling_can_remove_query_obligations(self):
        self.assertEqual(optimize((0, 1, 1, 0))["worst"], 2)
        self.assertEqual(optimize((7, 7, 7, 7))["worst"], 0)

    def test_unlabelled_blocks_do_not_preserve_coordinate_geometry(self):
        projection, parity = (0, 1, 0, 1), (0, 1, 1, 0)
        self.assertEqual(sorted(projection), sorted(parity))
        self.assertNotEqual(canonical(projection), canonical(parity))
        self.assertEqual((optimize(projection)["worst"], optimize(parity)["worst"]), (1, 2))
        self.assertEqual(optimize((0, 0, 1, 1), (1, 3))["worst"], 3)
        self.assertEqual(optimize(projection, (1, 3))["worst"], 1)

    def test_selector_joint_frontier_rejects_separate_minima_and_revives(self):
        table = (0, 0, 1, 1, 0, 1, 0, 1)
        prior = tuple(F(x, 15) for x in (1, 1, 1, 1, 1, 1, 1, 8))
        front = pointwise_frontier(table, (1, 2, 3))["frontier"]
        self.assertEqual(front, oracle(table, (1, 2, 3))["frontier"])
        joint = pareto((sum(p*c for p, c in zip(prior, v)), max(v)) for v in front)
        self.assertEqual(joint, {(F(19, 5), F(6)), (F(64, 15), F(5))})
        self.assertFalse(feasible(front, prior, F(19, 5), 5))
        self.assertTrue(feasible(front, prior, F(64, 15), 5))
        self.assertTrue(feasible(front, prior, F(19, 5), 6))

    def test_zero_mass_does_not_remove_correctness_on_other_inputs(self):
        result = optimize((0, 1, 1, 0), prior=(1, 0, 0, 0))
        self.assertEqual(result["mean"], 2)
        self.assertEqual(tuple(execute(result["mean_tree"], x, 2, (1, 1))[0] for x in range(4)), (0, 1, 1, 0))

    def test_prior_and_query_cost_are_essential_registers(self):
        table = (0, 1, 1, 1)
        self.assertEqual(optimize(table)["mean"], F(3, 2))
        self.assertEqual(optimize(table, (1, 3))["mean"], F(5, 2))
        self.assertEqual(optimize(table, prior=(0, 0, 0, 1))["mean"], 1)
        self.assertEqual(optimize(table, prior=(1, 0, 0, 0))["mean"], 2)

    def test_changed_primitive_changes_optimum_for_same_partition(self):
        table = (0, 1, 1, 0)
        parity_query = tuple(((x & 1) ^ ((x >> 1) & 1)) for x in range(4))
        self.assertEqual(table, parity_query)
        self.assertGreater(len(set(table)), 1)  # Zero probes cannot decide it.
        for answer in (0, 1):
            self.assertEqual({table[x] for x in range(4) if parity_query[x] == answer}, {answer})
        self.assertEqual(optimize(table)["worst"], 2)  # One registered parity probe suffices instead.

    def test_set_equality_partition_does_not_supply_joint_success(self):
        shared = ({"a", "b"}, {"b", "c"})
        separate = ({"a"}, {"c"})
        self.assertNotEqual(shared[0], shared[1])
        self.assertNotEqual(separate[0], separate[1])
        self.assertEqual(set.intersection(*shared), {"b"})
        self.assertEqual(set.intersection(*separate), set())
        triple = ({"a", "b"}, {"b", "c"}, {"a", "c"})
        self.assertTrue(all(triple[i] & triple[j] for i in range(3) for j in range(i)))
        self.assertEqual(set.intersection(*triple), set())

    def test_zero_dimension_free_queries_and_empty_feasible_set(self):
        self.assertEqual(optimize((9,))["mean"], 0)
        result = pointwise_frontier((0, 1, 1, 0), (0, 0))
        self.assertEqual(result["frontier"], {(F(0),)*4})
        self.assertFalse(feasible((), (1,), 0, 0))

    def test_development_categories_obey_registered_bounds(self):
        for n in range(4):
            result = optimize(tuple(x.bit_count() % 2 for x in range(1 << n)))
            count = result["development"]
            self.assertLessEqual(count["states"], 3**n)
            self.assertLessEqual(count["membership_tests"], 6**n)
            self.assertLessEqual(count["output_table_reads"], 4**n)
            self.assertLessEqual(count["candidate_queries"], n*3**(n-1) if n else 0)

    def test_malformed_and_infinite_registers_rejected(self):
        for table in ((), (0, 1, 2), (False,), (-1,)):
            with self.assertRaises(ValueError):
                optimize(table)
        for cost in (math.inf, math.nan, True, -1, 0.5):
            with self.assertRaises(ValueError):
                optimize((0, 1), (cost,))
            with self.assertRaises(ValueError):
                feasible(((F(0),),), (1,), cost, 1)
        with self.assertRaises(ValueError):
            optimize((0, 1), prior=(1, 1))
        with self.assertRaises(ValueError):
            feasible(((-1,),), (1,), 0, 0)

    def test_isolated_standalone_replay(self):
        script = Path(__file__).with_name("grand_gmi_query_partition_checks_v1.py")
        result = subprocess.run([sys.executable, "-I", "-B", str(script)], check=True, capture_output=True, text=True)
        receipt = json.loads(result.stdout)
        self.assertTrue(receipt["all_checks_green"])
        self.assertEqual(receipt["oracle"]["all_labelled_partitions"], 4158)


if __name__ == "__main__":
    unittest.main()
