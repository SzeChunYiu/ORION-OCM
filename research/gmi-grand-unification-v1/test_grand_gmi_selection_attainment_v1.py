import importlib.util
from pathlib import Path
from fractions import Fraction
import unittest


HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location(
    "selection_attainment", HERE / "grand_gmi_selection_attainment_checks_v1.py")
MOD = importlib.util.module_from_spec(spec)
spec.loader.exec_module(MOD)


class SelectionAttainmentTests(unittest.TestCase):
    def test_complete_finite_register_against_independent_scan(self):
        receipt = MOD.check_covering_registers()
        self.assertEqual(receipt["registers"], 3**6 - 2**6)
        self.assertEqual(receipt["registers"],
                         receipt["certified"] + receipt["rejected"])
        self.assertGreater(receipt["certified"], 0)
        self.assertGreater(receipt["rejected"], 0)

    def test_empty_set_does_not_derive_property_or_negation(self):
        self.assertEqual(MOD.selected_property(()), "NO_SELECTED_REALIZATION")
        self.assertEqual(MOD.selected_property(not x for x in ()),
                         "NO_SELECTED_REALIZATION")

    def test_nonempty_true_and_false_properties(self):
        self.assertEqual(MOD.selected_property((True, True)), "DERIVED")
        self.assertEqual(MOD.selected_property((True, False)), "NOT_DERIVED")
        for malformed in ((1,), ("true",), (None,)):
            with self.subTest(malformed=malformed):
                with self.assertRaises(MOD.SelectionInputError):
                    MOD.selected_property(malformed)

    def test_equal_profile_implementation_fibers_are_retained(self):
        rows = {"good": (1, 1), "bad_twin": (1, 1), "dominated": (4, 4)}
        got = MOD.covering_fibers(rows, ("good",), 2)
        self.assertEqual(got, {"good", "bad_twin"})
        self.assertEqual(MOD.selected_property(name == "good" for name in got),
                         "NOT_DERIVED")

    def test_missing_coverage_is_rejected(self):
        rows = {"construction": (2, 2), "hidden_better": (1, 1)}
        with self.assertRaises(MOD.SelectionInputError):
            MOD.covering_fibers(rows, ("construction",), 2)

    def test_undeclared_empty_duplicate_constructions_rejected(self):
        rows = {"x": (1, 1)}
        for ids in ((), ("absent",), ("x", "x")):
            with self.subTest(ids=ids):
                with self.assertRaises(MOD.SelectionInputError):
                    MOD.covering_fibers(rows, ids, 2)

    def test_dimension_and_exact_number_contract(self):
        for profile in ((1,), (1, 1, 1), (True, 1),
                        (float("nan"), 1), (float("inf"), 1), [1, 1]):
            with self.subTest(profile=profile):
                with self.assertRaises(MOD.SelectionInputError):
                    MOD.frontier({"x": profile}, 2)
        for dimension in (0, True, 1.0):
            with self.assertRaises(MOD.SelectionInputError):
                MOD.frontier({}, dimension)
        self.assertEqual(MOD.frontier({"x": (Fraction(1, 3), 2)}, 2), {"x"})

    def test_positive_and_negative_coordinates_obey_declared_order(self):
        rows = {"a": (-3, 2), "b": (-2, 3), "c": (-1, -1)}
        self.assertEqual(MOD.frontier(rows, 2), {"a", "c"})
        self.assertEqual(MOD.scan_reference(rows), {"a", "c"})

    def test_strict_family_separation_and_ties(self):
        self.assertEqual(MOD.gap_certificate(0, Fraction(1, 16), (2,)),
                         {"rivals_excluded": True, "regret_bound": "1/16"})
        self.assertFalse(MOD.gap_certificate(0, 2, (2,))["rivals_excluded"])
        for lower, upper in ((2, 1), (True, 1), (0, float("nan"))):
            with self.assertRaises(MOD.SelectionInputError):
                MOD.gap_certificate(lower, upper, (2,))

    def test_sequence_extension_and_constructive_approximate_revival(self):
        receipt = MOD.check_approximate_revival()
        self.assertEqual(receipt["finite_sequence_extensions"], 64)
        self.assertEqual(receipt["witness_cost"], "1/16")
        self.assertFalse(receipt["exact_optimum_claimed"])

    def test_receipt_replay(self):
        import json
        frozen = json.loads((HERE / "GRAND_GMI_SELECTION_ATTAINMENT_RECEIPT_V1.json").read_text())
        self.assertEqual(MOD.run(), frozen)


if __name__ == "__main__":
    unittest.main()
