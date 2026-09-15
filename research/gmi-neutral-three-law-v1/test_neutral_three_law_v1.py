from __future__ import annotations

from fractions import Fraction as F
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

MODULE_PATH = Path(__file__).with_name("neutral_three_law_v1.py")
spec = importlib.util.spec_from_file_location("neutral_three_law_v1", MODULE_PATH)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class NeutralThreeLawTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.targets = mod.load_targets()
        cls.search = mod.search_semantics()
        cls.receipt = mod.build_receipt()

    def test_frozen_hashes_and_target_custody(self):
        self.assertEqual(mod.verify_universe(), mod.UNIVERSE_SHA)
        self.assertEqual({oid for oid, _ in self.targets}, set(mod.TARGET_OBJECT_SHA))
        raw = json.loads(mod.TARGETS_PATH.read_text())
        for obj in raw["targets"]:
            self.assertEqual(mod.compact_sha(obj), mod.TARGET_OBJECT_SHA[obj["opaque_id"]])

    def test_exact_quotient_counts(self):
        self.assertEqual(
            self.receipt["quotient"]["new_semantic_tables_by_cost"],
            {"1": 7, "2": 6, "3": 60, "4": 128, "5": 650, "6": 1834},
        )
        self.assertEqual(self.receipt["quotient"]["total_semantic_tables"], 2685)

    def test_minimum_cost_recoveries(self):
        rows = {row["opaque_id"]: row for row in self.receipt["recoveries"]}
        for opaque_id, expected in mod.EXPECTED_COST.items():
            self.assertTrue(rows[opaque_id]["matched"])
            self.assertEqual(rows[opaque_id]["min_cost"], expected)
        self.assertEqual(rows["opaque_1"]["canonical_expression"], "half((w+y))")
        self.assertEqual(rows["opaque_2"]["canonical_expression"], "((half(x)*y)+w)")
        self.assertEqual(rows["opaque_3"]["canonical_expression"], "((half(r)*x)+w)")

    def test_dependency_signatures_and_invariance(self):
        rows = {row["opaque_id"]: row for row in self.receipt["recoveries"]}
        for opaque_id, expected in mod.EXPECTED_SIG.items():
            self.assertEqual(tuple(rows[opaque_id]["dependency_signature"]), expected)
            self.assertTrue(all(rows[opaque_id]["nonrequired_invariance"].values()))
            for name in expected:
                witness = rows[opaque_id]["dependency_witnesses"][name]
                a, b = witness["row_a"], witness["row_b"]
                changed = [i for i, (x, y) in enumerate(zip(a, b)) if x != y]
                self.assertEqual(changed, [mod.AXES.index(name)])
                self.assertNotEqual(witness["out_a"], witness["out_b"])

    def test_required_variable_ablations_fail(self):
        for variable, affected in self.receipt["required_variable_ablations"].items():
            for row in affected:
                self.assertIn(variable, mod.EXPECTED_SIG[row["opaque_id"]])
                self.assertFalse(row["matched_through_cap"])

    def test_half_is_load_bearing(self):
        for row in self.receipt["remove_half"].values():
            self.assertTrue(row["has_noninteger_output"])
            self.assertFalse(row["matched_through_cap"])

    def test_perturbed_table_is_not_recovered(self):
        self.assertFalse(self.receipt["perturbed_target"]["matched_through_cap"])
        self.assertEqual(
            self.receipt["perturbed_target"]["table_sha256"],
            "dbeca315479bb6d3b18b381b9fa1ec2f6221e22b9494c76eced4419ff5886766",
        )

    def test_equivalent_syntax_quotients_to_lower_cost(self):
        row = self.receipt["equivalent_syntax"]
        self.assertTrue(row["same_table"])
        self.assertEqual(row["lower_cost"], 4)
        self.assertEqual(row["higher_cost"], 5)
        self.assertEqual(row["quotient_min_cost"], 4)

    def test_opaque_id_order_invariant_and_protocol_locked(self):
        self.assertTrue(self.receipt["opaque_id_permutation_invariant"])
        self.assertTrue(self.receipt["post_activation_mutation_rejected"])
        protocol = mod.ActivatedProtocol()
        protocol.activate()
        with self.assertRaises(RuntimeError):
            protocol.mutate(cap=5)

    def test_independent_raw_syntax_through_cost_three_is_covered(self):
        # Independent tiny raw-syntax enumerator: it deliberately does not quotient.
        rows = mod.universe()
        raw = {1: []}
        for c in (-1, 0, 1):
            raw[1].append((tuple(F(c) for _ in rows), str(c)))
        for j, name in enumerate(mod.AXES):
            raw[1].append((tuple(F(row[j]) for row in rows), name))
        raw[2] = [(tuple(v / F(2) for v in table), f"half({expr})") for table, expr in raw[1]]
        raw[3] = [(tuple(v / F(2) for v in table), f"half({expr})") for table, expr in raw[2]]
        for left, left_expr in raw[1]:
            for right, right_expr in raw[1]:
                raw[3].extend(
                    [
                        (tuple(a + b for a, b in zip(left, right)), f"({left_expr}+{right_expr})"),
                        (tuple(a - b for a, b in zip(left, right)), f"({left_expr}-{right_expr})"),
                        (tuple(a * b for a, b in zip(left, right)), f"({left_expr}*{right_expr})"),
                    ]
                )
        for cost in (1, 2, 3):
            for table, _expr in raw[cost]:
                self.assertIn(table, self.search.best_cost)
                self.assertLessEqual(self.search.best_cost[table], cost)

    def test_malformed_target_fails_closed(self):
        raw = json.loads(mod.TARGETS_PATH.read_text())
        raw["targets"][0]["outputs"][0] = "999"
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bad.json"
            path.write_text(json.dumps(raw))
            with self.assertRaises(ValueError):
                mod.load_targets(path)

    def test_invalid_search_protocol_fails_closed(self):
        with self.assertRaises(ValueError):
            mod.search_semantics(cap=0)
        with self.assertRaises(ValueError):
            mod.search_semantics(allowed_vars=("w", "w"))
        with self.assertRaises(ValueError):
            mod.search_semantics(allowed_vars=("w", "bad"))
        with self.assertRaises(ValueError):
            mod.search_semantics(allow_half=1)

    def test_claim_boundary_is_explicit(self):
        self.assertEqual(self.receipt["claim_ceiling"], mod.CLAIM)
        self.assertIn("CROSS_GRAMMAR_REPLICATION", self.receipt["forbidden_claims"])
        self.assertIn("COMPLETE_GMI", self.receipt["forbidden_claims"])


if __name__ == "__main__":
    unittest.main()
