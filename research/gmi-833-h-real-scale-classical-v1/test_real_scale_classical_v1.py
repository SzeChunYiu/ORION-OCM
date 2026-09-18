"""Tests for gmi-833-h-real-scale-classical-v1. Stdlib only.

    python3 -I -B  test_real_scale_classical_v1.py -v
    python3 -I -O -B test_real_scale_classical_v1.py -v

Uses unittest (not bare `assert`) so that -O does not strip the checks.
"""
import ast
import json
import os
import subprocess
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import grammar_v1 as G                     # noqa: E402
import real_scale_classical_v1 as C        # noqa: E402
import independent_oracle_v1 as O          # noqa: E402

RUNS = os.path.join(HERE, "REAL_RUNS")
EXACT_FILES = ("grammar_v1.py", "real_scale_classical_v1.py",
               "independent_oracle_v1.py")


def jload(p):
    with open(p) as f:
        return json.load(f)


class Grammar(unittest.TestCase):
    def test_digest_is_stable(self):
        self.assertEqual(G.grammar_digest(), G.grammar_digest())
        self.assertEqual(len(G.grammar_digest()), 64)

    def test_enumeration_matches_independent_closed_form(self):
        nb, _ = O.cardinality(G.BODY_MAX_NODES, len(G.BODY_LEAVES))
        nh, _ = O.cardinality(G.HEAD_MAX_NODES, len(G.HEAD_LEAVES))
        self.assertEqual(len(G.enumerate_exprs(G.BODY_MAX_NODES, G.BODY_LEAVES)), nb)
        self.assertEqual(len(G.enumerate_exprs(G.HEAD_MAX_NODES, G.HEAD_LEAVES)), nh)

    def test_quotient_is_a_refinement(self):
        raw = G.enumerate_exprs(G.BODY_MAX_NODES, G.BODY_LEAVES)
        reps, den, nr, nc = G.quotient(raw, G.body_probe_points())
        self.assertEqual(nr, len(raw))
        self.assertEqual(len(reps), nc)
        self.assertLessEqual(nc, nr)

    def test_classifier_positives_and_negatives(self):
        aff = G.classify(("MUL", ("L", "ARG"), ("L", "PARAM")),
                         ("ADD", ("L", "S"), ("L", "BIAS")))
        self.assertEqual(aff["class"], "AFFINE_SCORE")
        st = G.classify(("MUL", ("L", "ARG"), ("L", "PARAM")),
                        ("ADD", ("L", "S"), ("STEP", ("L", "STATE"))))
        self.assertEqual(st["class"], "PERSISTENT_STATE")
        lift = G.classify(("ABS", ("L", "ARG")), ("ADD", ("L", "S"), ("L", "BIAS")))
        self.assertEqual(lift["class"], "LIFTED_BASIS")
        link = G.classify(("MUL", ("L", "ARG"), ("L", "PARAM")),
                          ("ABS", ("ADD", ("L", "S"), ("L", "BIAS"))))
        self.assertEqual(link["class"], "NONLINEAR_LINK")

    def test_classifier_agrees_with_the_oracle(self):
        for b, h in (("MUL(ARG,PARAM)", "ADD(S,BIAS)"),
                     ("MUL(ARG,PARAM)", "ADD(S,STEP(STATE))"),
                     ("ABS(ARG)", "ADD(S,BIAS)"),
                     ("MUL(ARG,PARAM)", "ABS(ADD(S,BIAS))")):
            p = G.classify(C.parse_expr(b), C.parse_expr(h))
            o = O.classify(b, h)
            self.assertEqual(p["class"], o["class"], (b, h))

    def test_crossover_is_the_smallest(self):
        b = ("MUL", ("L", "ARG"), ("L", "PARAM"))
        h = ("ADD", ("L", "S"), ("L", "BIAS"))
        m = G.table_crossover(b, h, False)
        self.assertIsNotNone(m)
        self.assertGreater(G.table_cost(m)["total"],
                           G.program_cost(b, h, m, False)["total"])
        for k in range(1, m):
            self.assertLessEqual(G.table_cost(k)["total"],
                                 G.program_cost(b, h, k, False)["total"])


class Independence(unittest.TestCase):
    def test_oracle_imports_nothing_from_this_package(self):
        src = open(os.path.join(HERE, "independent_oracle_v1.py")).read()
        local = set(f[:-3] for f in os.listdir(HERE) if f.endswith(".py"))
        local.discard("independent_oracle_v1")
        bad = []
        for node in ast.walk(ast.parse(src)):
            if isinstance(node, ast.Import):
                for a in node.names:
                    if a.name.split(".")[0] in local:
                        bad.append(a.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module and node.module.split(".")[0] in local:
                    bad.append(node.module)
        self.assertEqual(bad, [])

    def test_oracle_runs_without_the_primary_in_sys_modules(self):
        out = subprocess.run(
            [sys.executable, "-I", "-B", "-c",
             "import sys,os;sys.path.insert(0,%r);"
             "import independent_oracle_v1 as O;"
             "print(sorted(m for m in sys.modules if m in "
             "('grammar_v1','real_scale_classical_v1','run_real_scale_v1')))"
             % HERE],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        self.assertIn(b"[]", out.stdout, out.stdout)


class ExactArithmetic(unittest.TestCase):
    def test_no_float_literal_in_any_claim_path_file(self):
        for fn in EXACT_FILES:
            tree = ast.parse(open(os.path.join(HERE, fn)).read())
            floats = [n for n in ast.walk(tree)
                      if isinstance(n, ast.Constant) and isinstance(n.value, float)]
            self.assertEqual(floats, [], "%s contains a float literal" % fn)

    def test_no_float_import_in_any_claim_path_file(self):
        banned = {"numpy", "scipy", "torch", "pandas", "random"}
        for fn in EXACT_FILES:
            tree = ast.parse(open(os.path.join(HERE, fn)).read())
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for a in node.names:
                        self.assertNotIn(a.name.split(".")[0], banned, fn)
                elif isinstance(node, ast.ImportFrom) and node.module:
                    self.assertNotIn(node.module.split(".")[0], banned, fn)


@unittest.skipUnless(os.path.isdir(RUNS), "REAL_RUNS not present")
class Receipts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.res = jload(os.path.join(HERE, "RESULT_V1.json"))
        cls.orc = jload(os.path.join(HERE, "ORACLE_RESULT_V1.json"))

    def test_schema_and_ceiling(self):
        self.assertEqual(self.res["schema"], "GMI833HRealScaleClassicalResultV1")
        self.assertEqual(self.res["claim_ceiling"], C.CLAIM_CEILING)

    def test_forbidden_promotions_named(self):
        for k in ("CROSS_SCOPE_GATE_COMPOSITION", "INDEPENDENT_TEAM_REPLICATION",
                  "M5", "REAL_SCALE_VALIDATION_COMPLETE"):
            self.assertIn(k, self.res["forbidden_promotions"])

    def test_every_closed_row_has_eleven_gates_at_one_sigma(self):
        for rid in self.res["rows_closed"]:
            row = self.res["rows"][rid]
            self.assertTrue(row["single_sigma"], rid)
            self.assertEqual(len(row["gates"]), len(C.GATES), rid)
            self.assertEqual(row["supported"], len(C.GATES), rid)
            self.assertEqual(set(g["sigma"] for g in row["gates"]),
                             {"SIGMA_" + rid}, rid)

    def test_no_closed_row_imports_a_sigma_4f_certificate(self):
        for rid, row in self.res["rows"].items():
            for g in row["gates"]:
                self.assertNotEqual(g["sigma"], "SIGMA_4F", (rid, g["gate"]))

    def test_r01_and_r08_are_witnessed_by_different_evidence(self):
        for rid, row in self.res["rows"].items():
            ev = dict((g["gate"], g["evidence"]) for g in row["gates"])
            self.assertNotEqual(ev["R01_property_prediction_from_ecology"],
                                ev["R08_heldout_frozen_prediction"], rid)

    def test_every_closed_row_is_at_or_above_the_registered_scale(self):
        for rid in self.res["rows_closed"]:
            s = self.res["scale"][rid]
            self.assertGreaterEqual(s["n_fit"], C.MIN_FIT, rid)
            self.assertGreaterEqual(s["n_held"], C.MIN_HELD, rid)

    def test_every_closed_row_is_non_degenerate(self):
        for rid in self.res["rows_closed"]:
            rec = jload(os.path.join(RUNS, "scope_%s.json" % rid))
            for slot in ("held", "tail"):
                nd = rec["winner"]["evaluation"][slot]["nondegeneracy"]
                self.assertTrue(nd["non_degenerate"], (rid, slot))

    def test_hostiles_all_applicable_and_detected(self):
        for h in self.res["hostiles"]:
            self.assertTrue(h["applicable"], h["hostile"] + " is vacuous")
            self.assertTrue(h["detected"], h["hostile"] + " was not detected")

    def test_nulls(self):
        self.assertEqual(self.res["nulls"]["H01_order_randomised"]
                         ["stateful_strictly_better"], 0)
        self.assertEqual(self.res["nulls"]["H02_row_permuted_design"]
                         ["control_beats_constant"], 0)
        self.assertTrue(self.res["nulls"]["no_alarm_on_true_run"])

    def test_exact_replay_matches_between_primary_and_oracle(self):
        self.assertTrue(self.orc["all_agree"], self.orc["disagreements"])
        for rid, row in self.res["rows"].items():
            self.assertTrue(row["exact_replay"]["matches"], rid)

    def test_freeze_strictly_precedes_every_result_artifact(self):
        self.assertTrue(self.res["custody"].get("freeze_precedes_results"),
                        self.res["custody"])

    def test_negative_control_missing_artifact_fails_loudly(self):
        out = subprocess.run(
            [sys.executable, "-I", "-B", "-c",
             "import sys;sys.path.insert(0,%r);"
             "import real_scale_classical_v1 as C;C.RUNS=%r;C.load('scope_H02.json')"
             % (HERE, os.path.join(HERE, "NO_SUCH_DIR"))],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        self.assertNotEqual(out.returncode, 0)
        self.assertIn(b"MISSING REAL_RUN ARTIFACT", out.stdout)

    def test_reconciliation_only_names_closed_rows(self):
        p = os.path.join(HERE, "ISSUE_833_RECONCILIATION_H_REAL_SCALE_V1.json")
        if not os.path.exists(p):
            self.skipTest("reconciliation not yet emitted")
        r = jload(p)
        self.assertEqual(r["schema"], "GMI_ISSUE_RECONCILIATION_V2")
        self.assertEqual(r["issue"], 833)
        self.assertEqual(len(r["replacements"]), len(self.res["rows_closed"]))
        for rep in r["replacements"]:
            self.assertTrue(rep["old"].startswith("- [ ] "))
            self.assertTrue(rep["new"].startswith("- [x] "))
            self.assertEqual(rep["old"][6:], rep["new"][6:].split(" — ")[0])


if __name__ == "__main__":
    unittest.main(verbosity=2)
