"""Exact controls for the #602 F1 capability-coordinate registry."""

from pathlib import Path
import copy
import importlib.util
import math
import unittest

path = Path(__file__).with_name("f1_coordinates_v1.py")
spec = importlib.util.spec_from_loader("f1_coordinates_checked", loader=None)
mod = importlib.util.module_from_spec(spec)
mod.__file__ = str(path)
exec(compile(path.read_bytes(), str(path), "exec"), mod.__dict__)


class RegistryControls(unittest.TestCase):
    def load(self):
        return mod.load_coordinates(), mod.load_assay()

    def test_exact_registry_is_valid(self):
        rows, assay = self.load()
        self.assertEqual(mod.validate_coordinates(rows, assay), [])
        self.assertEqual(len(rows), 17)
        self.assertEqual({r["id"] for r in rows}, set(mod.EXPECTED_COORDINATES))

    def test_missing_coordinate_rejected(self):
        rows, assay = self.load()
        rows = copy.deepcopy(rows[:-1])
        self.assertTrue(any("coordinate ID set mismatch" in x for x in mod.validate_coordinates(rows, assay)))

    def test_duplicate_coordinate_rejected(self):
        rows, assay = self.load()
        rows = copy.deepcopy(rows)
        rows[-1]["id"] = rows[0]["id"]
        errors = mod.validate_coordinates(rows, assay)
        self.assertTrue(any("coordinate IDs must be unique" in x for x in errors))

    def test_missing_falsifier_rejected(self):
        rows, assay = self.load()
        rows = copy.deepcopy(rows)
        del rows[0]["falsifier"]
        self.assertTrue(any("missing fields" in x for x in mod.validate_coordinates(rows, assay)))

    def test_empty_assumptions_rejected(self):
        rows, assay = self.load()
        rows = copy.deepcopy(rows)
        rows[0]["assumptions"] = []
        self.assertTrue(any("assumptions must be nonempty" in x for x in mod.validate_coordinates(rows, assay)))

    def test_claim_escalation_rejected(self):
        rows, assay = self.load()
        rows = copy.deepcopy(rows)
        rows[0]["claim_ceiling"] = "G6"
        self.assertTrue(any("claim ceiling exceeds" in x for x in mod.validate_coordinates(rows, assay)))

    def test_common_assay_requires_independent_units(self):
        rows, assay = self.load()
        assay = copy.deepcopy(assay)
        assay["statistics"]["requires_independent_units"] = False
        self.assertTrue(any("independent units" in x for x in mod.validate_coordinates(rows, assay)))

    def test_resource_prices_must_be_frozen(self):
        rows, assay = self.load()
        assay = copy.deepcopy(assay)
        assay["resource_order"]["scalarization_rule"] = "prices chosen after scoring"
        self.assertTrue(any("frozen prices" in x for x in mod.validate_coordinates(rows, assay)))


class ConcentrationControls(unittest.TestCase):
    def test_hoeffding_radius_uses_three_tails(self):
        expected = math.sqrt(2.0 * math.log(60.0) / 200.0)
        self.assertAlmostEqual(mod.hoeffding_radius(200, 0.05), expected, places=14)

    def test_assay_accepts_separation_and_twin_collapse(self):
        self.assertTrue(
            mod.assay_pass([0.8] * 200, [0.0] * 200, tau_parent=0.5, tau_twin=0.25)
        )

    def test_assay_rejects_noncollapsed_twin(self):
        self.assertFalse(
            mod.assay_pass([0.8] * 200, [0.4] * 200, tau_parent=0.5, tau_twin=0.25)
        )

    def test_assay_rejects_out_of_range_differences(self):
        with self.assertRaises(ValueError):
            mod.assay_pass([1.01], [0.0], tau_parent=0.0, tau_twin=1.0)

    def test_run_reports_g1_only(self):
        result = mod.run()
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["coordinates"], 17)
        self.assertEqual(result["claim_ceiling"], "G1")
        self.assertTrue(result["independent_unit_gate"])


if __name__ == "__main__":
    unittest.main()
