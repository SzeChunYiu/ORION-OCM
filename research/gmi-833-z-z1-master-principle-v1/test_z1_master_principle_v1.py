"""Tests for IC-1 and the Z1 incompressibility separations (#833 Section Z, Z1).

Run:  python3 -I -B  test_z1_master_principle_v1.py -v
      python3 -I -O -B test_z1_master_principle_v1.py -v
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


A = _load("RESULT_V1.json", "z1_master_principle_v1.py")
B = _load("ORACLE_RESULT_V1.json", "independent_compression_oracle_v1.py")


class TestRouteAgreement(unittest.TestCase):
    def test_incompressible_and_compressible_sets_agree(self):
        self.assertEqual(A["incompressible_laws"], B["incompressible_laws"])
        self.assertEqual(A["compressible_laws"], B["compressible_laws"])

    def test_nonvacuity_counts_agree(self):
        for k in ("n_instances_nondegenerate", "n_profile_groups",
                  "n_groups_with_more_than_one_instance",
                  "n_instances_in_shared_groups", "largest_group"):
            self.assertEqual(A["nonvacuity"][k], B["nonvacuity"][k], k)

    def test_head_to_head_agrees(self):
        for k in ("lambda_star_eq_eta_p_over_2",
                  "lambda_star_eq_eta_p_one_minus_one_over_A",
                  "lambda_star_eq_eta_p_R0", "IC_1_on_ladder",
                  "Z13P1_two_price_ladder_on_ladder"):
            self.assertEqual(A["head_to_head"][k], B["head_to_head"][k], k)

    def test_ladder_floors_agree(self):
        for k, v in B["ladder_floors"].items():
            self.assertEqual(A["corollaries"]["IC_1d_ladder"]["floors"][k], v, k)

    def test_identification_agrees(self):
        self.assertEqual(A["null"]["two_level_laws_scoring_perfect"],
                         [list(x) for x in B["identification"]["two_level_perfect_laws"]])
        self.assertEqual(A["null"]["ladder_laws_scoring_perfect"],
                         [list(x) for x in B["identification"]["ladder_perfect_laws"]])


class TestPrinciple(unittest.TestCase):
    def test_all_corollaries_hold(self):
        self.assertTrue(A["IC_1_all_corollaries_hold"])
        for k, v in A["corollaries"].items():
            self.assertTrue(v.get("holds", True), k)

    def test_registered_floors_reproduce_the_published_numbers(self):
        f = A["corollaries"]["IC_1b_lambda_star_eq_eta_p_one_minus_one_over_A"]
        self.assertEqual(f["enumerated_table_counts"], {"2": 16, "3": 729, "4": 65536})
        self.assertEqual(f["floors"], {"2": "1/2", "3": "2/3", "4": "3/4"})
        self.assertEqual(A["corollaries"]["IC_1a_uniform_case_is_eta_p_over_2"]["R0_at_q_half"],
                         "1/2")

    def test_clause3_level_is_not_the_marginal(self):
        lad = A["corollaries"]["IC_1d_ladder"]
        self.assertEqual(lad["envelope_vs_interval_disagreements"], 0)
        self.assertIn("5/16", lad["clause3_level_is_not_marginal_witness"])
        self.assertIn("3/16", lad["clause3_level_is_not_marginal_witness"])
        self.assertEqual(
            lad["worlds_where_the_bare_level_formula_eta_p2_R0_matches_the_marginal"], 6)

    def test_ic1_beats_the_bag_on_the_ladder(self):
        self.assertEqual(A["head_to_head"]["IC_1_on_ladder"], "135/135")
        self.assertEqual(A["head_to_head"]["Z13P1_two_price_ladder_on_ladder"], "27/135")

    def test_two_level_cell_is_labelled_tautological(self):
        self.assertIn("TAUTOLOGICAL_AT_TWO_LEVELS", A["head_to_head"]["IC_1_two_level"])


class TestIncompressibility(unittest.TestCase):
    def test_nonvacuity(self):
        nv = A["nonvacuity"]
        self.assertTrue(nv["W_NONVACUITY_holds"])
        self.assertEqual(nv["n_instances_nondegenerate"], 264)
        self.assertEqual(nv["n_profile_groups"], 99)
        self.assertEqual(nv["n_groups_with_more_than_one_instance"], 75)
        self.assertEqual(nv["n_instances_in_shared_groups"], 240)
        self.assertEqual(nv["largest_group"], 9)
        self.assertEqual(nv["full_population_n_profile_groups"], 102)
        self.assertEqual(nv["full_population_n_shared_groups"], 78)

    def test_every_witness_is_non_degenerate(self):
        for name in A["incompressible_laws"]:
            w = A["incompressibility"][name]["separation_witness"]
            self.assertNotEqual(w["profile"]["E0"], w["profile"]["E1"], name)
            self.assertNotEqual(w["profile"]["E0"], "0", name)

    def test_four_laws_are_separated_with_an_exhibited_witness(self):
        self.assertEqual(A["incompressible_laws"],
                         ["L_DEGENERACY", "L_DISTINCT", "L_MDL", "L_REACH"])
        for name in A["incompressible_laws"]:
            w = A["incompressibility"][name]["separation_witness"]
            self.assertIsNotNone(w, name)
            self.assertEqual(w["instance_A"]["law_value"] == w["instance_B"]["law_value"],
                             False, name)
            self.assertEqual(w["profile"]["E0"], w["profile"]["E0"])

    def test_no_alarm_two_laws_are_compressible(self):
        self.assertTrue(A["W_NOALARM_holds"])
        self.assertEqual(A["compressible_laws"], ["L_ARGMIN_BUDGET", "L_THRESHOLD"])
        for name in A["compressible_laws"]:
            self.assertEqual(A["incompressibility"][name]["n_shared_profile_groups_split"], 0)


class TestCompressionMetrics(unittest.TestCase):
    def test_raw_pair_is_reported(self):
        c = A["compression"]
        self.assertEqual(c["raw_pair_IC_1"], [567, 0])
        self.assertEqual(c["IC_1_free_theoretical_dof"], 0)
        self.assertEqual(c["bag_free_theoretical_dof"], 5)
        self.assertEqual(c["bag_of_laws_members"], 4)

    def test_arbitrary_constants_are_named_not_hidden(self):
        self.assertEqual(len(A["arbitrary_constants_remaining"]), 1)
        self.assertIn("5/16", A["arbitrary_constants_remaining"][0])


class TestInstruments(unittest.TestCase):
    def test_all_hostiles_fire(self):
        self.assertTrue(A["hostiles_all_detected"])
        for k, v in A["hostiles"].items():
            self.assertTrue(v["detected"], k)

    def test_identification_is_unique(self):
        self.assertTrue(A["null"]["identified"])
        self.assertEqual(A["null"]["n_laws_scored"], 289)
        self.assertEqual(A["null"]["two_level_laws_scoring_perfect"], [["0", "1"]])
        self.assertEqual(A["null"]["ladder_laws_scoring_perfect"], [["1/2", "3/16"]])


if __name__ == "__main__":
    unittest.main(verbosity=2)
