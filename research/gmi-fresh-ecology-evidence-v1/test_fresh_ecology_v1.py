import copy
from fractions import Fraction as F
from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from records_v1 import analyze, load_scores, prose_comparison
from finite_controls_v1 import archive, controls
from check_v1 import run


class FreshEcologyTests(unittest.TestCase):
    def setUp(self):
        self.data = load_scores()

    def test_real_all_45_no_alarm(self):
        result = analyze(self.data)
        self.assertEqual(result["reported_score_rows"], 45)
        self.assertEqual(result["predictions"], {"P1": True, "P2": True, "P3": True, "P4": False})

    def test_memory_threshold_margin_failure_split(self):
        r = analyze(self.data)
        self.assertEqual(r["threshold_ecologies"]["hamming_knn_k3"],
                         ["E_fresh1", "E_fresh2", "E_fresh3", "E_fresh4"])
        self.assertEqual(r["accepted_ecologies"]["hamming_knn_k3"], [])
        self.assertEqual(list(r["memory_margins"].values()), ["78/125", "251/500", "0", "1/4", "-1/4"])

    def test_actual_prose_discrepancies(self):
        r = run()["source_comparison"]
        self.assertEqual([x["ecology"] for x in r["search_margin_discrepancies"]],
                         ["E_fresh1", "E_fresh2", "E_fresh4"])
        self.assertEqual(r["displayed_registry_comparison"], {"below": 3, "equal": 2, "above": 1})

    def test_corrected_margin_table_no_alarm(self):
        tip = HERE / "raw/tip"
        text = (tip / "GMI_CAPABILITY_MAP_PROSPECTIVE_TEST_V1.md").read_text()
        text = text.replace("+3.37", "+2.249").replace("+4.50", "+3.0")
        text = text.replace("| 0.9688 | +1.50 |", "| 0.9688 | +1.001 |")
        r = prose_comparison(self.data, text, (tip / "GMI_ECOLOGY_REGISTRY_SAMPLING_BIAS_V1.md").read_text())
        self.assertEqual(r["search_margin_discrepancies"], [])

    def test_real_flags_cannot_be_falsified(self):
        for e, block in self.data["results"].items():
            for name in block["rows"]:
                bad = copy.deepcopy(self.data)
                bad["results"][e]["rows"][name]["admissible"] ^= True
                with self.assertRaisesRegex(ValueError, "flag disagrees"):
                    analyze(bad)

    def test_missing_row_and_intervention_refused(self):
        bad = copy.deepcopy(self.data)
        del bad["results"]["E_fresh1"]["rows"]["program_search"]
        with self.assertRaisesRegex(ValueError, "row register"):
            analyze(bad)
        bad = copy.deepcopy(self.data)
        bad["interventions"].pop()
        with self.assertRaisesRegex(ValueError, "intervention"):
            analyze(bad)

    def test_no_fake_boolean_or_out_of_range_score(self):
        for field, value in [("admissible", 1), ("min_over_six", F(2))]:
            bad = copy.deepcopy(self.data)
            bad["results"]["E_fresh1"]["rows"]["program_search"][field] = value
            with self.assertRaises(ValueError):
                analyze(bad)

    def test_finite_family_and_rounding_countermodels(self):
        r = controls(self.data)
        self.assertEqual(r["same_observed_rows_possible_family_maxima"], ["4297/5000", "1"])
        self.assertEqual(r["completion_fixed_task"], "E_fresh4")
        self.assertEqual(r["completion_observed_members"],
                         {"gradient_net_h2": "8229/10000", "gradient_net_h4": "4297/5000"})
        self.assertTrue(r["all_observed_fields_preserved"])
        other_task = copy.deepcopy(self.data)
        other_task["results"]["E_fresh1"]["rows"]["gradient_net_h4"]["min_over_six"] = F(1)
        self.assertEqual(controls(other_task)["same_observed_rows_possible_family_maxima"],
                         r["same_observed_rows_possible_family_maxima"])
        self.assertLess(F(r["rounding_control"]["compatible_below_one"]), 1)
        self.assertGreater(F(r["rounding_control"]["printed_margin_model"]), 1)
        self.assertFalse(r["hypothetical_nonweak_baseline_admissible_score"]["realized_learner"])

    def test_cost_bin_control_not_cost_relief(self):
        r = controls(self.data)["archive"]
        self.assertEqual(r["distinct_cost_bins"], ["cheap", "expensive"])
        self.assertEqual(r["same_cost_bin"], ["expensive"])
        self.assertEqual(r["paid_before_insertion_each"], "101")
        elite, paid = archive([("old", F(1, 2), F(1), 0),
                               ("new", F(3, 4), F(2), 0)], lambda c: 0)
        self.assertEqual((elite, paid), (["new"], F(3)))

    def test_budget_ratio_not_uniform_work_ratio(self):
        r = controls(self.data)["search_prefix_visits"]
        self.assertEqual(r["grammar0"], [16, 2401])
        self.assertEqual(r["grammar1"], [16, 32])
        self.assertEqual(r["empty_evidence_scoring_calls"], 0)

    def test_tuple_distribution_is_not_semantic_uniformity(self):
        self.assertEqual(controls(self.data)["representation_vs_semantic_mass"], ["2/3", "1/2"])


if __name__ == "__main__":
    unittest.main()
