from __future__ import annotations

import unittest

from cross_grammar_four_family_v1 import validate_closure


class CrossGrammarFourFamilyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = validate_closure()

    def test_four_families_two_grammars(self):
        self.assertEqual((self.result["families"], self.result["grammars"]), (4, 2))
        for labels in self.result["positive_labels"].values():
            self.assertEqual(labels["A"], labels["B"])

    def test_every_positive_has_a_classification_flip(self):
        self.assertEqual(self.result["positive_twin_flips"], 8)
        self.assertEqual(self.result["ledger_rows"], 2)

    def test_every_failed_candidate_is_counted(self):
        accounting = self.result["search_accounting"]
        self.assertEqual(accounting["candidate_attempts"], 104240)
        self.assertEqual(accounting["failed_candidates"], 104136)


if __name__ == "__main__":
    unittest.main()
