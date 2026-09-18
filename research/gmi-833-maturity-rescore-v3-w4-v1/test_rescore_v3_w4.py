#!/usr/bin/env python3
"""Tests for the v3-W4 maturity correction.

Run:  python3 -I -O -B test_rescore_v3_w4.py
Stdlib only, Py3.8-safe.  Covers: the frozen rule's table and ceiling, the
custody predicate's ability to return FALSE on real data, the two-route
agreement, exact arithmetic, the hostile battery and the null.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, os.pardir, os.pardir))
sys.path.insert(0, HERE)

import rescore_v3_w4 as A  # noqa: E402


def run(script):
    p = subprocess.Popen([sys.executable, "-I", "-B", os.path.join(HERE, script)],
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=HERE)
    out, err = p.communicate()
    return p.returncode, out.decode("utf-8", "replace"), err.decode("utf-8", "replace")


class TestFrozenRule(unittest.TestCase):
    def test_table_is_the_v2_table(self):
        self.assertEqual(A.SUPPORT_TABLE["FROZEN_HELDOUT"], ("EV3", "M4"))
        self.assertEqual(A.SUPPORT_TABLE["EXACT_FINITE_CERTIFICATE"], ("EV2", "M2"))
        self.assertEqual(A.SUPPORT_TABLE["EMPIRICAL_UNFROZEN"], ("UNKNOWN", "M0"))

    def test_ceiling_map_is_respected(self):
        self.assertEqual(A.apply_rule("EXACT_FINITE_CERTIFICATE", False), ("EV2", "M2"))
        self.assertEqual(A.apply_rule("EXACT_FINITE_CERTIFICATE", True), ("EV2", "M3"))
        self.assertEqual(A.apply_rule("FROZEN_HELDOUT", False), ("EV3", "M4"))

    def test_unknown_support_kind_is_refused_not_guessed(self):
        self.assertRaises(KeyError, A.apply_rule, "SOMETHING_NEW", False)

    def test_m5_is_unreachable_from_the_table(self):
        for kind in A.SUPPORT_TABLE:
            _ev, m = A.SUPPORT_TABLE[kind]
            self.assertNotIn(m, ("M5", "M6"),
                             "no support kind may license M5/M6 (v1 rule 2)")


class TestPins(unittest.TestCase):
    def test_pinned_blobs_match_disk(self):
        self.assertEqual(A.git_blob_sha1(A.SCORES_REL), A.SCORES_BLOB)
        for p in A.REGISTER_RELS:
            base = os.path.basename(p)
            self.assertEqual(A.git_blob_sha1(p), A.REGISTER_BLOBS[base], base)

    def test_baseline_v1_exists_two_independent_ways(self):
        """A previous worker wrongly reported this file missing."""
        path = "research/gmi-833-theory-baseline-v1/BASELINE_V1.md"
        self.assertTrue(os.path.isfile(os.path.join(REPO, path)))
        out = A.git(["ls-tree", "-r", "--name-only", "HEAD", "--", path])
        self.assertIsNotNone(out)
        self.assertIn(path, out)
        blob = A.git(["rev-parse", "HEAD:" + path])
        self.assertIsNotNone(blob)
        self.assertEqual(len(blob.strip()), 40)


class TestCustody(unittest.TestCase):
    def test_parent_custody_is_false_on_real_data(self):
        """H5: the checker MUST be able to return FALSE, proved on real data."""
        state, _d = A.custody_on_ref("HEAD", A.PARENT_DIR,
                                     A.PARENT_FREEZE_FILES, A.PARENT_OUTCOME_FILES)
        self.assertEqual(state, A.NOT_PRECEDES)

    def test_arrival_custody_is_indeterminate_on_main(self):
        arr = A.arrival_custody()
        self.assertEqual(arr["on_source_main"], A.SINGLE,
                         "PR #988 squash-merged: main alone cannot show the order")

    def test_arrival_custody_holds_on_the_tagged_branch(self):
        arr = A.arrival_custody()
        self.assertEqual(arr["on_pr988_branch"], A.PRECEDES)
        self.assertTrue(arr["freeze_tree_is_exactly_the_freeze"],
                        "only the freeze documents may exist at the freeze commit")
        self.assertTrue(arr["blob_bridge_ok"])
        self.assertTrue(arr["custody_holds"])

    def test_unavailable_is_not_conflated_with_fine(self):
        state, _d = A.custody_on_ref("0000000000000000000000000000000000000000",
                                     A.PARENT_DIR, A.PARENT_FREEZE_FILES,
                                     A.PARENT_OUTCOME_FILES)
        self.assertEqual(state, A.UNAVAIL)
        self.assertNotEqual(state, A.PRECEDES)


class TestExactness(unittest.TestCase):
    def test_w4_executor_carries_no_float_and_no_sampling(self):
        e = A.executor_is_exact(A.PARENT_DIR + "/novel_intelligence_w4_v1.py")
        self.assertFalse(e["float_literal_or_cast"])
        self.assertFalse(e["imports_random"])
        self.assertFalse(e["imports_numpy"])
        self.assertFalse(e["samples"])

    def test_no_float_anywhere_in_the_emitted_result(self):
        path = os.path.join(HERE, "RESULT_V1.json")
        if not os.path.isfile(path):
            self.skipTest("run rescore_v3_w4.py first")
        with open(path) as fh:
            payload = json.load(fh)

        def scan(node, where):
            if isinstance(node, float):
                self.fail("float at %s" % where)
            if isinstance(node, dict):
                for k, v in node.items():
                    scan(v, where + "." + str(k))
            elif isinstance(node, list):
                for i, v in enumerate(node):
                    scan(v, "%s[%d]" % (where, i))
        scan(payload, "$")


class TestCensus(unittest.TestCase):
    def setUp(self):
        self.rows = A.load_json(A.SCORES_REL)

    def test_published_distribution_reproduces_the_checklist_line(self):
        self.assertEqual(len(self.rows), 197)
        self.assertEqual(A.distribution(self.rows, "maturity_M"), A.PUBLISHED_M)
        self.assertEqual(A.distribution(self.rows, "evidence_EV"), A.PUBLISHED_EV)
        self.assertEqual(sum(A.PUBLISHED_M.values()), 197)

    def test_no_published_row_mentions_post_hoc(self):
        blob = json.dumps(self.rows).upper()
        self.assertNotIn("POST_HOC", blob)

    def test_arrival_is_absent_from_the_published_scores(self):
        """Absence claim with a justified scope: substring over every full row."""
        hits = [r for r in self.rows if A.ARRIVAL_PKG in json.dumps(r)]
        self.assertEqual(hits, [])
        w4 = [r for r in self.rows if "novel-intelligence-w4" in json.dumps(r)]
        self.assertEqual(len(w4), 1)
        self.assertEqual(w4[0]["result_id"], A.PARENT_ROW_ID)

    def test_h4_arithmetic_tamper_is_detected(self):
        d = dict(A.distribution(self.rows, "maturity_M"))
        self.assertEqual(sum(d.values()), len(self.rows))
        d["M4"] += 1
        self.assertNotEqual(sum(d.values()), len(self.rows))


class TestPropagation(unittest.TestCase):
    def setUp(self):
        self.rows = A.load_json(A.SCORES_REL)
        self.registers = {}
        for p in A.REGISTER_RELS:
            self.registers[os.path.basename(p)] = A.load_json(p)

    def test_h2_real_positive_the_published_scores_are_flagged(self):
        sw = A.sweep(self.registers, self.rows)
        flagged = [r for r in sw["results"]
                   if A.PARENT_PKG in (r.get("resolved_packages") or [])
                   and r["outcome"] == A.UNREFLECTED]
        self.assertTrue(flagged, "the checker must catch the real W4 defect")

    def test_h3_no_alarm_on_a_scored_package_below_m4(self):
        sw = A.sweep(self.registers, self.rows)
        hits = [r for r in sw["results"]
                if "gmi-capability-interactions-unified-v1" in (r.get("resolved_packages") or [])]
        self.assertTrue(hits)
        for r in hits:
            self.assertEqual(r["outcome"], A.IMMATERIAL)

    def test_h3b_self_typed_false_positive_is_not_adverse(self):
        sw = A.sweep(self.registers, self.rows)
        hits = [r for r in sw["results"]
                if r.get("package") == "machine-intelligence-morphogenesis-v1"]
        self.assertTrue(hits)
        for r in hits:
            self.assertEqual(r["outcome"], A.NOT_ADVERSE)

    def test_h1_synthetic_plant_is_caught(self):
        h = A.hostiles(self.registers, self.rows)
        self.assertTrue(h["H1_synthetic_plant"]["detected"])

    def test_null_control_yields_zero_flags(self):
        n = A.null_control(self.registers, self.rows)
        self.assertEqual(n["flags"], 0)

    def test_out_of_population_is_a_distinct_outcome(self):
        sw = A.sweep(self.registers, self.rows)
        self.assertIn(A.OUT_OF_POP, sw["counts"])
        self.assertGreater(sw["counts"][A.OUT_OF_POP], 0)

    def test_correction_extinguishes_the_real_flag(self):
        path = os.path.join(HERE, "RESULT_V1.json")
        if not os.path.isfile(path):
            self.skipTest("run rescore_v3_w4.py first")
        with open(path) as fh:
            payload = json.load(fh)
        self.assertEqual(payload["W4R4_propagation"]["w4_still_unreflected_after_correction"], 0)


class TestAdjudication(unittest.TestCase):
    """A flag is not a finding until it is verified against the artifact."""

    def test_g0_flag_is_adjudicated_and_the_score_is_sustained(self):
        adj = A.adjudicate_g0()
        if adj["adjudication"] == "NOT_ADJUDICABLE__BRANCH_OBJECTS_UNAVAILABLE":
            self.skipTest("origin branch research/833-g0-grammar-expansion-v1 not fetched")
        self.assertEqual(adj["custody_on_source_main"], A.SINGLE,
                         "main alone cannot see the order: #945 squash-merged")
        self.assertEqual(adj["custody_on_origin_branch"], A.PRECEDES)
        self.assertTrue(adj["freeze_tree_is_exactly_the_freeze"])
        self.assertTrue(adj["wording_only"])
        self.assertEqual(adj["adjudication"], "SCORE_SUSTAINED__FLAG_IS_A_SQUASH_ARTIFACT")
        self.assertIsNone(adj["score_change_made_here"],
                          "this tranche alters no score outside its frozen scope")

    def test_not_adjudicable_is_distinct_from_not_sustained(self):
        """Could-not-check must never be reported as checked-and-failed."""
        saved = A.G0_BRANCH
        try:
            A.G0_BRANCH = "0" * 40
            adj = A.adjudicate_g0()
            self.assertEqual(adj["adjudication"], "NOT_ADJUDICABLE__BRANCH_OBJECTS_UNAVAILABLE")
            self.assertIn("NOT the same as checked-and-fine", adj["note"])
        finally:
            A.G0_BRANCH = saved


class TestTwoRoutes(unittest.TestCase):
    def test_routes_agree_exactly(self):
        rc, _o, err = run("rescore_v3_w4.py")
        self.assertEqual(rc, 0, err)
        rc2, _o2, err2 = run("oracle_v3_w4.py")
        self.assertEqual(rc2, 0, err2)
        with open(os.path.join(HERE, "RESULT_V1.json")) as fh:
            a = json.load(fh)
        with open(os.path.join(HERE, "ORACLE_RESULT_V1.json")) as fh:
            b = json.load(fh)
        da = a["W4R3_distribution"]
        self.assertEqual(da["published_M"], b["published_M"])
        self.assertEqual(da["corrected_M"], b["corrected_M"])
        self.assertEqual(da["published_EV"], b["published_EV"])
        self.assertEqual(da["corrected_EV"], b["corrected_EV"])
        self.assertEqual(da["published_rows"], b["published_rows"])
        self.assertEqual(da["corrected_rows"], b["corrected_rows"])
        self.assertEqual(da["M4_membership_left"], b["M4_left"])
        self.assertEqual(da["M4_membership_entered"], b["M4_entered"])
        self.assertEqual(da["M4_total_published"], b["M4_total_before"])
        self.assertEqual(da["M4_total_corrected"], b["M4_total_after"])
        # custody, by two different git mechanisms
        self.assertEqual(b["custody"]["parent_on_main"], "OUTCOME_FIRST")
        self.assertEqual(b["custody"]["arrival_on_main"], "SAME_COMMIT")
        self.assertEqual(b["custody"]["arrival_on_tagged_branch"], "FREEZE_FIRST")
        # the schema-agnostic walk must find the same UNREFLECTED packages
        a_un = set(a["W4R4_propagation"]["unreflected"])
        b_un = set(k[len("FRAGMENT:"):] if k.startswith("FRAGMENT:") else k
                   for k in b["propagation"]["unreflected"])
        self.assertEqual(
            sorted(x for x in a_un), sorted(x for x in b_un),
            "route A's explicit section enumeration and route B's schema-agnostic "
            "walk must agree on the UNREFLECTED set")

    def test_all_green(self):
        rc, _o, err = run("rescore_v3_w4.py")
        self.assertEqual(rc, 0, err)
        with open(os.path.join(HERE, "RESULT_V1.json")) as fh:
            a = json.load(fh)
        self.assertTrue(a["all_green"], json.dumps(a["self_checks"], indent=1))
        self.assertEqual(a["closes_issue_rows"], [])
        self.assertTrue(a["no_row_earned"])
        self.assertFalse(a["produces_reconciliation_json"])


class TestFrozenArtifactsUntouched(unittest.TestCase):
    def test_no_frozen_artifact_is_modified_by_this_branch(self):
        out = A.git(["diff", "--name-only", "origin/main...HEAD"])
        if out is None:
            self.skipTest("origin/main unavailable")
        changed = [ln.strip() for ln in out.splitlines() if ln.strip()]
        for path in changed:
            self.assertTrue(
                path.startswith("research/gmi-833-maturity-rescore-v3-w4-v1/")
                or path.startswith(".github/workflows/gmi-833-maturity-rescore-v3-w4"),
                "this branch touched %s" % path)


class TestFreezeIsFirst(unittest.TestCase):
    def test_freeze_precedes_every_other_file_of_this_package(self):
        pkg = "research/gmi-833-maturity-rescore-v3-w4-v1"
        fz = A.first_add_commit("HEAD", pkg + "/FREEZE_V3_W4.md")
        if not fz:
            self.skipTest("freeze not yet committed")
        out = A.git(["ls-tree", "-r", "--name-only", "HEAD", "--", pkg + "/"])
        self.assertIsNotNone(out)
        for path in [ln.strip() for ln in out.splitlines() if ln.strip()]:
            if path.endswith("FREEZE_V3_W4.md"):
                continue
            other = A.first_add_commit("HEAD", path)
            if not other:
                continue
            self.assertNotEqual(other, fz,
                                "%s shares the freeze commit" % path)
            self.assertTrue(A.is_ancestor(fz, other),
                            "freeze must strictly precede %s" % path)


if __name__ == "__main__":
    unittest.main(verbosity=2)
