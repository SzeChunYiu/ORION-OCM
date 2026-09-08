"""Bank must include lemma conclusions so 0-premise cuts can instantiate."""
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE))

import search_arms as S  # noqa: E402


LEMMA = {
    "label": "ocm-cut-11",
    "statement": [
        "|-", "(", "(", "B", "i^i", "A", ")", "\\", "C", ")", "=",
        "(", "(", "A", "i^i", "B", ")", "\\", "C", ")",
    ],
    "floating": [
        {"label": "cA", "statement": ["class", "A"]},
        {"label": "cB", "statement": ["class", "B"]},
        {"label": "cC", "statement": ["class", "C"]},
    ],
    "essential": [],
    "dv": [],
    "semantic_labels": ["incom", "difeq1i"],
}

GOAL = ["|-", "(", "(", "A", "i^i", "B", ")", "C_", "C", "<->",
        "(", "A", "i^i", "(", "B", "\\", "C", ")", ")", "=", "(/)", ")"]


class LemmaContracts(unittest.TestCase):
    def test_zero_premise_is_p1_shaped(self):
        row = S.lemma_contracts([LEMMA])[0]
        self.assertEqual(row["label"], "cut-lemma-11")
        self.assertEqual(row["essential"], [])
        self.assertEqual(len(row["floating"]), 3)
        self.assertTrue(row["zero_premise"])


class BankInclusion(unittest.TestCase):
    def test_lemma_conclusion_is_in_published_bank(self):
        contracts = S.lemma_contracts([LEMMA])
        bank = S.bank_from(GOAL, contracts)
        self.assertEqual(bank["kind"], "syntax_closure_plus_lemma_conclusions")
        keys = {tuple(r["tokens"]) for r in bank["wff"]}
        self.assertIn(tuple(LEMMA["statement"][1:]), keys)

    def test_lemma_instantiates_when_conclusion_is_in_bank(self):
        S.extend_class_syntax()
        contracts = S.lemma_contracts([LEMMA])
        bank = S.bank_from(GOAL, contracts)
        work = {}
        actions = S.FS.compile_parent(S.ordinary_parent_rows(contracts), bank, work, limit=5000)
        lemma_actions = [a for a in actions if a["label"] == "cut-lemma-11"]
        self.assertGreater(len(lemma_actions), 0, work)
        self.assertGreater(work.get("primitive_instances", 0), 0)

    def test_patches_native_match_typed_terms_not_only_finite_search(self):
        name = S.extend_class_syntax()
        self.assertEqual(name, "native_match_class_difference_and_empty")
        self.assertEqual(S.FS.M.T.syntax, S.FS.T.syntax)
        proof = S.FS.M.T.syntax("class", ["(", "A", "\\", "B", ")"])
        self.assertIn("cdif", proof)


class Mooney(unittest.TestCase):
    def test_two_lemma_uses_fail_limited_chaining(self):
        self.assertFalse(S.mooney_once(["cut-lemma-11", "syl", "cut-lemma-18"])["ok"])
        self.assertTrue(S.mooney_once(["cut-lemma-11", "syl"])["ok"])


if __name__ == "__main__":
    unittest.main()
