"""Tests for gmi-833-h-real-scale-diffusion-refinement-v1.

Runs under `python3 -I -B` and `python3 -I -O -B`. Every check is a unittest
assertion method, never a bare `assert`, so `-O` cannot strip it. The package
uses exact integer decision counts; no float enters any test.
"""
import ast
import json
import os
import subprocess
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import grammar_dr_v1 as G                  # noqa: E402
import real_scale_diffusion_refinement_v1 as C   # noqa: E402

PRIMARY = ("grammar_dr_v1", "run_real_scale_diffusion_refinement_v1",
           "real_scale_diffusion_refinement_v1")
SIGMA = "SIGMA_H33R"
ROW = "- [ ] Diffusion/iterative-refinement systems."
SOURCE_SHA = "9e66281f7e51445eab6857488ff6e3d768afffadb7fb1adbef5e4617bee4a53b"
KEY = "L:9e7477378715"
INTENDED = "REFINEMENT_INDEX"


def read(name):
    with open(os.path.join(HERE, name)) as fh:
        return fh.read()


def load_json(name):
    with open(os.path.join(HERE, name)) as fh:
        return json.load(fh)


class TwoRoutes(unittest.TestCase):

    def test_oracle_does_not_import_the_primary_executor(self):
        tree = ast.parse(read("independent_oracle_dr_v1.py"))
        named = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                named.extend(a.name for a in node.names)
            elif isinstance(node, ast.ImportFrom):
                named.append(node.module or "")
        for mod in PRIMARY:
            self.assertNotIn(mod, named)

    def test_oracle_module_namespace_is_clean(self):
        code = ("import sys, os; sys.path.insert(0, %r);"
                "import independent_oracle_dr_v1;"
                "print(','.join(m for m in %r if m in sys.modules))"
                % (HERE, PRIMARY))
        out = subprocess.check_output([sys.executable, "-I", "-B", "-c", code],
                                      cwd=HERE).decode().strip()
        self.assertEqual(out, "")

    def test_oracle_agrees(self):
        oracle = load_json("ORACLE_RESULT_V1.json")
        self.assertTrue(oracle["agrees"])
        self.assertFalse(oracle["imports_primary_executor"])
        self.assertGreaterEqual(len(oracle["checks"]), 20)
        for name, ok in oracle["checks"].items():
            self.assertTrue(ok, name)

    def test_the_checker_reads_no_parent_result_file(self):
        tree = ast.parse(read("real_scale_diffusion_refinement_v1.py"))
        literals = [n.value for n in ast.walk(tree)
                    if isinstance(n, ast.Constant) and isinstance(n.value, str)]
        for text in literals:
            self.assertNotIn("research/", text)
        roots = set()
        for node in ast.walk(tree):
            if (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                    and node.func.id == "load"):
                roots.add(ast.dump(node.args[0])[:24])
        self.assertTrue(roots)


class Custody(unittest.TestCase):

    def test_the_freeze_names_exactly_the_one_row(self):
        text = read("FREEZE_V1.md")
        self.assertIn(ROW, text)
        self.assertIn("No neighboring row is earned here.", text)
        self.assertNotIn("- [ ] Latent-variable generative systems.", text)
        self.assertNotIn("- [ ] Particle/population inference.", text)
        self.assertNotIn("- [ ] Energy-based systems.", text)

    def test_the_freeze_registers_the_design_and_not_the_outcome(self):
        text = read("FREEZE_V1.md")
        for token in ("SIGMA_H33R", "2654435761", "671,860", "587,877",
                      "83,983", "38,103", "9e66281f7e51", "T*"):
            self.assertIn(token, text)
        # the freeze names the criterion, not the configuration it selects
        self.assertIn("The rule is a criterion, not a named configuration", text)
        self.assertIn("REAL_RUNS/scope_SIGMA_H33R.json", text)

    def test_the_addendum_states_the_registered_forms(self):
        text = read("FREEZE_V1_SLICE_ADDENDUM_H33_V1.md")
        self.assertIn("key(i)  = (i * 2654435761) mod 2**32", text)
        self.assertIn("587,877", text)
        self.assertIn("83,983", text)
        self.assertIn("411,513", text)
        self.assertIn("176,364", text)
        self.assertIn("MEM_FALLBACK", text)
        self.assertIn("REFINE<=", text)
        self.assertIn("DRAW0", text)
        self.assertIn("20261001", text)
        self.assertIn("20261002", text)
        self.assertIn("must contain the registered `T*`", text)

    def test_the_first_run_receipts_are_still_committed(self):
        self.assertTrue(os.path.isfile(os.path.join(
            HERE, "REAL_RUNS", "scope_SIGMA_H33R.json")))
        self.assertTrue(os.path.isfile(os.path.join(
            HERE, "REAL_RUNS", "sources.json")))

    def test_the_manifest_names_the_freeze_files(self):
        man = load_json("MANIFEST_V1.json")
        self.assertEqual(man["freeze_addenda"],
                         ["FREEZE_V1_SLICE_ADDENDUM_H33_V1.md"])
        for pin in man["freeze_pins"].values():
            self.assertEqual(len(pin), 64)
        self.assertEqual(man["scopes"], {"SIGMA_H33R": ROW.replace("- [ ] ", "")})

    def test_the_manifest_excludes_the_sibling_scopes(self):
        man = load_json("MANIFEST_V1.json")
        for other in ("SIGMA_H31R", "SIGMA_H19R", "SIGMA_H05R"):
            self.assertIn(other, man["scope_exclusions"])
            self.assertNotIn(other, man["scopes"])


class Scopes(unittest.TestCase):

    def setUp(self):
        self.result = load_json("RESULT_V1.json")

    def test_no_gate_carries_a_foreign_sigma(self):
        row = self.result["rows"]["H33"]
        for gate in row["gates"]:
            self.assertEqual(gate["sigma"], SIGMA)
        self.assertTrue(self.result["no_gate_carries_a_foreign_sigma"])

    def test_no_gate_cites_a_parent_certificate(self):
        row = self.result["rows"]["H33"]
        for gate in row["gates"]:
            for other in ("SIGMA_H31R", "SIGMA_H19R", "SIGMA_H05R",
                          "SIGMA_H06R", "SIGMA_H08R", "SIGMA_H17R"):
                self.assertNotIn(other, gate["evidence"])
            self.assertNotIn("gmi-833-h-", gate["evidence"])

    def test_the_row_is_closed_only_with_eleven_coordinates(self):
        row = self.result["rows"]["H33"]
        if row["closed"]:
            self.assertEqual(row["coordinates_measured"], 11)
            self.assertEqual(row["open_gates"], [])
            self.assertEqual(self.result["rows_closed"],
                             [ROW.replace("- [ ] ", "")])
            self.assertEqual(self.result["rows_open"], [])
        else:
            self.assertTrue(row["open_gates"])

    def test_the_measured_class_is_the_intended_class(self):
        row = self.result["rows"]["H33"]
        self.assertEqual(row["measured_class"], INTENDED)
        self.assertEqual(row["intended_class"], INTENDED)

    def test_real_scale_thresholds_are_met(self):
        scale = self.result["scale"]
        self.assertGreaterEqual(scale["n_fit"], 100000)
        self.assertGreaterEqual(scale["n_held"], 20000)
        self.assertEqual(scale["n_fit"], 587877)
        self.assertEqual(scale["n_held"], 83983)
        self.assertEqual(scale["T_ctx"], 671860)
        self.assertEqual(scale["query_set"], 38103)
        self.assertEqual(scale["source_sha256"], SOURCE_SHA)
        self.assertEqual(scale["duplicate_tokens"], 0)
        self.assertEqual(scale["alphabet_size"], 69)

    def test_every_hostile_is_applicable_and_detected(self):
        self.assertEqual(len(self.result["hostiles"]), 6)
        for hostile in self.result["hostiles"]:
            self.assertTrue(hostile["applicable"], hostile["hostile"])
            self.assertTrue(hostile["detected"], hostile["hostile"])
            self.assertTrue(hostile["no_alarm_on_clean"], hostile["hostile"])

    def test_every_claimed_quantity_is_an_exact_integer(self):
        hold = self.result["holdout_replay"]
        for value in (hold["n"], hold["replayed_errors"],
                      hold["prototype_agreement"]):
            self.assertIsInstance(value, int)
        for value in self.result["ladder"]["errors"]:
            self.assertIsInstance(value, int)
        rec = C.load("scope_SIGMA_H33R.json")
        co = rec["crossover"]
        for value in (co["V"], co["alphabet_width"], co["index_cost"],
                      co["m_star"], co["scan_cost_at_m_star"]):
            self.assertIsInstance(value, int)
        self.assertTrue(self.result["crossover"]["matches_registered_arithmetic"])
        self.assertEqual(co["m_star"], 57567)
        self.assertEqual(co["V"], 115105)
        self.assertGreater(2 * co["m_star"], co["V"] + co["alphabet_width"])
        self.assertLessEqual(2 * (co["m_star"] - 1),
                             co["V"] + co["alphabet_width"])

    def test_the_family_separation_is_reported_and_holds(self):
        fam = self.result["family_separation"]
        self.assertTrue(fam["separated"])
        self.assertTrue(fam["matches_committed"])
        rec = C.load("scope_SIGMA_H33R.json")
        fs = rec["family_separation"]
        self.assertEqual(fs["refinement_best"]["arm"], "REFINE<=25")
        self.assertEqual(fs["refinement_best"]["errors"], 1479)
        self.assertEqual(fs["single_draw_best"]["arm"], "DRAW0")
        self.assertEqual(fs["single_draw_best"]["errors"], 30557)
        self.assertEqual(fs["cardinality_best"]["arm"], "CNT>=1")
        self.assertEqual(fs["cardinality_best"]["errors"], 5197)
        self.assertLess(fs["refinement_best"]["errors"],
                        fs["single_draw_best"]["errors"])

    def test_the_f1_margin_is_an_exact_integer_bound(self):
        rec = C.load("scope_SIGMA_H33R.json")
        ho = rec["holdout"]
        self.assertEqual(ho["f1_half_majority"], ho["majority_errors"] // 2)
        self.assertTrue(ho["f1_holds"])
        self.assertLessEqual(2 * ho["winner_errors"], ho["majority_errors"])

    def test_mem_fallback_is_admitted_and_not_the_winner(self):
        rec = C.load("scope_SIGMA_H33R.json")
        ho = rec["holdout"]
        self.assertFalse(ho["mem_fallback_is_winner"])
        self.assertNotEqual(ho["winner"], "MEM_FALLBACK")
        self.assertIn("MEM_FALLBACK", ho["per_readout_errors"])
        self.assertEqual(ho["mem_fallback_errors"],
                         ho["per_readout_errors"]["MEM_FALLBACK"])

    def test_the_registered_falsifiers_that_fired_are_named(self):
        row = self.result["rows"]["H33"]["recovery"]
        for name in ("CROSS_SCOPE_GATE_COMPOSITION",
                     "CONTRACT_IDENTITY_IMPLIES_FAMILY_IDENTITY",
                     "ROW_CLOSED_BY_MEASUREMENT", "BOUNDARY_IS_A_RECOVERY"):
            self.assertIn(name, self.result["forbidden_promotions"])
        self.assertTrue(row["design_null"]["gt_3x"])
        self.assertTrue(row["design_null"]["raw_arms_invariant"])


class SliceRule(unittest.TestCase):

    def test_the_permutation_and_slices_are_exact(self):
        T = 671860
        n_fit = (T * 7) // 8
        self.assertEqual(n_fit, 587877)
        self.assertEqual(T - n_fit, 83983)
        self.assertEqual((7 * n_fit) // 10, 411513)
        self.assertEqual(n_fit - (7 * n_fit) // 10, 176364)
        self.assertEqual(n_fit // 2, 293938)
        keyed = sorted(range(T), key=lambda i: (i * 2654435761) % (2 ** 32))
        self.assertEqual(len(keyed), T)
        self.assertEqual([(i * 2654435761) % (2 ** 32) for i in keyed],
                         sorted((i * 2654435761) % (2 ** 32) for i in range(T)))
        self.assertEqual(keyed[:n_fit] + keyed[n_fit:], keyed)

    def test_the_ladder_arithmetic_is_registered(self):
        self.assertEqual(len(G.REFINE_BASE), 12)
        self.assertIn(25, G.ladder((25,)))
        self.assertNotIn(25, G.ladder(()))
        self.assertEqual(len(G.ladder((25,))), len(G.REFINE_BASE) + 1)
        self.assertEqual(G.ladder((25,))[0], 1)
        self.assertEqual(G.STEP_CAP, 256)
        self.assertEqual(G.LEN_THRESHOLDS, (6, 7, 8, 9, 10, 11, 12))
        self.assertEqual(G.CARD_THRESHOLDS, (1, 2, 3, 4))
        self.assertEqual(G.DRAW_THRESHOLDS, (1, 2, 3, 4))


class GrammarAndReadouts(unittest.TestCase):

    def test_the_classifier_reads_the_name_alone(self):
        self.assertEqual(G.classify("REFINE<=4"), "REFINEMENT_INDEX")
        self.assertEqual(G.classify("REFINE>=16"), "REFINEMENT_INDEX")
        self.assertEqual(G.classify("REFINEIN<=2"), "REFINEMENT_INDEX")
        self.assertEqual(G.classify("DRAW0"), "SINGLE_DRAW_SOURCE")
        self.assertEqual(G.classify("DRAW>=3"), "SINGLE_DRAW_SOURCE")
        self.assertEqual(G.classify("C0"), "CONSTANT_ARM")
        self.assertEqual(G.classify("LEN<=9"), "DESCRIPTOR_LENGTH_THRESHOLD")
        self.assertEqual(G.classify("CNT>=1"), "STORE_MEMBERSHIP_COUNT")
        self.assertEqual(G.classify("CARD>=4"), "STORE_MEMBERSHIP_COUNT")
        self.assertEqual(G.classify("MEM_FALLBACK"),
                         "STORED_LABEL_READ_WITH_FALLBACK")
        self.assertRaises(ValueError, G.classify, "SQUARE")

    def test_the_costs_are_registered(self):
        self.assertEqual(G.cost("C0"), 0)
        self.assertEqual(G.cost("LEN<=9"), 0)
        self.assertEqual(G.cost("CNT>=1"), 1)
        self.assertEqual(G.cost("CARD>=1"), 1)
        self.assertEqual(G.cost("REFINE<=4"), 1)
        self.assertEqual(G.cost("DRAW0"), 1)
        self.assertEqual(G.cost("MEM_FALLBACK"), 2)

    def test_the_language_is_closed_and_outcome_free(self):
        self.assertIn("REFINE<=25", G.readouts((25,)))
        self.assertIn("MEM_FALLBACK", G.readouts())
        self.assertNotIn("SQUARE", G.readouts())
        self.assertNotIn("PROBE>=1", G.readouts())
        self.assertEqual(len(G.readouts()), 49)
        self.assertEqual(len(G.readouts((25,))), 51)
        self.assertEqual(len(set(G.readouts((25,)))), len(G.readouts((25,))))
        self.assertEqual(sum(1 for n in G.readouts()
                             if G.classify(n) == "REFINEMENT_INDEX"), 27)
        self.assertEqual(sum(1 for n in G.readouts()
                             if G.classify(n) == "SINGLE_DRAW_SOURCE"), 5)
        for name in G.readouts():
            self.assertIsInstance(G.cost(name), int)
            self.assertIsInstance(G.classify(name), str)

    def test_the_presentation_key_is_registered(self):
        self.assertEqual(G.order_key(0), 0)
        self.assertEqual(G.order_key(1), 2654435761 % (2 ** 32))
        self.assertEqual(G.digest().__len__(), 64)

    def test_an_extra_readout_moves_the_grammar_digest(self):
        before = G.digest()
        saved = G.READOUTS
        try:
            G.READOUTS = saved + ("SQUARE",)
            self.assertNotEqual(G.digest(), before)
        finally:
            G.READOUTS = saved
        self.assertEqual(G.digest(), before)
        self.assertNotEqual(G.digest(G.readouts()), G.digest(G.readouts((25,))))


class NegativeControls(unittest.TestCase):

    def test_a_wrong_artifact_path_fails_loudly(self):
        keep = C.RUNS
        try:
            C.RUNS = os.path.join(HERE, "NO_SUCH_DIR")
            self.assertRaises(SystemExit, C.load, "scope_SIGMA_H33R.json")
        finally:
            C.RUNS = keep
        self.assertIsInstance(C.load("sources.json"), dict)

    def test_a_tampered_replay_row_breaks_the_exact_replay(self):
        rec = C.load("scope_SIGMA_H33R.json")
        t_star = rec["label_config"]["T_star"]
        name = rec["holdout"]["winner"]
        rows = [list(r) for r in rec["replay"]["held_block"]["queries"]]
        clean = C.block_errors(rows, name, t_star)
        self.assertEqual(clean, rec["replay"]["held_block"]["winner_errors"])
        idx = C._first_flippable(rows, name, t_star)
        self.assertIsNotNone(idx)
        rows[idx][1] = 1 - rows[idx][1]
        self.assertNotEqual(C.block_errors(rows, name, t_star), clean)
        hostile = C.hostile_tampered_replay(rec)
        self.assertTrue(hostile["applicable"])
        self.assertTrue(hostile["detected"])
        self.assertTrue(hostile["no_alarm_on_clean"])

    def test_a_null_seed_drift_breaks_the_registered_count(self):
        rec = C.load("scope_SIGMA_H33R.json")
        hostile = C.hostile_null_seed_drift(rec)
        self.assertTrue(hostile["detected"])
        self.assertTrue(hostile["no_alarm_on_clean"])

    def test_a_moved_raw_arm_is_caught(self):
        rec = C.load("scope_SIGMA_H33R.json")
        hostile = C.hostile_raw_arm_moved(rec)
        self.assertTrue(hostile["detected"])
        self.assertTrue(hostile["no_alarm_on_clean"])

    def test_the_design_null_is_matched_and_separating(self):
        rec = C.load("scope_SIGMA_H33R.json")
        d = rec["nulls"]["design"]
        self.assertTrue(d["gt_3x"])
        self.assertGreater(d["reassigned"], 3 * d["real"])
        self.assertTrue(d["raw_arms_invariant"])
        self.assertEqual(d["cardinality_real"], d["cardinality_reassigned"])
        self.assertLess(d["single_draw_reassigned"],
                        d["reassigned"] * 6)


class Reconciliation(unittest.TestCase):

    def setUp(self):
        self.recon = load_json("ISSUE_833_RECONCILIATION_H33_V1.json")
        self.result = load_json("RESULT_V1.json")

    def test_the_schema_and_anchor_are_the_registered_ones(self):
        self.assertEqual(self.recon["schema"], "GMI_ISSUE_RECONCILIATION_V2")
        self.assertEqual(self.recon["issue"], 833)
        self.assertEqual(self.recon["row_key"], "9e7477378715")
        self.assertEqual(self.recon["evidence"]["key"], KEY)

    def test_the_replacement_preserves_its_row_and_carries_the_key(self):
        self.assertEqual(len(self.recon["replacements"]), 1)
        entry = self.recon["replacements"][0]
        self.assertEqual(entry["old"], ROW)
        self.assertTrue(entry["new"].startswith("- [x] " +
                                                 ROW.replace("- [ ] ", "")))
        self.assertIn(KEY, entry["new"])
        self.assertIn(SIGMA, entry["new"])

    def test_the_reconciliation_closes_exactly_the_measured_row(self):
        closed = self.recon["replacements"][0]["old"].replace("- [ ] ", "")
        self.assertEqual(self.result["rows_closed"], [closed])
        self.assertEqual(self.result["rows_open"], [])
        self.assertEqual(self.recon["rows_left_open_with_attribution"], {})

    def test_no_row_outside_this_package_is_named(self):
        for entry in self.recon["replacements"]:
            self.assertEqual(entry["old"], ROW)
            for other in ("Latent-variable generative systems.",
                          "Particle/population inference.",
                          "Energy-based systems.",
                          "Evolutionary/population search.",
                          "Flow-like transport systems."):
                self.assertNotIn(other, entry["old"])
                self.assertNotIn(other, entry["new"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
