"""Tests for the Z13-P1 adjudication (#833 Section Z, Z13).

Runs both routes if their receipts are absent, then asserts route agreement and
every number this package reconciles an issue row with.

Run:  python3 -I -B  test_z13_adjudication_v1.py -v
      python3 -I -O -B test_z13_adjudication_v1.py -v
"""
import json
import os
import subprocess
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))


def _load(name, script):
    p = os.path.join(HERE, name)
    if not os.path.exists(p):
        subprocess.check_call([sys.executable, "-I", "-B", os.path.join(HERE, script)],
                              stdout=subprocess.DEVNULL)
    with open(p) as f:
        return json.load(f)


A = _load("RESULT_V1.json", "z13_adjudication_v1.py")
B = _load("ORACLE_RESULT_V1.json", "independent_z13_oracle_v1.py")


class TestRouteAgreement(unittest.TestCase):
    def test_channel_minima_agree(self):
        for k, v in B["channel_minima"].items():
            self.assertEqual(A["channel_optima"][k]["R"], v, k)

    def test_threshold_scores_agree(self):
        self.assertEqual(A["thresholds"]["H1_lower_endpoint_matches_frozen"],
                         B["thresholds"]["H1_lower_matches_frozen"])
        self.assertEqual(A["thresholds"]["H2_upper_endpoint_matches_frozen"],
                         B["thresholds"]["H2_upper_matches_frozen"])
        self.assertEqual(A["thresholds"]["true_niche_nonempty_worlds"],
                         B["thresholds"]["true_niche_nonempty_worlds"])

    def test_negative_ecology_agrees(self):
        self.assertEqual(A["negative_ecology"]["p2_zero_worlds"],
                         B["thresholds"]["p2_zero_worlds"])
        self.assertEqual(A["negative_ecology"]["p2_zero_worlds_with_collapsed_interval"],
                         B["thresholds"]["p2_zero_collapsed"])
        self.assertEqual(A["negative_ecology"]["p2_zero_observed_widths"],
                         B["thresholds"]["p2_zero_widths"])

    def test_bundle_unsatisfiable_in_both_routes(self):
        self.assertFalse(A["satisfiability"]["P_b_all_and_P_c_satisfiable_at_b1"])
        self.assertFalse(B["satisfiability"]["bundle_satisfiable"])

    def test_verdicts_agree(self):
        self.assertEqual(A["verdict"], "MISS")
        self.assertEqual(B["verdict"], "MISS")


class TestReconciledNumbers(unittest.TestCase):
    def test_one_bit_delay2_floor(self):
        self.assertEqual(A["key_floors"]["R0_delay2_given_b1"], "5/16")
        self.assertEqual(B["channel_minima"]["b1_m2"], "5/16")

    def test_lower_endpoint_exact_everywhere(self):
        self.assertEqual(A["thresholds"]["H1_lower_endpoint_matches_frozen"], "135/135")

    def test_upper_endpoint_fails_off_the_p2_zero_slice(self):
        self.assertEqual(A["thresholds"]["H2_upper_endpoint_matches_frozen"], "27/135")
        self.assertEqual(A["thresholds"]["frozen_upper_excess_value"], "eta*p2*1/8")

    def test_true_collapse_condition(self):
        self.assertEqual(A["thresholds"]["width_coefficients"]["p1_coeff"], "1/2")
        self.assertEqual(A["thresholds"]["width_coefficients"]["p2_coeff"], "-1/8")

    def test_frozen_negative_ecology_is_where_the_niche_is_widest(self):
        self.assertTrue(A["negative_ecology"]["p2_zero_is_the_widest_niche_at_fixed_p1"])
        self.assertFalse(A["negative_ecology"]["H5_mechanism_claim_holds"])
        self.assertEqual(A["negative_ecology"]["p2_zero_worlds_with_collapsed_interval"], 3)

    def test_P_d_is_vacuous(self):
        self.assertEqual(A["P_d_status"], "VACUOUSLY_TRUE")
        self.assertFalse(A["HIT_conditions"]["H4_Pd_nonvacuous"])

    def test_universe_size_exact(self):
        self.assertEqual(A["universe"]["size_by_budget"]["2"], str(2 ** 72))
        self.assertEqual(A["universe"]["size_by_budget"]["1"], "16777216")
        self.assertEqual(A["universe"]["size_by_budget"]["0"], "64")

    def test_recovered_optimum_is_not_identity_state(self):
        fam = A["recovered_b1_optimum"]["families"]
        self.assertNotIn("F_IDENTITY_STATE", fam)
        self.assertIn("F_MEALY_PURE", fam)
        pr = A["recovered_b1_optimum"]["properties"]
        self.assertTrue(pr["P_c"])
        self.assertFalse(pr["P_b_all"])
        self.assertTrue(pr["identity_next_by_mode"]["1"])
        self.assertFalse(pr["identity_next_by_mode"]["2"])


class TestInstruments(unittest.TestCase):
    def test_every_hostile_moves_its_quantity(self):
        self.assertTrue(A["hostiles_all_detected"])
        for name, h in A["hostiles"].items():
            self.assertTrue(h["detected"], name)

    def test_no_alarm_control_is_silent(self):
        self.assertTrue(A["no_alarm_control"]["silent_as_required"])

    def test_null_is_beaten(self):
        self.assertEqual(A["null"]["marginal_law_score"], "135/135")
        self.assertEqual(A["null"]["nulls_reaching_all_worlds"], 0)
        self.assertEqual(A["null"]["frozen_Z13P1_law_score"], "27/135")

    def test_vacuity_probe_is_not_counted_as_evidence(self):
        self.assertIn("NOT counted", A["vacuity_probe"]["note"])

    def test_lemmas_verified_by_route_B(self):
        self.assertTrue(B["majority_optimality"]["b01_exhaustive_L4"])
        self.assertTrue(B["majority_optimality"]["b01_exhaustive_L3_L5"])
        self.assertTrue(B["majority_optimality"]["b2_sampled"])
        self.assertTrue(B["mode_independence"]["holds"])
        self.assertTrue(A["majority_optimality_checked_b01"])

    def test_remints_preserve_and_the_non_remint_control_fires(self):
        r = A["remints"]
        self.assertTrue(r["state_relabel_identity_preserved"])
        self.assertTrue(r["input_relabel_preserved"])
        self.assertTrue(r["control_broken_relabel_changes_numbers"])
        self.assertGreater(r["control_n_changed"], 0)

    def test_independent_searches_recover_the_same_optimum(self):
        for k, v in A["independent_searches"].items():
            self.assertTrue(v["agree"], k)
        self.assertTrue(A["independent_searches"]["b2_m2"]["single_start_stalled"])

    def test_scan_route_has_no_disagreements(self):
        self.assertEqual(B["thresholds"]["scan_disagreements"], 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
