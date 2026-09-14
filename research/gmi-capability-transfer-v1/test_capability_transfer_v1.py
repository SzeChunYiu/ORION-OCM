import importlib.util
import json
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("capability_transfer_v1", ROOT / "capability_transfer_v1.py")
mod = importlib.util.module_from_spec(SPEC)
if SPEC.loader is None:
    raise RuntimeError("cannot load transfer module")
SPEC.loader.exec_module(mod)


class TransferAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry = json.loads((ROOT / "TRANSFER_AUDIT_V1.json").read_text())
        cls.audit = mod.audit_transfer()

    def test_claim_gate_metadata(self):
        for field in ("scope", "assumptions", "evidence_class", "claim_ceiling", "strongest_parent", "negative_twin", "nearest_counterexample", "falsifier", "status"):
            self.assertTrue(self.registry[field], field)
        self.assertEqual("G3", self.registry["claim_ceiling"])

    def test_exact_registered_result(self):
        expected = self.registry["result"]
        for key in (
            "task_families", "members_per_family", "total_cells", "determinate_cells",
            "correct_determinate_cells", "incorrect_determinate_cells", "abstention_cells",
            "coverage_fraction", "abstention_fraction", "determinate_accuracy_fraction",
            "per_family", "per_target"
        ):
            self.assertEqual(expected[key], self.audit[key], key)

    def test_raw_families_are_scale_distinct_but_margin_equivalent(self):
        margins = {axis: 0 for axis in mod.AXES}
        alpha = mod.build_raw_task("TF_ALPHA", margins)
        beta = mod.build_raw_task("TF_BETA", margins)
        self.assertNotEqual(alpha["requirements"], beta["requirements"])
        self.assertNotEqual(alpha["capacities"], beta["capacities"])
        self.assertEqual(alpha["derived_margins"], beta["derived_margins"])

    def test_family_transfer_profiles_match_exactly(self):
        self.assertEqual(self.audit["per_family"]["TF_ALPHA"], self.audit["per_family"]["TF_BETA"])

    def test_abstention_is_visible_and_not_scored_correct(self):
        self.assertGreater(self.audit["abstention_cells"], 0)
        self.assertEqual(
            self.audit["total_cells"],
            self.audit["correct_determinate_cells"]
            + self.audit["incorrect_determinate_cells"]
            + self.audit["abstention_cells"],
        )
        self.assertLess(self.audit["correct_determinate_cells"], self.audit["total_cells"])

    def test_no_determinate_transfer_error(self):
        self.assertEqual(0, self.audit["incorrect_determinate_cells"])
        self.assertEqual("1", self.audit["determinate_accuracy_fraction"])

    def test_invalid_family_refused(self):
        margins = {axis: 0 for axis in mod.AXES}
        with self.assertRaises(ValueError):
            mod.build_raw_task("UNKNOWN", margins)


if __name__ == "__main__":
    unittest.main()
