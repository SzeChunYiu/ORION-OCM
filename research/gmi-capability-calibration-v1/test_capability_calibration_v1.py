from __future__ import annotations

from copy import deepcopy
from fractions import Fraction
import importlib.util
import unittest

spec = importlib.util.spec_from_file_location("capcal", __file__.replace("test_capability_calibration_v1.py", "capability_calibration_v1.py"))
capcal = importlib.util.module_from_spec(spec)
spec.loader.exec_module(capcal)


class ExactMathTests(unittest.TestCase):
    def test_frozen_zero_error_boundary(self):
        self.assertEqual(capcal.upper_error_count(128, 64, 0, Fraction(1,80)), 6)
        self.assertGreater(capcal.hypergeom_cdf(128, 6, 64, 0), Fraction(1,80))
        self.assertLessEqual(capcal.hypergeom_cdf(128, 7, 64, 0), Fraction(1,80))

    def test_one_error_does_not_pass_epsilon(self):
        self.assertEqual(capcal.upper_error_count(128, 64, 1, Fraction(1,80)), 9)
        self.assertGreater(Fraction(9,128), capcal.EPSILON)

    def test_pmf_is_exact_distribution(self):
        for N in range(1, 9):
            for n in range(1, N+1):
                for K in range(N+1):
                    self.assertEqual(sum((capcal.hypergeom_pmf(N,K,n,x) for x in range(n+1)), Fraction(0)), 1)

    def test_cdf_decreases_with_more_errors(self):
        for x in range(5):
            values = [capcal.hypergeom_cdf(8,K,4,x) for K in range(9)]
            self.assertTrue(all(b <= a for a,b in zip(values, values[1:])))

    def test_small_exhaustive_certificate(self):
        result = capcal.exhaustive_certificate(8)
        self.assertTrue(result["all_green"])
        for key, value in result.items():
            if key.endswith("_failures"):
                self.assertEqual(value, 0)


class SamplingTests(unittest.TestCase):
    def test_combination_unranking_complete_small(self):
        from itertools import combinations
        items = tuple("abcde")
        expected = list(combinations(items, 3))
        for rank, combo in enumerate(expected):
            self.assertEqual(capcal.unrank_combination(items, 3, rank), combo)

    def test_dependence_hostile_blocks_product_shortcut(self):
        hostile = capcal.dependence_hostile()
        self.assertTrue(hostile["product_is_unsound"])
        self.assertEqual(hostile["true_simultaneous_success_disjoint_failures"], "1/2")
        self.assertEqual(hostile["unjustified_independence_product"], "9/16")
        self.assertEqual(hostile["union_bound_lower"], "1/2")
        self.assertTrue(hostile["union_bound_can_be_conservative"])


class FrozenRepositoryTests(unittest.TestCase):
    def test_population_reconstructs_and_is_fresh(self):
        manifest = capcal._load_json(capcal.POPULATION_PATH)
        populations = capcal.reconstruct_population(manifest)
        self.assertEqual(tuple(populations), capcal.TARGETS)
        for rows in populations.values():
            self.assertEqual(len(rows), 128)
            self.assertEqual(len({cid for cid,_ in rows}), 128)
            for _, point in rows:
                self.assertFalse(all(point[a] in (-1,0,1) for a in capcal.AXES))

    def test_population_scored_field_hostile(self):
        hostile = deepcopy(capcal._load_json(capcal.POPULATION_PATH))
        hostile["truth"] = 1
        with self.assertRaises(ValueError):
            capcal.reconstruct_population(hostile)

    def test_exact_sample_replays_all_coordinates(self):
        populations = capcal.reconstruct_population(capcal._load_json(capcal.POPULATION_PATH))
        samples = capcal.validate_sample(populations, capcal._load_json(capcal.SAMPLE_PATH))
        for target in capcal.TARGETS:
            self.assertEqual(len(samples[target]), 64)
            self.assertEqual(len(set(samples[target])), 64)

    def test_scored_sample_master_fails_closed(self):
        populations = capcal.reconstruct_population(capcal._load_json(capcal.POPULATION_PATH))
        sample = capcal._load_json(capcal.SAMPLE_PATH)
        sample["scored_fields_present"] = True
        with self.assertRaises(ValueError):
            capcal.validate_sample(populations, sample)

    def test_pinned_predictor_scoring_and_corrupted_control(self):
        populations = capcal.reconstruct_population(capcal._load_json(capcal.POPULATION_PATH))
        samples = capcal.validate_sample(populations, capcal._load_json(capcal.SAMPLE_PATH))
        scored = capcal.score_coordinates(populations, samples)
        for target in capcal.TARGETS:
            row = scored[target]
            self.assertEqual(row["sample_abstentions"], 0)
            self.assertEqual(row["sample_errors"], 0)
            self.assertEqual(row["upper_error_count"], 6)
            self.assertEqual(row["upper_error_rate"], "3/64")
            self.assertEqual(row["terminal"], capcal.PASS)
            self.assertEqual(row["corrupted_control"]["sample_errors"], 64)
            self.assertEqual(row["corrupted_control"]["upper_error_count"], 128)
            self.assertEqual(row["corrupted_control"]["terminal"], capcal.FAIL)
            self.assertEqual(row["census"]["fixed_population_errors"], 0)
            self.assertTrue(row["census"]["certificate_covers_fixed_truth"])

    def test_small_receipt_preserves_claim_boundary(self):
        receipt = capcal.build_receipt(max_exact_N=8)
        self.assertEqual(receipt["claim_ceiling"], capcal.CLAIM)
        self.assertEqual(receipt["constants"]["simultaneous_confidence_lower"], "19/20")
        self.assertIn("COMPLETE_GMI", receipt["forbidden_claims"])
        self.assertTrue(receipt["exact_certificate"]["all_green"])


if __name__ == "__main__":
    unittest.main()
