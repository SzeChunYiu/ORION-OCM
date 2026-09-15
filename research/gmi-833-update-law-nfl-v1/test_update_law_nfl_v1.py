#!/usr/bin/env python3
from __future__ import annotations

from fractions import Fraction
import importlib.util
import json
from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("update_law_nfl_v1", HERE / "update_law_nfl_v1.py")
assert SPEC and SPEC.loader
mod = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = mod
SPEC.loader.exec_module(mod)


class FiniteUpdateLawNFLV1Tests(unittest.TestCase):
    def receipt(self):
        return mod.build_receipt()

    def test_receipt_green_and_byte_reproducible(self):
        r = self.receipt()
        expected = json.loads((HERE / "RESULT_V1.json").read_text())
        self.assertEqual(r["verdict"], "GREEN")
        self.assertTrue(all(r["checks"].values()))
        self.assertEqual(json.loads(mod.canonical_json(r)), expected)
        self.assertEqual(mod.canonical_json(r), (HERE / "RESULT_V1.json").read_text())

    def test_binary_deterministic_law_uniform_half(self):
        cert = mod.uniform_nfl_certificate(
            2, 2, {0: 1}, {1: (Fraction(1), Fraction(0))}
        )
        self.assertEqual(cert["terminal"], "UNIFORM_COMPLETION_NFL_EQUALITY")
        self.assertEqual(cert["accuracy"], Fraction(1, 2))
        self.assertEqual(cert["error"], Fraction(1, 2))

    def test_ternary_randomized_law_uniform_third(self):
        cert = mod.uniform_nfl_certificate(
            2, 3, {0: 2}, {1: (Fraction(1, 7), Fraction(2, 7), Fraction(4, 7))}
        )
        self.assertEqual(cert["accuracy"], Fraction(1, 3))
        self.assertEqual(cert["error"], Fraction(2, 3))

    def test_randomized_multiheldout_still_nfl(self):
        cert = mod.uniform_nfl_certificate(
            2,
            3,
            {},
            {
                0: (Fraction(1, 7), Fraction(2, 7), Fraction(4, 7)),
                1: (Fraction(1, 2), Fraction(1, 3), Fraction(1, 6)),
            },
        )
        self.assertEqual(cert["completion_count"], 9)
        self.assertEqual(cert["accuracy"], Fraction(1, 3))

    def test_observed_histories_do_not_break_unconstrained_uniformity(self):
        for observed_label in (0, 1):
            cert = mod.uniform_nfl_certificate(
                3,
                2,
                {0: observed_label},
                {
                    1: (Fraction(3, 5), Fraction(2, 5)),
                    2: (Fraction(1, 4), Fraction(3, 4)),
                },
            )
            self.assertEqual(cert["completion_count"], 4)
            self.assertEqual(cert["accuracy"], Fraction(1, 2))

    def test_deterministic_exhaustive_census(self):
        c = mod.deterministic_exhaustive_census()
        self.assertEqual(c["law_history_cases"], 136)
        self.assertEqual(c["failures"], [])
        configs = set(c["configs"])
        self.assertIn((5, 2, 3, 2), configs)
        self.assertIn((4, 2, 2, 3), configs)

    def test_all_registered_randomized_controls_equal(self):
        r = mod.randomized_controls()
        self.assertEqual(r["cases"], 5)
        self.assertTrue(r["all_equal"])
        self.assertTrue(all(x["equality"] for x in r["controls"]))

    def test_any_distinct_randomized_laws_admit_opposite_ecologies(self):
        r = mod.pairwise_ecology_reversal(
            2,
            3,
            {},
            {
                0: (Fraction(1, 7), Fraction(2, 7), Fraction(4, 7)),
                1: (Fraction(1, 2), Fraction(1, 3), Fraction(1, 6)),
            },
            {
                0: (Fraction(4, 7), Fraction(2, 7), Fraction(1, 7)),
                1: (Fraction(1, 6), Fraction(1, 3), Fraction(1, 2)),
            },
        )
        self.assertEqual(r["terminal"], "PAIRWISE_ECOLOGY_PREFERENCE_REVERSAL")
        self.assertTrue(r["A_preferred_under_PA"])
        self.assertTrue(r["B_preferred_under_PB"])

    def test_identical_laws_do_not_fake_pairwise_reversal(self):
        law = {0: (Fraction(1, 3), Fraction(2, 3))}
        with self.assertRaisesRegex(ValueError, "distinct"):
            mod.pairwise_ecology_reversal(1, 2, {}, law, law)

    def test_nonuniform_ecology_prefers_opposite_laws(self):
        r = mod.preference_reversal()
        self.assertEqual(r["terminal"], "NONUNIFORM_ECOLOGY_PREFERENCE")
        self.assertEqual(r["P0"], {"A0": Fraction(3, 4), "A1": Fraction(1, 4)})
        self.assertEqual(r["P1"], {"A0": Fraction(1, 4), "A1": Fraction(3, 4)})
        self.assertTrue(r["P0_prefers_A0"])
        self.assertTrue(r["P1_prefers_A1"])

    def test_no_heldout_is_not_applicable(self):
        cert = mod.uniform_nfl_certificate(1, 2, {0: 0}, {})
        self.assertEqual(cert["terminal"], "NOT_APPLICABLE_NO_HELDOUT")

    def test_k_less_than_two_rejected(self):
        with self.assertRaisesRegex(ValueError, "k must"):
            mod.validate_problem(2, 1, {0: 0})

    def test_unnormalized_prediction_rejected(self):
        with self.assertRaisesRegex(ValueError, "normalize"):
            mod.validate_law(1, 2, {}, {0: (Fraction(2, 3), Fraction(2, 3))})

    def test_negative_prediction_rejected(self):
        with self.assertRaisesRegex(ValueError, "negative"):
            mod.validate_law(1, 2, {}, {0: (Fraction(-1, 3), Fraction(4, 3))})

    def test_float_prediction_rejected(self):
        with self.assertRaisesRegex(ValueError, "floats"):
            mod.validate_law(1, 2, {}, {0: (0.5, 0.5)})

    def test_false_uniform_declaration_rejected(self):
        cs = mod.enumerate_completions(1, 2, {})
        with self.assertRaisesRegex(ValueError, "declared UNIFORM"):
            mod.validate_ecology(
                cs,
                {cs[0]: Fraction(3, 4), cs[1]: Fraction(1, 4)},
                declared_uniform=True,
            )

    def test_incomplete_completion_support_declared_uniform_rejected(self):
        cs = mod.enumerate_completions(1, 2, {})
        with self.assertRaisesRegex(ValueError, "support"):
            mod.validate_ecology(cs, {cs[0]: Fraction(1)}, declared_uniform=True)

    def test_inconsistent_observed_history_target_rejected(self):
        cs = mod.enumerate_completions(2, 2, {0: 1})
        bad_target = (0, 0)
        weights = {f: Fraction(1, len(cs)) for f in cs}
        weights.pop(cs[0])
        weights[bad_target] = Fraction(1, len(cs))
        with self.assertRaisesRegex(ValueError, "support"):
            mod.validate_ecology(cs, weights, declared_uniform=False)

    def test_unnormalized_ecology_rejected(self):
        cs = mod.enumerate_completions(1, 2, {})
        with self.assertRaisesRegex(ValueError, "normalize"):
            mod.validate_ecology(
                cs, {cs[0]: Fraction(1, 3), cs[1]: Fraction(1, 3)}
            )

    def test_negative_ecology_weight_rejected(self):
        cs = mod.enumerate_completions(1, 2, {})
        with self.assertRaisesRegex(ValueError, "negative"):
            mod.validate_ecology(
                cs, {cs[0]: Fraction(-1, 4), cs[1]: Fraction(5, 4)}
            )

    def test_float_ecology_weight_rejected(self):
        cs = mod.enumerate_completions(1, 2, {})
        with self.assertRaisesRegex(ValueError, "floats"):
            mod.validate_ecology(cs, {cs[0]: 0.5, cs[1]: 0.5})

    def test_uniform_ecology_support_size_exact(self):
        cs = mod.enumerate_completions(4, 3, {0: 1, 1: 2})
        weights = mod.uniform_ecology(cs)
        self.assertEqual(len(cs), 9)
        self.assertEqual(set(weights), set(cs))
        self.assertEqual(set(weights.values()), {Fraction(1, 9)})

    def test_deterministic_law_constructor_is_exact(self):
        law = mod.deterministic_law((1, 3), 3, (2, 0))
        self.assertEqual(law[1], (Fraction(0), Fraction(0), Fraction(1)))
        self.assertEqual(law[3], (Fraction(1), Fraction(0), Fraction(0)))

    def test_claim_ceiling_is_bounded(self):
        r = self.receipt()
        self.assertEqual(
            r["claim_ceiling"],
            "GMI_FINITE_UPDATE_LAW_NO_FREE_LUNCH_BOUNDARY_AT_UNIFORM_COMPLETION_SCOPE",
        )
        self.assertIn("ALL_ALGORITHMS_EQUAL_IN_REAL_WORLD", r["forbidden_promotions"])
        self.assertIn("COMPLETE_GMI", r["forbidden_promotions"])

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
