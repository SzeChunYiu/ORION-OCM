"""Structural controls for TM-1--8.

The map is a synthesis ledger, so these checks enforce its *discipline* rather
than proving any parent theorem: every row must state what is inherited, what is
restricted and what is not claimed; thin rows must be declared thin; and no row
may assert novelty.
"""

from pathlib import Path
import re
import unittest

MAP = Path(__file__).resolve().parent / "THEORY_MAP_V1.md"
TEXT = MAP.read_text(encoding="utf-8")
ROW = re.compile(r"^## (TM-\d+)\. (.+)$", re.M)


def rows():
    marks = [(m.group(1), m.group(2), m.start()) for m in ROW.finditer(TEXT)]
    out = {}
    for i, (rid, title, start) in enumerate(marks):
        end = marks[i + 1][2] if i + 1 < len(marks) else len(TEXT)
        out[rid] = (title, TEXT[start:end])
    return out


class TheoryMapDiscipline(unittest.TestCase):
    def test_eight_rows_with_unique_ids(self) -> None:
        r = rows()
        self.assertEqual(len(r), 8)
        self.assertEqual(sorted(r), ["TM-%d" % i for i in range(1, 9)])

    def test_every_row_states_what_it_inherits(self) -> None:
        for rid, (title, body) in rows().items():
            with self.subTest(row=rid):
                self.assertIn("**Inherited:**", body, rid)

    def test_every_row_restricts_or_declares_itself_thin(self) -> None:
        for rid, (title, body) in rows().items():
            with self.subTest(row=rid):
                self.assertTrue("**Restricted:**" in body or "THIN" in body, rid)

    def test_every_row_states_what_is_not_claimed(self) -> None:
        for rid, (title, body) in rows().items():
            with self.subTest(row=rid):
                self.assertTrue(
                    "**Not claimed:**" in body or "not a claim" in body, rid)

    def test_thin_row_is_declared_and_not_dressed_as_a_result(self) -> None:
        title, body = rows()["TM-4"]
        self.assertIn("THIN", body)
        self.assertIn("declared gap", body.lower())
        # A thin row must not assert a difference it has not earned.
        self.assertNotIn("**Difference:**", body)

    def test_no_row_claims_novelty(self) -> None:
        for rid, (title, body) in rows().items():
            with self.subTest(row=rid):
                lowered = body.lower()
                for phrase in ("we prove for the first time", "novel result",
                               "new theorem", "improves on the parent"):
                    self.assertNotIn(phrase, lowered, rid)

    def test_map_declares_no_novelty_and_carries_a_falsifier(self) -> None:
        self.assertIn("NO NOVELTY CLAIM", TEXT)
        self.assertIn("Falsifier", TEXT)

    def test_representable_and_selected_are_kept_distinct(self) -> None:
        self.assertIn("`REPRESENTABLE` and `SELECTED` are distinct", TEXT)


if __name__ == "__main__":
    unittest.main()
