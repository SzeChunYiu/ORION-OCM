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
               "diagnosis": {}}
        out = E.verdict(doc)
        self.assertEqual(out["terminal"], "REPRESENTATION_PRIOR_DOMINATES")
        self.assertIn("almost no redundancy", out["terminal_reason"])

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


if __name__ == "__main__":
    unittest.main(verbosity=2)
