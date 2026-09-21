#!/usr/bin/env python3
"""Tests for gmi-833-h-family-tranche-d-v1 (nine exotic Section-H rows).

Stdlib only; must run green in normal and optimized Python:
    python3 -I -B test_tranche_d_v1.py
    python3 -I -O -B test_tranche_d_v1.py
"""
import json
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))

SIGMAS = set("SIGMA_TD%02d" % i for i in range(1, 10))
ROWS = {
    "H35": "Evolutionary/population search.",
    "H36": "Cellular/local-field computation.",
    "H37": "Distributed/collective intelligence.",
    "H38": "Tool-using/solver-routing intelligence.",
    "H39": "Neuro-symbolic/statistical-symbolic hybrids.",
    "H40": "Continual-learning systems.",
    "H41": "Meta-learning systems.",
    "H42": "Self-modifying/morphogenetic systems.",
    "H43": "Multi-agent emergent communication systems.",
}
EXPECTED_CLASS = {
    "H35": "STOCHASTIC_SOURCE_CHANNEL",
    "H36": "EXTERNAL_PEER_TOOL_CHANNEL",
    "H37": "EXTERNAL_PEER_TOOL_CHANNEL",
    "H38": "EXTERNAL_PEER_TOOL_CHANNEL",
    "H39": "TRIPLE_PARITY",
    "H40": "UPDATE_FEEDBACK_CHANNEL",
    "H41": "UPDATE_FEEDBACK_CHANNEL",
    "H42": "UPDATE_FEEDBACK_CHANNEL",
    "H43": "EXTERNAL_PEER_TOOL_CHANNEL",
}
EXPECTED_COST = {h: (5 if h == "H39" else 3) for h in ROWS}
DIGEST = "16289266d044cb1c1e26e48e7df20c71767ee1064d9b19da65dbfa60dbea1b34"


class ResultArtifacts(unittest.TestCase):
    def load(self, name):
        with open(os.path.join(HERE, name)) as fh:
            return json.load(fh)

    def test_result_exists_and_nine_rows(self):
        r = self.load("RESULT_V1.json")
        self.assertEqual(len(r["rows"]), 9)
        self.assertEqual(set(r["rows"]), set(ROWS))
        for hid, row in r["rows"].items():
            self.assertEqual(row["row"], ROWS[hid])

    def test_oracle_agrees_and_its_own_search_is_correct(self):
        o = self.load("ORACLE_RESULT_V1.json")
        self.assertEqual(o["schema"], "GMI833HFAMILY_TRANCHE_D_ORACLE_V1")
        self.assertTrue(o["all_classes_match"])
        self.assertTrue(o["all_twins_rejected"])
        r = self.load("RESULT_V1.json")
        self.assertTrue(r["independent_search"]["ok"])
        for hid in ROWS:
            sel = o["selections"][hid]
            self.assertEqual(sel["class"], r["rows"][hid]["recovery"]["recovered_class"])
            self.assertEqual(sel["cost"], r["rows"][hid]["recovery"]["recovered_cost"])

    def test_every_row_ten_gates_one_sigma_r11_open(self):
        r = self.load("RESULT_V1.json")
        for hid, rd in r["rows"].items():
            self.assertEqual(rd["sigma"], "SIGMA_TD%02d" % (int(hid[1:]) - 34))
            self.assertEqual(rd["gates_total"], 10)
            self.assertEqual(rd["all_eleven"], False)
            self.assertIn("R11_real_scale_test", rd["gates"])
            self.assertFalse(rd["gates"]["R11_real_scale_test"])
            # every certificate carries only this package's own scope
            self.assertIn(rd["sigma"], SIGMAS)
        # no row is closed, and no open row lacks an open gate
        self.assertEqual(r["verdict"]["rows_closed"], [])
        self.assertEqual(len(r["verdict"]["rows_open"]), 9)
        for entry in r["verdict"]["rows_open"]:
            self.assertTrue(entry["open_gates"])

    def test_recovery_classes_and_costs(self):
        r = self.load("RESULT_V1.json")
        for hid in ROWS:
            rec = r["rows"][hid]["recovery"]
            self.assertEqual(rec["predicted_class"], EXPECTED_CLASS[hid])
            self.assertEqual(rec["recovered_class"], EXPECTED_CLASS[hid])
            self.assertEqual(rec["recovered_cost"], EXPECTED_COST[hid])
            self.assertTrue(rec["recovered"])
            self.assertEqual(r["rows"][hid]["selected"]["class"], EXPECTED_CLASS[hid])

    def test_negative_controls_rejected(self):
        r = self.load("RESULT_V1.json")
        for hid in ROWS:
            self.assertTrue(r["rows"][hid]["negative_control"]["rejected"])
            self.assertNotEqual(r["rows"][hid]["negative_control"]["selected_class"],
                                EXPECTED_CLASS[hid])

    def test_lower_bound_exact(self):
        r = self.load("RESULT_V1.json")
        for hid in ROWS:
            lb = r["rows"][hid]["lower_bound"]
            self.assertEqual(lb["cost"], EXPECTED_COST[hid])
            self.assertEqual(lb["strictly_cheaper_candidates"], [])

    def test_grammar_digest_unchanged_and_census(self):
        r = self.load("RESULT_V1.json")
        g = r["grammar"]
        self.assertEqual(g["digest"], DIGEST)
        self.assertTrue(g["unchanged"])
        self.assertEqual(g["raw_trees"], 10050)
        self.assertEqual(g["semantic_classes"], 718)
        self.assertEqual(g["classes_by_cost"], {"1": 10, "2": 8, "3": 56,
                                                "4": 112, "5": 532})

    def test_cross_family_crossover_and_regeneration(self):
        r = self.load("RESULT_V1.json")
        self.assertTrue(r["cross_family"]["crossover"]["crossed_all"])
        for hid in ROWS:
            row = r["cross_family"]["crossover"]["rows"][hid]
            self.assertTrue(row["crossed"])
            self.assertEqual(row["winner_A"], "replay")
            self.assertEqual(row["winner_B"], "stored")
        self.assertTrue(r["cross_family"]["regeneration"]["ok"])
        for hid in ROWS:
            self.assertTrue(r["cross_family"]["regeneration"]["rows"][hid]["ok"])

    def test_held_out_disjoint_predictions(self):
        r = self.load("RESULT_V1.json")
        self.assertTrue(r["held_out"]["ok"])
        for row in r["held_out"]["contracts"]:
            self.assertTrue(row["ok"])
            self.assertEqual(row["recovered_cost"], row["predicted_cost"])
            self.assertEqual(row["recovered_class"], row["predicted_class"])

    def test_null_batteries_zero_of_n(self):
        r = self.load("RESULT_V1.json")
        self.assertTrue(r["nulls"]["ok"])
        self.assertEqual(r["nulls"]["rows"]["H39"]["drawn"], 182)
        for hid in ROWS:
            nrow = r["nulls"]["rows"][hid]
            self.assertEqual(nrow["recover"], 0)
            self.assertTrue(nrow["distinct"])

    def test_no_smuggling_audit_clean(self):
        r = self.load("RESULT_V1.json")
        a = r["no_smuggling_audit"]
        self.assertTrue(a["ok"])
        self.assertEqual(a["hits"], [])
        self.assertTrue(a["positive_control_caught"])
        self.assertTrue(r["semantic_macro_audit"]["ok"])

    def test_hostiles_all_ok_and_applicable(self):
        r = self.load("RESULT_V1.json")
        self.assertTrue(r["hostiles"]["ok"])
        for name, h in r["hostiles"]["hostiles"].items():
            self.assertTrue(h["applicable"], name)
            self.assertTrue(h["ok"], name)

    def test_claim_ceiling_and_r11_open(self):
        r = self.load("RESULT_V1.json")
        self.assertEqual(r["real_scale"]["status"], "OPEN_REAL_SCALE_PENDING")
        self.assertEqual(r["claim_ceiling"],
                         "TRANCHE_D_NAMED_FAMILY_CONTRACT_DERIVED_AT_REGISTERED_"
                         "FINITE_SCOPE__REAL_SCALE_OPEN_PENDING")
        self.assertIn("CROSS_SCOPE_GATE_COMPOSITION", r["forbidden_promotions"])
        self.assertIn("FINITE_EVIDENCE_IMPLIES_REAL_SCALE", r["forbidden_promotions"])
        self.assertIn("NAMED_FAMILY_ROW_CLOSED_AT_REAL_SCALE", r["forbidden_promotions"])

    def test_no_float_in_claimed_quantities(self):
        r = self.load("RESULT_V1.json")
        self.assertFalse(_has_float(r))

    def test_no_parent_result_file_read(self):
        r = self.load("RESULT_V1.json")
        for p in r["evidence_read"]:
            self.assertTrue(p.startswith("ORACLE_RESULT_V1.json"))

    def test_reconciliation(self):
        rec = self.load("ISSUE_833_RECONCILIATION_H_TRANCHE_D_V1.json")
        self.assertEqual(rec["schema"], "GMI_ISSUE_RECONCILIATION_V2")
        self.assertEqual(rec["issue"], 833)
        self.assertEqual(rec["replacements"], [])
        self.assertEqual(rec["anchor"], "# H. Prior-free derivation of known machine-intelligence families")
        for hid in ROWS:
            entry = rec["rows_left_open_with_attribution"][hid]
            self.assertEqual(entry["row"], ROWS[hid])
            self.assertEqual(entry["supported_gates"], 10)
            self.assertEqual(entry["open_gates"], ["R11_real_scale_test"])
            self.assertEqual(entry["predicted_class"], EXPECTED_CLASS[hid])
            self.assertEqual(entry["recovered_class"], EXPECTED_CLASS[hid])


def _has_float(node):
    if isinstance(node, dict):
        return any(_has_float(v) for v in node.values())
    if isinstance(node, list):
        return any(_has_float(v) for v in node)
    return isinstance(node, float)


if __name__ == "__main__":
    sys.exit(unittest.main())
