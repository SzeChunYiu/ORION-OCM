from fractions import Fraction as F
import copy
import unittest
from grid_v1 import baseline, paired_loss, scan_loss, targets
from joint_law_v1 import achieved, constant_upper, controls, sandwich
from record_audit_v1 import audit, load
from check_v1 import band_census, late_controls, source_check


class NicheTests(unittest.TestCase):
    def test_actual_record_no_alarm_all108(self):
        a = audit(load())
        self.assertEqual(a["cell_count"], 108)
        self.assertEqual(a["counts"]["program_search"], 11)
        self.assertEqual(a["counts"]["hamming_knn_k3"], 3)
        self.assertEqual(a["threshold_only_counts"]["gradient_net_h2"], 1)
        self.assertFalse(a["N4_strict"])
        self.assertTrue(a["N4_noninversion"])

    def test_actual_missing_cell_and_margin_and_flag_rejected(self):
        for field in ("margin", "flag", "missing"):
            p = load()
            if field == "margin":
                p["results"]["E_niche1"]["rows"]["program_search"]["margin_fx"] += 1
            elif field == "flag":
                p["results"]["E_niche1"]["rows"]["program_search"]["admissible"] = False
            else:
                del p["results"]["E_niche1"]["rows"]["program_search"]
            with self.subTest(field=field), self.assertRaises(ValueError):
                audit(p)

    def test_actual_seed_or_current_label_substitution_rejected(self):
        p = load()
        p["seed"] += 1
        with self.assertRaises(ValueError):
            audit(p)
        p = load()
        p["interventions"][-1] += "_v2"
        with self.assertRaises(ValueError):
            audit(p)

    def test_actual_baseline_and_grid_source_controls(self):
        p = load()
        p["ecologies"]["E_niche1"][0] += F(1, 100)
        with self.assertRaises(ValueError):
            audit(p)
        self.assertEqual(source_check(), 18)
        self.assertEqual(targets((8, -8, 3, 0), (1, 2, 4, 8)), (8, -8, 3, 0))

    def test_actual_conditional_unrounded_boundary_is_separate(self):
        a = audit(load())
        self.assertEqual(a["conditional_unrounded_changes"],
                         [["E_niche12", "compiled_search", False, True, "1/24"],
                          ["E_niche12", "program_search", False, True, "1/24"]])
        self.assertEqual(a["counts"]["program_search"], 11)
        self.assertEqual(a["conditional_unrounded_gate_counts"]["program_search"], 12)

    def test_reported_mean_cannot_be_uniform_ceiling(self):
        p = load()
        s = p["results"]["E_niche8"]["rows"]["gradient_net_h2"]["min_over_six"]
        b = p["results"]["E_niche8"]["best_constant"]
        self.assertGreater(s, F(17, 20))
        with self.assertRaises(ValueError):
            constant_upper([(F(1), b, s)], F("0.6788"))

    def test_attained_and_unattained_upper_controls(self):
        c = controls()
        self.assertEqual(c["constant_attained_equality"], ["1/2", "1/2"])
        self.assertEqual(c["ceiling_only_counterexample"], ["0", "1/2"])

    def test_same_marginals_do_not_determine_joint_frequency(self):
        self.assertEqual(controls()["same_marginals_different_joint_frequency"], ["1", "1/2"])

    def test_sharp_bands_and_bad_mass(self):
        c = controls()
        self.assertEqual(c["sharp_lower"], ["1/2", "1/2", "1"])
        self.assertEqual(c["sharp_upper"], ["1", "1/2", "1"])
        self.assertEqual(c["below_theta_except_bad_mass"], ["1/4", "0", "1/4"])

    def test_threshold_equality_and_missing_approximation_refused(self):
        atoms = [(F(1), F(0), F(1, 2))]
        self.assertEqual(sandwich(atoms, F(0), F(1, 2), theta=F(1, 2)), (0, 1))
        self.assertEqual(achieved(atoms, F(1, 2)), 1)
        with self.assertRaises(ValueError):
            sandwich(atoms, F(0), F(0), theta=F(1, 2))

    def test_invalid_probability_contracts_refused(self):
        for atoms in ([], [(F(1, 2), F(0), F(1))], [(F(1), F(2), F(1))]):
            with self.assertRaises(ValueError):
                achieved(atoms)
        with self.assertRaises(ValueError):
            sandwich([(F(1), F(0), F(1))], F(1), F(-1))

    def test_nonfinite_or_inexact_parameters_refused(self):
        for bad in (float("nan"), float("inf"), True, 0.5):
            with self.subTest(value=bad), self.assertRaises(ValueError):
                sandwich([(F(1), F(0), F(1))], F(1), bad)

    def test_constant_oracle_and_zero_control(self):
        for k in ((0, 0, 0, 0), (8, 8, 8, 8), (-8, 8, -8, 8), (-8, -8, -8, -4), (1, 1, 1, 0)):
            self.assertEqual(paired_loss(k), scan_loss(k))
        self.assertEqual(baseline((0, 0, 0, 0)), 1)
        self.assertEqual(baseline((-8, -8, -8, -4)), F(17, 24))

    def test_late_literal_boundary_and_descriptor_countermodels(self):
        import json
        from pathlib import Path
        grid = json.loads((Path(__file__).parent / "raw/EXACT_GRID_V1.json").read_text())
        c = late_controls(grid)
        self.assertTrue(c["literal_09583_exclusion_counterexample"]["admissible"])
        self.assertTrue(c["literal_09583_exclusion_counterexample"]["above_literal_decimal"])
        self.assertEqual(c["new_grid_capacity_forbidden_mass"], "73/83521")
        self.assertEqual(F(c["new_grid_hypothetical_headroom_mass"]), F(1768, 83521))
        self.assertEqual(c["descriptor_only_noncarrier_enrichment"], "5")

    def test_finite_contract_census(self):
        c = band_census()
        self.assertGreater(c["valid_approximation_contracts"], 0)
        self.assertGreater(c["contracts_outside_stated_assumptions"], 0)
        self.assertEqual(sum(v for v in c.values() if isinstance(v, int)), 4374)


if __name__ == "__main__":
    unittest.main()
