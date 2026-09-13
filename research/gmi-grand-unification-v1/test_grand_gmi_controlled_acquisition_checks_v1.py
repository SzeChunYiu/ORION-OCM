import importlib.util
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent
TARGET = HERE / "grand_gmi_controlled_acquisition_checks_v1.py"
SPEC = importlib.util.spec_from_file_location("controlled_acquisition", TARGET)
MOD = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MOD)


class ControlledAcquisitionChecks(unittest.TestCase):
    def test_destructive_probe_breaks_world_only_state(self):
        r = MOD.destructive_probe_counterexample()
        self.assertTrue(r["same_world_support"])
        self.assertEqual(r["fresh_value"], 1)
        self.assertEqual(r["burned_value"], "INF")

    def test_control_can_create_compatibility_without_learning_world(self):
        r = MOD.control_to_compatibility_witness()
        self.assertEqual(r["world_support_before"], r["world_support_after"])
        self.assertFalse(r["terminal_before"])
        self.assertTrue(r["terminal_after"])
        self.assertEqual(r["value"], 1)

    def test_budget_is_load_bearing_state(self):
        r = MOD.budget_augmentation_witness()
        self.assertEqual(r["remaining_budget_0"], "INF")
        self.assertEqual(r["remaining_budget_1"], 1)

    def test_exhaustive_pair_state_equals_history_policy(self):
        r = MOD.exhaustive_pair_vs_history()
        self.assertEqual(r["kernels_checked"], 390625)
        self.assertEqual(r["mismatches"], 0)
        self.assertEqual(r["value_counts"], {"1": 210000, "2": 60944, "INF": 119681})


if __name__ == "__main__":
    unittest.main()
