"""Tests for the post-hoc adversarial bound on the frozen R0 receipt."""
from __future__ import annotations

import json
from pathlib import Path
import unittest

import adversarial_bound as A

HERE = Path(__file__).resolve().parent
RECEIPT = json.loads(
    (HERE / "results" / "RESIDUAL_ROUTING_OPPORTUNITY_V1.json").read_text())
ROWS = RECEIPT["raw_records"]
BOUND = A.bound(ROWS)


def row(admissible, passing, total_c, total_v, chosen_c=0, chosen_v=0,
        chosen_known=True):
    return {"A_admissible_count": admissible, "passing_candidate_count": passing,
            "work_split": {"chosen_known": chosen_known,
                           "total": {"composition_work": total_c,
                                     "verification_calls": total_v},
                           "chosen": {"composition_work": chosen_c,
                                      "verification_calls": chosen_v}}}


class Definability(unittest.TestCase):
    def test_routing_needs_something_to_prefer(self):
        self.assertFalse(A.routing_is_definable(row(1, 1, 1, 2)))   # nothing to choose
        self.assertFalse(A.routing_is_definable(row(3, 0, 3, 6)))   # nothing passes
        self.assertFalse(A.routing_is_definable(row(2, 2, 2, 4)))   # all pass
        self.assertTrue(A.routing_is_definable(row(3, 1, 3, 6)))    # mixed

    def test_the_population_contains_no_mixed_query_at_all(self):
        """The load-bearing fact. If this ever becomes non-zero, #71 is live."""
        self.assertEqual(BOUND["queries_where_routing_is_definable"], 0)
        self.assertNotIn("MIXED: some pass, some do not", BOUND["query_shapes"])
        self.assertEqual(sum(BOUND["query_shapes"].values()), len(ROWS))


class AnswerSafety(unittest.TestCase):
    def test_multiple_passing_contributes_nothing_rather_than_zero(self):
        """A contract violation must be excluded, not counted as a zero.

        Counting it as zero would let a query that cannot be reordered at all
        pad the denominator of a negative, which flatters the negative.
        """
        self.assertIsNone(A.adversarial_residual(row(2, 2, 2, 4)))
        self.assertEqual(BOUND["excluded_multiple_passing"],
                         sum(1 for r in ROWS if r["passing_candidate_count"] > 1))
        self.assertEqual(BOUND["answer_safe_queries"] + BOUND["excluded_multiple_passing"],
                         len(ROWS))

    def test_the_worst_ordering_charges_every_non_passing_candidate(self):
        """A synthetic mixed query, to show the bound is not vacuously zero."""
        residual = A.adversarial_residual(row(3, 1, total_c=9, total_v=6,
                                              chosen_c=2, chosen_v=2))
        self.assertEqual(residual, {"composition_work": 7, "verification_calls": 4})


class Correction(unittest.TestCase):
    def test_the_worst_ordering_gives_the_same_zero_as_the_observed_one(self):
        self.assertTrue(BOUND["worst_case_equals_observed"])
        self.assertEqual(BOUND["adversarial_routing_residual"],
                         {"composition_work": 0, "verification_calls": 0})

    def test_every_single_passing_query_had_no_alternative_to_order(self):
        """Why the worst case ties the observed case: there was no order."""
        for r in ROWS:
            if r["passing_candidate_count"] == 1:
                self.assertEqual(r["A_admissible_count"], 1,
                                 "a single-passing query with alternatives would "
                                 "make the observed order load-bearing after all")

    def test_the_analysis_declares_itself_post_hoc(self):
        self.assertEqual(BOUND["analysis_status"], "POST_HOC_ON_FROZEN_RECEIPT")
        self.assertIn("Not a pre-registered prediction", BOUND["authority"])
        self.assertIn("Ecology independence",
                      BOUND["what_this_still_does_not_establish"])

    def test_the_entry_condition_for_71_is_checkable(self):
        for phrase in ("|A^E| > 1", "mixed", "0 of these"):
            self.assertIn(phrase, BOUND["entry_condition_for_71"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
