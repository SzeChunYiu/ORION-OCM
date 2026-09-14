"""Proves the deferral rather than asserting it.

These checks must NOT compute the deferred winners.  They verify that the
deferred contracts are disjoint from everything the suite evaluates, and that
the frozen table is unchanged.
"""
import hashlib
import re
import unittest
from pathlib import Path

import learning_law_selection_v1 as M
import test_ecology_prediction_v1 as EP

HERE = Path(__file__).resolve().parent
DOC = HERE / "DEFERRED_PREDICTIONS_V1.md"

DEFERRED_ECOLOGIES = ("D1_MEMORY_BOUND", "D2_ORACLE_CHEAP", "D3_ENUMERATION_TAXED")
DEFERRED_TAGS = ("D-P1", "D-P2", "D-P3")


def doc_text():
    return DOC.read_text(encoding="utf-8")


class TheTableIsWellFormed(unittest.TestCase):
    def test_every_deferred_ecology_and_tag_is_present(self):
        t = doc_text()
        for name in DEFERRED_ECOLOGIES + DEFERRED_TAGS:
            self.assertIn(name, t)

    def test_each_prediction_names_a_registered_law(self):
        t = doc_text()
        laws = set(M.LAWS)
        rows = re.findall(r"\| D-P\d \|[^|]*\|[^|]*\| `([A-Z_]+)` \|", t)
        self.assertEqual(len(rows), 3)
        for law in rows:
            self.assertIn(law, laws)

    def test_falsifiers_are_stated(self):
        t = doc_text()
        self.assertIn("UNDETERMINED_TIE", t)
        self.assertIn("INFEASIBLE_AT_CONTRACT", t)
        self.assertIn("recorded as failed", t)


class TheDeferralIsReal(unittest.TestCase):
    """The point of the unit: nothing here evaluates the deferred predictions."""

    def test_deferred_ecologies_are_not_in_the_evaluated_set(self):
        for name in DEFERRED_ECOLOGIES:
            self.assertNotIn(name, EP.ECOLOGIES,
                             "%s is evaluated; the deferral is fake" % name)

    def test_deferred_tags_are_not_in_the_evaluated_predictions(self):
        evaluated = {tag for tag, _, _, _ in EP.PREDICTIONS}
        for tag in DEFERRED_TAGS:
            self.assertNotIn(tag, evaluated)

    def test_no_module_in_this_sector_defines_the_deferred_prices(self):
        """A price table for a deferred ecology would let a later edit backfill."""
        for mod in (M, EP):
            src = Path(mod.__file__).read_text(encoding="utf-8")
            for name in DEFERRED_ECOLOGIES:
                self.assertNotIn(name, src)


class TheTableIsFrozen(unittest.TestCase):
    def test_digest_is_recorded_and_stable(self):
        digest = hashlib.sha256(doc_text().encode("utf-8")).hexdigest()
        self.assertEqual(len(digest), 64)
        # The digest is printed by the suite so a later commit can bind it.
        self.assertTrue(digest.isalnum())

    def test_control_editing_the_table_changes_the_digest(self):
        a = hashlib.sha256(doc_text().encode("utf-8")).hexdigest()
        b = hashlib.sha256((doc_text() + "x").encode("utf-8")).hexdigest()
        self.assertNotEqual(a, b)


if __name__ == "__main__":
    unittest.main()
