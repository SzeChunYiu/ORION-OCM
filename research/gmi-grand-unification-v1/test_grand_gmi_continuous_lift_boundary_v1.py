import importlib.util
import pathlib
import unittest
from fractions import Fraction

HERE = pathlib.Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "grand_gmi_continuous_lift_boundary_checks_v1",
    HERE / "grand_gmi_continuous_lift_boundary_checks_v1.py",
)
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)


class ContinuousLiftBoundaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.aggregate = MOD.run()

    def test_terminal_and_ceiling(self):
        self.assertEqual(
            self.aggregate["terminal"],
            "GRAND_GMI_CONTINUOUS_LIFT_BOUNDARY_GREEN_AT_FINITE_SCOPE",
        )
        self.assertFalse(self.aggregate["physical_continuum_measured"])

    def test_cl1_bound_lifts_without_regularity(self):
        r = self.aggregate["lower_bound_lifts_without_regularity"]
        self.assertEqual(r["members_sampled"], 64)
        self.assertEqual(r["transported_comparisons"], 192)
        self.assertTrue(r["every_member_respects_the_bound"])
        self.assertTrue(r["lower_bound_requires_no_regularity"])

    def test_cl2_no_tightness_certificate_without_attainment(self):
        r = self.aggregate["attainment_fails_without_compactness"]
        self.assertFalse(r["infimum_attained"])
        self.assertFalse(r["tightness_certificate_available"])
        self.assertEqual(r["smallest_sampled_gap"], "1/64")
        self.assertEqual(r["smallest_deeper_gap"], "1/128")

    def test_cl3_finite_windows_overestimate(self):
        r = self.aggregate["no_finite_window_determines_the_bound"]
        self.assertEqual(
            r["window_minima"],
            {"2": "3/2", "4": "5/4", "8": "9/8", "16": "17/16", "32": "33/32"},
        )
        self.assertTrue(r["every_finite_window_strictly_overestimates"])

    def test_cl4_accounting_soundness_is_required(self):
        r = self.aggregate["accounting_soundness_still_load_bearing"]
        self.assertEqual(r["sound_cost"], "4/3")
        self.assertEqual(r["undercharged_cost"], "5/6")
        self.assertTrue(r["undercharged_accounting_breaks_the_bound"])

    def test_cl5_contract_gates_by_field(self):
        r = self.aggregate["contract_predicate_gates_each_result"]
        self.assertTrue(r["complete_contract_licenses_all_results"])
        self.assertTrue(r["empty_contract_licenses_nothing"])
        self.assertEqual(r["malformed_declarations_rejected"], 4)
        self.assertEqual(
            r["results_withheld_per_missing_field"]["measured_resource_contract"],
            ["PL2_derived_lower_bound"],
        )
        self.assertEqual(
            r["results_withheld_per_missing_field"]["attainment_witness"],
            ["PL3b_tightness_certificate"],
        )

    def test_cl5_rejects_malformed_declarations_directly(self):
        with self.assertRaises(MOD.ContractError):
            MOD.available_results({})
        with self.assertRaises(MOD.ContractError):
            MOD.available_results({name: True for name in MOD.CONTRACT_FIELDS} | {"x": True})
        full = {name: True for name in MOD.CONTRACT_FIELDS}
        self.assertTrue(all(v == "AVAILABLE" for v in MOD.available_results(full).values()))

    def test_declared_infimum_is_a_lower_bound_on_a_deeper_sample(self):
        bound = MOD.declared_infimum("open_above_one")
        self.assertEqual(bound, Fraction(1))
        for value in MOD.sample("open_above_one", 256):
            self.assertGreater(value, bound)


if __name__ == "__main__":
    unittest.main()
