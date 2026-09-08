"""Admission inventory tests. Native mmverify is recorded, not rerun here."""
import json
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
import sys
sys.path.insert(0, str(HERE))
import extract as E  # noqa: E402


class ExtractTests(unittest.TestCase):
    def test_unique_negatives_are_22_with_seven_zero_premise(self):
        rows = E.unique_negatives()
        self.assertEqual(len(rows), 22)
        self.assertEqual(sum(1 for r in rows if not r["hypotheses"]), 7)
        self.assertTrue(all(r["proof"] and r["target"][0] == "|-" for r in rows))

    def test_zero_premise_suffix_is_ordinary_p(self):
        lemma = next(r for r in E.unique_negatives() if not r["hypotheses"])
        text = E.emit_suffix(lemma, "cut-lemma-test")
        self.assertIn("cut-lemma-test $p", text)
        self.assertNotIn(" $e ", text)
        self.assertTrue(text.strip().startswith("${"))
        self.assertTrue(text.strip().endswith("$}"))


class RecordTests(unittest.TestCase):
    def test_admit_record_is_complete_and_negative_on_causal_use(self):
        admit = json.loads((HERE / "records" / "admit-01" / "ADMIT.json").read_text())
        summary = json.loads((HERE / "SUMMARY.json").read_text())
        self.assertEqual(admit["n_verified"], 22)
        self.assertEqual(admit["native_calls"], 22)
        self.assertEqual(summary["terminal"], "NATIVE_ORDINARY_LEMMAS_ADMITTED_NO_HELD_OUT_INVOCATION")
        self.assertFalse(summary["causal_method_reuse_supported"])


if __name__ == "__main__":
    unittest.main()
