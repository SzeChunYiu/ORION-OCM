"""Exact controls; these finite tests are not a proof of an infinite theorem."""
from dataclasses import replace
from fractions import Fraction as F
from itertools import product
from pathlib import Path
import importlib.util
import sys
import unittest

path = Path(__file__).with_name("countable_rows_v1.py")
spec = importlib.util.spec_from_file_location("arc6_checked", str(path))
arc = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = arc
spec.loader.exec_module(arc)


class Allocation(unittest.TestCase):
    def test_exact_telescoping_every_prefix(self):
        total = F(0)
        for j in range(1, 201):
            total += arc.row_weight(j)
            self.assertEqual(total, arc.allocated_mass(j))
            self.assertEqual(1 - total, F(1, j + 1))
            self.assertGreater(arc.row_weight(j), 0)

    def test_double_allocation_exact(self):
        alpha = F(1, 20)
        for rows, visits in product(range(1, 8), repeat=2):
            mass = sum((arc.allowance(alpha, j, n)
                        for j in range(1, rows + 1)
                        for n in range(1, visits + 1)), F(0))
            self.assertEqual(mass, alpha * F(rows, rows + 1) * F(visits, visits + 1))
            self.assertLess(mass, alpha)

    def test_positive_weight_has_no_radius_floor(self):
        # A large fixed row gets a small, nonzero allowance but vanishing width.
        j = 10**9
        self.assertLess(arc.certificate(F(1, 20), j, 10**12).radius, F(1, 10**4))

    def test_no_uniform_shrink_across_new_rows(self):
        self.assertEqual(arc.certificate(F(1, 20), 10**100, 100).radius, F(1))

    def test_zero_rows(self):
        self.assertEqual(arc.allocated_mass(0), 0)

    def test_equal_allocations_can_overspend(self):
        self.assertGreater(5 * F(1, 4), 1)
        self.assertGreater(arc.independent_alarm_probability(F(1, 20), 20), F(1, 20))

    def test_overspending_is_not_universal_impossibility(self):
        # Three identical events {1} on a uniform 20-point space still union to 1/20.
        events = [frozenset({1}) for _ in range(100)]
        self.assertEqual(F(len(frozenset().union(*events)), 20), F(1, 20))
        self.assertGreater(sum((F(len(e), 20) for e in events), F(0)), 1)

    def test_bad_allocations_rejected(self):
        for bad in (0, -1, True, 1.0, "1"):
            with self.assertRaises(ValueError):
                arc.row_weight(bad)
        for bad in (F(0), F(1), F(-1), 0.05, True):
            with self.assertRaises(ValueError):
                arc.allowance(bad, 1, 1)


class ExactCertificates(unittest.TestCase):
    def test_generated_certificates_all_pass(self):
        for alpha, j, n in product((F(1, 4), F(1, 20), F(1, 1000)),
                                   (1, 2, 100, 10**8),
                                   (0, 1, 2, 7, 32, 128, 1000, 10**8)):
            self.assertTrue(arc.verify_certificate(arc.certificate(alpha, j, n)))

    def test_dyadic_and_radius_inequalities_exact(self):
        for n in range(1, 401):
            cert = arc.certificate(F(1, 20), 3, n)
            if cert.radius < 1:
                delta = arc.allowance(cert.alpha, cert.row, n)
                self.assertLessEqual(F(2, 2**cert.exponent), delta)
                self.assertGreater(F(2, 2**(cert.exponent - 1)), delta)
                self.assertGreaterEqual(2 * cert.numerator**2, cert.exponent * n)
                self.assertLess(2 * (cert.numerator - 1)**2, cert.exponent * n)

    def test_rounded_down_radius_rejected(self):
        cert = arc.certificate(F(1, 20), 1, 1000)
        k = cert.numerator - 1
        self.assertFalse(arc.verify_certificate(replace(cert, numerator=k, radius=F(k, 1000))))

    def test_missing_tail_factor_rejected(self):
        cert = arc.certificate(F(1, 20), 1, 1000)
        self.assertFalse(arc.verify_certificate(replace(cert, exponent=cert.exponent - 1)))

    def test_mismatched_numerator_rejected(self):
        cert = arc.certificate(F(1, 20), 1, 1000)
        self.assertFalse(arc.verify_certificate(replace(cert, radius=F(0))))

    def test_booleans_and_floats_rejected(self):
        cert = arc.certificate(F(1, 20), 1, 1000)
        for key, value in (("row", True), ("visits", True), ("numerator", True),
                           ("exponent", True), ("radius", 0.5), ("alpha", 0.05)):
            self.assertFalse(arc.verify_certificate(replace(cert, **{key: value})))
        self.assertFalse(arc.verify_certificate({"radius": 1}))

    def test_bad_visits_rejected(self):
        for n in (-1, True, 2.0):
            with self.assertRaises(ValueError):
                arc.certificate(F(1, 20), 1, n)

    def test_ceil_sqrt_exact(self):
        for value in range(300):
            root = arc.ceil_sqrt(value)
            self.assertGreaterEqual(root * root, value)
            if root:
                self.assertLess((root - 1)**2, value)

    def test_no_samples_whole_interval(self):
        self.assertEqual(arc.interval([], F(1, 20), 1), (F(0), F(1)))
        self.assertTrue(arc.verify_certificate(arc.certificate(F(1, 20), 1, 0)))

    def test_exact_sufficient_sum_matches_list(self):
        samples = (F(1, 4), F(1), F(0), F(2, 3)) * 100
        self.assertEqual(arc.interval(samples, F(1, 20), 1),
                         arc.interval_from_sum(sum(samples), F(1, 20), 1, len(samples)))

    def test_support_and_total_refusals(self):
        for bad in ([F(-1)], [F(2)], [0.5], [True]):
            with self.assertRaises(ValueError):
                arc.interval(bad, F(1, 20), 1)
        for total, n in ((F(1), 0), (F(-1), 2), (F(3), 2), (1.0, 2)):
            with self.assertRaises(ValueError):
                arc.interval_from_sum(total, F(1, 20), 1, n)

    def test_interval_clipping(self):
        self.assertEqual(arc.interval_from_sum(F(0), F(1, 20), 1, 1000)[0], 0)
        self.assertEqual(arc.interval_from_sum(F(1000), F(1, 20), 1, 1000)[1], 1)

    def test_copying_one_draw_is_not_fresh_evidence(self):
        # Under one Bernoulli(1/2) draw copied 1000 times, BOTH possible records
        # exclude 1/2. A numerical certificate alone cannot license this sampler.
        for bit in (F(0), F(1)):
            lo, hi = arc.interval_from_sum(1000 * bit, F(1, 20), 1, 1000)
            self.assertFalse(lo <= F(1, 2) <= hi)

    def test_fixed_row_width_shrinks_at_registered_scales(self):
        widths = [arc.certificate(F(1, 20), 17, n).radius for n in (100, 10000, 10**6, 10**8)]
        self.assertTrue(all(a > b for a, b in zip(widths, widths[1:])))
        self.assertLess(widths[-1], F(1, 1000))


class FiniteProbabilityOracle(unittest.TestCase):
    def test_exact_fixed_look_coverage_on_bernoulli_grid(self):
        # Enumerate the binomial sufficient statistic, not sampled Monte Carlo.
        from math import comb
        for p, n in product((F(1, 10), F(1, 2), F(9, 10)), (40, 80, 160)):
            fail = F(0)
            for k in range(n + 1):
                lo, hi = arc.interval_from_sum(F(k), F(1, 4), 1, n)
                if not lo <= p <= hi:
                    fail += comb(n, k) * p**k * (1-p)**(n-k)
            self.assertLessEqual(fail, arc.allowance(F(1, 4), 1, n))

    def test_optional_monitoring_parent_counterexample_exact(self):
        p = F(3, 5)
        bad = F(0)
        for bits in product((0, 1), repeat=3):
            mass = p**sum(bits) * (1-p)**(3-sum(bits))
            if bits[:2] == (0, 0) or bits == (1, 1, 1):
                bad += mass
        self.assertEqual(bad, F(47, 125))
        self.assertGreater(bad, F(1, 4))


if __name__ == "__main__":
    unittest.main()
