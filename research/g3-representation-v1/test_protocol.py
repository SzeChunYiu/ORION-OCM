"""Hostile tests for G3.3 representation improvement and G3.4 diagnosis.

The dangerous outcomes here are a representation study that cannot fail, and a
diagnosis that licenses a strong conclusion from a timeout. #165 names the second
one directly -- "timeout alone cannot license JUMP" -- so it gets its own test.
"""

from __future__ import annotations

import importlib.util
from fractions import Fraction
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent


def _load():
    spec = importlib.util.spec_from_file_location("g33", HERE / "experiment.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


E = _load()

#: A real census over a small budget, so the terminal tests are exercised against
#: measured redundancy rather than a hand-written stub.
CENSUS = E.redundancy_census(budget=3)


class RegisteredLanguage(unittest.TestCase):
    def test_a_misleading_representation_is_included_by_design(self):
        """G3.3 asks for at least one. A study that only registers sound
        candidates cannot expose the failure mode it exists to test."""
        self.assertTrue(set(E.EXPECTED_MISLEADING) & set(E.REPRESENTATIONS))
        self.assertGreaterEqual(len(E.EXPECTED_MISLEADING), 2)

    def test_the_exact_representation_is_the_reference_not_a_candidate(self):
        """Selecting EXACT would make the study vacuous -- it is what soundness is
        defined against."""
        source = " ".join((HERE / "experiment.py").read_text().split())
        self.assertIn('k != "EXACT"', source)
        self.assertIn("it is the reference, not a candidate improvement", source)
        self.assertEqual(E.run.__doc__ is None, False)

    def test_an_unregistered_representation_is_refused(self):
        with self.assertRaises(ValueError):
            E.abstract((Fraction(1),), "INVENTED")

    def test_the_added_candidates_are_declared_as_training_selected(self):
        source = (HERE / "experiment.py").read_text()
        self.assertIn("no protected later outcome was consulted", source)
        self.assertIn("CANNOT_CHECK_NO_COARSER_REPRESENTATION_FIT_TRAINING", source)


class Abstractions(unittest.TestCase):
    def test_exact_distinguishes_everything_it_should(self):
        a = (Fraction(1), Fraction(2))
        b = (Fraction(1), Fraction(3))
        self.assertNotEqual(E.abstract(a, "EXACT"), E.abstract(b, "EXACT"))

    def test_degree_merges_states_that_differ(self):
        a = (Fraction(1), Fraction(2))
        b = (Fraction(9), Fraction(9))
        self.assertEqual(E.abstract(a, "DEGREE"), E.abstract(b, "DEGREE"))

    def test_a_hash_collides_only_on_a_multiple_of_its_modulus(self):
        a = (Fraction(1),)
        self.assertEqual(E.abstract(a, "MOD_997"), E.abstract((Fraction(998),), "MOD_997"))
        self.assertNotEqual(E.abstract(a, "MOD_997"), E.abstract((Fraction(2),), "MOD_997"))

    def test_truncation_keeps_the_degree_so_it_cannot_merge_across_degrees(self):
        a = (Fraction(1), Fraction(2), Fraction(3), Fraction(4))
        b = (Fraction(1), Fraction(2), Fraction(3))
        self.assertNotEqual(E.abstract(a, "TRUNCATED_3"), E.abstract(b, "TRUNCATED_3"))


class Diagnosis(unittest.TestCase):
    """G3.4."""

    def test_the_diagnosis_vocabulary_covers_the_registered_categories(self):
        source = (HERE / "experiment.py").read_text()
        for category in ("REPRESENTATION_INSUFFICIENT", "SEARCH_MORE",
                         "MISSING_OPERATOR", "RESOURCE_BOUND", "CANNOT_CHECK"):
            self.assertIn(category, source)

    def test_a_timeout_can_never_license_representation_insufficient(self):
        """#165: 'Timeout alone cannot license JUMP.' In this study that means an
        exhausted budget must map to RESOURCE_BOUND, and REPRESENTATION_INSUFFICIENT
        may only be returned when the EXACT representation solves the SAME task at
        the SAME budget -- a positive re-run, never an absence."""
        source = (HERE / "experiment.py").read_text()
        body = source[source.index("def diagnose("):source.index("def evaluate(")]
        first = body.index("REPRESENTATION_INSUFFICIENT")
        self.assertIn('search(task, budget, "EXACT")["solved"]', body[:first])
        self.assertLess(body.index("RESOURCE_BOUND"), body.index("CANNOT_CHECK"))
        self.assertIn('["exhausted"]', body)

    def test_diagnosis_re_runs_rather_than_guessing_from_the_failure(self):
        body = (HERE / "experiment.py").read_text()
        body = body[body.index("def diagnose("):body.index("def evaluate(")]
        self.assertGreaterEqual(body.count("search("), 4)


class Vacuity(unittest.TestCase):
    def test_the_terminal_says_so_when_the_population_cannot_discriminate(self):
        doc = {"discovery": {"selected": "EXACT", "fits_training": ["EXACT"],
                             "charged_construction": 10},
               "later": {"by_representation": {"EXACT": {"extensions": 100, "solved": []}},
                         "reference_solved": [],
                         "fits_training_but_disagrees_later": []},
               "invalidation": {"selected_still_matches_exact": True},
               "diagnosis": {}}
        out = E.verdict(doc)
        self.assertEqual(out["terminal"], "CANNOT_CHECK_NO_COARSER_REPRESENTATION_FIT_TRAINING")
        self.assertIn("cannot discriminate", out["terminal_reason"])

    def test_an_unsound_selection_is_the_channel_insufficient_terminal(self):
        doc = {"discovery": {"selected": "DEGREE", "fits_training": ["EXACT", "DEGREE"],
                             "charged_construction": 10},
               "later": {"by_representation": {"EXACT": {"extensions": 100, "solved": ["a"]},
                                               "DEGREE": {"extensions": 10, "solved": []}},
                         "reference_solved": ["a"],
                         "fits_training_but_disagrees_later": ["DEGREE"]},
               "invalidation": {"selected_still_matches_exact": True},
               "diagnosis": {}}
        out = E.verdict(doc)
        self.assertEqual(out["terminal"], "REPRESENTATION_CHANNEL_INSUFFICIENT")
        self.assertIn("Fitting training is not sufficient", out["terminal_reason"])

    def test_a_sound_coarser_representation_that_saves_nothing_is_prior_dominates(self):
        doc = {"discovery": {"selected": "MOD_997", "fits_training": ["EXACT", "MOD_997"],
                             "charged_construction": 60},
               "later": {"by_representation": {"EXACT": {"extensions": 100, "solved": ["a"]},
                                               "MOD_997": {"extensions": 100, "solved": ["a"]}},
                         "reference_solved": ["a"],
                         "fits_training_but_disagrees_later": []},
               "invalidation": {"selected_still_matches_exact": True},
               "diagnosis": {}, "redundancy": CENSUS}
        out = E.verdict(doc)
        self.assertEqual(out["terminal"], "REPRESENTATION_PRIOR_DOMINATES")
        # CORRECTED, not deleted. This assertion used to pin the phrase "almost no
        # redundancy", which was the terminal's stated mechanism and was false --
        # the state space is 62% redundant. The test passed for as long as the
        # explanation was wrong, which is what makes it worth keeping visible. It
        # now pins the measured mechanism instead.
        self.assertIn("bisimulation", out["terminal_reason"])
        self.assertIn("already merges everything that can be soundly merged",
                      out["terminal_reason"])
        # The phrase survives, but only inside the sentence that retracts it.
        idx = out["terminal_reason"].index("almost no redundancy")
        self.assertIn("corrects an earlier version",
                      out["terminal_reason"][:idx])

    def test_prior_dominates_cannot_be_reported_without_a_redundancy_census(self):
        """The mechanism claim is evidence, so the terminal may not be issued
        without it. The earlier version asserted a mechanism it had not measured."""
        doc = {"discovery": {"selected": "MOD_997", "fits_training": ["EXACT", "MOD_997"],
                             "charged_construction": 60},
               "later": {"by_representation": {"EXACT": {"extensions": 100, "solved": ["a"]},
                                               "MOD_997": {"extensions": 100, "solved": ["a"]}},
                         "reference_solved": ["a"],
                         "fits_training_but_disagrees_later": []},
               "invalidation": {"selected_still_matches_exact": True},
               "diagnosis": {}}
        with self.assertRaises(KeyError):
            E.verdict(doc)

    def test_the_positive_requires_soundness_and_net_saving(self):
        doc = {"discovery": {"selected": "MOD_997", "fits_training": ["EXACT", "MOD_997"],
                             "charged_construction": 5},
               "later": {"by_representation": {"EXACT": {"extensions": 1000, "solved": ["a"]},
                                               "MOD_997": {"extensions": 100, "solved": ["a"]}},
                         "reference_solved": ["a"],
                         "fits_training_but_disagrees_later": []},
               "invalidation": {"selected_still_matches_exact": True},
               "diagnosis": {}}
        out = E.verdict(doc)
        self.assertEqual(out["terminal"], "REPRESENTATION_CHANGE_CAUSALLY_USEFUL")


class Invalidation(unittest.TestCase):
    def test_the_new_operator_invalidation_check_is_actually_run(self):
        """G3.3: 'Invalidate representation when a newly admitted operator
        distinguishes previously equivalent states.'"""
        source = (HERE / "experiment.py").read_text()
        self.assertIn("newly_admitted_operator", source)
        self.assertIn("selected_still_matches_exact", source)
        self.assertIn("G2.MACRO_TOKEN", source)


class Charging(unittest.TestCase):
    def test_discovery_is_charged_and_subtracted_from_the_saving(self):
        source = (HERE / "experiment.py").read_text()
        self.assertIn("charged_construction", source)
        self.assertIn("net_saving_after_construction", source)

    def test_selection_reads_training_only(self):
        source = (HERE / "experiment.py").read_text()
        block = source[source.index("discovery = {"):source.index("# Protected later")]
        self.assertIn("train", block)
        self.assertNotIn("later", block)


class Proposition2(unittest.TestCase):
    """The G3.3 negative is structural, and its earlier explanation was wrong."""

    def test_equality_of_normal_form_is_a_bisimulation(self):
        """Step (1): if two prefixes agree on normal form, so do all extensions.

        This is what makes EXACT merging sound for every task at once, and it is
        checked rather than assumed.
        """
        import itertools
        by_nf = {}
        for depth in (1, 2, 3):
            for word in itertools.product(E.G2.M.PRIMITIVES, repeat=depth):
                by_nf.setdefault(tuple(E.G2.M.normal_form(word)), []).append(word)
        pairs = [v for v in by_nf.values() if len(v) > 1]
        self.assertTrue(pairs, "no colliding pair found, the test would be vacuous")
        for group in pairs:
            p, q = group[0], group[1]
            for token in E.G2.M.PRIMITIVES:
                self.assertEqual(E.G2.M.normal_form(p + (token,)),
                                 E.G2.M.normal_form(q + (token,)))

    def test_every_registered_representation_coarsens_exact(self):
        """Step (2): R = f o nf, so nf(p) == nf(q) forces R(p) == R(q)."""
        census = CENSUS
        for kind in E.REPRESENTATIONS:
            self.assertLessEqual(census["per_representation"][kind]["distinct_states"],
                                 census["distinct_normal_forms"],
                                 f"{kind} distinguishes more than the normal form, "
                                 "which would break Proposition 2 step (2)")

    def test_marginal_merges_cost_targets_and_zero_marginal_merges_cost_none(self):
        """Step (3): extra merging is paid for in lost targets, one way or other."""
        # The provable pair, in both directions, at two budgets. The strong form
        # -- every marginal merge loses a target -- is FALSE and was in the first
        # draft: at budget 3 TRUNCATED_3 merges beyond EXACT and loses nothing,
        # because a discarded subtree can be redundant with a surviving one.
        for budget in (3, 6):
            census = CENSUS if budget == 3 else E.redundancy_census(budget=6)
            for kind, extra in census["marginal_merges_beyond_exact"].items():
                lost = census["per_representation"][kind]["targets_lost_vs_exact"]
                if extra == 0:
                    self.assertEqual(lost, 0, f"{kind} merges no more than EXACT yet "
                                              "loses targets, which is impossible")
                if lost > 0:
                    self.assertGreater(extra, 0, f"{kind} lost targets without "
                                                 "merging more than EXACT, which "
                                                 "would falsify step (1)")

    def test_the_strong_form_of_step_three_is_recorded_as_false(self):
        self.assertIn("This is a bet, not a certain loss", E.PROPOSITION_2)
        self.assertIn("at budget 3\n    TRUNCATED_3 performs marginal merges and "
                      "loses no target at all", E.PROPOSITION_2)
        self.assertEqual(
            CENSUS["per_representation"]["TRUNCATED_3"]["targets_lost_vs_exact"], 0,
            "the counterexample the proposition cites must actually hold")
        self.assertGreater(CENSUS["marginal_merges_beyond_exact"]["TRUNCATED_3"], 0)

    def test_the_state_space_is_richly_redundant_refuting_the_earlier_claim(self):
        census = E.redundancy_census(budget=6)
        self.assertGreater(census["exact_redundancy_fraction"], 0.5)
        self.assertGreater(census["per_representation"]["EXACT"]["largest_class"], 10)
        self.assertIn("very nearly a bijection", census["refutes_earlier_claim"])

    def test_the_selected_representation_is_the_identity_on_the_reachable_set(self):
        """MOD_997 saving zero is a tautology here, and the record should say so."""
        census = E.redundancy_census(budget=6)
        self.assertEqual(census["per_representation"]["MOD_997"],
                         census["per_representation"]["EXACT"])

    def test_the_proposition_states_the_conditions_that_would_break_it(self):
        for phrase in ("BISIMULATION", "COARSENS", "The escape",
                       "A CORRECTION IS RECORDED HERE"):
            self.assertIn(phrase, E.PROPOSITION_2)


if __name__ == "__main__":
    unittest.main(verbosity=2)
