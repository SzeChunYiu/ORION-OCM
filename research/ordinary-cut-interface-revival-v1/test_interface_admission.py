"""Predecessor class-packet refusals stay; successor admits 2-class and 0-ary P1 syntax."""
import importlib.util
import sys
import unittest
from pathlib import Path

REVIVAL = Path(__file__).resolve().parent
CONSUMER = REVIVAL.parent / "ordinary-cut-source-evidence-v1" / "consumer-v3"
DONOR = CONSUMER / "donor"
sys.path[:0] = [str(REVIVAL / "successor")]

import classify as C
import load_frozen as frozen


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


predecessor_ctx = _load("predecessor_typed_context", DONOR / "typed_context.py")
successor_ctx = _load("successor_typed_context", REVIVAL / "successor" / "typed_context.py")
successor_grammar = _load("successor_typed_grammar", REVIVAL / "successor" / "typed_grammar.py")


TWO_CLASS = {
    "dv": [], "active_dv": [], "essential": [],
    "floating": [
        {"label": "cA", "statement": ["class", "A"]},
        {"label": "cB", "statement": ["class", "B"]},
    ],
}


class FrozenCapsule(unittest.TestCase):
    def test_unknown_interface_population_and_exclusive_subtypes(self):
        rows = frozen.unknown_interface_roots()
        self.assertEqual(len(rows), 54)
        p1 = frozen.p1_index(frozen.load_p1())
        classified = [{"subtype": C.classify(p1[row["label"]])} for row in rows]
        self.assertEqual(C.subtype_counts(classified), {
            "extra_DV": 0, "extra_$e": 10, "non_class_floats": 14,
            "missing_3_params": 22, "other": 8,
        })


class PredecessorRefusals(unittest.TestCase):
    def test_two_class_source_is_refused(self):
        with self.assertRaises(ValueError) as ctx:
            predecessor_ctx.from_source(TWO_CLASS)
        self.assertEqual(str(ctx.exception), "three mandatory floats")


class SuccessorAdmission(unittest.TestCase):
    def test_two_class_source_is_admitted(self):
        context = successor_ctx.from_source(TWO_CLASS)
        self.assertEqual([r["id"] for r in context["parameters"]], ["V0", "V1"])
        self.assertEqual({r["type"] for r in context["parameters"]}, {"class"})

    def test_extra_essential_stays_unknown(self):
        source = dict(TWO_CLASS)
        source["essential"] = [{"label": "h1", "statement": ["|-", "A", "=", "B"]}]
        with self.assertRaises(ValueError) as ctx:
            successor_ctx.from_source(source)
        self.assertEqual(str(ctx.exception), "extra essential hypotheses")

    def test_p1_syntax_admits_two_class_and_zero_ary_grounds(self):
        p1 = frozen.load_p1()
        syntax = successor_grammar.checker(successor_ctx.parameters("class", 2), p1)
        self.assertTrue(syntax("class", ["(", "V0", "/_\\", "V1", ")"]))
        self.assertTrue(syntax("class", ["(/)"]))
        self.assertTrue(syntax("wff", ["V0", "=", "V1"]))
        self.assertTrue(syntax("class", ["_V"]))


if __name__ == "__main__":
    unittest.main()
