"""Tests for gmi-833-h-real-scale-particle-population-v1.

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
import grammar_pp_v1 as G          # noqa: E402
import real_scale_particle_population_v1 as C   # noqa: E402

PRIMARY = ("grammar_pp_v1", "run_real_scale_particle_population_v1",
           "real_scale_particle_population_v1")
SIGMA = "SIGMA_H19R"
ROW = "- [ ] Particle/population inference."
SOURCE_SHA = "9e66281f7e51445eab6857488ff6e3d768afffadb7fb1adbef5e4617bee4a53b"


def read(name):
    with open(os.path.join(HERE, name)) as fh:
        return fh.read()


def load_json(name):
    with open(os.path.join(HERE, name)) as fh:
        return json.load(fh)


class TwoRoutes(unittest.TestCase):

    def test_oracle_does_not_import_the_primary_executor(self):
        tree = ast.parse(read("independent_oracle_pp_v1.py"))
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
                "import independent_oracle_pp_v1;"
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
        tree = ast.parse(read("real_scale_particle_population_v1.py"))
        literals = [n.value for n in ast.walk(tree)
                    if isinstance(n, ast.Constant) and isinstance(n.value, str)]
        for text in literals:
            self.assertNotIn("research/", text)
            self.assertNotIn("..", text)
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
        self.assertIn("No neighboring row is earned here.", text)
        self.assertNotIn("- [ ] Bayesian inference/belief-state systems.", text)
        self.assertNotIn("- [ ] Probabilistic graphical models.", text)

    def test_the_slice_addenda_state_the_registered_forms(self):
        text = read("FREEZE_V1_SLICE_ADDENDUM.md")
        self.assertIn("key(i)  = (i * 2654435761) mod 2**32", text)
        self.assertIn("679124", text)
        self.assertIn("97018", text)
        self.assertIn("475,386", text)
        self.assertIn("203,738", text)
        self.assertIn("VOTE_K = 3", text)
        self.assertIn("PLUR", text)
        self.assertIn("MEM_FALLBACK", text)
        text2 = read("FREEZE_V1_SLICE_ADDENDUM_R2.md")
        self.assertIn("fit_lo", text2)
        self.assertIn("fit_hi", text2)
        self.assertIn("20260926", text2)
        self.assertIn("20260927", text2)
        self.assertIn("single-particle-store", text2)

    def test_the_first_run_receipts_are_still_committed(self):
        self.assertTrue(os.path.isfile(os.path.join(
            HERE, "REAL_RUNS", "scope_SIGMA_H19R.json")))
        self.assertTrue(os.path.isfile(os.path.join(
            HERE, "REAL_RUNS", "sources.json")))
        self.assertTrue(os.path.isfile(os.path.join(
            HERE, "REAL_RUNS", "FROZEN_PREDICTIONS_R8.json")))

    def test_the_manifest_names_the_freeze_files(self):
        man = load_json("MANIFEST_V1.json")
        self.assertEqual(man["freeze_addenda"],
                         ["FREEZE_V1_SLICE_ADDENDUM.md",
                          "FREEZE_V1_SLICE_ADDENDUM_R2.md"])
        for pin in man["freeze_pins"].values():
            self.assertEqual(len(pin), 64)
        self.assertEqual(man["row_evidence_key"], "L:17a6204cf5d5")


class Scopes(unittest.TestCase):

    def setUp(self):
        self.result = load_json("RESULT_V1.json")

    def test_no_gate_carries_a_foreign_sigma(self):
        row = self.result["rows"]["H19"]
        for gate in row["gates"]:
            self.assertEqual(gate["sigma"], SIGMA)
        self.assertTrue(self.result["no_gate_carries_a_foreign_sigma"])

    def test_no_gate_cites_a_parent_certificate(self):
        row = self.result["rows"]["H19"]
        for gate in row["gates"]:
            self.assertNotIn("SIGMA_H05R", gate["evidence"])
            self.assertNotIn("SIGMA_H06R", gate["evidence"])
            self.assertNotIn("SIGMA_H08R", gate["evidence"])
            self.assertNotIn("SIGMA_HA", gate["evidence"])
            self.assertNotIn("gmi-833-h-", gate["evidence"])

    def test_forbidden_promotions_name_cross_scope_composition(self):
        self.assertIn("CROSS_SCOPE_GATE_COMPOSITION",
                      self.result["forbidden_promotions"])
        self.assertIn("ECOLOGY_ITERATION_UNTIL_POSITIVE",
                      self.result["forbidden_promotions"])
        self.assertIn("M5", self.result["forbidden_promotions"])
        self.assertIn("INDEPENDENT_TEAM_REPLICATION",
                      self.result["forbidden_promotions"])

    def test_real_scale_thresholds_are_met(self):
        scale = self.result["scale"]
        self.assertGreaterEqual(scale["n_fit"], 100000)
        self.assertGreaterEqual(scale["n_held"], 20000)
        self.assertEqual(scale["n_fit"], 679124)
        self.assertEqual(scale["n_held"], 97018)
        self.assertEqual(scale["source_sha256"], SOURCE_SHA)

    def test_the_closed_row_has_eleven_gates_at_one_sigma(self):
        row = self.result["rows"]["H19"]
        self.assertTrue(row["complete"])
        self.assertEqual(row["supported"], 11)
        self.assertTrue(row["single_sigma"])
        self.assertEqual(row["open_gates"], [])
        self.assertEqual(row["failed_predictions"], [])
        self.assertEqual(self.result["rows_closed"], [ROW.replace("- [ ] ", "")])

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
        self.assertEqual(self.result["scale"]["n_held"], 97018)
        self.assertIsInstance(self.result["ladder"]["errors"][0], int)


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
        self.assertEqual(G.classify("PLUR"), "POPULATION_PLURALITY")
        self.assertEqual(G.classify("PLUR_W"), "POPULATION_PLURALITY")
        self.assertEqual(G.classify("LEN<=6&CNT>=3"), "THRESHOLD_CONJUNCTION")
        self.assertEqual(G.classify("C0"), "CONSTANT_ARM")
        self.assertEqual(G.classify("LEN<=10"), "DESCRIPTOR_LENGTH_THRESHOLD")
        self.assertEqual(G.classify("CNT>=1"), "STORED_EXEMPLAR_MEMBERSHIP")
        self.assertEqual(G.classify("ASSOC>=2"), "CUE_ASSOCIATION_FANOUT")
        self.assertEqual(G.classify("MEM_FALLBACK"),
                         "STORED_TABLE_READ_WITH_FALLBACK")
        self.assertEqual(G.classify("PARTICLE_1"),
                         "STORED_SINGLE_PARTICLE_READ_WITH_FALLBACK")
        self.assertEqual(G.classify("PREF_VOTE"), "NEIGHBORHOOD_MAJORITY_VOTE")
        self.assertRaises(ValueError, G.classify, "SQUARE")

    def test_the_language_is_closed_and_outcome_free(self):
        self.assertIn("PLUR", G.READOUTS)
        self.assertIn("PLUR_W", G.READOUTS)
        self.assertIn("PARTICLE_1", G.READOUTS)
        self.assertIn("MEM_FALLBACK", G.READOUTS)
        self.assertIn("LEN<=9&CNT>=1", G.READOUTS)
        self.assertNotIn("SQUARE", G.READOUTS)
        self.assertNotIn("RETRIEVE", G.READOUTS)
        self.assertEqual(len(G.READOUTS), 63)
        self.assertEqual(G.VOTE_K, 3)
        self.assertEqual(G.MIN_POP, 2)

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

    def test_the_plurality_reads_are_exact_on_planted_tallies(self):
        def d(name, **kw):
            f = {"ql": 10, "cnt": 0, "fanout": 0, "in_store": 0, "p1": 0,
                 "p0": 0, "e1": 0, "e0": 0, "n1": 0, "n0": 0, "nw1": 0,
                 "nw0": 0, "m1": 0, "m0": 0, "one_vote": -1}
            f.update(kw)
            return C.decision(name, f["ql"], f["cnt"], f["fanout"], f["in_store"],
                              f["p1"], f["p0"], f["e1"], f["e0"], f["n1"],
                              f["n0"], f["nw1"], f["nw0"], f["m1"], f["m0"],
                              f["one_vote"])
        # the plurality over the stored particles' full votes
        self.assertEqual(d("PLUR", n1=2, n0=1), 1)
        self.assertEqual(d("PLUR", n1=1, n0=2), 0)
        self.assertEqual(d("PLUR", n1=1, n0=1), 0)         # a tie is negative
        self.assertEqual(d("PLUR", n1=0, n0=0), 1)         # empty -> fit majority
        # the count-weighted plurality is a different aggregation
        self.assertEqual(d("PLUR_W", nw1=1, nw0=3), 0)
        self.assertEqual(d("PLUR_W", nw1=3, nw0=1), 1)
        # the stored-table read is two-valued and only fires for a stored query
        self.assertEqual(d("MEM_FALLBACK", in_store=1, m1=2, m0=1), 1)
        self.assertEqual(d("MEM_FALLBACK", in_store=1, m1=1, m0=2), 0)
        self.assertEqual(d("MEM_FALLBACK", in_store=0, m1=9, m0=0), 1)
        # the one-particle read needs a stored query and a stored particle
        self.assertEqual(d("PARTICLE_1", in_store=1, one_vote=0), 0)
        self.assertEqual(d("PARTICLE_1", in_store=1, one_vote=1), 1)
        self.assertEqual(d("PARTICLE_1", in_store=1, one_vote=-1), 1)
        self.assertEqual(d("PARTICLE_1", in_store=0, one_vote=0), 1)
        # a conjunction fires iff every conjunct fires
        self.assertEqual(d("LEN<=6&CNT>=3", ql=5, cnt=3), 1)
        self.assertEqual(d("LEN<=6&CNT>=3", ql=7, cnt=3), 0)
        self.assertEqual(d("LEN<=6&CNT>=3", ql=5, cnt=2), 0)


class NegativeControls(unittest.TestCase):

    def test_a_wrong_artifact_path_fails_loudly(self):
        keep = C.RUNS
        try:
            C.RUNS = os.path.join(HERE, "NO_SUCH_DIR")
            self.assertRaises(SystemExit, C.load, "scope_SIGMA_H19R.json")
        finally:
            C.RUNS = keep
        self.assertIsInstance(C.load("sources.json"), dict)

    def test_a_tampered_replay_row_breaks_the_exact_replay(self):
        rec = C.load("scope_SIGMA_H19R.json")
        rows = [list(r) for r in rec["replay"]["held_block"]["queries"]]
        clean = C.block_errors(rows, "PLUR")
        rows[0][1] = 1 - rows[0][1]
        dirty = C.block_errors(rows, "PLUR")
        self.assertEqual(clean, rec["replay"]["held_block"]["winner_errors"])
        self.assertNotEqual(dirty, clean)

    def test_a_null_seed_drift_breaks_the_registered_count(self):
        rec = C.load("scope_SIGMA_H19R.json")
        self.assertEqual(C.hostile_null_seed_drift(rec)["detected"], True)

    def test_the_frozen_prediction_record_is_honoured(self):
        rec = C.load("scope_SIGMA_H19R.json")
        frozen = C.check_frozen(rec)
        self.assertTrue(frozen["present"])
        self.assertTrue(frozen["matches"])


class Reconciliation(unittest.TestCase):

    def setUp(self):
        self.recon = load_json("ISSUE_833_RECONCILIATION_H19_V1.json")
        self.result = load_json("RESULT_V1.json")

    def test_the_schema_and_anchor_are_the_registered_ones(self):
        self.assertEqual(self.recon["schema"], "GMI_ISSUE_RECONCILIATION_V2")
        self.assertEqual(self.recon["issue"], 833)
        for entry in self.recon["replacements"]:
            self.assertTrue(entry["anchor"].startswith("# H. "))

    def test_only_rows_the_result_closed_appear_as_replacements(self):
        closed = set(self.result["rows_closed"])
        for entry in self.recon["replacements"]:
            row = entry["old"].replace("- [ ] ", "")
            self.assertIn(row, closed)
            self.assertTrue(entry["new"].startswith("- [x] " + row))
            self.assertIn("L:17a6204cf5d5", entry["new"])

    def test_the_annotation_fits_the_measured_body_budget(self):
        budget = self.recon["annotation_budget"]["measured_payload_limit_characters"]
        self.assertGreaterEqual(budget, 2143)
        for entry in self.recon["replacements"]:
            parts = entry["new"].split(u" — ✅ ", 1)
            self.assertEqual(len(parts), 2, entry["new"])
            self.assertLessEqual(len(parts[1]), budget, parts[1])

    def test_no_row_outside_the_freeze_is_touched(self):
        for entry in self.recon["replacements"]:
            self.assertEqual(entry["old"], ROW)


if __name__ == "__main__":
    unittest.main(verbosity=2)
