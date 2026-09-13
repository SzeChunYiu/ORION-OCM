"""Source-bound checks for DC-1..DC-5.

Every figure is parsed out of the parent receipt and compared, and a mutation
control proves the check goes red when the parent disagrees.  A substring test
would pass on the wrong record; these assert the parsed values.
"""
import re
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
RECEIPT = REPO / "research" / "m2-traversal-capital-v1" / "m2p1" / "BEHAVIOURAL_RECEIPT.md"
AXIOMS = (REPO / "research" / "machine-intelligence-morphogenesis-v1"
          / "GMI_AXIOMS_AND_THEOREMS_V1.md")
PARENTMAP = (REPO / "research" / "machine-intelligence-morphogenesis-v1"
             / "FACILITATED_VARIATION_OCM_PARENT_MAP_V1.md")
DOC = HERE / "DEVELOPMENTAL_CAPITAL_V1.md"


def read(p):
    if not p.exists():
        raise FileNotFoundError("cited parent missing: %s" % p)
    return p.read_text(encoding="utf-8")


def parse_counts(text):
    """Pull the recorded figures out of the receipt's census block."""
    def grab(pattern):
        m = re.search(pattern, text)
        if not m:
            raise ValueError("receipt figure not found: %s" % pattern)
        return int(m.group(1).replace(",", ""))
    return {
        "targets": grab(r"targets\s*:\s*([\d,]+)"),
        "earlier": grab(r"rank_H earlier than rank_0\s*:\s*([\d,]+)"),
        "later": grab(r"rank_H later\s*:\s*([\d,]+)"),
        "worlds": grab(r"worlds\s*:\s*([\d,]+)"),
    }


class DC2_Clause1IsSupportedAtItsScope(unittest.TestCase):
    def setUp(self):
        self.c = parse_counts(read(RECEIPT))

    def test_recorded_counts_are_the_ones_this_unit_cites(self):
        self.assertEqual(self.c["targets"], 2741)
        self.assertEqual(self.c["earlier"], 2536)
        self.assertEqual(self.c["later"], 202)
        self.assertEqual(self.c["worlds"], 29)

    def test_the_census_is_arithmetically_consistent(self):
        tied = self.c["targets"] - self.c["earlier"] - self.c["later"]
        self.assertEqual(tied, 3, "earlier+later+tied must exhaust the targets")
        self.assertGreaterEqual(tied, 0)

    def test_the_reported_percentage_is_against_the_full_target_count(self):
        pct = 100.0 * self.c["earlier"] / self.c["targets"]
        self.assertAlmostEqual(pct, 92.5, places=1)

    def test_the_no_leakage_guard_is_recorded(self):
        text = read(RECEIPT)
        self.assertIn("LEAKAGE_ALARM", text)
        self.assertIn("baseline_first_index", text)


class DC3_Clause2IsNotEstablished(unittest.TestCase):
    def test_k2_is_recorded_not_established_in_the_axioms(self):
        text = read(AXIOMS)
        m = re.search(r"GMI-T08.*?Current OCM status:\*\*\s*([A-Z_]+)", text, re.S)
        self.assertIsNotNone(m, "K2 status line not found")
        self.assertEqual(m.group(1), "NOT_ESTABLISHED")

    def test_the_seed_count_agrees_across_two_independent_documents(self):
        a = re.search(r"bar met on (\d+)/(\d+) fresh seeds", read(AXIOMS))
        b = re.search(r"bar held on `(\d+)/(\d+)` fresh seeds", read(PARENTMAP))
        self.assertIsNotNone(a); self.assertIsNotNone(b)
        self.assertEqual(a.groups(), b.groups())
        self.assertEqual(a.groups(), ("2", "9"))

    def test_no_document_reports_k2_as_established(self):
        for p in (AXIOMS, PARENTMAP):
            self.assertNotIn("K2 established", read(p))


class DC1_TheClausesAreDistinct(unittest.TestCase):
    def test_k2_is_about_acquiring_new_capital_not_solving_targets(self):
        text = read(AXIOMS)
        self.assertIn("cheaper acquisition of **new K1**", text)

    def test_this_unit_does_not_claim_k2(self):
        doc = read(DOC)
        self.assertIn("NOT_ESTABLISHED", doc)
        self.assertNotIn("K2 is established", doc)


class MutationControlsGoRed(unittest.TestCase):
    """Prove the checks discriminate: feed them wrong parents and require failure."""

    def test_wrong_counts_fail_the_census(self):
        broken = read(RECEIPT).replace("rank_H later                   : 202",
                                       "rank_H later                   : 999")
        c = parse_counts(broken)
        tied = c["targets"] - c["earlier"] - c["later"]
        self.assertNotEqual(tied, 3)

    def test_missing_figure_raises_rather_than_defaults(self):
        with self.assertRaises(ValueError):
            parse_counts("no figures here at all")

    def test_altered_status_is_detected(self):
        broken = read(AXIOMS).replace("NOT_ESTABLISHED", "ESTABLISHED", 1)
        m = re.search(r"GMI-T08.*?Current OCM status:\*\*\s*([A-Z_]+)", broken, re.S)
        if m:
            self.assertNotEqual(m.group(1), "NOT_ESTABLISHED")


if __name__ == "__main__":
    unittest.main()


class K2RetryRegistrationIsHonest(unittest.TestCase):
    """The retry registration must not soften the standing negative."""

    RETRY = HERE / "K2_RETRY_REGISTRATION_V1.md"

    def test_it_declares_itself_unexecuted(self):
        t = read(self.RETRY)
        self.assertIn("REGISTERED_NOT_EXECUTED", t)
        self.assertIn("K2 REMAINS NOT_ESTABLISHED", t)

    def test_it_does_not_claim_k2(self):
        t = read(self.RETRY)
        for forbidden in ("K2 is established", "K2 SUPPORTED at scope",
                          "establishes K2", "K2 now holds"):
            self.assertNotIn(forbidden, t)

    def test_the_standing_verdict_is_unchanged_in_the_parent(self):
        m = re.search(r"GMI-T08.*?Current OCM status:\*\*\s*([A-Z_]+)",
                      read(AXIOMS), re.S)
        self.assertEqual(m.group(1), "NOT_ESTABLISHED")

    def test_parent_subtraction_is_mandatory_not_optional(self):
        t = read(self.RETRY)
        self.assertIn("PARENT_SUFFICIENT", t)
        self.assertIn("required, not optional", t)

    def test_a_second_failure_is_pre_registered_as_structural_evidence(self):
        t = read(self.RETRY)
        self.assertIn("NOT_ESTABLISHED_SECOND_GRAMMAR", t)
        self.assertIn("structural", t)

    def test_every_outcome_terminal_is_distinct(self):
        t = read(self.RETRY)
        terms = re.findall(r"`(K2_SUPPORTED_AT_REGISTERED_SCOPE|PARENT_SUFFICIENT|"
                           r"NOT_ESTABLISHED_SECOND_GRAMMAR|CANNOT_CHECK)`", t)
        self.assertEqual(len(set(terms)), 4, "outcome table must cover four distinct terminals")
