from __future__ import annotations

import json
import math
import sys
import tempfile
import unittest
from fractions import Fraction as F
from pathlib import Path
from unittest import mock

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import capability_calibration_v2 as cc


class CapabilityCalibrationV2Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.frame = cc.load_frame_rows()
        cls.samples = cc.load_samples(cls.frame)

    def test_frame_has_exactly_64_cells(self):
        self.assertEqual(len(self.frame), 64)

    def test_frame_predictions_binary(self):
        self.assertEqual({row["frozen_prediction"] for row in self.frame.values()}, {0, 1})

    def test_frame_builder_reproduces_all_four_coordinate_frames(self):
        builder = cc._load_module(cc.BUILDER_PATH, "frame_builder_test")
        payload = builder.build_frame()
        expected = [
            [sid, *(self.frame[sid][axis] for axis in cc.AXES), self.frame[sid]["frozen_prediction"]]
            for sid in sorted(self.frame)
        ]
        for target in cc.TARGETS:
            self.assertEqual(payload["coordinate_frames"][target]["rows"], expected)

    def test_frozen_samples_48_unique_each(self):
        for target in cc.TARGETS:
            self.assertEqual(len(self.samples[target]), 48)
            self.assertEqual(len(set(self.samples[target])), 48)
            self.assertTrue(set(self.samples[target]).issubset(self.frame))

    def test_samples_are_canonical_sorted_realizations(self):
        for target in cc.TARGETS:
            self.assertEqual(self.samples[target], tuple(sorted(self.samples[target])))

    def test_hypergeom_pmf_sums_to_one(self):
        for N, K, n in ((8, 3, 4), (10, 7, 6), (20, 11, 9)):
            total = sum((cc.hypergeom_pmf(N, K, n, x) for x in range(n + 1)), F(0))
            self.assertEqual(total, F(1))

    def test_hypergeom_matches_simple_case(self):
        self.assertEqual(cc.hypergeom_pmf(4, 2, 2, 0), F(1, 6))
        self.assertEqual(cc.hypergeom_pmf(4, 2, 2, 1), F(2, 3))
        self.assertEqual(cc.hypergeom_pmf(4, 2, 2, 2), F(1, 6))

    def test_cdf_monotone_in_x(self):
        values = [cc.hypergeom_cdf(12, 5, 7, x) for x in range(8)]
        self.assertEqual(values, sorted(values))
        self.assertEqual(values[-1], F(1))

    def test_frozen_zero_error_upper_bound(self):
        self.assertEqual(cc.upper_error_count(64, 48, 0, F(1, 80)), 3)
        self.assertEqual(F(3, 64), F(3, 64))
        self.assertLessEqual(F(3, 64), F(1, 20))

    def test_one_more_population_error_not_admitted_at_x0(self):
        self.assertGreater(cc.hypergeom_cdf(64, 3, 48, 0), F(1, 80))
        self.assertLessEqual(cc.hypergeom_cdf(64, 4, 48, 0), F(1, 80))

    def test_upper_bound_nondecreasing_in_observed_errors(self):
        bounds = [cc.upper_error_count(20, 10, x, F(1, 20)) for x in range(11)]
        self.assertEqual(bounds, sorted(bounds))

    def test_independent_dp_matches_frozen_small_distribution(self):
        counts = cc.independent_subset_error_counts(4, 2, 2)
        self.assertEqual(counts, {0: 1, 1: 4, 2: 1})
        self.assertEqual(sum(counts.values()), math.comb(4, 2))

    def test_exhaustive_small_theorem_check(self):
        result = cc.exhaustive_small_theorem_check(20)
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["pmf_cases"], 10395)
        self.assertEqual(result["coverage_cases"], 12320)
        self.assertEqual(result["deltas"], ["1/2", "1/5", "1/20", "1/80"])

    def test_dependence_hostile(self):
        row = cc.dependence_hostile()
        self.assertEqual(row["marginal_success_each"], "79/80")
        self.assertEqual(row["actual_joint_success"], "19/20")
        self.assertEqual(row["union_bound_lower"], "19/20")
        self.assertEqual(row["independence_product"], "38950081/40960000")
        self.assertTrue(row["actual_equals_union_bound"])
        self.assertTrue(row["independence_product_differs"])
        self.assertFalse(row["independence_used"])

    def test_principal_frozen_sample_is_zero_error(self):
        principal, _ = cc._score_principal(self.frame, self.samples)
        for target in cc.TARGETS:
            self.assertEqual(principal[target]["sample_errors"], 0)
            self.assertEqual(principal[target]["upper_error_count"], 3)
            self.assertEqual(principal[target]["upper_error_rate"], "3/64")
            self.assertEqual(principal[target]["terminal"], "CALIBRATED_AT_REGISTERED_DETERMINATE_FRAME")

    def test_post_certificate_census_is_covered(self):
        principal, _ = cc._score_principal(self.frame, self.samples)
        for target in cc.TARGETS:
            self.assertEqual(principal[target]["true_total_errors_post_certificate_census"], 0)
            self.assertTrue(principal[target]["truth_covered"])

    def test_candidate_grid_coverage_is_reported_not_hidden(self):
        principal, _ = cc._score_principal(self.frame, self.samples)
        for target in cc.TARGETS:
            self.assertEqual(principal[target]["candidate_grid_count"], 1024)
            self.assertEqual(principal[target]["determinate_frame_count"], 64)
            self.assertEqual(principal[target]["candidate_grid_coverage"], "1/16")

    def test_complement_control_fails_all_four_coordinates(self):
        principal, truths = cc._score_principal(self.frame, self.samples)
        self.assertTrue(all(row["terminal"] == "CALIBRATED_AT_REGISTERED_DETERMINATE_FRAME" for row in principal.values()))
        corrupted = cc.complement_control(self.frame, self.samples, truths)
        for target in cc.TARGETS:
            self.assertEqual(corrupted[target]["sample_errors"], 48)
            self.assertEqual(corrupted[target]["upper_error_count"], 64)
            self.assertEqual(corrupted[target]["upper_error_rate"], "1")
            self.assertEqual(corrupted[target]["true_total_errors"], 64)
            self.assertFalse(corrupted[target]["certified"])

    def test_abstention_control_reduces_coverage(self):
        _, truths = cc._score_principal(self.frame, self.samples)
        row = cc.abstention_control(self.frame, truths)
        self.assertEqual(row["frame_count"], 64)
        self.assertEqual(row["abstentions"], 10)
        self.assertEqual(row["determinate"], 54)
        self.assertEqual(row["determinate_coverage"], "27/32")
        self.assertFalse(row["abstentions_counted_as_correct"])

    def _mutated_sample_file(self, mutator):
        payload = json.loads(cc.SAMPLE_PATH.read_text())
        mutator(payload)
        temp = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False)
        try:
            json.dump(payload, temp)
            temp.close()
            return Path(temp.name)
        except Exception:
            temp.close()
            raise

    def test_duplicate_sample_id_rejected(self):
        path = self._mutated_sample_file(lambda p: p["samples"]["memory_exact"].__setitem__(1, p["samples"]["memory_exact"][0]))
        try:
            with mock.patch.object(cc, "SAMPLE_PATH", path):
                with self.assertRaises(ValueError):
                    cc.load_samples(self.frame)
        finally:
            path.unlink(missing_ok=True)

    def test_unknown_sample_id_rejected(self):
        path = self._mutated_sample_file(lambda p: p["samples"]["memory_exact"].__setitem__(0, "AC2_NOT_IN_FRAME"))
        try:
            with mock.patch.object(cc, "SAMPLE_PATH", path):
                with self.assertRaises(ValueError):
                    cc.load_samples(self.frame)
        finally:
            path.unlink(missing_ok=True)

    def test_wrong_sample_size_rejected(self):
        path = self._mutated_sample_file(lambda p: p["samples"]["memory_exact"].pop())
        try:
            with mock.patch.object(cc, "SAMPLE_PATH", path):
                with self.assertRaises(ValueError):
                    cc.load_samples(self.frame)
        finally:
            path.unlink(missing_ok=True)

    def test_outcome_like_sample_field_rejected(self):
        path = self._mutated_sample_file(lambda p: p.__setitem__("correctness", []))
        try:
            with mock.patch.object(cc, "SAMPLE_PATH", path):
                with self.assertRaises(ValueError):
                    cc.load_samples(self.frame)
        finally:
            path.unlink(missing_ok=True)

    def test_receipt_deterministic(self):
        self.assertEqual(cc.build_receipt(), cc.build_receipt())

    def test_receipt_core_claims(self):
        row = cc.build_receipt()
        self.assertTrue(row["all_principal_coordinates_certified"])
        self.assertTrue(row["all_post_certificate_truths_covered"])
        self.assertTrue(row["complement_control_fails_all_coordinates"])
        self.assertEqual(row["simultaneous_coverage_lower_bound"], "19/20")
        self.assertFalse(row["iid_assumption"])
        self.assertFalse(row["replacement_sampling"])
        self.assertFalse(row["oracle_used_for_frame_construction"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
