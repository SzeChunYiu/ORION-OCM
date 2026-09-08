"""Inventory tests. Native mmverify is recorded, not rerun here."""
import json
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
import sys
sys.path.insert(0, str(HERE))
import extract as E  # noqa: E402


class ExtractTests(unittest.TestCase):
    def test_extra_negatives_are_eight_two_step(self):
        inventory, rows = E.extra_lemmas()
        self.assertEqual(inventory["replay01_unique"], 22)
        self.assertEqual(inventory["replay02_unique"], 30)
        self.assertEqual(len(rows), 8)
        self.assertEqual(sum(1 for r in rows if not r["hypotheses"]), 1)
        self.assertTrue(all(r["semantic_applications"] == 2 for r in rows))
        self.assertTrue(all(r["proof"] and r["target"][0] == "|-" for r in rows))
        self.assertEqual([r["source_label"] for r in rows],
                         ["sscon34b"] * 3 + ["rcompleq"] * 5)

    def test_zero_premise_suffix_is_ordinary_p(self):
        _, rows = E.extra_lemmas()
        lemma = next(r for r in rows if not r["hypotheses"])
        text = E.emit_suffix(lemma, "extra-cut-test")
        self.assertIn("extra-cut-test $p", text)
        self.assertNotIn(" $e ", text)
        self.assertTrue(text.strip().startswith("${"))
        self.assertTrue(text.strip().endswith("$}"))


class RecordTests(unittest.TestCase):
    def test_admit_record_is_complete_and_holds_g2_4(self):
        admit = json.loads((HERE / "records" / "admit-01" / "ADMIT.json").read_text())
        summary = json.loads((HERE / "SUMMARY.json").read_text())
        self.assertEqual(admit["n_verified"], 8)
        self.assertEqual(admit["native_calls"], 8)
        self.assertEqual(admit["n_two_step"], 8)
        self.assertEqual(admit["n_deeper_named_alias"], 0)
        self.assertEqual(summary["terminal"], "EXTRA_NEGATIVES_NATIVE_VERIFIED_LIBRARY_ENLARGED")
        self.assertFalse(summary["causal_method_reuse_supported"])
        self.assertEqual(summary["g2_4"], "NOT_YET")


if __name__ == "__main__":
    unittest.main()
