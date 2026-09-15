from __future__ import annotations

from fractions import Fraction as F
import importlib.util
from pathlib import Path
import sys
import unittest

MODULE_PATH = Path(__file__).with_name("useful_descendant_v1.py")
spec = importlib.util.spec_from_file_location("useful_descendant_v1", MODULE_PATH)
mod = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = mod
spec.loader.exec_module(mod)


class UsefulDescendantTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.receipt = mod.build_receipt()

    def test_space_and_kernel_normalization(self):
        self.assertEqual(len(mod.SPACE), 64)
        self.assertIn(mod.CURRENT_OBJECT, mod.SPACE)
        for name, ps in mod.KERNELS.items():
            dist = mod.distribution(ps)
            self.assertEqual(len(dist), 64)
            self.assertEqual(sum((mass for _, mass in dist), F(0)), 1, name)
            self.assertEqual(self.receipt["kernel_normalization"][name], "1")

    def test_all_frozen_mass_predictions_exact(self):
        for held, expected_by_kernel in mod.EXPECTED.items():
            for kernel, expected in expected_by_kernel.items():
                enum = mod.useful_mass_enum(mod.KERNELS[kernel], mod.CONJUNCTIONS[held])
                closed = mod.useful_mass_closed(mod.KERNELS[kernel], mod.CONJUNCTIONS[held])
                self.assertEqual(enum, expected)
                self.assertEqual(closed, expected)
                self.assertEqual(self.receipt["held_tasks"][held][kernel]["useful_mass_enum"], mod.frac(expected))
                self.assertEqual(self.receipt["held_tasks"][held][kernel]["useful_mass_closed_form"], mod.frac(expected))

    def test_first_hit_burdens(self):
        expected = {
            "U_AND": {"RESET": "4", "CONTINUED": "16/9", "SHUFFLED_HISTORY": "4"},
            "U_ANTI": {"RESET": "4", "CONTINUED": "16", "SHUFFLED_HISTORY": "4"},
            "U_45": {"RESET": "4", "CONTINUED": "4", "SHUFFLED_HISTORY": "16/9"},
        }
        for held, by_kernel in expected.items():
            for kernel, burden in by_kernel.items():
                self.assertEqual(self.receipt["held_tasks"][held][kernel]["expected_iid_proposals_to_first_useful"], burden)

    def test_positive_and_negative_transfer_orderings(self):
        self.assertGreater(mod.EXPECTED["U_AND"]["CONTINUED"], mod.EXPECTED["U_AND"]["RESET"])
        self.assertEqual(mod.EXPECTED["U_AND"]["RESET"], mod.EXPECTED["U_AND"]["SHUFFLED_HISTORY"])
        self.assertLess(mod.EXPECTED["U_ANTI"]["CONTINUED"], mod.EXPECTED["U_ANTI"]["RESET"])
        self.assertEqual(mod.EXPECTED["U_ANTI"]["RESET"], mod.EXPECTED["U_ANTI"]["SHUFFLED_HISTORY"])
        self.assertGreater(mod.EXPECTED["U_45"]["SHUFFLED_HISTORY"], mod.EXPECTED["U_45"]["CONTINUED"])
        self.assertEqual(mod.EXPECTED["U_45"]["CONTINUED"], mod.EXPECTED["U_45"]["RESET"])
        self.assertTrue(self.receipt["negative_transfer_observed"])

    def test_held_tasks_are_not_developmental_tasks(self):
        matrix = self.receipt["held_history_nonidentity"]
        for held in ("U_AND", "U_ANTI", "U_45"):
            self.assertTrue(matrix[held]["H0"])
            self.assertTrue(matrix[held]["H1"])
            self.assertNotEqual(mod.truth_table(mod.CONJUNCTIONS[held]), mod.truth_table(mod.CONJUNCTIONS["H0"]))
            self.assertNotEqual(mod.truth_table(mod.CONJUNCTIONS[held]), mod.truth_table(mod.CONJUNCTIONS["H1"]))

    def test_semantic_remint_preserves_concentration(self):
        row = self.receipt["semantic_remint_control"]
        self.assertTrue(row["same_coordinate_parameter_multiset"])
        self.assertTrue(row["same_symbolic_shannon_entropy"])
        self.assertTrue(row["same_sorted_64_point_mass_multiset"])
        self.assertEqual(
            mod.symbolic_entropy_signature(mod.KERNELS["CONTINUED"]),
            mod.symbolic_entropy_signature(mod.KERNELS["SHUFFLED_HISTORY"]),
        )
        self.assertEqual(
            mod.sorted_mass_signature(mod.KERNELS["CONTINUED"]),
            mod.sorted_mass_signature(mod.KERNELS["SHUFFLED_HISTORY"]),
        )

    def test_zero_useful_mass_fails_closed(self):
        self.assertEqual(self.receipt["zero_mass_hostile"]["useful_mass"], "0")
        self.assertEqual(self.receipt["zero_mass_hostile"]["first_hit_burden"], mod.ZERO_TERMINAL)
        self.assertEqual(mod.first_hit_burden(F(0)), mod.ZERO_TERMINAL)

    def test_common_state_contract(self):
        row = self.receipt["registered_common_state"]
        self.assertEqual(row["current_object"], [0,0,0,0,0,0])
        self.assertEqual(row["descendant_space_size"], 64)
        self.assertTrue(row["same_current_object_across_arms"])
        self.assertTrue(row["same_descendant_space_across_arms"])
        self.assertTrue(row["same_admissibility_across_arms"])
        self.assertTrue(row["same_membership_verifier_per_held_task"])

    def test_invalid_inputs_fail_closed(self):
        with self.assertRaises(ValueError):
            mod.point_mass((0,1), mod.KERNELS["RESET"])
        with self.assertRaises(ValueError):
            mod.point_mass((0,0,0,0,0,2), mod.KERNELS["RESET"])
        with self.assertRaises(ValueError):
            mod.first_hit_burden(F(-1,2))
        with self.assertRaises(ValueError):
            mod.first_hit_burden(F(3,2))

    def test_claim_boundary(self):
        self.assertEqual(self.receipt["claim_ceiling"], mod.CLAIM)
        self.assertIn("CONTINUED_DEVELOPMENT_ALWAYS_BETTER", self.receipt["forbidden_claims"])
        self.assertIn("OPEN_ENDED_EVOLUTION_PROVED", self.receipt["forbidden_claims"])
        self.assertIn("COMPLETE_GMI", self.receipt["forbidden_claims"])


if __name__ == "__main__":
    unittest.main()
