#!/usr/bin/env python3
from __future__ import annotations

from fractions import Fraction
import importlib.util
import json
from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "global_vs_reachable_v1", HERE / "global_vs_reachable_v1.py"
)
assert SPEC and SPEC.loader
mod = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = mod
SPEC.loader.exec_module(mod)


class GlobalVsReachableMorphologyV1Tests(unittest.TestCase):
    def receipt(self):
        return mod.build_receipt()

    def test_receipt_green_and_byte_reproducible(self):
        r = self.receipt()
        expected = json.loads((HERE / "RESULT_V1.json").read_text())
        self.assertEqual(r["verdict"], "GREEN")
        self.assertTrue(all(r["checks"].values()))
        self.assertEqual(json.loads(mod.canonical_json(r)), expected)
        self.assertEqual(mod.canonical_json(r), (HERE / "RESULT_V1.json").read_text())

    def test_strict_reachable_gap(self):
        c = mod.scalar_separation_certificate(
            ("g", "r"), ("r",), {"g": 0, "r": 1}
        )
        self.assertEqual(c["global_value"], Fraction(0))
        self.assertEqual(c["reachable_value"], Fraction(1))
        self.assertFalse(c["value_equality"])
        self.assertFalse(c["reachable_global_optimizer_exists"])

    def test_reachable_global_optimizer_gives_equal_value(self):
        c = mod.scalar_separation_certificate(
            ("a", "b", "c"), ("b", "c"), {"a": 0, "b": 0, "c": 2}
        )
        self.assertEqual(c["global_value"], c["reachable_value"])
        self.assertTrue(c["reachable_global_optimizer_exists"])
        self.assertTrue(c["equality_iff_global_optimizer_reachable"])

    def test_equal_value_does_not_force_same_optimizer_identity(self):
        c = mod.scalar_separation_certificate(
            ("a", "b", "c"), ("b", "c"), {"a": 0, "b": 0, "c": 1}
        )
        self.assertEqual(c["global_argmin"], ("a", "b"))
        self.assertEqual(c["reachable_argmin"], ("b",))
        self.assertTrue(c["value_equality"])
        self.assertFalse(c["optimizer_sets_equal"])

    def test_nested_reachability_cannot_worsen_minimum(self):
        c = mod.nested_reachability_certificate(
            ("a", "b", "c"), ("c",), ("b", "c"), {"a": 0, "b": 1, "c": 2}
        )
        self.assertEqual(c["smaller_value"], Fraction(2))
        self.assertEqual(c["larger_value"], Fraction(1))
        self.assertTrue(c["expanded_reachability_cannot_worsen_minimum"])

    def test_scalar_exhaustive_census(self):
        c = mod.scalar_exhaustive_census()
        self.assertEqual(c["world_subset_cases"], 1434)
        self.assertEqual(c["nested_reachability_cases"], 5826)
        self.assertEqual(c["failures"], [])

    def test_pareto_global_reachable_points_remain_reachable_pareto(self):
        c = mod.pareto_restriction_certificate(
            ("a", "b", "c"), ("a", "b"), {"a": (0, 2), "b": (2, 0), "c": (3, 3)}
        )
        self.assertTrue(c["safe_inclusion"])
        self.assertEqual(set(c["reachable_pareto"]), {"a", "b"})

    def test_pareto_reverse_inclusion_is_false_in_hostile(self):
        c = mod.pareto_restriction_certificate(
            ("a", "b", "c"), ("b", "c"), {"a": (0, 0), "b": (1, 1), "c": (0, 2)}
        )
        self.assertEqual(c["global_pareto"], ("a",))
        self.assertEqual(set(c["reachable_pareto"]), {"b", "c"})
        self.assertIn("b", c["reachable_only_pareto"])
        self.assertFalse(c["reverse_inclusion_holds_in_this_instance"])

    def test_pareto_exhaustive_census(self):
        c = mod.pareto_exhaustive_census()
        self.assertEqual(c["world_subset_cases"], 500)
        self.assertGreater(c["strict_inclusion_cases"], 0)
        self.assertEqual(c["failures"], [])

    def test_parent_budget_projection_values(self):
        p = mod.parent_budget_witness()
        self.assertEqual(p["budget_2"]["reachable_value"], Fraction(4))
        self.assertEqual(p["budget_3"]["reachable_value"], Fraction(2))
        self.assertEqual(p["budget_10"]["reachable_value"], Fraction(0))

    def test_parent_full_lifecycle_boundary_is_explicit(self):
        p = mod.parent_budget_witness()
        self.assertEqual(
            p["corrected_parent_full_lifecycle_frontiers"]["budget_3"],
            ("N_good", "P_good"),
        )
        self.assertIn("does not replace", p["boundary"])
        self.assertEqual(
            p["corrected_parent_terminal"],
            "GRAND_GMI_DEVELOPMENTAL_LIFECYCLE_SELECTION_V2_ALL_GREEN",
        )

    def test_empty_universe_rejected(self):
        with self.assertRaisesRegex(ValueError, "nonempty"):
            mod.validate_universe(())

    def test_duplicate_morphology_rejected(self):
        with self.assertRaisesRegex(ValueError, "unique"):
            mod.validate_universe(("a", "a"))

    def test_empty_reachable_rejected(self):
        with self.assertRaisesRegex(ValueError, "nonempty"):
            mod.validate_reachable(("a",), ())

    def test_reachable_outside_universe_rejected(self):
        with self.assertRaisesRegex(ValueError, "subset"):
            mod.validate_reachable(("a",), ("b",))

    def test_duplicate_reachable_rejected(self):
        with self.assertRaisesRegex(ValueError, "unique"):
            mod.validate_reachable(("a", "b"), ("a", "a"))

    def test_missing_scalar_score_rejected(self):
        with self.assertRaisesRegex(ValueError, "exactly every"):
            mod.validate_scores(("a", "b"), {"a": 0})

    def test_extra_scalar_score_rejected(self):
        with self.assertRaisesRegex(ValueError, "exactly every"):
            mod.validate_scores(("a",), {"a": 0, "b": 1})

    def test_float_scalar_rejected(self):
        with self.assertRaisesRegex(ValueError, "floats"):
            mod.validate_scores(("a",), {"a": 0.5})

    def test_bool_scalar_rejected(self):
        with self.assertRaisesRegex(ValueError, "booleans"):
            mod.validate_scores(("a",), {"a": True})

    def test_false_nested_reachability_rejected(self):
        with self.assertRaisesRegex(ValueError, "not nested"):
            mod.nested_reachability_certificate(
                ("a", "b"), ("a",), ("b",), {"a": 0, "b": 1}
            )

    def test_missing_pareto_profile_rejected(self):
        with self.assertRaisesRegex(ValueError, "exactly every"):
            mod.validate_profiles(("a", "b"), {"a": (0, 1)})

    def test_empty_pareto_vector_rejected(self):
        with self.assertRaisesRegex(ValueError, "nonempty"):
            mod.validate_profiles(("a",), {"a": ()})

    def test_pareto_dimension_mismatch_rejected(self):
        with self.assertRaisesRegex(ValueError, "one dimension"):
            mod.validate_profiles(("a", "b"), {"a": (0,), "b": (0, 1)})

    def test_float_pareto_coordinate_rejected(self):
        with self.assertRaisesRegex(ValueError, "floats"):
            mod.validate_profiles(("a",), {"a": (0.5, 1)})

    def test_dominance_requires_same_dimension(self):
        with self.assertRaisesRegex(ValueError, "same nonzero"):
            mod.dominates((0,), (0, 1))

    def test_exact_rational_strings_supported(self):
        scores = mod.validate_scores(("a", "b"), {"a": "1/3", "b": "2/3"})
        self.assertEqual(scores, {"a": Fraction(1, 3), "b": Fraction(2, 3)})

    def test_claim_ceiling_and_forbidden_promotions(self):
        r = self.receipt()
        self.assertEqual(
            r["claim_ceiling"],
            "GMI_FINITE_GLOBAL_VS_REACHABLE_MORPHOLOGY_SELECTION_SEPARATED_AT_REGISTERED_SCOPE",
        )
        self.assertIn(
            "PARETO_REACHABLE_FRONTIER_SUBSET_OF_GLOBAL_FRONTIER",
            r["forbidden_promotions"],
        )
        self.assertIn("COMPLETE_GMI", r["forbidden_promotions"])

    def test_parent_pins_are_exact(self):
        r = self.receipt()
        self.assertEqual(
            r["parent_pins"]["developmental_lifecycle_v2"]["blob"],
            "8b7acb21cc21d41e54b23c91a9fca75af5612208",
        )
        self.assertEqual(
            r["parent_pins"]["developmental_theorem"]["blob"],
            "27ecb316987bca886c1fc882a4f8c9e270bba4dc",
        )

    def test_no_floats_in_receipt(self):
        def walk(x):
            if isinstance(x, float):
                self.fail("float found in exact receipt")
            if isinstance(x, dict):
                for v in x.values():
                    walk(v)
            elif isinstance(x, (list, tuple)):
                for v in x:
                    walk(v)
        walk(self.receipt())


if __name__ == "__main__":
    unittest.main()
