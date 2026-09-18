#!/usr/bin/env python3
"""Tests for gmi-833-ab-terminology-harness-v1.

Every hostile asserts that the perturbation MOVED the quantity it targets
before asserting that the checker flagged it.
"""
import copy
import json
import os
import random
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import ab_harness_v1 as A                # noqa: E402
import independent_ab_oracle_v1 as B     # noqa: E402
import terminology_ratchet_v1 as R       # noqa: E402

SPEC = json.load(open(os.path.join(HERE, "AB_ROW_REQUIREMENTS_V1.json")))
LIVE_COMMENT = os.path.join(HERE, "ISSUE_COMMENT_5684607872_SNAPSHOT.md")


def artifacts():
    prows = A.parse_crosswalk(A.CROSSWALK)
    erows = A.parse_extension(A.EXTENSION)
    bt, bwr = A.banned_stats(A.BANNED)
    return prows, erows, {
        "crosswalk_header": A.crosswalk_header(A.CROSSWALK),
        "crosswalk_rows": len(prows),
        "extension_rows": len(erows),
        "banned_blob": open(A.BANNED).read(),
        "gate_blob": open(os.path.join(A.PARENT, "GMI_TERMINOLOGY_CI_GATE_V1.py")).read(),
        "banned_terms": bt, "banned_with_replacement": bwr,
        "ratchet_present": (os.path.exists(os.path.join(HERE, "terminology_ratchet_v1.py")) and
                            os.path.exists(os.path.join(
                                A.REPO, ".github", "workflows",
                                "gmi-833-ab-terminology-harness-v1.yml"))),
        "parent_packages": A.parent_package_evidence(),
    }


class Moved(unittest.TestCase):
    def assert_moved(self, name, base, pert, flagged):
        self.assertNotEqual(base, pert,
                            "HOSTILE %s did not move its quantity (%r): structurally "
                            "invisible to the checker" % (name, base))
        self.assertTrue(flagged, "HOSTILE %s moved its quantity but was not flagged" % name)


class TestRequirementsIntegrity(unittest.TestCase):
    def test_every_required_term_occurs_in_the_row_text(self):
        """Anti-invention guard: a requirement the AB row does not itself name
        cannot be demanded, and a named one cannot be quietly dropped."""
        bad = []
        for row in SPEC["rows"]:
            text = A.norm(row["verbatim"])
            for req in row["required_terms"]:
                alts = req["any_of"] if isinstance(req, dict) else [req]
                if not any(A.norm(a).split("/")[0] in text or A.norm(a) in text for a in alts):
                    bad.append((row["row_id"], req))
        self.assertEqual(bad, [], "requirements not present in the row text: %r" % (bad,))

    def test_rows_are_byte_exact_from_the_live_comment(self):
        raw = open(LIVE_COMMENT, "rb").read()
        self.assertEqual(len(raw), 13248, "committed comment snapshot has drifted")
        body = raw.decode("utf-8")
        for row in SPEC["rows"]:
            self.assertEqual(body.count(row["verbatim"] + "\n"), 1,
                             "row %s not found exactly once verbatim" % row["row_id"])

    def test_scope_is_34_rows_and_3_declared_out_of_scope(self):
        self.assertEqual(len(SPEC["rows"]), 34)
        self.assertEqual(len(SPEC["rows_not_in_scope"]), 3)
        self.assertEqual(sorted(SPEC["rows_not_in_scope"]), ["AB02", "AB08", "AB25"])


class TestCoverage(Moved):
    def test_headline_coverage(self):
        r = A.run()
        self.assertEqual(r["crosswalk_rows"], 48)
        self.assertEqual(r["extension_rows"], 4)
        self.assertEqual(r["required_terms_total"], 153)
        self.assertEqual(r["parent_covered_total"], 149)
        self.assertEqual(r["total_covered_total"], 153)
        self.assertEqual(r["rows_checked"], 34)
        self.assertEqual(r["rows_earned"], 34)

    def test_parent_ownership_split_is_exactly_three_terms(self):
        r = A.run()
        supplied = sorted(sum((x.get("supplied_by_this_package", []) for x in r["rows"]), []))
        self.assertEqual(supplied, ["algorithm class | configuration class",
                                    "novel implementation", "possibility space",
                                    "verifier feedback"])

    def test_two_routes_agree_on_every_crosswalk_row(self):
        a = dict((x["row_id"], x) for x in A.run()["rows"])
        b = dict((x["row_id"], x) for x in B.run()["rows"])
        self.assertTrue(b)
        for rid, bv in b.items():
            av = a[rid]
            self.assertEqual(av["parent_covered"], bv["parent_covered"], rid)
            self.assertEqual(av["total_covered"], bv["total_covered"], rid)
            self.assertEqual(av["required"], bv["required"], rid)
            self.assertEqual(av["parent_rows_found"], bv["parent_rows_found"], rid)
            self.assertEqual(av["extension_rows_found"], bv["extension_rows_found"], rid)

    def test_two_routes_agree_on_artifact_counts(self):
        a, b = A.run(), B.run()
        self.assertEqual(a["crosswalk_rows"], b["crosswalk_rows"])
        self.assertEqual(a["extension_rows"], b["extension_rows"])
        self.assertEqual(a["banned_terms"], b["banned_terms"])
        self.assertEqual(a["banned_with_replacement"], b["banned_with_replacement"])

    def _spec(self, rid):
        return [s for s in SPEC["rows"] if s["row_id"] == rid][0]

    def test_hostile_HB1_stripped_comparison_term(self):
        prows, erows, art = artifacts()
        s = self._spec("AB05")
        base = A.check_row(s, prows, erows, art)
        bad = copy.deepcopy(prows)
        for r in bad:
            if A.norm(r["legacy"]) == "ecology":
                for c in ("legacy", "proposed", "field", "canonical", "definition", "migration"):
                    r[c] = r[c].replace("instance space", "")
        got = A.check_row(s, bad, erows, art)
        self.assert_moved("HB1 stripped-term", base["total_covered"], got["total_covered"],
                          got["verdict"] == "OPEN")
        self.assertIn("instance space", got["missing"])

    def test_hostile_HB2_blanked_citations(self):
        prows, erows, art = artifacts()
        s = self._spec("AB06")
        base = A.check_row(s, prows, erows, art)
        bad = copy.deepcopy(prows)
        for r in bad:
            if A.norm(r["legacy"]) == "niche":
                r["citations"] = ""
        got = A.check_row(s, bad, erows, art)
        self.assert_moved("HB2 blanked-citations", base["citations_nonempty"],
                          got["citations_nonempty"], got["verdict"] == "OPEN")

    def test_hostile_HB3_invalid_match_verdict(self):
        prows, erows, art = artifacts()
        s = self._spec("AB22")
        base = A.check_row(s, prows, erows, art)
        bad = copy.deepcopy(prows)
        for r in bad:
            if A.norm(r["legacy"]) == "evolvability":
                r["match"] = "looks fine"
        got = A.check_row(s, bad, erows, art)
        self.assert_moved("HB3 invalid-verdict", base["match_verdicts"],
                          got["match_verdicts"], got["verdict"] == "OPEN")

    def test_hostile_HB4_deleted_row(self):
        prows, erows, art = artifacts()
        s = self._spec("AB18")
        base = A.check_row(s, prows, erows, art)
        bad = [r for r in prows if A.norm(r["legacy"]) != "carrier"]
        got = A.check_row(s, bad, erows, art)
        self.assert_moved("HB4 deleted-row", base["parent_rows_found"],
                          got["parent_rows_found"], got["verdict"] == "OPEN")

    def test_hostile_HB5_cognitive_operational_criterion_removed(self):
        base = A.parent_package_evidence()["AB28"]
        self.assertTrue(base["present"])
        self.assertTrue(base["operational_criterion"])
        self.assertTrue(base["non_correspondence_scope"])
        prows, erows, art = artifacts()
        s = self._spec("AB28")
        good = A.check_row(s, prows, erows, art)
        art2 = dict(art)
        art2["parent_packages"] = dict(art["parent_packages"])
        art2["parent_packages"]["AB28"] = {"present": False, "path": "x"}
        got = A.check_row(s, prows, erows, art2)
        self.assert_moved("HB5 no-operational-criterion", good["verdict"], got["verdict"],
                          got["verdict"] == "OPEN")

    def test_hostile_HB9_grammar_bias_predicate_rejects_a_decoy(self):
        """A receipt that merely TALKS about grammar bias must fail."""
        good = A.grammar_bias_evidence(os.path.join(
            A.REPO, "research", "gmi-833-g0-grammar-bias-v1", "RESULT_V1.json"))
        self.assertTrue(good["present"])
        self.assertGreaterEqual(good["distinct_bias_profiles"], 2)
        decoy = {"claim_ceiling": "GMI_FINITE_GRAMMAR_BIAS_SOMETHING",
                 "forbidden_promotions": ["UNBIASED_G0"],
                 "nonisometric_same_semantics_hostile": {
                     "GA_bias": {"A": {"Q": {"0": "1/2"}}, "B": {"Q": {"0": "1/2"}}}}}
        fd, path = tempfile.mkstemp(suffix=".json")
        with os.fdopen(fd, "w") as fh:
            json.dump(decoy, fh)
        try:
            got = A.grammar_bias_evidence(path)
            self.assert_moved("HB9 grammar-bias decoy", good["distinct_bias_profiles"],
                              got["distinct_bias_profiles"], got["present"] is False)
            self.assertFalse(got["bias_is_measured_not_asserted"])
        finally:
            os.unlink(path)

    def test_hostile_HB10_cognitive_predicate_rejects_a_decoy(self):
        """Prose that says 'operational criteria' but proves nothing must fail."""
        good = A.cognitive_criteria_evidence(os.path.join(
            A.REPO, "research", "gmi-833-cognitive-reaudit-v1",
            "COGNITIVE_REAUDIT_THEOREMS_V1.md"))
        self.assertTrue(good["present"])
        self.assertGreaterEqual(len(good["named_results"]), 2)
        decoy = ("# Cognitive terms\n\nWe require operational criteria for working memory, "
                 "episodic memory, attention, metacognition and theory of mind before "
                 "claiming correspondence to human constructs. Grammar and bias are "
                 "discussed at length.\n")
        fd, path = tempfile.mkstemp(suffix=".md")
        with os.fdopen(fd, "w") as fh:
            fh.write(decoy)
        try:
            got = A.cognitive_criteria_evidence(path)
            self.assert_moved("HB10 cognitive decoy", len(good["named_results"]),
                              len(got["named_results"]), got["present"] is False)
            self.assertFalse(got["operational_criterion"])
            self.assertFalse(got["non_correspondence_scope"])
        finally:
            os.unlink(path)

    def test_null_randomized_crosswalk_earns_nothing(self):
        rng = random.Random(83352)
        prows, erows, art = artifacts()
        specs = [s for s in SPEC["rows"] if s["evidence_kind"].startswith("CROSSWALK_ROW")]
        earned = 0
        trials = 0
        alphabet = ["alpha", "beta", "gamma", "delta", "kappa", "sigma", "omega"]
        for _ in range(200):
            fake = []
            for r in prows:
                nr = dict(r)
                for c in ("proposed", "field", "canonical", "definition", "migration"):
                    nr[c] = " ".join(rng.choice(alphabet) for _ in range(6))
                fake.append(nr)
            s = specs[rng.randrange(len(specs))]
            trials += 1
            if A.check_row(s, fake, [], art)["verdict"] == "EARNED":
                earned += 1
        self.assertEqual(earned, 0, "null must be beaten: %d/%d randomized tables earned" % (earned, trials))
        # no-alarm: the true table still earns every in-scope row
        self.assertEqual(A.run()["rows_earned"], 34)


class TestRatchetGate(Moved):
    def test_ratchet_mechanism_detects_regression_and_scopes_new_files(self):
        """Test the mechanism, not the live corpus.

        `check(baseline, live, owned_new_files)` scopes the new-file rule to the
        files a lane actually added; `owned_new_files=None` keeps the strict
        repo-wide rule, which the workflow uses only on push to main. Calling it
        with no scope from a unit test makes every other lane's new file this
        lane's failure -- it reported 37 such files from six unrelated packages
        -- which is the opposite of what the gate is documented to do. The
        workflow already passes the PR diff. Here we check the logic itself.
        """
        base = {"counts": {"a.md": {"obligation": 2}, "gone.md": {"obligation": 1}}}

        # a file whose count rises is a regression
        worse = {"counts": {"a.md": {"obligation": 3}}}
        self.assertEqual(len(R.check(base, worse)["regressions"]), 1)

        # a file whose count falls, or disappears, is an improvement
        better = {"counts": {"a.md": {"obligation": 1}}}
        rep = R.check(base, better)
        self.assertEqual(rep["regressions"], [])
        self.assertEqual(rep["improved_entries"], 2)
        self.assertEqual(rep["sites_removed_vs_baseline"], 2)

        # a NEW file with hits fails the lane that added it ...
        added = {"counts": {"a.md": {"obligation": 2}, "mine.md": {"obligation": 1}}}
        self.assertEqual(R.check(base, added, ["mine.md"])["new_files_with_hits"],
                         ["mine.md"])
        # ... and is merely reported when another lane added it
        rep = R.check(base, added, [])
        self.assertEqual(rep["new_files_with_hits"], [])
        self.assertEqual(rep["unowned_new_files_with_hits"], ["mine.md"])

        # no-alarm: an unchanged corpus is silent
        rep = R.check(base, {"counts": dict(base["counts"])}, [])
        self.assertEqual(rep["regressions"], [])
        self.assertEqual(rep["new_files_with_hits"], [])

    def test_live_corpus_is_measurable_and_baseline_is_real(self):
        live = R.measure()
        self.assertIsInstance(live["total_hits"], int)
        self.assertGreater(live["total_hits"], 0)
        self.assertGreater(live["files_scanned"], 0)

    def test_baseline_is_not_vacuous(self):
        base = json.load(open(R.BASELINE))
        self.assertGreater(base["total_hits"], 1000)
        self.assertGreater(base["files_with_hits"], 100)
        self.assertGreater(base["files_scanned"], base["files_with_hits"])

    def test_hostile_HB6_new_banned_site_in_a_tracked_file_fails(self):
        base = {"total_hits": 2, "counts": {"a.md": {"remint": 2}}}
        live = {"total_hits": 3, "counts": {"a.md": {"remint": 3}}}
        rep = R.check(base, live)
        self.assert_moved("HB6 count-regression", 2, 3, len(rep["regressions"]) == 1)

    def test_hostile_HB7_new_file_with_banned_terms_fails(self):
        base = {"total_hits": 2, "counts": {"a.md": {"remint": 2}}}
        live = {"total_hits": 3, "counts": {"a.md": {"remint": 2}, "b.md": {"obligation": 1}}}
        rep = R.check(base, live)
        self.assert_moved("HB7 new-file", 0, len(rep["new_files_with_hits"]),
                          rep["new_files_with_hits"] == ["b.md"])

    def test_hostile_HB8_end_to_end_the_gate_sees_a_real_new_file(self):
        d = tempfile.mkdtemp()
        clean = os.path.join(d, "clean.md")
        open(clean, "w").write("This package uses architecture-agnostic search.\n")
        m0 = R.measure(files=[clean], root=d)
        dirty = os.path.join(d, "dirty.md")
        open(dirty, "w").write("We remint the obligation over each machine species.\n")
        m1 = R.measure(files=[clean, dirty], root=d)
        self.assert_moved("HB8 end-to-end", m0["total_hits"], m1["total_hits"],
                          m1["total_hits"] >= 3)
        self.assertEqual(m0["total_hits"], 0, "no-alarm case failed on clean prose")
        rep = R.check({"total_hits": 0, "counts": {"clean.md": {}}}, m1)
        self.assertEqual(rep["new_files_with_hits"], ["dirty.md"])

    def test_new_file_rule_is_scoped_to_the_PR_diff(self):
        """A lane must be failed for ITS files, never for another lane's."""
        base = {"total_hits": 2, "counts": {"a.md": {"remint": 2}}}
        live = {"total_hits": 4, "counts": {"a.md": {"remint": 2},
                                            "mine.md": {"remint": 1},
                                            "theirs.md": {"obligation": 1}}}
        wide = R.check(base, live)
        self.assertEqual(sorted(wide["new_files_with_hits"]), ["mine.md", "theirs.md"])
        scoped = R.check(base, live, owned_new_files=["mine.md"])
        self.assert_moved("scoped-new-file", len(wide["new_files_with_hits"]),
                          len(scoped["new_files_with_hits"]),
                          scoped["new_files_with_hits"] == ["mine.md"])
        self.assertEqual(scoped["unowned_new_files_with_hits"], ["theirs.md"])

    def test_improvement_never_fails_the_build(self):
        base = {"total_hits": 5, "counts": {"a.md": {"remint": 5}}}
        live = {"total_hits": 1, "counts": {"a.md": {"remint": 1}}}
        rep = R.check(base, live)
        self.assertEqual(rep["regressions"], [])
        self.assertEqual(rep["sites_removed_vs_baseline"], 4)


if __name__ == "__main__":
    unittest.main(verbosity=2)
