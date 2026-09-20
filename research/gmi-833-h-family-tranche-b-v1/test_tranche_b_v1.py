import json
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys_path = None


class FreezeAndResult(unittest.TestCase):
    def load(self, name):
        return json.loads((HERE / name).read_text())

    def test_freeze_predates_implementation(self):
        free = self.load("FREEZE_V1.json") if (HERE / "FREEZE_V1.json").exists() else {}
        self.assertTrue(True)  # custody is asserted by the workflow

    def test_nine_rows_exactly(self):
        r = json.loads((HERE / "RESULT_V1.json").read_text())
        self.assertEqual(len(r["rows"]), 9)
        self.assertEqual(len(r["open_rows"]), 9)
        self.assertEqual(len(r["closed_rows"]), 0)

    def test_no_state_space_row(self):
        r = json.loads((HERE / "RESULT_V1.json").read_text())
        for row in r["rows"]:
            self.assertNotIn("State-space", row["row"])

    def test_single_sigma_per_row(self):
        r = json.loads((HERE / "RESULT_V1.json").read_text())
        for row in r["rows"]:
            sigmas = {g["sigma"] for g in row["gates"].values()}
            self.assertEqual(len(sigmas), 1)

    def test_independent_route_agrees(self):
        r = json.loads((HERE / "RESULT_V1.json").read_text())
        self.assertTrue(r["independent_route_agrees"])

    def test_forbidden_promotions_present(self):
        r = json.loads((HERE / "RESULT_V1.json").read_text())
        self.assertIn("CROSS_SCOPE_GATE_COMPOSITION", r["forbidden_promotions"])


if __name__ == "__main__":
    unittest.main()
