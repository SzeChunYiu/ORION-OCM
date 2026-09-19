#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for `gmi-833-aa-logical-form-register-v1`.

    python3 -I -B  research/gmi-833-aa-logical-form-register-v1/test_logical_form_register_v1.py
    python3 -I -O -B research/gmi-833-aa-logical-form-register-v1/test_logical_form_register_v1.py

Under -O every `assert` statement is stripped, so no test relies on `assert`:
every check is a unittest assertion.
"""
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import unittest
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
PKG = "research/gmi-833-aa-logical-form-register-v1"


def load(name: str):
    spec = importlib.util.spec_from_file_location(name, str(HERE / (name + ".py")))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod


A = load("logical_form_register_v1")
B = load("independent_form_oracle_v1")

_RESULT = {}


def route_a():
    if "A" not in _RESULT:
        _RESULT["A"] = A.build(write=False)
    return _RESULT["A"]


def route_b():
    if "B" not in _RESULT:
        _RESULT["B"] = B.main()
    return _RESULT["B"]


def git(*args):
    try:
        p = subprocess.run(["git", "-C", str(REPO)] + list(args), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except OSError:
        return 1, ""
    return p.returncode, p.stdout.decode("utf-8", "replace")


PINS = {
    "research/gmi-833-corpus-census-v1/CORPUS_INDEX_V1.json": "709159c53c6284366aaf1f05380f5fada8d81a98",
    "research/gmi-833-census-registration-pass-v1/DECIDABILITY_V1.json": "b154d5c2a49902665f3e35462a7ad4ad53122651",
}


class TestCustody(unittest.TestCase):
    def test_freeze_is_first(self):
        rc, out = git("log", "--reverse", "--format=%H", "--", PKG + "/")
        if rc != 0 or not out.strip():
            self.skipTest("no git history available")
        first = out.split()[0]
        rc, files = git("show", "--name-only", "--format=", first, "--", PKG + "/")
        names = [f for f in files.splitlines() if f.strip()]
        self.assertTrue(any(f.endswith("FREEZE_V1.md") for f in names), names)
        if len(names) == 1:
            self.assertTrue(names[0].endswith("FREEZE_V1.md"))

    def test_frozen_parents_unchanged(self):
        for path, blob in PINS.items():
            rc, out = git("rev-parse", "HEAD:" + path)
            if rc != 0:
                self.skipTest("git unavailable for %s" % path)
            self.assertEqual(out.strip(), blob, path)

    def test_route_b_imports_nothing_from_a_and_uses_no_regex(self):
        src = (HERE / "independent_form_oracle_v1.py").read_text(encoding="utf-8")
        self.assertNotIn("logical_form_register_v1", src)
        self.assertNotIn("import re\n", src)
        self.assertNotIn("import re ", src)
        self.assertNotIn("re.compile", src)


class TestPopulation(unittest.TestCase):
    def test_population_rule_counts(self):
        r = route_a()
        self.assertEqual(r["population"]["total"], 391)
        self.assertEqual(r["population"]["heading_objects"], 346)
        self.assertEqual(r["population"]["bold_led"], 45)
        self.assertEqual(r["population"]["not_a_statement_line"], 266)
        self.assertEqual(r["population"]["pinned_blobs"], 114)
        self.assertEqual(r["census_frozen_sha"], A.CENSUS_FROZEN_SHA)

    def test_snapshot_consistent_when_blobs_reachable(self):
        r = route_a()
        self.assertIn(r["blob_state"], ("BLOBS_REACHABLE", "BLOBS_UNREACHABLE"))
        if r["blob_state"] == "BLOBS_REACHABLE":
            self.assertTrue(r["snapshot_byte_identical_to_committed"])

    def test_coverage_is_exact_fraction(self):
        r = route_a()
        cov = r["coverage"]
        self.assertEqual(cov["registered"], cov["by_status"].get("REGISTERED_MACHINE", 0) + cov["by_status"].get("REGISTERED_HAND", 0))
        self.assertEqual(Fraction(cov["fraction"]), Fraction(cov["registered"], cov["of"]))
        self.assertEqual(sum(cov["by_status"].values()), cov["of"])


class TestGrammar(unittest.TestCase):
    def test_if_then(self):
        f, rule = A.parse_sentence("If the cut is finite, then the code is exact.", "")
        self.assertEqual(rule, "R2_IF_THEN")
        self.assertEqual(f["matrix"][0], "->")
        self.assertIn("cut", f["matrix"][1][1])
        self.assertIn("code", f["matrix"][2][1])

    def test_trailing_if_same_form(self):
        f, rule = A.parse_sentence("The code is exact if the cut is finite.", "")
        self.assertEqual(rule, "R2_TRAIL_IF")
        self.assertIn("cut", f["matrix"][1][1])
        self.assertIn("code", f["matrix"][2][1])

    def test_iff_and_necessary(self):
        f, _ = A.parse_sentence("The code is exact iff the cut is finite.", "")
        self.assertEqual(f["matrix"][0], "<->")
        self.assertEqual(A.roles_of(f["matrix"]), {"sufficient": [1, 2], "necessary": [1, 2]})
        n, rule = A.parse_sentence("A finite cut is necessary for an exact code.", "")
        self.assertEqual(rule, "R5_NECESSARY")
        self.assertIn("code", n["matrix"][1][1])
        self.assertIn("cut", n["matrix"][2][1])
        self.assertEqual(A.roles_of(n["matrix"]), {"sufficient": [1], "necessary": [2]})

    def test_quantifier_prefix_order(self):
        f, _ = A.parse_sentence("For every machine M, there exists a witness w such that w certifies M.", "")
        self.assertEqual([p[0] for p in f["prefix"]], ["forall", "exists"])
        g, _ = A.parse_sentence("There exists a witness w such that for every machine M, w certifies M.", "")
        self.assertEqual([p[0] for p in g["prefix"]], ["exists", "forall"])

    def test_unless_and_no(self):
        f, rule = A.parse_sentence("The bound holds unless the domain is empty.", "")
        self.assertEqual(rule, "R4_UNLESS")
        self.assertEqual(f["matrix"][1][0], "not")
        g, rule = A.parse_sentence("No finite panel determines the class exactly.", "")
        self.assertTrue(rule.startswith("R7_NO"))
        self.assertEqual(g["prefix"][0][0], "forall")

    def test_no_cue_is_unavailable(self):
        f, rule = A.parse_sentence("This is the positive result.", "")
        self.assertIsNone(f)
        self.assertEqual(rule, "NO_GRAMMAR_RULE")

    def test_requires_quantity_is_not_a_necessity(self):
        f, rule = A.parse_sentence("Encoding every task independently requires <MATH> bits of target identity information.", "")
        self.assertNotEqual(rule, "R5_REQUIRES")

    def test_rel_classes(self):
        self.assertEqual(A.rel_class("the minimum burden is <MATH>"), "OPT")
        self.assertEqual(A.rel_class("X causes Y"), "CAUSAL")
        self.assertEqual(A.rel_class("the value is at most 3"), "LE")
        self.assertEqual(A.rel_class("the count is exactly 4"), "EQ")
        self.assertEqual(A.rel_class("a plain sentence"), "PRED")

    def test_route_b_grammar_matches_a_on_fixtures(self):
        for s in ("If the cut is finite, then the code is exact.",
                  "The code is exact if the cut is finite.",
                  "The code is exact iff the cut is finite.",
                  "A finite cut is necessary for an exact code.",
                  "For every machine M, there exists a witness w such that w certifies M.",
                  "Under the independence assumptions, the failure probability is exactly <MATH>",
                  "No finite panel identifies the class exactly.",
                  "This is the positive result."):
            fa, ra = A.parse_sentence(s, "")
            fb, rb = B.parse_sentence(s, "")
            self.assertEqual(fa is None, fb is None, s)
            if fa is not None:
                self.assertEqual(B.canon_form({"prefix": fa["prefix"], "matrix": fa["matrix"]}),
                                 B.canon_form({"prefix": fb["prefix"], "matrix": fb["matrix"]}), s)


class TestHandRegister(unittest.TestCase):
    def test_hand_samples_match_file(self):
        r = route_a()
        self.assertTrue(r["hand_sample"]["hand_file_present"])
        self.assertTrue(r["hand_sample"]["keys_match_hand_file"])
        self.assertEqual(r["hand_sample"]["size"], 40)
        self.assertTrue(r["hand_warrant_sample"]["keys_match_hand_file"])
        self.assertEqual(r["hand_warrant_sample"]["size"], 20)

    def test_hand_sample_is_reproducible_by_the_lcg(self):
        r = route_a()
        # the draw is a pure function of the sorted unavailable set and the seed
        rng = A.LCG(A.HAND_SEED)
        with open(A.REGISTER, encoding="utf-8") as fh:
            entries = json.load(fh)["entries"]
        pool = sorted(k for k, e in entries.items() if e["form_status"] == "FORM_UNAVAILABLE" or e["rule"] == "HAND")
        self.assertEqual(rng.sample(pool, A.HAND_SAMPLE_SIZE), r["hand_sample"]["keys"])

    def test_lcg_high_bits_not_degenerate(self):
        rng = A.LCG(7)
        draws = [rng.below(4) for _ in range(64)]
        self.assertGreater(len(set(draws)), 2)


class TestDiscriminators(unittest.TestCase):
    def test_every_targeted_row_evaluable_on_real_objects(self):
        r = route_a()
        for row in A.ROWS:
            self.assertGreaterEqual(r["rows"][row]["evaluable"], 1, row)
            self.assertLessEqual(r["rows"][row]["evaluable"], r["rows"][row]["applicable"], row)
            self.assertEqual(r["rows"][row]["queued"] + r["rows"][row]["agreeing"], r["rows"][row]["evaluable"], row)

    def test_partition_aa17_aa18(self):
        self.assertTrue(route_a()["aa17_aa18_partition_disjoint"])

    def test_no_alarm_on_hand_verified_clean_set(self):
        r = route_a()
        self.assertGreater(r["no_alarm_clean_set"]["size"], 0)
        self.assertEqual(r["no_alarm_clean_set"]["alarms"], 0)

    def test_real_data_positive_recall(self):
        r = route_a()
        rp = r["real_data_positives"]
        self.assertGreaterEqual(len(rp["expected"]), 1)
        self.assertEqual(rp["missed"], [])
        self.assertEqual(sorted(rp["queued"]), sorted(rp["expected"]))

    def test_every_hostile_applicable_and_detected(self):
        r = route_a()
        ids = [h["id"] for h in r["hostiles"]]
        self.assertEqual(ids, ["H%d" % i for i in range(1, 13)])
        for h in r["hostiles"]:
            self.assertTrue(h["applicable"], h["id"])
            if "planted" in h:
                self.assertGreater(h["planted"], 0, h["id"])
                self.assertEqual(h["detected"], h["planted"], h["id"])

    def test_loosening_hostile_inflates(self):
        r = route_a()
        h11 = [h for h in r["hostiles"] if h["id"] == "H11"][0]
        for row in A.ROWS:
            self.assertGreaterEqual(h11["queue_if_warrant_conjunct_dropped"][row], h11["true_queue"][row])
        self.assertGreater(sum(h11["queue_if_warrant_conjunct_dropped"].values()), sum(h11["true_queue"].values()))

    def test_null_beaten_and_exact(self):
        r = route_a()
        n = r["null"]
        self.assertEqual(n["draws"], 200)
        self.assertEqual(n["shuffled_reach_true"], 0)
        self.assertTrue(n["beaten"])
        self.assertLess(n["shuffled_max"], n["true_pooled"])
        Fraction(n["shuffled_mean"])  # exact rational, parses

    def test_swap_hostile_moves_the_quantity(self):
        """A planted prefix swap on a real agreeing object is queued; the
        unplanted object is not (the hostile is not vacuous)."""
        with open(A.REGISTER, encoding="utf-8") as fh:
            reg = json.load(fh)["entries"]
        r = route_a()
        key = r["rows"]["AA16"]["evaluable_keys"][0]
        e = json.loads(json.dumps(reg[key]))
        base = A.run_discriminators({key: e})
        self.assertEqual(len(base["queues"]["AA16"]), 0)
        e["form"]["prefix"] = list(reversed(e["form"]["prefix"]))
        e["form"]["conclusion_prefix"] = list(reversed(e["form"]["conclusion_prefix"]))
        swapped = A.run_discriminators({key: e})
        self.assertEqual(len(swapped["queues"]["AA16"]), 1)

    def test_contrapositive_is_not_a_converse(self):
        e = {"form_status": "REGISTERED_MACHINE", "role_vocabulary": False,
             "form": {"prefix": [], "conclusion_prefix": [],
                      "matrix": ["->", ["atom", "the graph is connected", "PRED"], ["atom", "the cut is finite", "PRED"]]},
             "warrant": {"warrant_status": "PROOF_BLOCK", "evidence_mode": "ANALYTIC_DEDUCTIVE",
                         "proof_first_quantifier": None, "proof_opening_literal": "the cut is not finite",
                         "proof_opening_polarity": "neg", "proof_second_direction": False, "falsifier_text": None},
             "hand_warrant": None}
        out = A.run_discriminators({"k": e})
        self.assertEqual(out["queues"]["AA17"], [])
        self.assertEqual(out["agree"]["AA17"], 1)
        e["warrant"]["proof_opening_polarity"] = "pos"
        out = A.run_discriminators({"k": e})
        self.assertEqual([q["kind"] for q in out["queues"]["AA17"]], ["CONVERSE"])


class TestRoutes(unittest.TestCase):
    def test_routes_agree_on_every_form_and_queue(self):
        b = route_b()
        self.assertEqual(b["population"], 391)
        self.assertTrue(b["all_forms_agree"], b["form_disagree"][:5])
        self.assertTrue(b["all_queues_agree"])
        self.assertEqual(b["form_agree"], 391)
        a = route_a()
        for row in A.ROWS:
            self.assertEqual(b["queues"][row]["route_a"], a["rows"][row]["queued"], row)
            self.assertEqual(b["queues"][row]["evaluable_b"], a["rows"][row]["evaluable"], row)
            self.assertEqual(b["queues"][row]["applicable_b"], a["rows"][row]["applicable"], row)
            self.assertEqual(b["queues"][row]["agreeing_b"], a["rows"][row]["agreeing"], row)
        self.assertEqual(b["registered_b"], a["coverage"]["registered"])


class TestReceipt(unittest.TestCase):
    def test_no_float_anywhere(self):
        def walk(x):
            if isinstance(x, float):
                raise AssertionError("float in receipt")
            if isinstance(x, dict):
                for v in x.values():
                    walk(v)
            elif isinstance(x, list):
                for v in x:
                    walk(v)
        walk(route_a())
        walk(route_b())

    def test_committed_receipt_matches_live_run(self):
        p = HERE / "RESULT_V1.json"
        if not p.exists():
            self.skipTest("RESULT_V1.json not yet written")
        with open(p, encoding="utf-8") as fh:
            doc = json.load(fh)
        live = route_a()
        for k in ("population", "coverage", "rows", "hostiles", "null", "no_alarm_clean_set", "real_data_positives",
                  "aa17_aa18_partition_disjoint", "warrant", "hand_sample", "hand_warrant_sample"):
            self.assertEqual(doc["route_a"][k], live[k], k)


if __name__ == "__main__":
    unittest.main(argv=[sys.argv[0], "-v"])
