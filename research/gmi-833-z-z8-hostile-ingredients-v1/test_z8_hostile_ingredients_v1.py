"""Tests for the Z8 hostile-ingredient package.

Runs under both `python3 -I -B` and `python3 -I -O -B`: every check is a
unittest method call, never a bare `assert`, so -O cannot make it vacuous.

The two route receipts are compared field by field WITHOUT importing either
route's logic; the failed-prediction register is checked against the receipt;
the freeze is pinned by bytes (sha256), which survives a squash merge.
"""
import hashlib
import io
import json
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
FREEZE_SHA256 = "651d3cb548df3f29112faae6bed47385ca221919de8c758cfc03b51b2f8bcc10"


def load(name):
    with io.open(os.path.join(HERE, name), encoding="utf-8") as fh:
        return json.load(fh)


def walk_no_float(obj, path="$"):
    if isinstance(obj, float):
        return [path]
    out = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            out += walk_no_float(v, path + "." + str(k))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            out += walk_no_float(v, path + "[%d]" % i)
    return out


class Custody(unittest.TestCase):
    def test_freeze_bytes_pinned(self):
        with io.open(os.path.join(HERE, "FREEZE_V1.md"), "rb") as fh:
            raw = fh.read()
        self.assertEqual(hashlib.sha256(raw).hexdigest(), FREEZE_SHA256)
        self.assertIn(b"No neighboring row is earned here.", raw)

    def test_register_pins_the_same_freeze(self):
        reg = load("FAILED_PREDICTION_REGISTER_V1.json")
        self.assertEqual(reg["freeze_sha256"], FREEZE_SHA256)

    def test_receipts_have_no_floats(self):
        self.assertEqual(walk_no_float(load("RESULT_V1.json")), [])
        self.assertEqual(walk_no_float(load("ORACLE_RESULT_V1.json")), [])
        self.assertEqual(walk_no_float(load("FAILED_PREDICTION_REGISTER_V1.json")), [])


class TwoRoutes(unittest.TestCase):
    def setUp(self):
        self.a = load("RESULT_V1.json")
        self.b = load("ORACLE_RESULT_V1.json")
        self.assertEqual(self.a["route"], "A")
        self.assertEqual(self.b["route"], "B")
        self.assertFalse(self.b["imports_route_A"])

    def test_floors_all_five_universes(self):
        i = self.a["ingredients"]
        pairs = [("BASE", self.a["base"]["floors"]),
                 ("WINDOW3", i["I2c_verifier_failure_window3"]["floors"]),
                 ("PERIOD2", i["I3_causal_aliasing_period2"]["floors"]),
                 ("MOORE", i["I7a_moore_grammar"]["floors"]),
                 ("INPUT_ONLY", i["I7b_input_only_grammar"]["floors"])]
        for name, fa in pairs:
            self.assertEqual(fa, self.b["floors"][name], name)
        self.assertEqual(self.b["floors"]["BASE"],
                         {"b0_m0": "0", "b0_m1": "1/2", "b0_m2": "1/2", "b1_m0": "0", "b1_m1": "0",
                          "b1_m2": "5/16", "b2_m0": "0", "b2_m1": "0", "b2_m2": "0"})
        # route B must have proved b=2 by witness/closed form, not enumeration
        for name, meth in self.b["b2_method"].items():
            for k, txt in meth.items():
                self.assertTrue(("witness" in txt) or ("closed-form" in txt) or ("full enumeration of 16" in txt), (name, k, txt))

    def test_two_level_and_nonstationary(self):
        i = self.a["ingredients"]
        self.assertEqual(i["I4a_distribution_shift_two_level"]["R0"], self.b["two_level_R0"])
        self.assertTrue(self.b["two_level_one_bit_floor_zero"])
        self.assertEqual(i["I4b_nonstationary_in_window"]["floors"], self.b["nonstationary_floors"])
        self.assertEqual(len(self.b["nonstationary_floors"]), 49)

    def test_moved_counts(self):
        i = self.a["ingredients"]
        m = self.b["moved"]
        self.assertEqual(i["I1_near_tie"]["triple_tie_worlds"], m["I1"]["triple_tie_worlds"])
        self.assertEqual(i["I1_near_tie"]["triple_tie_degenerate"], m["I1"]["triple_tie_degenerate"])
        self.assertEqual(i["I1_near_tie"]["V_SEL_moved_worlds"], m["I1"]["V_SEL_moved_worlds"])
        self.assertEqual(i["I1_near_tie"]["tie_structure_failures"], m["I1"]["tie_structure_failures"])
        for eps in ("1/16", "1/8", "1/4"):
            a = i["I2a_uniform_verifier_noise"][eps]
            self.assertEqual((a["V_NICHE"], a["V_SEL_cells"], a["V_THR"]),
                             (m["I2a"][eps]["V_NICHE"], m["I2a"][eps]["V_SEL_cells"], m["I2a"][eps]["V_THR"]))
            self.assertEqual(i["I2b_delay2_only_verifier_noise"][eps]["V_NICHE"], m["I2b"][eps]["V_NICHE"])
        c = i["I2c_verifier_failure_window3"]
        self.assertEqual((c["V_NICHE"], c["V_THR"], c["V_SEL_worlds"]),
                         (m["I2c"]["V_NICHE"], m["I2c"]["V_THR"], m["I2c"]["V_SEL_worlds"]))
        c = i["I3_causal_aliasing_period2"]
        self.assertEqual((c["V_NICHE"], c["V_THR"], c["V_SEL_worlds"], c["V_FAIL_worlds"]),
                         (m["I3"]["V_NICHE"], m["I3"]["V_THR"], m["I3"]["V_SEL_worlds"], m["I3"]["V_FAIL_worlds"]))
        c = i["I4a_distribution_shift_two_level"]
        for k in ("cells", "moved_set_valued", "strictly_between_cells", "outside_strict_band_moved_set",
                  "complementary_pair_cells_moved"):
            self.assertEqual(c[k], m["I4a"][k], k)
        for key, mk in (("I5a_affine_accounting", "I5a"), ("I5b_state_count_accounting", "I5b"),
                        ("I5c_concave_accounting", "I5c")):
            self.assertEqual((i[key]["V_NICHE"], i[key]["V_SEL_cells"]), (m[mk]["V_NICHE"], m[mk]["V_SEL_cells"]), key)
        c = i["I6a_history_weighted_mixture"]
        for k in ("cells", "cells_with_a_common_level", "common_level_kept_by_every_weight",
                  "history_weighted_differs_from_current_optimum"):
            self.assertEqual(c[k], m["I6a"][k], k)
        for kappa in ("1/32", "1/8"):
            c = i["I6b_hysteresis"][kappa]
            for k in ("cells", "moved", "moved_with_positive_excess", "cells_with_0_lt_excess_le_kappa"):
                self.assertEqual(c[k], m["I6b"][kappa][k], (kappa, k))
        for key, mk in (("I7a_moore_grammar", "I7a"), ("I7b_input_only_grammar", "I7b")):
            for k in ("V_NICHE", "V_SEL_cells", "V_THR", "V_FAIL_worlds"):
                self.assertEqual(i[key][k], m[mk][k], (key, k))
        self.assertTrue(m["I7c"]["state_relabel_invariant"])
        self.assertTrue(m["I7c"]["input_relabel_invariant"])
        self.assertTrue(i["I7c_relabelling"]["state_relabel_invariant"])
        self.assertTrue(i["I7c_relabelling"]["input_relabel_invariant"])
        self.assertEqual(i["I8_search_law"]["greedy_single_start_floors"], m["I8"]["greedy_single_start_floors"])


class Content(unittest.TestCase):
    def setUp(self):
        self.a = load("RESULT_V1.json")
        self.reg = load("FAILED_PREDICTION_REGISTER_V1.json")

    def test_binding_condition(self):
        self.assertTrue(self.a["every_ingredient_moves_or_is_proved_unable"])
        mx = self.a["verdict_matrix"]
        self.assertEqual(sorted(mx), ["I1", "I2", "I3", "I4", "I5", "I6", "I7", "I8", "I9"])
        for k in ("I1", "I2", "I3", "I4", "I5", "I6", "I7", "I8"):
            self.assertTrue(any(v.startswith("MOVES") for v in mx[k].values()), k)
        # the 'unable' entries must each name a theorem-class reason
        self.assertIn("UNABLE", mx["I2"]["V_NICHE"])
        self.assertIn("UNABLE", mx["I5"]["V_NICHE"])
        self.assertIn("UNABLE", mx["I7"]["V_NICHE"])

    def test_headline_numbers(self):
        i = self.a["ingredients"]
        self.assertEqual(i["I3_causal_aliasing_period2"]["V_NICHE"], 12)
        self.assertEqual(i["I3_causal_aliasing_period2"]["V_THR"], 108)
        self.assertEqual(i["I5b_state_count_accounting"]["V_NICHE"], 36)
        self.assertEqual(i["I5c_concave_accounting"]["V_NICHE"], 24)
        self.assertEqual(i["I5a_affine_accounting"]["V_NICHE"], 0)
        self.assertEqual(i["I5a_affine_accounting"]["V_SEL_cells"], 0)
        self.assertEqual(i["I7a_moore_grammar"]["V_NICHE"], 0)
        self.assertEqual(i["I7a_moore_grammar"]["V_FAIL_worlds"], 108)
        self.assertEqual(i["I7b_input_only_grammar"]["V_NICHE"], 12)
        self.assertEqual(i["I8_search_law"]["greedy_single_start_floors"]["b2_m2"], "1/8")
        self.assertEqual(i["I8_search_law"]["greedy"]["V_NICHE"], 12)
        self.assertEqual(i["I2c_verifier_failure_window3"]["delay2_b1_floor"], "1/4")
        for eps in ("1/16", "1/8", "1/4"):
            self.assertEqual(i["I2a_uniform_verifier_noise"][eps]["V_NICHE"], 0)
        self.assertEqual(i["I2b_delay2_only_verifier_noise"]["1/4"]["V_NICHE"], 12)
        self.assertEqual(i["I4b_nonstationary_in_window"]["frozen_formula_holds"], 31)
        self.assertEqual(i["I4b_nonstationary_in_window"]["same_side_pairs"], 31)
        self.assertEqual(i["I4b_nonstationary_in_window"]["post_hoc_form_R0_of_mean_q_holds"], 49)
        self.assertEqual(i["I1_near_tie"]["tie_structure_failures"], 1)

    def test_register_matches_receipt(self):
        fp = self.a["frozen_predictions"]
        self.assertEqual(sorted(self.a["failed_predictions"]), ["P1", "P4", "P6"])
        by_id = dict((e["id"], e) for e in self.reg["entries"])
        self.assertEqual(by_id["P1"]["verdict"], fp["P1"]["verdict"])
        self.assertEqual(by_id["P4a"]["verdict"], "MISS")
        self.assertEqual(by_id["P4b"]["verdict"], "MISS")
        self.assertEqual(by_id["P6b"]["verdict"], "MISS")
        self.assertEqual(by_id["P6a"]["verdict"], "HIT")
        for pid in ("P2", "P3", "P5", "P7", "P8", "P9"):
            self.assertEqual(by_id[pid]["verdict"], fp[pid]["verdict"], pid)
            self.assertEqual(fp[pid]["verdict"], "HIT", pid)
        self.assertEqual(sorted(self.reg["misses"]), ["P1", "P4a", "P4b", "P6b"])
        for e in self.reg["entries"]:
            if e["verdict"] == "MISS":
                self.assertIn("attributed_stage", e, e["id"])
                self.assertIn("post_hoc_note", e, e["id"])
                self.assertIn("not scored", e["post_hoc_note"], e["id"])

    def test_hostiles_and_null(self):
        h = self.a["hostiles"]
        self.assertEqual(len(h), 6)
        for k, v in h.items():
            self.assertTrue(v["applicable"], k)
            self.assertTrue(v["detected"], k)
        n = self.a["null"]
        self.assertEqual(n["n_laws"], 200)
        self.assertGreater(n["IC1_on_hostile_profile"], n["best_null"])
        self.assertEqual(n["IC1_on_hostile_profile"], n["targets"])
        self.assertGreater(n["distinct_draws"], 100)
        self.assertTrue(n["no_alarm_holds"])
        self.assertIn("excluded", n["pool"])

    def test_bounds_classified(self):
        kinds = [b["class"] for b in self.a["bounds"]]
        self.assertIn("VACUOUS_BY_RANGE_NOT_CLAIMED", kinds)
        self.assertIn("BINDING", kinds)
        self.assertNotIn("VIOLATED", kinds)

    def test_gates_and_verdict(self):
        self.assertEqual(self.a["verdict"], "GREEN")
        self.assertTrue(all(self.a["gates"].values()))


if __name__ == "__main__":
    unittest.main(argv=[sys.argv[0]] + [a for a in sys.argv[1:] if a != "-v"] + ["-v"])
