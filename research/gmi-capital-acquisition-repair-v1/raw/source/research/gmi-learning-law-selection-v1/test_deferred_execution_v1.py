"""The execution must reproduce 3/3 against the frozen digest, and its controls
must go red when the registration or a prediction is tampered with."""
import hashlib
import json
import unittest
from pathlib import Path

import execute_deferred_v1 as E
import learning_law_selection_v1 as M

HERE = Path(__file__).resolve().parent
RECEIPT = HERE / "DEFERRED_EXECUTION_RECEIPT_V1.json"
FROZEN_DIGEST = "38493781de864856409a607ff75afea80a3f51ad89d5c8b947a66d77a6f84787"


class TheRegistrationIsTheOneThatMerged(unittest.TestCase):
    def test_digest_matches_the_frozen_value(self):
        self.assertEqual(E.frozen_digest(), FROZEN_DIGEST)

    def test_receipt_records_the_same_digest(self):
        self.assertEqual(json.loads(RECEIPT.read_text())["frozen_digest"],
                         FROZEN_DIGEST)


class TheExecutionReproduces(unittest.TestCase):
    def setUp(self):
        self.out = E.execute()

    def test_all_three_held(self):
        self.assertEqual(self.out["terminal"], "ALL_DEFERRED_PREDICTIONS_HELD")
        self.assertEqual((self.out["held"], self.out["total"]), (3, 3))

    def test_each_prediction_selected_the_registered_law(self):
        expected = {"D-P1": "MIRROR_DESCENT", "D-P2": "BAYES_UPDATE",
                    "D-P3": "ORDINAL_HILL_CLIMB"}
        for row in self.out["predictions"]:
            self.assertEqual(row["terminal"], "SELECTED", row["tag"])
            self.assertEqual(row["observed"], expected[row["tag"]], row["tag"])
            self.assertTrue(row["held"], row["tag"])

    def test_matches_the_receipt(self):
        self.assertEqual(self.out["predictions"],
                         json.loads(RECEIPT.read_text())["predictions"])


class ParsersAreScopedToTheirSections(unittest.TestCase):
    """The defect found during execution: an unscoped pattern read a prediction
    row's law cell as a price clause."""

    def test_ecology_parser_ignores_the_prediction_table(self):
        eco = E.parse_ecologies(E.frozen_text())
        self.assertEqual(set(eco), {"D1_MEMORY_BOUND", "D2_ORACLE_CHEAP",
                                    "D3_ENUMERATION_TAXED"})
        for prices in eco.values():
            for op in prices:
                self.assertIn(op, M.OPERATIONS)

    def test_prediction_parser_finds_exactly_three_rows(self):
        self.assertEqual(len(E.parse_predictions(E.frozen_text())), 3)

    def test_unscoped_matching_would_have_failed(self):
        """Feeding the prediction section to the ecology parser must raise."""
        section = E._section(E.frozen_text(), "Predictions not evaluated here")
        with self.assertRaises(ValueError):
            E.parse_ecologies("## Frozen ecologies\n" + section)


class ControlsGoRed(unittest.TestCase):
    def test_a_changed_prediction_would_not_hold(self):
        text = E.frozen_text().replace("`MIRROR_DESCENT` |", "`BAYES_UPDATE` |", 1)
        preds = E.parse_predictions(text)
        eco = E.parse_ecologies(E.frozen_text())
        p = preds[0]
        prices = M.uniform_prices(); prices.update(eco[p["ecology"]])
        got = M.select(p["capabilities"], prices)
        self.assertNotEqual(got["law"], p["predicted"],
                            "a tampered prediction must fail")

    def test_an_unknown_capability_word_raises(self):
        bad = "## Predictions not evaluated here\n| D-P9 | telepathy | `D1_MEMORY_BOUND` | `BAYES_UPDATE` |\n"
        with self.assertRaises(ValueError):
            E.parse_predictions(bad)

    def test_a_missing_section_raises(self):
        with self.assertRaises(ValueError):
            E._section("no headings here", "Frozen ecologies")


if __name__ == "__main__":
    unittest.main()
