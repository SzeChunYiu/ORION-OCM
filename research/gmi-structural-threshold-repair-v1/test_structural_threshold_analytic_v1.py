"""Portable scientific controls; no archive path or interpreter identity assumptions."""
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parent))
import structural_threshold_costs_v1 as costs
import structural_threshold_geometry_v1 as geometry
from structural_threshold_analytic_v1 import run
from structural_threshold_countercontrols_v1 import (bounded_output_counterexample,
    delegation_counterexample, rendering_counterexample)


class StructuralThresholdAnalyticTests(unittest.TestCase):
    def test_all_same_parity_midpoint_pairs(self):
        certificates = geometry.midpoint_certificates()
        self.assertEqual(len(certificates), 12)
        for item in certificates:
            a, b = item["same"]; c, d = item["opposite"]
            self.assertEqual(tuple(x+y for x, y in zip(a, b)), tuple(x+y for x, y in zip(c, d)))
            self.assertEqual(sum(a) % 2, sum(b) % 2)
            self.assertNotEqual(sum(a) % 2, sum(c) % 2)

    def test_dropped_cube_vertex_does_not_pass_complete_geometry(self):
        with patch.object(geometry, "INPUTS", costs.INPUTS[:-1]):
            with self.assertRaises(ValueError):
                geometry.midpoint_certificates()

    def test_two_hidden_output_classification(self):
        result = geometry.two_input_threshold_certificate()
        self.assertEqual(result["categories"],
                         {"constant": 2, "literal": 4, "one_corner": 4, "three_corners": 4})

    def test_each_parity_coordinate_is_nonunate(self):
        rows = geometry.nonunate_controls()["parity_edge_differences_each_axis"]
        self.assertEqual(len(rows), 3)
        self.assertTrue(all(set(row) == {-1, 1} for row in rows))

    def test_output_skip_is_a_load_bearing_boundary(self):
        result = geometry.nonunate_controls()
        self.assertTrue(result["one_hidden_gate_with_raw_input_skip_computes_parity"])
        self.assertFalse(result["skip_connections_inside_registered_class"])

    def test_native_contract_no_alarm(self):
        self.assertEqual(costs.native_cost_contract()["shared_unit"], 6)

    def test_native_contract_mismatch_is_unverifiable(self):
        with patch.object(costs, "compiled", return_value=(0, None, ())):
            with self.assertRaisesRegex(ValueError, "^UNVERIFIABLE:"):
                costs.native_cost_contract()

    def test_large_signed_and_extended_argument_controls(self):
        result = costs.syntax_stress_controls()
        self.assertEqual(result["signed_zero_large_support_patterns"], 124)
        self.assertTrue(result["extended_argument_control"])
        self.assertFalse(result["general_compiler_verified_by_sampling"])

    def test_unproved_gate_count_cannot_license_lower_bound(self):
        with self.assertRaisesRegex(ValueError, "active-gate"):
            costs.certified_lower("A", 2, 6)

    def test_unproved_input_incidence_cannot_license_lower_bound(self):
        with self.assertRaisesRegex(ValueError, "support-incidence"):
            costs.certified_lower("A", 3, 5)

    def test_nonintegral_or_impossible_count_register_rejects(self):
        for args in (("A", True, 6), ("A", 3, 10), ("A", 3.0, 6), ("Q", 3, 6)):
            with self.subTest(args=args), self.assertRaises(ValueError):
                costs.certified_lower(*args)

    def test_explicit_parity_witness_attains_global_lower(self):
        count, witness, _ = costs.compiled(costs.SHARED_WITNESS)
        self.assertEqual(tuple(witness(x) for x in costs.INPUTS), costs.PARITY)
        self.assertEqual(count, 39)
        self.assertEqual(costs.certified_lower("A", 3, 6), count)
        self.assertEqual(costs.certified_lower("B", 3), count)

    def test_arbitrarily_large_scaled_coefficients_are_not_grid_assumed(self):
        weight = 10**100
        source = ("def f(x):\n    a,b,c=x\n    s=" + str(weight) + "*a+"
                  + str(weight) + "*b+" + str(weight) + "*c\n"
                  + "".join("    h"+str(i)+"=int(s>="+str((i+1)*weight)+")\n" for i in range(3))
                  + "    return int(h0-h1+h2>=1)\n")
        count, witness, _ = costs.compiled(source)
        self.assertEqual(tuple(witness(x) for x in costs.INPUTS), costs.PARITY)
        self.assertGreaterEqual(count, 39)

    def test_bounded_output_grid_omits_legal_threshold(self):
        result = bounded_output_counterexample()
        self.assertEqual(result["omitted_weights"], (3, 2, 2, 1))
        self.assertFalse(result["bounded_grid_covers_arbitrary_output_coefficients"])

    def test_reordering_refutes_old_minimal_rendering_lemma(self):
        result = rendering_counterexample()
        self.assertEqual((result["fixed_order_opcodes"], result["reordered_opcodes"]), (18, 17))
        self.assertTrue(result["all8_outputs_equal"])

    def test_delegated_network_ties_delegated_xor(self):
        result = delegation_counterexample()
        self.assertEqual((result["neural_wrapper_per_sweep"], result["non_neural_wrapper_per_sweep"]), (32, 32))
        self.assertTrue(result["candidate_frame_call_opcode_included"])
        self.assertFalse(result["callee_work_included"])
        self.assertFalse(result["universal_exclusion_of_delegating_class"])

    def test_outer_code_absence_does_not_remove_python_descendants(self):
        result = delegation_counterexample()
        self.assertFalse(result["outer_callable_has_python_code"])
        self.assertTrue(result["python_descendant_is_explicitly_present"])

    def test_aggregate_keeps_complete_scope_and_countercontrols(self):
        result = run()
        self.assertEqual(result["arbitrary_coefficient_lower_bound"]["independent_finite_degree_cases"], 3251)
        self.assertEqual(result["attainment"]["minimum_per_sweep"], 312)
        self.assertFalse(result["runtime_patch_identity_claim"])
        self.assertFalse(result["timing_or_ecology_measurements"])
        self.assertIn("omitted_output_counterexample", result)
        self.assertIn("delegation_counterexample", result)


if __name__ == "__main__":
    unittest.main()
