"""Admission tests for the #165 syntax-boundary repair.

Predecessor parsers must keep refusing the retained class-packet vectors.
Successor tests fail until the P1-syntax grammar is implemented.
"""
import importlib.util
import sys
import unittest
from pathlib import Path

REVIVAL = Path(__file__).resolve().parent
CONSUMER = REVIVAL.parent / "ordinary-cut-source-evidence-v1" / "consumer-v3"
DONOR = CONSUMER / "donor"
sys.path[:0] = [str(REVIVAL / "successor"), str(CONSUMER), str(DONOR)]

import load_frozen as frozen  # noqa: E402


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


predecessor = _load("predecessor_typed_grammar", DONOR / "typed_grammar.py")


class PredecessorRefusals(unittest.TestCase):
    def setUp(self):
        self.syntax = predecessor.checker(frozen.CLASS_PARAMETERS)

    def test_ssrin_style_is_refused_as_wff_operator(self):
        with self.assertRaises(ValueError) as ctx:
            self.syntax("wff", frozen.SSRIN_STYLE)
        self.assertEqual(str(ctx.exception), "wff operator")

    def test_membership_is_refused_as_wff_type(self):
        with self.assertRaises(ValueError) as ctx:
            self.syntax("wff", frozen.MEMBERSHIP)
        self.assertEqual(str(ctx.exception), "wff type")

    def test_equality_is_refused_as_wff_type(self):
        with self.assertRaises(ValueError) as ctx:
            self.syntax("wff", frozen.EQUALITY)
        self.assertEqual(str(ctx.exception), "wff type")

    def test_tiny_class_subset_and_conjunction_remain_admitted(self):
        self.assertTrue(self.syntax("wff", frozen.PREDECESSOR_SUBSET))
        self.assertTrue(self.syntax("wff", frozen.PREDECESSOR_AND))
        self.assertTrue(self.syntax("class", ["(", "V0", "i^i", "V1", ")"]))

    def test_raw_ssrin_premise_is_the_same_refused_vector(self):
        proposals = frozen.proposals_in_order()
        found = None
        for row in proposals:
            for statement in [row["query"]] + row["premises"]:
                if statement[1:] == frozen.SSRIN_STYLE:
                    found = statement
                    break
            if found:
                break
        self.assertIsNotNone(found, "ssrin-style vector missing from frozen proposals")
        with self.assertRaises(ValueError) as ctx:
            self.syntax("wff", found[1:])
        self.assertEqual(str(ctx.exception), "wff operator")


class SuccessorAdmission(unittest.TestCase):
    def setUp(self):
        self.p1 = frozen.load_p1()
        self.successor = _load("successor_typed_grammar", REVIVAL / "successor" / "typed_grammar.py")
        self.syntax = self.successor.checker(frozen.CLASS_PARAMETERS, self.p1)

    def test_ssrin_style_parses_as_wff(self):
        self.assertTrue(self.syntax("wff", frozen.SSRIN_STYLE))

    def test_membership_and_equality_parse_as_wff(self):
        self.assertTrue(self.syntax("wff", frozen.MEMBERSHIP))
        self.assertTrue(self.syntax("wff", frozen.EQUALITY))

    def test_predecessor_domain_still_parses(self):
        self.assertTrue(self.syntax("wff", frozen.PREDECESSOR_SUBSET))
        self.assertTrue(self.syntax("wff", frozen.PREDECESSOR_AND))

    def test_unsupported_operator_stays_unknown(self):
        with self.assertRaises(ValueError):
            self.syntax("wff", ["V0", "??", "V1"])

    def test_all_frozen_proposal_grounds_are_wffs(self):
        proposals = frozen.proposals_in_order()
        self.assertEqual(len(proposals), 76)
        for row in proposals:
            self.syntax("wff", row["query"][1:])
            for premise in row["premises"]:
                self.syntax("wff", premise[1:])

    def test_ssrin_style_syntax_proof_replays_p1_contracts(self):
        import p1_syntax as S
        import alias_screen as alias
        catalogue = {row["label"]: row for row in self.p1}
        proof = alias.syntax_proof("wff", frozen.SSRIN_STYLE, frozen.CLASS_PARAMETERS, catalogue)
        self.assertEqual(proof[-1], "wi")
        self.assertIn("wss", proof)
        self.assertIn("cin", proof)
        raw = S.proof("wff", frozen.SSRIN_STYLE,
                      {p["id"]: p["type"] for p in frozen.CLASS_PARAMETERS},
                      S.syntax_contracts(self.p1))
        self.assertEqual(raw[-1], "wi")


if __name__ == "__main__":
    unittest.main()
