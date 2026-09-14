"""Exact controls for ARC-7 adaptive row creation. Python 3.8 safe, unittest."""
from fractions import Fraction as F
from pathlib import Path
import importlib.util
import sys
import unittest

path = Path(__file__).with_name("row_creation_witness.py")
spec = importlib.util.spec_from_file_location("arc7_checked", str(path))
arc7 = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = arc7
spec.loader.exec_module(arc7)


class GeometricBudget(unittest.TestCase):
    def test_geometric_telescopes_exact(self):
        alpha = F(1, 4)
        for T in (10, 100, 1000):
            self.assertEqual(arc7.geometric_budget_telescopes(alpha, T),
                             alpha * F(T, T + 1))

    def test_geometric_budget_positive(self):
        alpha = F(1, 4)
        for t in range(1, 101):
            self.assertGreater(arc7.geometric_budget(alpha, t), 0)

    def test_geometric_budget_bounded(self):
        alpha = F(1, 4)
        total = arc7.geometric_budget_telescopes(alpha, 10000)
        self.assertLess(total, alpha)

    def test_uniform_does_not_telescope(self):
        alpha = F(1, 4)
        for T in (10, 50, 100):
            ok, ut, gt = arc7.verify_uniform_budget_fails(alpha, T)
            self.assertTrue(ok)
            self.assertNotEqual(ut, gt)


class PerRowCertificates(unittest.TestCase):
    def test_certificate_valid(self):
        """Every generated certificate passes verification."""
        alpha = F(1, 4)
        for weight in (F(1, 4), F(1, 3), F(1, 2)):
            for n in (1, 2, 5, 10, 50, 100, 500):
                cert = arc7.certificate(alpha, weight, n)
                self.assertIsInstance(cert, arc7.Certificate)
                self.assertTrue(arc7.verify_certificate(cert),
                                "n=%d w=%s" % (n, weight))

    def test_certificate_one_at_zero_visits(self):
        cert = arc7.certificate(F(1, 4), F(1, 3), 0)
        self.assertIsInstance(cert, arc7.Certificate)
        self.assertEqual(cert.radius, F(1))
        self.assertTrue(arc7.verify_certificate(cert))

    def test_certificate_eventually_shrinks(self):
        alpha = F(1, 4)
        weight = F(1, 3)
        cert = arc7.certificate(alpha, weight, 500)
        self.assertLess(cert.radius, F(1, 5))

    def test_certificate_bad_alpha_rejected(self):
        with self.assertRaises(ValueError):
            arc7.certificate(F(0), F(1, 3), 10)

    def test_certificate_bad_weight_rejected(self):
        with self.assertRaises(ValueError):
            arc7.certificate(F(1, 4), F(0), 10)

    def test_certificate_bad_visits_rejected(self):
        with self.assertRaises(ValueError):
            arc7.certificate(F(1, 4), F(1, 3), -1)

    def test_verify_rejects_bad_radius(self):
        alpha, weight, n = F(1, 4), F(1, 3), 100
        cert = arc7.certificate(alpha, weight, n)
        bad = arc7.Certificate(cert.alpha, cert.weight, cert.visits,
                               cert.effective_n, cert.exponent,
                               cert.numerator, F(0))
        self.assertFalse(arc7.verify_certificate(bad))
        bad2 = arc7.Certificate(cert.alpha, cert.weight, cert.visits,
                                cert.effective_n, cert.exponent,
                                cert.numerator, F(1, 2))
        self.assertFalse(arc7.verify_certificate(bad2))

    def test_verify_rejects_non_certificate(self):
        self.assertFalse(arc7.verify_certificate(42))
        self.assertFalse(arc7.verify_certificate({"radius": 1}))


class SimultaneousConfidence(unittest.TestCase):
    def test_deterministic_sampler(self):
        alpha = F(1, 4)
        ev = arc7.simulate_creation_process(
            alpha, initial_rows=3, max_creations=3,
            steps=30, creation_threshold=F(1, 8))
        self.assertTrue(ev['simultaneous_holds'])

    def test_budget_never_exceeded(self):
        alpha = F(1, 4)
        ev = arc7.simulate_creation_process(
            alpha, initial_rows=3, max_creations=10,
            steps=50, creation_threshold=F(1, 4))
        self.assertLessEqual(ev['budget_spent'], alpha)


class UnlimitedHorizon(unittest.TestCase):
    def test_bound_T10(self):
        alpha = F(1, 4)
        self.assertEqual(arc7.geometric_budget_telescopes(alpha, 10),
                         alpha * F(10, 11))

    def test_bound_T100(self):
        alpha = F(1, 4)
        self.assertEqual(arc7.geometric_budget_telescopes(alpha, 100),
                         alpha * F(100, 101))

    def test_bound_T1000(self):
        alpha = F(1, 4)
        self.assertEqual(arc7.geometric_budget_telescopes(alpha, 1000),
                         alpha * F(1000, 1001))


class NegativeControls(unittest.TestCase):
    def test_uniform_fails_to_telescope(self):
        alpha = F(1, 4)
        M = 10
        total = F(0)
        for t in range(1, M + 1):
            total += alpha / (M * (t + 1))
        geometric = alpha * F(M, M + 1)
        self.assertNotEqual(total, geometric)

    def test_bad_step_rejected(self):
        with self.assertRaises(ValueError):
            arc7.geometric_budget(F(1, 4), 0)

    def test_bad_alpha_rejected(self):
        with self.assertRaises(ValueError):
            arc7.geometric_budget(F(0), 1)
        with self.assertRaises(ValueError):
            arc7.geometric_budget(F(1), 1)


class AdaptiveCreatorLogic(unittest.TestCase):
    def test_does_not_create_when_exhausted(self):
        c = arc7.AdaptiveCreator(F(1, 4), initial_rows=2,
                                 creation_threshold=F(1, 4),
                                 max_creations=0)
        self.assertFalse(c.should_create())

    def test_interval_covers_known_mean(self):
        c = arc7.AdaptiveCreator(F(1, 4), initial_rows=2,
                                 creation_threshold=F(1, 4),
                                 max_creations=3)
        c.create_row(1)
        for _ in range(64):
            c.observe(2, F(0))
        lo, hi = c.get_interval(2)
        self.assertLessEqual(lo, c.rows[2]['mean'])
        self.assertGreaterEqual(hi, c.rows[2]['mean'])

    def test_radius_eventually_drops_below_threshold(self):
        alpha = F(1, 4)
        c = arc7.AdaptiveCreator(alpha, initial_rows=2,
                                 creation_threshold=F(1, 4),
                                 max_creations=5)
        for _ in range(500):
            c.observe(0, F(1))
        self.assertLess(c.get_radius(0), F(1, 4))
        self.assertTrue(c.should_create())


if __name__ == "__main__":
    unittest.main()
