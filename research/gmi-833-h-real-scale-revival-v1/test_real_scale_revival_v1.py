"""Tests for gmi-833-h-real-scale-revival-v1.

Runs under `python3 -I -B` and `python3 -I -O -B`. Every check is a unittest
assertion method, never a bare `assert` statement, so `-O` cannot strip it.
"""
from fractions import Fraction as Q
import ast
import json
import os
import subprocess
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import grammar_s_v1 as G
import real_scale_revival_v1 as C

PRIMARY = ("grammar_s_v1", "run_real_scale_revival_v1", "real_scale_revival_v1")
SCOPES = ("R02", "R03", "R04")
OWN_SIGMA = set(["SIGMA_R02", "SIGMA_R03", "SIGMA_R04"])
ROWS = ("- [ ] Linear regression / linear classifiers.",
        "- [ ] GLMs.",
        "- [ ] Basis/kernel methods.")


def read(name):
    with open(os.path.join(HERE, name)) as fh:
        return fh.read()


def load_json(name):
    with open(os.path.join(HERE, name)) as fh:
        return json.load(fh)


class TwoRoutes(unittest.TestCase):

    def test_oracle_does_not_import_the_primary_executor(self):
        tree = ast.parse(read("independent_oracle_v1.py"))
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
                "import independent_oracle_v1;"
                "print(','.join(m for m in %r if m in sys.modules))"
                % (HERE, PRIMARY))
        out = subprocess.check_output([sys.executable, "-I", "-B", "-c", code],
                                      cwd=HERE).decode().strip()
        self.assertEqual(out, "")

    def test_oracle_agrees_on_every_scope(self):
        oracle = load_json("ORACLE_RESULT_V1.json")
        for key in SCOPES:
            self.assertTrue(oracle["scopes"][key]["exact_replay_sse_matches"])
            self.assertTrue(oracle["scopes"][key]["class_matches"])
            self.assertTrue(oracle["scopes"][key]["agrees"], key)

    def test_the_checker_reads_no_parent_result_file(self):
        text = read("real_scale_revival_v1.py")
        for needle in ("gmi-833-h-neutral-four-family-v1",
                       "gmi-833-h-real-scale-classical-v1",
                       "gmi-833-h-family-requirement-ledger-v1"):
            self.assertNotIn(needle + "/RESULT", text)


class Custody(unittest.TestCase):

    def test_the_freeze_names_exactly_the_three_rows(self):
        text = read("FREEZE_V1.md")
        for row in ROWS:
            self.assertIn(row, text)
        self.assertIn("No neighboring row is earned here.", text)
        self.assertNotIn("- [ ] Finite-state/automata intelligence.", text)

    def test_the_arithmetic_addendum_changes_no_prediction(self):
        text = read("FREEZE_V1_ARITHMETIC_ADDENDUM.md")
        self.assertIn("No prediction of section 8 changes.", text)
        self.assertIn("Fraction(round(x * 10**9), 10**9)", text)

    def test_the_obstruction_note_closes_nothing(self):
        text = read("SECTION_H_RESIDUAL_OBSTRUCTION_V1.md")
        self.assertNotIn("- [x]", text)
        self.assertIn("closes no checkbox", text)


class Scopes(unittest.TestCase):

    def setUp(self):
        self.result = load_json("RESULT_V1.json")

    def test_no_gate_carries_a_foreign_sigma(self):
        for key in SCOPES:
            row = self.result["rows"][key]
            for gate in row["gates"]:
                self.assertIn(gate["sigma"], OWN_SIGMA)
                self.assertEqual(gate["sigma"], row["sigma"])
        self.assertTrue(self.result["no_gate_carries_a_foreign_sigma"])

    def test_no_gate_cites_a_parent_certificate(self):
        for key in SCOPES:
            for gate in self.result["rows"][key]["gates"]:
                self.assertNotIn("SIGMA_4F", gate["evidence"])
                self.assertNotIn("SIGMA_H0", gate["evidence"])
                self.assertNotIn("gmi-833-h-", gate["evidence"])

    def test_forbidden_promotions_name_cross_scope_composition(self):
        self.assertIn("CROSS_SCOPE_GATE_COMPOSITION",
                      self.result["forbidden_promotions"])
        self.assertIn("REGISTERED_CONTROL_SUBSTITUTION",
                      self.result["forbidden_promotions"])
        self.assertIn("M5", self.result["forbidden_promotions"])
        self.assertIn("INDEPENDENT_TEAM_REPLICATION",
                      self.result["forbidden_promotions"])

    def test_real_scale_thresholds_are_met_at_every_scope(self):
        for key in SCOPES:
            self.assertGreaterEqual(self.result["scale"][key]["n_fit"], 100000)
            self.assertGreaterEqual(self.result["scale"][key]["n_held"], 20000)

    def test_every_hostile_is_applicable_and_detected(self):
        for hostile in self.result["hostiles"]:
            self.assertTrue(hostile["applicable"], hostile["hostile"])
            self.assertTrue(hostile["detected"], hostile["hostile"])
            self.assertTrue(hostile["no_alarm_on_clean"], hostile["hostile"])

    def test_every_claimed_quantity_is_exact(self):
        for key in SCOPES:
            row = self.result["rows"][key]
            self.assertTrue(C.exact_string(row["n_fit"]))
            for name in ("m_star",):
                value = row["crossover"].get(name)
                if value is not None:
                    self.assertTrue(C.exact_string(value))
        for name, pred in self.result["predictions"].items():
            self.assertIsInstance(pred["held"], bool)

    def test_a_closed_row_has_eleven_gates_at_one_sigma(self):
        for key in SCOPES:
            row = self.result["rows"][key]
            if row["complete"]:
                self.assertEqual(row["supported"], 11)
                self.assertTrue(row["single_sigma"])
                self.assertEqual(row["open_gates"], [])
                self.assertEqual(row["failed_predictions"], [])

    def test_an_open_row_names_its_failure(self):
        for key in SCOPES:
            row = self.result["rows"][key]
            if not row["complete"]:
                self.assertTrue(row["open_gates"])


class SliceRule(unittest.TestCase):

    def test_the_partition_is_exact_and_the_slices_are_disjoint(self):
        for n in (1000, 265641, 614233):
            counts = C.slices_of(n)
            self.assertEqual(counts["search"] + counts["held"] + counts["fit"], n)
            self.assertEqual(counts["search"], sum(1 for i in range(n) if i % 7 == 5))
            self.assertEqual(counts["held"], sum(1 for i in range(n) if i % 7 == 6))
            overlap = [i for i in range(n)
                       if i % 7 in (0, 1, 2, 3) and i % 7 in (5, 6)]
            self.assertEqual(overlap, [])

    def test_the_regeneration_slices_never_touch_the_held_out_slice(self):
        n = 100000
        regen = set(i for i in range(n) if i % 7 in (0, 1, 2, 3))
        held = set(i for i in range(n) if i % 7 == 6)
        search = set(i for i in range(n) if i % 7 == 5)
        self.assertEqual(regen & held, set())
        self.assertEqual(regen & search, set())


class GrammarAndClassifier(unittest.TestCase):

    def test_the_classifier_priority_is_the_frozen_one(self):
        arg = ("LEAF", "ARG")
        param = ("LEAF", "PARAM")
        s = ("LEAF", "S")
        bias = ("LEAF", "BIAS")
        state = ("LEAF", "STATE")
        affine_body = ("MUL", arg, param)
        affine_head = ("ADD", s, bias)
        self.assertEqual(G.classify(affine_body, affine_head)["class"],
                         "AFFINE_SCORE")
        self.assertEqual(G.classify(affine_body, ("MUL", s, s))["class"],
                         "NONLINEAR_LINK")
        self.assertEqual(G.classify(("MUL", ("STEP", arg), param),
                                    affine_head)["class"], "LIFTED_BASIS")
        self.assertEqual(G.classify(affine_body, ("ADD", s, state))["class"],
                         "PERSISTENT_STATE")
        # state dominates a lifted body, which is the frozen priority
        self.assertEqual(G.classify(("STEP", arg), ("ADD", s, state))["class"],
                         "PERSISTENT_STATE")

    def test_the_classifier_refuses_a_family_label(self):
        self.assertRaises(TypeError, G.classify, "GLMs.", "Linear regression")

    def test_an_extra_operation_moves_the_grammar_digest(self):
        before = G.digest()
        saved = G.UNARY_OPS
        try:
            G.UNARY_OPS = saved + ("SQUARE",)
            self.assertNotEqual(G.digest(), before)
        finally:
            G.UNARY_OPS = saved
        self.assertEqual(G.digest(), before)

    def test_the_enumeration_is_complete_and_response_independent(self):
        trees = G.all_trees(2, ("ARG", "PARAM"))
        rendered = set(G.show(t) for t in trees)
        self.assertIn("ARG", rendered)
        self.assertIn("NEG(ARG)", rendered)
        self.assertIn("STEP(PARAM)", rendered)
        self.assertEqual(len(trees), len(set(G.show(t) for t in trees)))

    def test_every_denotation_is_total_on_the_probe_grid(self):
        for tree in G.all_trees(2, G.BODY_LEAVES):
            for point in G.body_grid()[:8]:
                self.assertIsInstance(G.value(tree, point), Q)

    def test_the_cost_model_crosses_over_and_the_crossover_is_tight(self):
        body = ("MUL", ("LEAF", "ARG"), ("LEAF", "PARAM"))
        head = ("ADD", ("LEAF", "S"), ("LEAF", "BIAS"))
        m = G.table_crossover(body, head, False)
        self.assertIsNotNone(m)
        self.assertGreater(G.table_cost(m)["total"],
                           G.program_cost(body, head, m, False)["total"])
        if m > 1:
            self.assertLessEqual(G.table_cost(m - 1)["total"],
                                 G.program_cost(body, head, m - 1, False)["total"])


class NegativeControls(unittest.TestCase):

    def test_a_wrong_artifact_path_fails_loudly(self):
        keep = C.RUNS
        try:
            C.RUNS = os.path.join(HERE, "NO_SUCH_DIR")
            self.assertRaises(SystemExit, C.load, "sources.json")
        finally:
            C.RUNS = keep
        self.assertIsInstance(C.load("sources.json"), dict)

    def test_a_tampered_replay_row_breaks_the_exact_replay(self):
        rec = C.load("scope_R02.json")
        clean, _ = C.replay_scope(rec)
        dirty, _ = C.replay_scope(rec, tamper=0)
        self.assertEqual(clean, Q(rec["replay"]["partial_sse"]))
        self.assertNotEqual(dirty, clean)

    def test_a_float_in_a_claimed_quantity_is_caught(self):
        self.assertTrue(C.exact_string("3/4"))
        self.assertTrue(C.exact_string(17))
        self.assertFalse(C.exact_string(0.75))
        self.assertFalse(C.exact_string(True))


class Reconciliation(unittest.TestCase):

    def setUp(self):
        self.recon = load_json("ISSUE_833_RECONCILIATION_H2_V1.json")
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

    def test_every_open_row_is_reported_with_an_attribution(self):
        for row in self.result["rows_open"]:
            found = [k for k in self.recon["rows_left_open_with_attribution"]
                     if self.recon["rows_left_open_with_attribution"][k]["row"] == row]
            self.assertTrue(found, row)

    def test_no_row_outside_the_freeze_is_touched(self):
        allowed = set(r.replace("- [ ] ", "") for r in ROWS)
        for entry in self.recon["replacements"]:
            self.assertIn(entry["old"].replace("- [ ] ", ""), allowed)


if __name__ == "__main__":
    unittest.main(verbosity=2)
