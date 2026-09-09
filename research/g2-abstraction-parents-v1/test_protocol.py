"""Hostile tests for the G2.2 tiny library-learning parents.

The economics capsule already showed compression FAILING the argmax against the
tournament and SEARCH_AWARE succeeding. These tests attack this capsule's
parents and its custody of that frozen receipt: a silently retuned compressor,
a rerun tournament, or an ADOPT on `dec square` would manufacture a G2.2 win
the evidence does not license.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import unittest

import experiment as E


class FrozenEconomicsCustody(unittest.TestCase):
    def test_the_frozen_receipt_is_imported_and_not_rewritten(self):
        self.assertTrue(E.FROZEN_PATH.is_file())
        frozen = E.load_frozen()
        self.assertEqual(frozen["verdict"]["terminal"], E.FROZEN_TERMINAL)
        self.assertEqual(frozen["verdict"]["terminal"],
                         "CHEAP_SEARCH_AWARE_SELECTION_REPRODUCES_THE_TOURNAMENT_CHOICE")
        source = (E.HERE / "experiment.py").read_text(encoding="utf-8")
        self.assertIn("G2_ACQUISITION_ECONOMICS_V1.json", source)
        self.assertIn("refusing to retune", source)

    def test_compression_still_chose_dec_square_and_search_aware_the_tournament(self):
        frozen = E.load_frozen()
        mdl = next(r for r in frozen["cheap_selectors"] if r["selector"] == "MDL_COMPRESSION")
        pt = next(r for r in frozen["cheap_selectors"] if r["selector"] == "COMPRESSION_PER_TOKEN")
        sa = next(r for r in frozen["cheap_selectors"] if r["selector"] == "SEARCH_AWARE")
        self.assertEqual(" ".join(mdl["chosen"]), "dec square")
        self.assertEqual(" ".join(pt["chosen"]), "dec square")
        self.assertEqual(" ".join(sa["chosen"]), "square dec square")
        self.assertEqual(" ".join(frozen["tournament"]["choice"]), "square dec square")
        self.assertEqual(
            frozen["verdict"]["agreement_analysis"]["selectors"]["MDL_COMPRESSION"]["chosen_utility_rank_of_pool"],
            13,
        )
        self.assertEqual(
            frozen["verdict"]["agreement_analysis"]["selectors"]["SEARCH_AWARE"]["chosen_utility_rank_of_pool"],
            1,
        )

    def test_the_tournament_is_not_rerun(self):
        source = (E.HERE / "experiment.py").read_text(encoding="utf-8")
        body = source.split('"""', 2)[-1]
        self.assertNotIn("evaluate_index(", body)
        self.assertNotIn("build_search_index(", body)
        self.assertIn("9,010,526", source)
        self.assertIn("tournament_rerun", source)

    def test_stdlib_only_no_pip_parents(self):
        source = (E.HERE / "experiment.py").read_text(encoding="utf-8")
        for banned in ("import stitch", "import dreamcoder", "from egg", "subprocess.check_call"):
            self.assertNotIn(banned, source)
        self.assertIn("Stdlib only", source)


class AntiUnification(unittest.TestCase):
    def test_identical_programs_return_the_whole_inner_chain(self):
        p = ("square", "dec", "square")
        self.assertEqual(E.antiunify_inner(p, p), p)
        self.assertEqual(E.antiunify_outer(p, p), p)
        self.assertEqual(E.antiunify_positional(p, p), p)

    def test_disjoint_programs_have_empty_inner_and_outer(self):
        self.assertEqual(E.antiunify_inner(("inc", "inc"), ("dec", "dec")), ())
        self.assertEqual(E.antiunify_outer(("inc", "inc"), ("dec", "dec")), ())
        self.assertEqual(E.antiunify_positional(("inc", "square"), ("dec", "double")), ())

    def test_a_middle_hole_keeps_the_grounded_runs(self):
        left = ("square", "inc", "square")
        right = ("square", "dec", "square")
        self.assertEqual(E.antiunify_inner(left, right), ("square",))
        self.assertEqual(E.antiunify_outer(left, right), ("square",))
        self.assertEqual(E.antiunify_positional(left, right), ("square",))

    def test_longest_common_substring_is_the_grounded_au_residue(self):
        found = E.longest_common_substrings(
            ("inc", "square", "dec", "square"),
            ("double", "square", "dec", "square"),
        )
        self.assertEqual(found, {("square", "dec", "square")})

    def test_pair_parent_needs_two_programs(self):
        with self.assertRaises(RuntimeError):
            E.parent_antiunification([("inc", "dec")], (("inc", "dec"),))


class TinyEGraph(unittest.TestCase):
    def test_hashcons_returns_the_same_id_for_the_same_term(self):
        g = E.TinyEGraph()
        x = g.input_id()
        a = g.apply("inc", x)
        b = g.apply("inc", x)
        self.assertEqual(a, b)

    def test_inc_dec_saturates_to_identity(self):
        g = E.TinyEGraph()
        trace = g.add_program(("inc", "dec"))
        g.saturate()
        self.assertEqual(g.find(trace[0]), g.find(trace[-1]))
        self.assertEqual(g.irreducible_ngrams(("inc", "dec"), trace, 2), [])

    def test_dec_inc_saturates_to_identity(self):
        g = E.TinyEGraph()
        trace = g.add_program(("dec", "inc"))
        g.saturate()
        self.assertEqual(g.find(trace[0]), g.find(trace[-1]))

    def test_square_dec_is_not_identity(self):
        g = E.TinyEGraph()
        trace = g.add_program(("dec", "square"))
        g.saturate()
        self.assertNotEqual(g.find(trace[0]), g.find(trace[-1]))
        self.assertEqual(
            g.irreducible_ngrams(("dec", "square"), trace, 2),
            [("dec", "square")],
        )

    def test_cancelled_windows_are_not_extracted_as_abstractions(self):
        programs = [("inc", "dec", "square"), ("dec", "inc", "square")]
        candidates = (("dec", "square"), ("inc", "dec"), ("square", "dec", "square"))
        out = E.parent_egraph(programs, candidates)
        self.assertNotEqual(out["chosen"], ["inc", "dec"])
        self.assertNotEqual(out["chosen"], ["dec", "inc"])
        self.assertGreater(out["identity_cancelled_windows"], 0)
        self.assertGreater(out["nodes"], 1)
        self.assertLessEqual(out["eclasses"], out["nodes"])


class GrammarInduction(unittest.TestCase):
    def test_counts_productions_and_picks_the_hottest_bigram_in_the_pool(self):
        programs = [
            ("dec", "square", "inc"),
            ("dec", "square", "double"),
            ("inc", "inc", "inc"),
        ]
        candidates = (("dec", "square"), ("inc", "inc"), ("square", "dec", "square"))
        out = E.parent_grammar_induction(programs, candidates)
        self.assertEqual(out["chosen"], ["dec", "square"])
        self.assertGreaterEqual(out["n_productions"], 3)
        self.assertGreaterEqual(out["n_binary_productions"], 1)

    def test_empty_corpus_does_not_invent_a_fragment(self):
        out = E.parent_grammar_induction([], (("dec", "square"),))
        self.assertEqual(out["chosen"], [])
        self.assertEqual(out["n_binary_productions"], 0)


class GrammarWidening(unittest.TestCase):
    def test_length_two_widens_more_than_length_three(self):
        """The economics diagnosis, pinned here so a parent cannot ignore it."""
        prim = E.grammar_word_count(None)
        two = E.grammar_word_count(2)
        three = E.grammar_word_count(3)
        four = E.grammar_word_count(4)
        self.assertEqual(prim, 21845)
        self.assertEqual(two, 30348)
        self.assertEqual(three, 23451)
        self.assertEqual(four, 22158)
        self.assertGreater(two - prim, three - prim)

    def test_integration_cost_is_the_width_delta(self):
        cost = E.integration_cost(("dec", "square"))
        self.assertEqual(cost["grammar_width_delta"], 30348 - 21845)
        self.assertGreater(cost["relative_widening"], 0.3)
        long_cost = E.integration_cost(("square", "dec", "square"))
        self.assertLess(long_cost["grammar_width_delta"], cost["grammar_width_delta"])


class Dispositions(unittest.TestCase):
    def test_vocabulary_is_exactly_the_five_g22_words(self):
        self.assertEqual(E.DISPOSITIONS, ("ADOPT", "ADAPT", "GENERALIZE", "REJECT", "OPEN"))

    def test_compression_is_rejected_not_adopted(self):
        frozen = E.load_frozen()
        utility = E.lookup_utility(("dec", "square"), frozen)
        disp, residual = E.dispositions_for(utility, "compression")
        self.assertEqual(disp, "REJECT")
        self.assertIn("FAILED", residual)
        self.assertNotIn("ADOPT", disp)

    def test_search_aware_is_adopted(self):
        frozen = E.load_frozen()
        utility = E.lookup_utility(("square", "dec", "square"), frozen)
        disp, residual = E.dispositions_for(utility, "search_aware")
        self.assertEqual(disp, "ADOPT")
        self.assertIn("No OCM-specific residual", residual)

    def test_program_compression_generalizes_the_scan(self):
        frozen = E.load_frozen()
        utility = E.lookup_utility(("dec", "square"), frozen)
        disp, residual = E.dispositions_for(utility, "generalize_scan")
        self.assertEqual(disp, "GENERALIZE")
        self.assertIn("SEARCH_AWARE", residual)

    def test_unknown_fragment_is_open_because_the_tournament_is_not_rerun(self):
        frozen = E.load_frozen()
        utility = E.lookup_utility(("inc", "dec", "inc", "dec"), frozen)
        self.assertFalse(utility["in_frozen_pool"])
        disp, _residual = E.dispositions_for(utility, "antiunification")
        self.assertEqual(disp, "OPEN")

    def test_a_live_match_without_width_is_adapt_not_adopt(self):
        frozen = E.load_frozen()
        utility = E.lookup_utility(("square", "dec", "square"), frozen)
        disp, residual = E.dispositions_for(utility, "antiunification")
        self.assertEqual(disp, "ADAPT")
        self.assertIn("justification", residual)

    def test_every_g22_box_is_registered(self):
        self.assertEqual(len(E.G22_BOXES), 8)
        self.assertIn("Stitch-style library learning", E.G22_BOXES)
        self.assertIn("DreamCoder-class abstraction", E.G22_BOXES)
        self.assertIn("anti-unification", E.G22_BOXES)
        self.assertIn("grammar induction", E.G22_BOXES)
        self.assertIn("e-graph / rewrite-derived abstraction", E.G22_BOXES)
        self.assertIn("program compression", E.G22_BOXES)
        self.assertIn("domain-native method induction", E.G22_BOXES)
        self.assertIn("strong conventional parent with same primitive library", E.G22_BOXES)


class SourceCustody(unittest.TestCase):
    def test_methods_blob_pinned(self):
        self.assertEqual(E.git_blob_sha1(E.SRC / "ocm" / "learning" / "methods.py"), E.METHOD_BLOB)

    def test_no_production_source_is_written_except_the_receipt(self):
        source = (E.HERE / "experiment.py").read_text(encoding="utf-8")
        self.assertEqual(source.count("write_text"), 1)
        self.assertNotIn("unlink", source)
        self.assertNotIn("rmtree", source)

    def test_harness_modules_are_loaded_by_unique_names(self):
        """`import experiment as G2` would shadow this file. Path load is required."""
        source = (E.HERE / "experiment.py").read_text(encoding="utf-8")
        self.assertIn("g2_macro_operator_v1_experiment", source)
        self.assertIn("g2_acquisition_economics_v1_experiment", source)
        self.assertIn("spec_from_file_location", source)

    def test_sibling_receipts_are_not_overwritten(self):
        source = (E.HERE / "experiment.py").read_text(encoding="utf-8")
        self.assertNotIn("g2-strong-parents-v1", source)
        self.assertNotIn("g2-utility-gated-parents-v2", source)
        self.assertNotIn("FROZEN_PATH.write_text", source)
        self.assertNotIn("FROZEN_PATH.write_bytes", source)


class ResultContract(unittest.TestCase):
    def test_committed_result_earns_the_compare_boxes_without_inventing_library_learning(self):
        path = E.HERE / "RESULT.json"
        if not path.is_file():
            self.skipTest("RESULT.json not yet written")
        doc = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(doc["schema"], E.SCHEMA)
        self.assertEqual(doc["terminal"], "CONVENTIONAL_LIBRARY_PARENTS_SUBORDINATE_TO_SEARCH_AWARE")
        self.assertEqual(doc["imported_receipt"]["terminal"], E.FROZEN_TERMINAL)
        self.assertTrue(doc["imported_receipt"]["compression_failed_argmax"])
        self.assertFalse(doc["tournament_rerun"])
        self.assertIn("conventional-same-library", doc["adopt"])
        self.assertIn("stitch-style-library", doc["reject"])
        self.assertIn("dreamcoder-class-abstraction", doc["reject"])
        self.assertEqual(set(doc["g22_boxes"]), set(E.G22_BOXES))
        self.assertEqual(set(doc["box_mapping"]), set(E.G22_BOXES))
        self.assertEqual(set(doc["dispositions_used"]), set(E.DISPOSITIONS))
        by = {row["parent"]: row for row in doc["parents"]}
        self.assertEqual(by["stitch-style-library"]["disposition"], "REJECT")
        self.assertEqual(by["dreamcoder-class-abstraction"]["disposition"], "REJECT")
        self.assertEqual(by["program-compression"]["disposition"], "GENERALIZE")
        self.assertEqual(by["conventional-same-library"]["disposition"], "ADOPT")
        self.assertEqual(by["conventional-same-library"]["chosen"], ["square", "dec", "square"])
        self.assertEqual(by["stitch-style-library"]["chosen"], ["dec", "square"])
        self.assertEqual(by["stitch-style-library"]["utility_rank_of_pool"], 13)
        self.assertEqual(by["conventional-same-library"]["utility_rank_of_pool"], 1)
        self.assertEqual(by["conventional-same-library"]["tournament_twin"]["disposition"], "ADAPT")
        self.assertIn("No OCM-specific claim", doc["authority"])
        self.assertIn("not retuned", doc["terminal_reason"].lower())
        frozen = json.loads(E.FROZEN_PATH.read_text(encoding="utf-8"))
        self.assertEqual(
            doc["imported_receipt"]["sha256"],
            hashlib.sha256(E.FROZEN_PATH.read_bytes()).hexdigest(),
        )
        self.assertEqual(
            frozen["tournament"]["acquisition_enumeration_attempts"],
            doc["imported_receipt"]["tournament_acquisition_enumeration_attempts"],
        )
        for row in doc["parents"]:
            self.assertIn(row["disposition"], E.DISPOSITIONS)
            self.assertIn("origin_identity", row)
            self.assertIn("prior_information", row)
            self.assertIn("integration_cost", row)
            self.assertIn("residual_after_subtraction", row)
            self.assertEqual(row["origin_identity"], row["parent"])
            self.assertEqual((row.get("acquisition_work") or {}).get("enumeration_attempts", 0), 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
