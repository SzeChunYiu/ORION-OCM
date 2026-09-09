"""Hostile tests for the G2 acquisition-economics study.

The study exists to test whether a corpus scan can replace a search tournament.
Its result is a negative, and a negative is only worth keeping if the cheap
selectors were given a fair run. So most of these tests attack the selectors'
implementation rather than the conclusion: a compression score that is silently
broken would manufacture exactly the negative this study reports.
"""

from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parent


def _load():
    spec = importlib.util.spec_from_file_location("acq", HERE / "experiment.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


E = _load()


class Rewrite(unittest.TestCase):
    """The compression score is only as good as the rewriter under it."""

    def test_disjoint_occurrences_are_all_replaced(self):
        self.assertEqual(E._rewrite(["a", "b", "c", "a", "b"], ("a", "b")), (3, 2))

    def test_absent_fragment_changes_nothing(self):
        self.assertEqual(E._rewrite(["a", "b", "c"], ("x", "y")), (3, 0))

    def test_overlapping_occurrences_are_taken_greedily_not_twice(self):
        """`aaa` contains `aa` twice by overlap but a macro expander can only take
        one. Counting both would inflate compression for self-overlapping
        fragments and bias the selector toward exactly the short repeated
        fragments this study is testing."""
        self.assertEqual(E._rewrite(["a", "a", "a"], ("a", "a")), (2, 1))

    def test_a_fragment_as_long_as_the_program_collapses_it_to_one_token(self):
        self.assertEqual(E._rewrite(["a", "b"], ("a", "b")), (1, 1))

    def test_rewriting_never_lengthens_a_program(self):
        for program, fragment in ((["a", "b", "c"], ("a", "b")), (["a"], ("a", "b")),
                                  (["a", "b", "a", "b"], ("b", "a"))):
            length, _ = E._rewrite(program, fragment)
            self.assertLessEqual(length, len(program), (program, fragment))


class Selectors(unittest.TestCase):
    def _corpus(self, programs):
        class Result:
            def __init__(self, program):
                self.program = list(program)
        return tuple((None, Result(p)) for p in programs)

    def test_compression_prefers_the_fragment_that_saves_more_tokens(self):
        rows = self._corpus([["a", "b", "c"], ["a", "b", "d"], ["a", "b", "e"]])
        work = {"token_operations": 0}
        scores = E.score_compression((("a", "b"), ("c", "d")), {}, rows, work)
        self.assertGreater(scores[("a", "b")], scores[("c", "d")])
        self.assertGreater(work["token_operations"], 0)

    def test_compression_charges_the_library_entry_it_adds(self):
        """A macro that fires once saves one token and costs its own length, so a
        long fragment with a single occurrence must not score positive."""
        rows = self._corpus([["a", "b", "c", "d"]])
        scores = E.score_compression((("a", "b", "c"),), {}, rows, {"token_operations": 0})
        self.assertLess(scores[("a", "b", "c")], 0)

    def test_per_token_normalisation_actually_divides_by_library_size(self):
        rows = self._corpus([["a", "b", "x"], ["a", "b", "y"]])
        raw = E.score_compression((("a", "b"),), {}, rows, {"token_operations": 0})
        per = E.score_compression_per_token((("a", "b"),), {}, rows, {"token_operations": 0})
        self.assertAlmostEqual(per[("a", "b")], raw[("a", "b")] / 2)

    def test_frequency_is_the_support_count_and_nothing_else(self):
        support = {("a", "b"): 7, ("c", "d"): 3}
        scores = E.score_frequency(tuple(support), support, (), {"token_operations": 0})
        self.assertEqual(scores, {("a", "b"): 7.0, ("c", "d"): 3.0})

    def test_no_selector_runs_a_search(self):
        """The whole claim is that these cost a scan. If any of them ever charged an
        enumeration attempt the comparison against the tournament would be void."""
        rows = self._corpus([["a", "b", "c"], ["a", "b", "d"]])
        for name in E.SELECTORS:
            out = E.select(name, (("a", "b"), ("b", "c")), {("a", "b"): 2, ("b", "c"): 1}, rows)
            self.assertEqual(out["acquisition_work"]["enumeration_attempts"], 0, name)
            self.assertEqual(out["acquisition_work"]["unique_checks"], 0, name)

    def test_ties_break_on_the_frozen_candidate_order(self):
        rows = self._corpus([["a", "b", "c", "d"], ["a", "b", "c", "d"]])
        first = E.select("FREQUENCY", (("a", "b"), ("c", "d")),
                         {("a", "b"): 5, ("c", "d"): 5}, rows)
        self.assertEqual(tuple(first["chosen"]), ("a", "b"))
        second = E.select("FREQUENCY", (("c", "d"), ("a", "b")),
                          {("a", "b"): 5, ("c", "d"): 5}, rows)
        self.assertEqual(tuple(second["chosen"]), ("c", "d"))


class Statistics(unittest.TestCase):
    def test_spearman_is_one_on_a_monotone_pair(self):
        self.assertAlmostEqual(E.spearman([1, 2, 3, 4], [10, 20, 30, 40]), 1.0)

    def test_spearman_is_minus_one_on_a_reversed_pair(self):
        self.assertAlmostEqual(E.spearman([1, 2, 3, 4], [40, 30, 20, 10]), -1.0)

    def test_spearman_is_zero_on_a_constant(self):
        """A score that says nothing must correlate with nothing. Sort-position
        ranking returned 1.0 here, which would dress a meaningless selector up as
        a strong one."""
        self.assertEqual(E.spearman([1, 2, 3, 4], [5, 5, 5, 5]), 0.0)

    def test_tied_scores_take_the_average_rank(self):
        """The real compression scores contain a three-way tie at the top of the
        pool, so tie handling decides the reported number, not decorates it."""
        self.assertAlmostEqual(E.spearman([1, 1, 2, 2], [1, 1, 2, 2]), 1.0)
        self.assertAlmostEqual(E.spearman([1, 1, 2, 2], [2, 2, 1, 1]), -1.0)


class Terminals(unittest.TestCase):
    """Every terminal must be reachable, including the ones that would embarrass
    this study's own framing."""

    def _doc(self, chosen, savings, support=None):
        candidates = list(savings)
        return {
            "candidates": candidates,
            "support": support or {c: 1 for c in candidates},
            "training_search_slots": 1000,
            "reused_from_192": {"test_tasks": 64},
            "tournament": {"choice": candidates[0].split(),
                           "savings": savings,
                           "acquisition_enumeration_attempts": 9_000_000},
            "cheap_selectors": [
                {"selector": name, "chosen": chosen[name].split(),
                 "scores": {c: float(len(c)) for c in candidates},
                 "acquisition_work": {"token_operations": 10}}
                for name in chosen],
            "test_by_macro": {c: {"saving": savings[c]} for c in candidates},
        }

    def test_disagreement_gives_the_no_cheap_acquisition_terminal(self):
        doc = self._doc({"FREQUENCY": "b b", "MDL_COMPRESSION": "b b"},
                        {"a a": 100, "b b": -50})
        out = E.verdict(doc)
        self.assertEqual(out["terminal"], "NO_CHEAP_ACQUISITION_AT_THIS_ECOLOGY")
        self.assertIn("ARGMAX failure", out["terminal_reason"])

    def test_universal_agreement_is_reported_against_the_protocol_not_for_it(self):
        """If even raw frequency picks the tournament's macro, the tournament bought
        no information. That is a negative about #192's protocol and the study must
        say so rather than bank it as a cheap-acquisition win."""
        doc = self._doc({"FREQUENCY": "a a", "MDL_COMPRESSION": "a a"},
                        {"a a": 100, "b b": -50})
        out = E.verdict(doc)
        self.assertEqual(out["terminal"],
                         "ANY_CHEAP_RULE_AGREES_SELECTION_IS_NOT_DISCRIMINATING")
        self.assertIn("bought no information", out["terminal_reason"])

    def test_partial_agreement_without_search_aware_does_not_claim_search_aware(self):
        doc = self._doc({"FREQUENCY": "b b", "MDL_COMPRESSION": "a a"},
                        {"a a": 100, "b b": -50})
        out = E.verdict(doc)
        self.assertEqual(out["terminal"],
                         "CHEAP_NON_SEARCH_AWARE_SELECTOR_AGREES_WITH_TOURNAMENT")
        self.assertIn("MDL_COMPRESSION", out["terminal_reason"])
        self.assertNotIn("SEARCH_AWARE", out["selectors_agreeing_with_the_tournament"])
        self.assertIn("No OCM-specific claim follows", out["terminal_reason"])

    def test_search_aware_partial_agreement_is_the_named_positive(self):
        doc = self._doc({"FREQUENCY": "b b", "SEARCH_AWARE": "a a"},
                        {"a a": 100, "b b": -50})
        out = E.verdict(doc)
        self.assertEqual(out["terminal"],
                         "CHEAP_SEARCH_AWARE_SELECTION_REPRODUCES_THE_TOURNAMENT_CHOICE")
        self.assertIn("SEARCH_AWARE", out["terminal_reason"])
        self.assertIn("No OCM-specific claim follows", out["terminal_reason"])

    def test_break_even_falls_when_acquisition_becomes_free(self):
        doc = self._doc({"FREQUENCY": "b b", "MDL_COMPRESSION": "a a"},
                        {"a a": 100, "b b": -50})
        out = E.verdict(doc)
        self.assertLess(out["break_even_tasks_with_zero_search_acquisition"],
                        out["break_even_tasks_with_tournament"])

    def test_a_non_positive_per_task_saving_has_no_horizon_rather_than_a_huge_one(self):
        doc = self._doc({"FREQUENCY": "a a", "MDL_COMPRESSION": "b b"},
                        {"a a": -10, "b b": -50})
        out = E.verdict(doc)
        self.assertIsNone(out["break_even_tasks_with_tournament"])
        self.assertIsNone(out["break_even_tasks_with_zero_search_acquisition"])


class Custody(unittest.TestCase):
    def test_the_incumbent_harness_is_imported_not_reimplemented(self):
        source = (HERE / "experiment.py").read_text()
        self.assertIn("import experiment as G2", source)
        for name in ("frozen_partition", "candidate_pool", "build_search_index",
                     "evaluate_index"):
            self.assertIn(f"G2.{name}", source)

    def test_the_test_stratum_exposure_is_declared(self):
        source = " ".join((HERE / "experiment.py").read_text().split())
        self.assertIn("test stratum is no longer naive", source)
        self.assertIn("already-seen population", source)
        self.assertIn("SELECTION AGREEMENT", source)

    def test_no_production_source_is_written(self):
        source = (HERE / "experiment.py").read_text()
        for banned in ("open(", "write_text", "unlink", "rmtree"):
            if banned == "write_text":
                self.assertEqual(source.count("write_text"), 1,
                                 "only the receipt may be written")




    def test_frozen_receipt_names_search_aware_not_a_generic_partial(self):
        doc = json.loads((HERE / "G2_ACQUISITION_ECONOMICS_V1.json").read_text())
        verdict = doc["verdict"]
        self.assertEqual(
            verdict["terminal"],
            "CHEAP_SEARCH_AWARE_SELECTION_REPRODUCES_THE_TOURNAMENT_CHOICE",
        )
        self.assertEqual(verdict["selectors_agreeing_with_the_tournament"], ["SEARCH_AWARE"])


class SearchAwareSelector(unittest.TestCase):
    """The selector that overturned this study's own first negative."""

    def test_the_widening_term_is_countable_without_any_search(self):
        """A word with m macro tokens and (d-m) primitives expands to m*L+(d-m),
        so the grammar's width at each depth is a sum of binomial terms. This is
        the term compression cannot see, and it needs no enumeration."""
        self.assertEqual(E._words_at_depth(0, 4, None, 7), 1)
        self.assertEqual(E._words_at_depth(1, 4, None, 7), 4)
        self.assertEqual(E._words_at_depth(2, 4, None, 7), 16)
        # With a length-2 macro at depth 2: 1 word of two macros (expands to 4),
        # 2*4 words of one macro and one primitive, 16 all-primitive.
        self.assertEqual(E._words_at_depth(2, 4, 2, 7), 1 + 2 * 4 + 16)

    def test_a_short_macro_widens_the_grammar_more_than_a_long_one(self):
        """The whole mechanism in one assertion: short macros save least per
        firing and widen most, which is why every compressor picks wrong."""
        short = E._cumulative(7, 4, 2, 7)
        long = E._cumulative(7, 4, 3, 7)
        primitive = E._cumulative(7, 4, None, 7)
        self.assertGreater(short, long)
        self.assertGreater(long, primitive)

    def test_the_macro_length_bound_is_respected_in_the_count(self):
        """A macro longer than the budget can never appear in a valid word."""
        self.assertEqual(E._words_at_depth(1, 4, 9, 7), 4)

    def test_the_selector_charges_a_scan_and_never_an_enumeration(self):
        class R:
            def __init__(self, program):
                self.program = list(program)
        rows = ((None, R(["inc", "dec", "inc", "dec"])),)
        work = {"token_operations": 0, "enumeration_attempts": 0, "unique_checks": 0}
        E.score_search_aware((("inc", "dec"),), {}, rows, work, budget=7, primitives=4)
        self.assertGreater(work["token_operations"], 0)
        self.assertEqual(work["enumeration_attempts"], 0)

    def test_it_is_registered_as_a_selector_like_any_other(self):
        self.assertIn("SEARCH_AWARE", E.SELECTORS)


if __name__ == "__main__":
    unittest.main(verbosity=2)
