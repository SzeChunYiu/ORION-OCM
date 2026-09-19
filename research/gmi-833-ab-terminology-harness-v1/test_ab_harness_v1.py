#!/usr/bin/env python3
"""Tests for gmi-833-ab-terminology-harness-v1.

Every hostile asserts that the perturbation MOVED the quantity it targets
before asserting that the checker flagged it.
"""
import copy
import json
import os
import random
import shutil
import subprocess
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

    def test_verbatim_issue_row_quotations_are_exempt(self):
        """A freeze must quote its issue rows byte-exact and never be edited.

        Those rows contain banned terms, so the ratchet and the closure standard
        were in direct conflict: a lane could satisfy one only by falsifying a
        quotation or tampering with custody. Three lanes hit this independently,
        and 41 already-committed freezes carry the identical hit and were
        grandfathered into the baseline -- so it was never enforced on them
        either.
        """
        quoted = {"file": "/x/FREEZE_V1.md", "line_no": "27", "term": "obligation",
                  "text": "- [ ] Replace ambiguous uses of `obligation` in theory."}
        blockquoted = dict(quoted, text="> - [x] Re-audit the obligation ledger.")
        prose = dict(quoted, text="This tranche discharges the obligation above.")

        self.assertTrue(R._is_quoted_issue_row(quoted))
        self.assertTrue(R._is_quoted_issue_row(blockquoted))
        # no-alarm: the lane's OWN prose is still scanned, in the same file
        self.assertFalse(R._is_quoted_issue_row(prose))

        # and the exemption actually fires on the real corpus
        live = R.measure()
        self.assertGreater(live["quoted_issue_rows_exempt"], 0,
                           "exemption never fired; the hit shape may have changed")

    # ------------------------------------------------------------------
    # Non-prose exemptions. Each case shows the parent DETECTS the token
    # (raw hit count moved), the ratchet EXEMPTS it, and a genuine prose hit
    # in the same file still fires. Five open PRs were failed on these.
    # ------------------------------------------------------------------
    def _raw_and_measured(self, body, name="NOTE.md", subdir="gmi-833-x-fixture-v1"):
        d = tempfile.mkdtemp()
        pkg = os.path.join(d, "research", subdir)
        os.makedirs(pkg)
        path = os.path.join(pkg, name)
        open(path, "w").write(body)
        raw = R.load_gate().scan_paths([path], context="paper-facing")
        live = R.measure(files=[path], root=d)
        rel = os.path.relpath(path, d)
        return raw, live, live["counts"].get(rel, {}), rel

    def test_identifier_tokens_and_inline_code_are_not_prose(self):
        body = ("# Parent ownership -- gmi-833-ae-morphology-sweep-v1\n\n"
                "| `gmi-833-morphology-selection-v1` | the no-flip law | `6511cba4` |\n\n"
                "Reproduce: python3 -I -B research/gmi-833-ae-morphology-sweep-v1/"
                "test_morphology_sweep_v1.py -v\n\n"
                "The `selection` correspondence is pinned by blob sha.\n")
        raw, live, counts, _ = self._raw_and_measured(body)
        raw_terms = sorted({h["term"] for h in raw})
        self.assert_moved("identifier-detected-by-parent", 0, len(raw),
                          "bare morphology" in raw_terms and
                          "bare selection (undisambiguated)" in raw_terms)
        self.assertEqual(counts, {}, "identifier / code-span hits survived: %r" % counts)
        self.assertEqual(live["total_hits"], 0)
        self.assertEqual(live["identifiers_exempt"] + live["code_spans_exempt"], len(raw))
        self.assertGreater(live["identifiers_exempt"], 0)
        self.assertGreater(live["code_spans_exempt"], 0)

        # no-alarm for the exemption itself: prose in the SAME file still fires,
        # and a line mixing a package name with prose keeps exactly the prose hit.
        body2 = body + ("\nA morphology verdict needs two conventions.\n"
                        "Under `gmi-833-morphology-selection-v1` every selection "
                        "threshold is a marginal error mass.\n")
        raw2, live2, counts2, _ = self._raw_and_measured(body2)
        self.assertGreater(len(raw2), len(raw))
        self.assertEqual(counts2, {"bare morphology": 1,
                                   "bare selection (undisambiguated)": 1}, counts2)

    def test_hyphenated_prose_compound_still_fires(self):
        """A hyphen alone does not make an identifier."""
        body = ("The transport onto the morphology-selection correspondence and the "
                "morphology-sweep lane's correction both need morphology/resource cost.\n")
        raw, live, counts, _ = self._raw_and_measured(body)
        self.assertEqual(len(raw), 4, raw)
        self.assertEqual(counts, {"bare morphology": 3,
                                  "bare selection (undisambiguated)": 1}, counts)
        self.assertEqual(live["identifiers_exempt"], 0)

    def test_fenced_code_blocks_are_not_prose(self):
        body = ("# Reproduce\n\n```bash\ncmp /tmp/sweep.json "
                "research/x/RESULT.json  # selection receipt\nrun morphology\n```\n\n"
                "Then a selection threshold is compared.\n")
        raw, live, counts, _ = self._raw_and_measured(body)
        self.assert_moved("fenced-detected-by-parent", 0, len(raw), len(raw) == 3)
        self.assertEqual(counts, {"bare selection (undisambiguated)": 1}, counts)
        self.assertEqual(live["code_spans_exempt"], 2)

    def test_quoted_rows_by_shape_numbered_and_backticked(self):
        body = ("# FREEZE\n\n"
                "3. `- [ ] Construct adversarial recodings designed to flip morphology conclusions.`\n"
                "`- [x] Test whether causal structure changes selected morphology.`\n"
                "1. `- [ ] Identify control parameters producing morphology phase transitions.`\n"
                "> - [ ] Reproduce under grammar remints.\n\n"
                "This tranche flips a morphology conclusion in its own words.\n")
        raw, live, counts, _ = self._raw_and_measured(body, name="FREEZE_V1.md")
        self.assert_moved("quoted-rows-detected-by-parent", 0, len(raw), len(raw) == 5)
        self.assertEqual(live["quoted_issue_rows_exempt"], 4)
        self.assertEqual(counts, {"bare morphology": 1}, counts)
        for t in ("3. `- [ ] a morphology`", "`- [x] a morphology`", "1. `- [ ] x`",
                  "- [ ] x", "> - [x] x", "2) `- [ ] x`"):
            self.assertTrue(R._is_quoted_issue_row({"text": t}), t)
        for t in ("the morphology-selection rule", "row `- [ ]` style is discussed",
                  "1. a numbered prose line about selection"):
            self.assertFalse(R._is_quoted_issue_row({"text": t}), t)

    def test_package_directory_heading_is_exempt(self):
        body = ("# gmi-833-ae-morphology-sweep-v1\n\n"
                "# FREEZE -- gmi-833-ae-morphology-sweep-v1\n\n"
                "## Which quantity predicts the selected morphology?\n")
        raw, live, counts, _ = self._raw_and_measured(body, subdir="gmi-833-ae-morphology-sweep-v1")
        self.assert_moved("heading-detected-by-parent", 0, len(raw), len(raw) == 3)
        self.assertEqual(counts, {"bare morphology": 1}, counts)
        self.assertEqual(live["identifiers_exempt"], 2)

    def test_ratchet_still_fails_on_a_planted_prose_hit_after_rebaseline(self):
        """The committed baseline was regenerated under the exemption
        semantics. It must still catch (a) a new owned file with a prose hit
        and (b) a count regression on a baselined file."""
        base = json.load(open(R.BASELINE))
        self.assertIn("count_semantics", base)
        d = tempfile.mkdtemp()
        pkg = os.path.join(d, "research", "gmi-833-planted-v1")
        os.makedirs(pkg)
        planted = os.path.join(pkg, "PLANTED_THEOREMS_V1.md")
        open(planted, "w").write("# gmi-833-planted-v1\n\nEvery selection threshold "
                                 "is a marginal error mass; see `gmi-833-morphology-selection-v1`.\n")
        live = R.measure(files=[planted], root=d)
        rel = os.path.relpath(planted, d)
        self.assertEqual(live["counts"], {rel: {"bare selection (undisambiguated)": 1}})
        rep = R.check(base, live, [rel])
        self.assertEqual(rep["new_files_with_hits"], [rel])
        # (b) a baselined file whose prose count rises by one is a regression
        some = sorted(base["counts"])[0]
        term = sorted(base["counts"][some])[0]
        bumped = {"counts": {some: {term: base["counts"][some][term] + 1}}}
        self.assertEqual(len(R.check(base, bumped, [])["regressions"]), 1)
        # no-alarm: the identical baseline counts are silent
        same = {"counts": {some: dict(base["counts"][some])}}
        self.assertEqual(R.check(base, same, [])["regressions"], [])

    # ------------------------------------------------------------------
    # Immutable custody files. A freeze may never be edited after its
    # receipt exists, so a banned term in it cannot be reworded -- but the
    # exemption is earned by a PIN on the file's bytes, never by its name.
    # Each case below is tested both ways.
    # ------------------------------------------------------------------
    def _custody_repo(self):
        """Scratch git repo: research/gmi-833-cust-fixture-v1 with a freeze
        committed FIRST and pinned by `freeze_commit`, a snapshot pinned by
        hash in RESULT_V1.json, an amendment nobody pinned, and a CORE.md --
        every one of them carrying the same prose hit."""
        d = tempfile.mkdtemp()
        git = shutil.which("git") or "/usr/bin/git"

        def run(*args):
            r = subprocess.run([git, "-C", d] + list(args), capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, r.stderr)
            return r.stdout.strip()
        run("init", "-q")
        run("config", "user.email", "t@example.invalid")
        run("config", "user.name", "t")
        pkg = os.path.join(d, "research", "gmi-833-cust-fixture-v1")
        os.makedirs(pkg)
        hit = "This tranche discharges the obligation it names.\n"
        open(os.path.join(pkg, "FREEZE_V1.md"), "w").write("# FREEZE\n\n" + hit)
        run("add", "-A")
        run("commit", "-q", "-m", "freeze")
        freeze_commit = run("rev-parse", "HEAD")
        open(os.path.join(pkg, "FREEZE_V1_AMENDMENT_1.md"), "w").write("# AMENDMENT\n\n" + hit)
        open(os.path.join(pkg, "CORE.md"), "w").write("# CORE\n\n" + hit)
        snap = "# snapshot\n\n" + hit
        open(os.path.join(pkg, "SNAPSHOT.md"), "w").write(snap)
        json.dump({"freeze_commit": freeze_commit, "amendments": ["FREEZE_V1_AMENDMENT_1.md"]},
                  open(os.path.join(pkg, "MANIFEST_V1.json"), "w"), indent=1)
        json.dump({"snapshot_blob_sha": R.blob_sha1(snap.encode("utf-8"))},
                  open(os.path.join(pkg, "RESULT_V1.json"), "w"), indent=1)
        run("add", "-A")
        run("commit", "-q", "-m", "implementation")
        rels = {k: "research/gmi-833-cust-fixture-v1/" + v for k, v in
                (("freeze", "FREEZE_V1.md"), ("amend", "FREEZE_V1_AMENDMENT_1.md"),
                 ("core", "CORE.md"), ("snap", "SNAPSHOT.md"))}
        return d, pkg, rels, freeze_commit

    def test_custody_pin_not_filename_decides_immutability(self):
        d, pkg, rels, freeze_commit = self._custody_repo()
        st = {k: R.custody_state(os.path.join(d, v), d) for k, v in rels.items()}
        self.assertEqual(st["freeze"]["state"], "PINNED_COMMIT")
        self.assertEqual(st["freeze"]["pinned_by"], freeze_commit)
        self.assertEqual(st["snap"]["state"], "PINNED_HASH")
        self.assertTrue(st["snap"]["pinned_by"].endswith("RESULT_V1.json"))
        # a FREEZE-named file nobody pinned is an ordinary file
        self.assertEqual(st["amend"]["state"], "UNPINNED")
        self.assertEqual(st["core"]["state"], "UNPINNED")

        files = [os.path.join(d, v) for v in sorted(rels.values())]
        live = R.measure(files=files, root=d)
        self.assertEqual(live["total_hits"], 4, live["counts"])
        rep = R.check({"counts": {}}, live, sorted(rels.values()), root=d)
        # pinned-freeze-with-hit and pinned-snapshot-with-hit -> informational
        self.assertEqual(sorted(e["path"] for e in rep["immutable_files_with_hits"]),
                         sorted([rels["freeze"], rels["snap"]]))
        self.assertEqual({e["path"]: e["state"] for e in rep["immutable_files_with_hits"]},
                         {rels["freeze"]: "PINNED_COMMIT", rels["snap"]: "PINNED_HASH"})
        # unpinned-freeze-with-hit and mutable CORE with a hit -> still fail
        self.assertEqual(rep["new_files_with_hits"], sorted([rels["amend"], rels["core"]]))
        self.assertEqual(rep["custody_states"][rels["amend"]], "UNPINNED")
        # the same repo with NO custody consulted enforces all four (the pin
        # is what moved two of them, not the file names)
        plain = R.check({"counts": {}}, live, sorted(rels.values()),
                        custody=lambda p: {"state": "UNPINNED", "pinned_by": None})
        self.assert_moved("custody-pin-moves-enforcement", len(plain["new_files_with_hits"]),
                          len(rep["new_files_with_hits"]), len(plain["new_files_with_hits"]) == 4)
        # regressions are never relaxed by a pin
        base = {"counts": {rels["freeze"]: {"obligation": 0}}}
        self.assertEqual(len(R.check(base, live, [], root=d)["regressions"]), 1)

    def test_custody_pin_dies_with_the_bytes_it_pins(self):
        """Editing a pinned file breaks its pin: the exemption cannot outlive
        the custody it rests on, so a lane cannot edit a freeze AND keep it
        exempt. An unverifiable pin is reported distinctly and enforced."""
        d, pkg, rels, freeze_commit = self._custody_repo()
        fz = os.path.join(d, rels["freeze"])
        self.assertEqual(R.custody_state(fz, d)["state"], "PINNED_COMMIT")
        open(fz, "a").write("An obligation added after the freeze.\n")
        tampered = R.custody_state(fz, d)
        self.assert_moved("tamper-breaks-pin", 1, 0, tampered["state"] == "UNPINNED")
        live = R.measure(files=[fz], root=d)
        rep = R.check({"counts": {}}, live, [rels["freeze"]], root=d)
        self.assertEqual(rep["new_files_with_hits"], [rels["freeze"]])
        self.assertEqual(rep["immutable_files_with_hits"], [])
        # hash pin: same property
        sn = os.path.join(d, rels["snap"])
        self.assertEqual(R.custody_state(sn, d)["state"], "PINNED_HASH")
        open(sn, "a").write("\n")
        self.assertEqual(R.custody_state(sn, d)["state"], "UNPINNED")
        # an unreachable custody commit is UNREACHABLE, not PINNED and not UNPINNED
        open(fz, "w").write("# FREEZE\n\nThis tranche discharges the obligation it names.\n")
        self.assertEqual(R.custody_state(fz, d)["state"], "PINNED_COMMIT")
        man = os.path.join(pkg, "MANIFEST_V1.json")
        json.dump({"freeze_commit": "0" * 40}, open(man, "w"))
        unreach = R.custody_state(fz, d)
        self.assertEqual(unreach["state"], "UNREACHABLE")
        rep = R.check({"counts": {}}, R.measure(files=[fz], root=d), [rels["freeze"]], root=d)
        self.assertEqual(rep["new_files_with_hits"], [rels["freeze"]])
        self.assertEqual(rep["custody_states"][rels["freeze"]], "UNREACHABLE")
        # a commit that exists but carries different bytes does not pin
        json.dump({"freeze_commit": freeze_commit}, open(man, "w"))
        open(fz, "w").write("# FREEZE\n\nReworded: this tranche discharges the requirement.\n")
        self.assertEqual(R.custody_state(fz, d)["state"], "UNPINNED")
        # no-alarm: a pinned file with no hits appears nowhere
        clean = os.path.join(pkg, "CLEAN.md")
        open(clean, "w").write("Architecture-agnostic search only.\n")
        json.dump({"clean": R.blob_sha1(open(clean, "rb").read())},
                  open(os.path.join(pkg, "RESULT_V1.json"), "w"))
        self.assertEqual(R.custody_state(clean, d)["state"], "PINNED_HASH")
        rep = R.check({"counts": {}}, R.measure(files=[clean], root=d),
                      ["research/gmi-833-cust-fixture-v1/CLEAN.md"], root=d)
        self.assertEqual(rep["new_files_with_hits"], [])
        self.assertEqual(rep["immutable_files_with_hits"], [])

    def test_custody_states_on_the_live_corpus(self):
        """The rule fires on real receipts: this package's own freeze is
        pinned by its manifest's `freeze_commit` (or, on a checkout without
        that commit, reported UNREACHABLE -- never silently UNPINNED), and its
        CORE.md is pinned by nothing."""
        fz = R.custody_state(os.path.join(HERE, "FREEZE_V1.md"))
        self.assertIn(fz["state"], ("PINNED_COMMIT", "PINNED_HASH", "UNREACHABLE"), fz)
        core = R.custody_state(os.path.join(HERE, "CORE.md"))
        self.assertEqual(core["state"], "UNPINNED", core)
        self.assertEqual(R._custody_commit_tokens(
            {"freeze_commit": "abcdef1234", "parent_pins": [{"blob_sha": "0123456789abcdef"}],
             "freeze_amendments": {"v1_e46003d5": "x", "A2": "ba5e0552784ed4f5bf98"},
             "freeze_date": "20260913", "freeze_seq": 12345678,
             "notes": "commit 1234567 is not custody"}),
            ["abcdef1234", "e46003d5", "ba5e0552784ed4f5bf98"])

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
