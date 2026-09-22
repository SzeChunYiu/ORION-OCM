"""Tests for gmi-833-h-real-scale-belief-state-v1.

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
import grammar_bs_v1 as G                  # noqa: E402
import real_scale_belief_state_v1 as C     # noqa: E402

PRIMARY = ("grammar_bs_v1", "run_real_scale_belief_state_v1",
           "real_scale_belief_state_v1")
SIGMA = "SIGMA_H17R"
ROW = "- [ ] Bayesian inference/belief-state systems."
SOURCE_SHA = "9e66281f7e51445eab6857488ff6e3d768afffadb7fb1adbef5e4617bee4a53b"
KEY = "L:a4efd89ed9a9"


def read(name):
    with open(os.path.join(HERE, name)) as fh:
        return fh.read()


def load_json(name):
    with open(os.path.join(HERE, name)) as fh:
        return json.load(fh)


class TwoRoutes(unittest.TestCase):

    def test_oracle_does_not_import_the_primary_executor(self):
        tree = ast.parse(read("independent_oracle_bs_v1.py"))
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
                "import independent_oracle_bs_v1;"
                "print(','.join(m for m in %r if m in sys.modules))"
                % (HERE, PRIMARY))
        out = subprocess.check_output([sys.executable, "-I", "-B", "-c", code],
                                      cwd=HERE).decode().strip()
        self.assertEqual(out, "")

    def test_oracle_agrees(self):
        oracle = load_json("ORACLE_RESULT_V1.json")
        self.assertTrue(oracle["agrees"])
        self.assertFalse(oracle["imports_primary_executor"])
        for name, ok in oracle["checks"].items():
            self.assertTrue(ok, name)

    def test_the_checker_reads_no_parent_result_file(self):
        tree = ast.parse(read("real_scale_belief_state_v1.py"))
        literals = [n.value for n in ast.walk(tree)
                    if isinstance(n, ast.Constant) and isinstance(n.value, str)]
        for text in literals:
            self.assertNotIn("research/", text)
        roots = set()
        for node in ast.walk(tree):
            if (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                    and node.func.id == "open"):
                roots.add(ast.dump(node.args[0])[:24])
        self.assertTrue(roots)


class Custody(unittest.TestCase):

    def test_the_freeze_names_exactly_the_one_row(self):
        text = read("FREEZE_V1.md")
        self.assertIn(ROW, text)
        self.assertIn("No neighboring row is earned here, and this package "
                      "closes nothing.", text)
        self.assertNotIn("- [ ] Associative memory.", text)
        self.assertNotIn("- [ ] Decision trees/rule systems.", text)
        self.assertNotIn("- [ ] Model-free RL-like learning.", text)

    def test_the_freeze_declares_the_row_open(self):
        text = read("FREEZE_V1.md")
        self.assertIn("ROW_LEFT_OPEN", text)
        self.assertIn("The row\nstays open.", text)
        self.assertIn("this package closes nothing", text)

    def test_the_slice_addendum_states_the_registered_forms(self):
        text = read("FREEZE_V1_SLICE_ADDENDUM_H17_V1.md")
        self.assertIn("key(i)  = (i * 2654435761) mod 2**32", text)
        self.assertIn("679124", text)
        self.assertIn("97018", text)
        self.assertIn("475,386", text)
        self.assertIn("203,738", text)
        self.assertIn("MEM_FALLBACK", text)
        self.assertIn("WPAIR", text)
        self.assertIn("20260930", text)
        self.assertIn("20260931", text)

    def test_the_first_run_receipts_are_still_committed(self):
        self.assertTrue(os.path.isfile(os.path.join(
            HERE, "REAL_RUNS", "scope_SIGMA_H17R.json")))
        self.assertTrue(os.path.isfile(os.path.join(
            HERE, "REAL_RUNS", "sources.json")))

    def test_the_manifest_names_the_freeze_files(self):
        man = load_json("MANIFEST_V1.json")
        self.assertEqual(man["freeze_addenda"],
                         ["FREEZE_V1_SLICE_ADDENDUM_H17_V1.md"])
        for pin in man["freeze_pins"].values():
            self.assertEqual(len(pin), 64)
        self.assertEqual(man["scopes"], {"SIGMA_H17R": ROW.replace("- [ ] ", "")})

    def test_the_manifest_excludes_the_adjacent_scope(self):
        man = load_json("MANIFEST_V1.json")
        self.assertIn("SIGMA_H15R", man["scope_exclusions"])
        self.assertNotIn("SIGMA_H15R", man["scopes"])

    def test_the_boundary_documents_are_committed(self):
        self.assertTrue(os.path.isfile(os.path.join(
            HERE, "F15_EARNED_BOUNDARY_V1.md")))
        self.assertTrue(os.path.isfile(os.path.join(
            HERE, "CORRECTED_CLAIM_V1.md")))


class Scopes(unittest.TestCase):

    def setUp(self):
        self.result = load_json("RESULT_V1.json")

    def test_no_gate_carries_a_foreign_sigma(self):
        row = self.result["rows"]["H17"]
        for gate in row["gates"]:
            self.assertEqual(gate["sigma"], SIGMA)
        self.assertTrue(self.result["no_gate_carries_a_foreign_sigma"])

    def test_no_gate_cites_a_parent_certificate(self):
        row = self.result["rows"]["H17"]
        for gate in row["gates"]:
            self.assertNotIn("SIGMA_H15R", gate["evidence"])
            self.assertNotIn("SIGMA_H05R", gate["evidence"])
            self.assertNotIn("SIGMA_H06R", gate["evidence"])
            self.assertNotIn("SIGMA_H08R", gate["evidence"])
            self.assertNotIn("gmi-833-h-", gate["evidence"])

    def test_the_row_is_not_closed(self):
        row = self.result["rows"]["H17"]
        self.assertFalse(row["closed"])
        self.assertEqual(self.result["rows_closed"], [])
        self.assertEqual(self.result["rows_open"], [ROW.replace("- [ ] ", "")])
        self.assertIn("ROW_LEFT_OPEN", self.result["claim_ceiling"])

    def test_forbidden_promotions_name_the_boundary_risks(self):
        for name in ("CROSS_SCOPE_GATE_COMPOSITION", "ROW_CLOSED_BY_MEASUREMENT",
                     "BOUNDARY_IS_A_RECOVERY", "RAW_COUNT_ARM_IS_THE_FAMILY",
                     "ECOLOGY_ITERATION_UNTIL_POSITIVE"):
            self.assertIn(name, self.result["forbidden_promotions"])

    def test_real_scale_thresholds_are_met(self):
        scale = self.result["scale"]
        self.assertGreaterEqual(scale["n_fit"], 100000)
        self.assertGreaterEqual(scale["n_held"], 20000)
        self.assertEqual(scale["n_fit"], 679124)
        self.assertEqual(scale["n_held"], 97018)
        self.assertEqual(scale["source_sha256"], SOURCE_SHA)
        self.assertEqual(scale["duplicate_tokens"], 0)
        self.assertEqual(scale["label_t_star"], 8)

    def test_every_hostile_is_applicable_and_detected(self):
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
        # the crossover is registered as an exact inequality over the receipt's
        # own integers: m* is the smallest m with 2m > V + 27.
        rec = C.load("scope_SIGMA_H17R.json")
        co = rec["crossover"]
        for value in (co["V"], co["alphabet_width"], co["index_cost"],
                      co["m_star"], co["scan_cost_at_m_star"]):
            self.assertIsInstance(value, int)
        self.assertTrue(self.result["crossover"]["matches_registered_arithmetic"])
        self.assertGreater(2 * co["m_star"], co["V"] + co["alphabet_width"])
        self.assertLessEqual(2 * (co["m_star"] - 1), co["V"] + co["alphabet_width"])
        self.assertEqual(co["m_star"], 110799)
        self.assertEqual(co["V"], 221569)

    def test_the_measured_class_is_not_the_intended_class(self):
        row = self.result["rows"]["H17"]
        self.assertEqual(row["measured_class"], "STORED_LABEL_READ_WITH_FALLBACK")
        self.assertEqual(row["intended_class"], "WEIGHTED_EVIDENCE_BELIEF")
        self.assertNotEqual(row["measured_class"], row["intended_class"])

    def test_the_registered_falsifier_that_fired_is_reported(self):
        fals = self.result["registered_falsifier_3"]
        self.assertTrue(fals["falsifier_3_fired"])
        self.assertEqual(fals["full_source_optimum_errors"], 0)
        self.assertLessEqual(fals["full_source_optimum_errors"],
                             fals["half_majority"])
        self.assertTrue(self.result["verdict"].endswith(
            "REGISTERED_FALSIFIER_3_FIRED"))

    def test_the_adjacent_scoped_positive_is_not_claimed_for_the_row(self):
        sc = self.result["rows"]["H17"]["adjacent_scoped_positive"]
        self.assertFalse(sc["claimed_for_this_row"])
        self.assertTrue(sc["class_sharing"])
        self.assertTrue(sc["held"]["f1_holds"])
        self.assertEqual(sc["n_held"], 75618)
        self.assertEqual(sc["n_held_full"], 97018)
        self.assertEqual(sc["held"]["winner_class"],
                         "STORED_LABEL_READ_WITH_FALLBACK")
        self.assertEqual(sc["held"]["winner_errors"], 917)
        self.assertEqual(sc["held"]["majority_errors"], 8399)
        # all four stages of the registered winner rule agree on the class
        for stage in ("rank", "held", "regen_lo", "regen_hi"):
            self.assertEqual(sc[stage]["winner_class"],
                             "STORED_LABEL_READ_WITH_FALLBACK", stage)


class SliceRule(unittest.TestCase):

    def test_the_permutation_and_slices_are_exact(self):
        n_fit = (776142 * 7) // 8
        self.assertEqual(n_fit, 679124)
        self.assertEqual(776142 - n_fit, 97018)
        self.assertEqual((7 * n_fit) // 10, 475386)
        self.assertEqual(n_fit - (7 * n_fit) // 10, 203738)
        self.assertEqual(n_fit // 2, 339562)
        keyed = sorted(range(776142), key=lambda i: (i * 2654435761) % (2 ** 32))
        self.assertEqual(len(keyed), 776142)
        self.assertEqual([(i * 2654435761) % (2 ** 32) for i in keyed],
                         sorted((i * 2654435761) % (2 ** 32)
                                for i in range(776142)))
        self.assertEqual(keyed[:n_fit] + keyed[n_fit:], keyed)


class GrammarAndReadouts(unittest.TestCase):

    def test_the_classifier_reads_the_name_alone(self):
        self.assertEqual(G.classify("WPAIR>=3_12"),
                         "WEIGHTED_EVIDENCE_BELIEF")
        self.assertEqual(G.classify("WDOM>=4"), "WEIGHTED_EVIDENCE_BELIEF")
        self.assertEqual(G.classify("WSUM>=16"), "WEIGHTED_EVIDENCE_BELIEF")
        self.assertEqual(G.classify("C0"), "CONSTANT_ARM")
        self.assertEqual(G.classify("LEN<=9"), "DESCRIPTOR_LENGTH_THRESHOLD")
        self.assertEqual(G.classify("CNT>=1"), "STORE_MEMBERSHIP_COUNT")
        self.assertEqual(G.classify("EXT>=2"), "EXTENSION_COUNT")
        self.assertEqual(G.classify("MEM_FALLBACK"),
                         "STORED_LABEL_READ_WITH_FALLBACK")
        self.assertRaises(ValueError, G.classify, "SQUARE")

    def test_the_costs_are_registered(self):
        self.assertEqual(G.cost("C0"), 0)
        self.assertEqual(G.cost("LEN<=9"), 0)
        self.assertEqual(G.cost("EXT>=2"), 1)
        self.assertEqual(G.cost("WPAIR>=3_12"), 1)
        self.assertEqual(G.cost("MEM_FALLBACK"), 2)

    def test_the_language_is_closed_and_outcome_free(self):
        self.assertIn("WPAIR>=3_12", G.READOUTS)
        self.assertIn("MEM_FALLBACK", G.READOUTS)
        self.assertNotIn("SQUARE", G.READOUTS)
        self.assertNotIn("RETRIEVE", G.READOUTS)
        # the registered language is exactly the addendum's table:
        # 2 constants + 7 LEN + 3 CNT + 4 EXT + 8 WSUM + 8 WMAX + 6 WAVG
        # + 7 WDOM + 42 WPAIR + MEM_FALLBACK = 88 arms.
        self.assertEqual(len(G.READOUTS), 88)
        self.assertEqual(len(set(G.READOUTS)), 88)
        self.assertEqual(sum(1 for n in G.READOUTS if G.is_weighted(n)), 71)
        self.assertEqual(sum(1 for n in G.READOUTS
                              if G.classify(n) == "WEIGHTED_EVIDENCE_BELIEF"),
                         71)
        self.assertEqual(sum(1 for n in G.READOUTS
                              if n.startswith("EXT>=")), 4)
        self.assertEqual(sum(1 for n in G.READOUTS
                              if n.startswith("WPAIR>=")), 42)
        for name in G.READOUTS:
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


class NegativeControls(unittest.TestCase):

    def test_a_wrong_artifact_path_fails_loudly(self):
        keep = C.RUNS
        try:
            C.RUNS = os.path.join(HERE, "NO_SUCH_DIR")
            self.assertRaises(SystemExit, C.load, "scope_SIGMA_H17R.json")
        finally:
            C.RUNS = keep
        self.assertIsInstance(C.load("sources.json"), dict)

    def test_a_tampered_replay_row_breaks_the_exact_replay(self):
        rec = C.load("scope_SIGMA_H17R.json")
        name = rec["holdout"]["winner"]
        rows = [list(r) for r in rec["replay"]["held_block"]["queries"]]
        clean = C.block_errors(rows, name)
        self.assertEqual(clean, rec["replay"]["held_block"]["winner_errors"])
        idx = C._first_flippable(rows, name)
        self.assertIsNotNone(idx)
        rows[idx][1] = 1 - rows[idx][1]
        dirty = C.block_errors(rows, name)
        self.assertNotEqual(dirty, clean)
        # and the hostile that does this is applicable on the clean receipt
        hostile = C.hostile_tampered_replay(rec)
        self.assertTrue(hostile["applicable"])
        self.assertTrue(hostile["detected"])
        self.assertTrue(hostile["no_alarm_on_clean"])

    def test_a_null_seed_drift_breaks_the_registered_count(self):
        rec = C.load("scope_SIGMA_H17R.json")
        self.assertEqual(C.hostile_null_seed_drift(rec)["detected"], True)

    def test_a_moved_raw_arm_is_caught(self):
        rec = C.load("scope_SIGMA_H17R.json")
        self.assertEqual(C.hostile_raw_arm_moved(rec)["detected"], True)
        self.assertTrue(C.hostile_raw_arm_moved(rec)["no_alarm_on_clean"])


class Reconciliation(unittest.TestCase):

    def setUp(self):
        self.recon = load_json("ISSUE_833_RECONCILIATION_H17_V1.json")
        self.result = load_json("RESULT_V1.json")

    def test_the_schema_and_anchor_are_the_registered_ones(self):
        self.assertEqual(self.recon["schema"], "GMI_ISSUE_RECONCILIATION_V2")
        self.assertEqual(self.recon["issue"], 833)
        self.assertEqual(self.recon["replacements"], [])
        self.assertEqual(self.recon["row_key"], "a4efd89ed9a9")
        self.assertEqual(self.recon["evidence"]["key"], KEY)

    def test_the_reconciliation_closes_nothing(self):
        self.assertEqual(self.result["rows_closed"], [])
        self.assertEqual(self.recon["replacements"], [])
        for row in self.recon["rows_left_open_with_attribution"]:
            self.assertIn(row, self.result["rows_open"])

    def test_the_open_row_carries_its_attribution_and_its_key(self):
        entry = self.recon["rows_left_open_with_attribution"][
            "Bayesian inference/belief-state systems."]
        self.assertEqual(entry["row_text"], "Bayesian inference/belief-state systems.")
        self.assertEqual(entry["key"], KEY)
        self.assertIsNone(entry["replacement"])
        self.assertIn("STORED_LABEL_READ_WITH_FALLBACK", entry["attribution"])
        self.assertIn("WEIGHTED_EVIDENCE_BELIEF", entry["attribution"])

    def test_no_row_outside_this_package_is_named(self):
        for row in self.recon["rows_left_open_with_attribution"]:
            self.assertEqual(row, "Bayesian inference/belief-state systems.")


if __name__ == "__main__":
    unittest.main(verbosity=2)
