import importlib.util
import json
import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("capability_interactions_v3", ROOT / "capability_interactions_v3.py")
mod = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = mod
assert SPEC.loader is not None
SPEC.loader.exec_module(mod)


class RegistryTests(unittest.TestCase):
    def setUp(self):
        self.registry = json.loads((ROOT / "INTERACTIONS_TRANCHE3_V1.json").read_text())

    def test_exact_two_cross_cutting_rows(self):
        self.assertEqual(2, len(self.registry["rows"]))
        self.assertEqual(
            {
                "Identify superadditive thresholds where capabilities appear only jointly.",
                "Identify interference cases where adding one component harms another.",
            },
            {row["ledger_row"] for row in self.registry["rows"]},
        )

    def test_required_claim_fields(self):
        for row in self.registry["rows"]:
            for field in (
                "scope", "assumptions", "theorem", "strongest_parent",
                "negative_twin", "nearest_counterexample", "falsifier", "status",
            ):
                self.assertTrue(row[field], (row["id"], field))
        self.assertEqual("G2", self.registry["claim_ceiling"])
        self.assertIn("does not establish G6", self.registry["claim_boundary"])


class SuperadditivityTests(unittest.TestCase):
    def test_joint_only_witness(self):
        self.assertTrue(mod.joint_only_emergence(a0=1, a1=2, b0=1, b1=2, threshold=4))
        self.assertEqual(1, mod.discrete_interaction_indicator(a0=1, a1=2, b0=1, b1=2, threshold=4))

    def test_negative_twin_removes_joint_only_emergence(self):
        self.assertFalse(mod.joint_only_emergence(a0=1, a1=2, b0=1, b1=2, threshold=2))

    def test_exhaustive_predicate_equivalence(self):
        for a0 in range(1, 4):
            for a1 in range(a0, 5):
                for b0 in range(1, 4):
                    for b1 in range(b0, 5):
                        for threshold in range(1, 17):
                            expected = (
                                a0 * b0 < threshold
                                and a1 * b0 < threshold
                                and a0 * b1 < threshold
                                and a1 * b1 >= threshold
                            )
                            self.assertEqual(
                                expected,
                                mod.joint_only_emergence(
                                    a0=a0, a1=a1, b0=b0, b1=b1, threshold=threshold
                                ),
                            )

    def test_invalid_downgrade_refused(self):
        with self.assertRaises(ValueError):
            mod.joint_only_emergence(a0=2, a1=1, b0=1, b1=2, threshold=4)


class InterferenceTests(unittest.TestCase):
    def test_frozen_budget_interference_witness(self):
        self.assertTrue(mod.capability_a_success(total_budget=2, required_budget=2))
        self.assertFalse(
            mod.capability_a_success(total_budget=2, required_budget=2, mandatory_other_cost=1)
        )
        self.assertTrue(mod.interference_occurs(total_budget=2, required_budget=2, mandatory_other_cost=1))

    def test_budget_restoration_negative_twin(self):
        self.assertTrue(mod.capability_a_success(total_budget=3, required_budget=2))
        self.assertTrue(
            mod.capability_a_success(total_budget=3, required_budget=2, mandatory_other_cost=1)
        )
        self.assertFalse(mod.interference_occurs(total_budget=3, required_budget=2, mandatory_other_cost=1))

    def test_exhaustive_interference_equivalence(self):
        for total in range(0, 7):
            for required in range(1, 7):
                for cost in range(0, 7):
                    expected = total >= required and total - cost < required
                    self.assertEqual(
                        expected,
                        mod.interference_occurs(
                            total_budget=total,
                            required_budget=required,
                            mandatory_other_cost=cost,
                        ),
                    )

    def test_zero_cost_never_harms(self):
        for total in range(0, 7):
            for required in range(1, 7):
                self.assertFalse(
                    mod.interference_occurs(
                        total_budget=total,
                        required_budget=required,
                        mandatory_other_cost=0,
                    )
                )

    def test_free_optional_extension_monotonicity(self):
        old_sets = ((0.0,), (1.0, 3.0), (-5.0, -2.0, -9.0))
        additions = ((), (2.0,), (100.0, -100.0))
        for old in old_sets:
            old_optimum = max(old)
            for new in additions:
                self.assertGreaterEqual(mod.optional_extension_optimum(old, new), old_optimum)

    def test_empty_old_feasible_set_refused(self):
        with self.assertRaises(ValueError):
            mod.optional_extension_optimum((), (1.0,))


if __name__ == "__main__":
    unittest.main()
