from __future__ import annotations

import importlib.util
import itertools
import json
import sys
import unittest
from fractions import Fraction as F
from math import comb
from pathlib import Path

HERE = Path(__file__).resolve().parent


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


CAL = load("calv2", HERE / "capability_calibration_v2.py")
POP = load("popv2", HERE / "materialize_population_v2.py")
V1 = load("v1census", HERE / "preoutcome_v1_census.py")


def oracle_count(N, K, n, x):
    if x < max(0, n - (N - K)) or x > min(n, K):
        return 0
    return comb(K, x) * comb(N - K, n - x)


def oracle_cdf(N, K, n, x):
    den = comb(N, n)
    return F(sum(oracle_count(N, K, n, j) for j in range(0, x + 1)), den)


def oracle_upper(N, n, x, delta):
    admissible = [K for K in range(N + 1) if oracle_cdf(N, K, n, x) > delta]
    return max(admissible)


class V1ProtocolFailureTests(unittest.TestCase):
    def test_v1_failure_reproduces_without_oracle(self):
        expected = json.loads((HERE / "V1_PREOUTCOME_CENSUS.json").read_text())
        actual = V1.build_census()
        self.assertEqual(actual, expected)
        self.assertFalse(actual["oracle_outcomes_read"])
        for row in actual["targets"].values():
            self.assertEqual(row["determinate"], 10)
            self.assertFalse(row["sample_possible"])


class V2PopulationAndCustodyTests(unittest.TestCase):
    def test_population_reproduces_from_predictor_only_generator(self):
        committed = json.loads((HERE / "AUDIT_POPULATION_V2.json").read_text())
        self.assertEqual(POP.build_manifest(), committed)
        self.assertFalse(committed["oracle_outcomes_included"])
        self.assertFalse(committed["predictor_binary_predictions_included"])

    def test_v2_determinate_pool_counts(self):
        manifest = POP.build_manifest()
        expected = {
            "memory_exact": 4132,
            "planning_exact": 4382,
            "coordination_exact": 4132,
            "verified_tool_exact": 4382,
        }
        self.assertEqual(
            {k: v["determinate_pool_count"] for k, v in manifest["coordinate_populations"].items()},
            expected,
        )
        self.assertTrue(all(v["population_count"] == 128 for v in manifest["coordinate_populations"].values()))

    def test_committed_sample_passes_custody(self):
        self.assertIsNotNone(CAL.validate_custody())

    def test_duplicate_sample_id_rejected(self):
        population, mutants = CAL.custody_mutants_for_tests()
        with self.assertRaises(ValueError):
            CAL.validate_manifests(population, mutants[0], verify_population=False)

    def test_outsider_sample_id_rejected(self):
        population, mutants = CAL.custody_mutants_for_tests()
        with self.assertRaises(ValueError):
            CAL.validate_manifests(population, mutants[1], verify_population=False)

    def test_short_sample_rejected(self):
        population, mutants = CAL.custody_mutants_for_tests()
        with self.assertRaises(ValueError):
            CAL.validate_manifests(population, mutants[2], verify_population=False)

    def test_outcome_contaminated_sample_rejected(self):
        population, mutants = CAL.custody_mutants_for_tests()
        with self.assertRaises(ValueError):
            CAL.validate_manifests(population, mutants[3], verify_population=False)


class HypergeometricTests(unittest.TestCase):
    def test_frozen_numeric_control(self):
        self.assertEqual(CAL.upper_error_count(128, 64, 0, F(1,80)), 6)
        self.assertEqual(F(6,128), F(3,64))
        self.assertLess(F(3,64), F(1,20))

    def test_pmf_sums_to_one_registered_row(self):
        for K in (0, 1, 6, 32, 64, 127, 128):
            total = sum((CAL.hypergeom_pmf(128, K, 64, x) for x in range(65)), F(0))
            self.assertEqual(total, F(1))

    def test_literal_subset_enumeration_matches_hypergeometric_small_worlds(self):
        for N in range(1, 9):
            universe = tuple(range(N))
            for n in range(1, N + 1):
                den = comb(N, n)
                for K in range(N + 1):
                    errors = set(range(K))
                    histogram = {x: 0 for x in range(n + 1)}
                    for subset in itertools.combinations(universe, n):
                        histogram[len(errors.intersection(subset))] += 1
                    self.assertEqual(sum(histogram.values()), den)
                    for x in range(n + 1):
                        self.assertEqual(F(histogram[x], den), CAL.hypergeom_pmf(N, K, n, x))

    def test_exhaustive_N_le_20_upper_oracle_and_coverage(self):
        deltas = (F(1,2), F(1,5), F(1,20), F(1,80))
        cases = 0
        for N in range(1, 21):
            for n in range(1, N + 1):
                den = comb(N, n)
                for delta in deltas:
                    independent_U = [oracle_upper(N, n, x, delta) for x in range(n + 1)]
                    production_U = [CAL.upper_error_count(N, n, x, delta) for x in range(n + 1)]
                    self.assertEqual(production_U, independent_U)
                    for K in range(N + 1):
                        pmf_sum = sum((F(oracle_count(N, K, n, x), den) for x in range(n + 1)), F(0))
                        self.assertEqual(pmf_sum, F(1))
                        under = sum(
                            (F(oracle_count(N, K, n, x), den) for x in range(n + 1) if K > independent_U[x]),
                            F(0),
                        )
                        self.assertLessEqual(under, delta)
                        cases += 1
        self.assertEqual(cases, 4 * sum(N * (N + 1) for N in range(1, 21)))

    def test_invalid_dimensions_fail_closed(self):
        for args in ((0,0,0,0), (5,6,3,1), (5,2,6,1)):
            with self.assertRaises(ValueError):
                CAL.hypergeom_count(*args)

    def test_float_delta_rejected(self):
        with self.assertRaises(ValueError):
            CAL.upper_error_count(128, 64, 0, 0.0125)


class CertificateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cert = CAL.build_sample_certificate()

    def test_principal_sample_result(self):
        self.assertFalse(self.cert["full_population_census_performed"])
        for row in self.cert["coordinates"].values():
            self.assertEqual(row["sample_errors"], 0)
            self.assertEqual(row["upper_error_count"], 6)
            self.assertEqual(row["upper_error_rate"], "3/64")
            self.assertEqual(row["terminal"], "CALIBRATED_AT_REGISTERED_FINITE_POPULATION")

    def test_corrupted_predictor_fails(self):
        for row in self.cert["corrupted_predictor_control"].values():
            self.assertEqual(row["sample_errors"], 64)
            self.assertEqual(row["upper_error_count"], 128)
            self.assertEqual(row["terminal"], "CANNOT_CERTIFY_ERROR_RATE")

    def test_abstentions_leave_denominator(self):
        for row in self.cert["abstention_accounting_control"].values():
            self.assertEqual(row["synthetic_abstentions"], 18)
            self.assertEqual(row["remaining_determinate_denominator"], 110)
            self.assertFalse(row["abstentions_counted_correct"])

    def test_dependence_hostile_uses_union_not_product(self):
        dep = self.cert["dependence_hostile"]
        self.assertEqual(dep["actual_simultaneous_good"], "19/20")
        self.assertEqual(dep["union_bound_good"], "19/20")
        self.assertEqual(dep["independence_product"], "38950081/40960000")
        self.assertFalse(dep["independence_used"])

    def test_simultaneous_budget(self):
        self.assertEqual(self.cert["delta_total"], "1/20")
        self.assertEqual(self.cert["simultaneous_coverage_lower_bound"], "19/20")


if __name__ == "__main__":
    unittest.main(verbosity=2)
