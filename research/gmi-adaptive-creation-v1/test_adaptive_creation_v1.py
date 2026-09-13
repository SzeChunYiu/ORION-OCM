"""11 exact controls for ARC-5. Sibling source compiled explicitly; -I safe."""

from fractions import Fraction as F
from pathlib import Path
import importlib.util
import unittest

path = Path(__file__).with_name("adaptive_creation_v1.py")
spec = importlib.util.spec_from_loader("adaptive_creation_checked", loader=None)
arc = importlib.util.module_from_spec(spec)
exec(compile(path.read_bytes(), str(path), "exec"), arc.__dict__)

ALPHA = F(1, 4)


class BoundedCreation(unittest.TestCase):
    def test_register_requires_summable_weights(self):
        with self.assertRaises(ValueError):
            arc.PotentialRegister((F(3, 4), F(1, 2)), 1)

    def test_creation_spends_budget(self):
        reg = arc.PotentialRegister((F(1, 2), F(1, 4), F(1, 8)), 1)
        self.assertEqual(reg.create(1), F(1, 4))
        self.assertEqual(reg.spent, 1)
        with self.assertRaisesRegex(ValueError, "budget exhausted"):
            reg.create(2)

    def test_unbudgeted_creation_refused(self):
        reg = arc.PotentialRegister((F(1, 2), F(1, 4)), 0)
        with self.assertRaisesRegex(ValueError, "budget exhausted"):
            arc.PotentialRegister((F(1, 2), F(1, 4)), 0).create(1)
        with self.assertRaisesRegex(ValueError, "already live"):
            reg.create(0)
        with self.assertRaisesRegex(ValueError, "out of potential register"):
            reg.create(5)

    def test_every_live_row_holds_own_certificate(self):
        reg = arc.PotentialRegister((F(1, 2), F(1, 4)), 1)
        reg.create(1)
        for w in reg.live_weights():
            for n in (1, 2, 4, 8, 12):
                r = arc.grid_radius(n, ALPHA, w)
                target = ALPHA * w / (n * (n + 1))
                self.assertLessEqual(arc.tail_upper_2(n, r), target)
                if r > 0:
                    self.assertGreater(arc.tail_upper_2(n, r - F(1, n)), target)

    def test_creation_keeps_total_weight_bounded(self):
        reg = arc.PotentialRegister((F(1, 2), F(1, 4), F(1, 8)), 2)
        reg.create(1)
        reg.create(2)
        self.assertLessEqual(sum(reg.live_weights()), F(1))


class UnlimitedHorizons(unittest.TestCase):
    def test_certificates_hold_to_512(self):
        for n in (64, 128, 256, 512):
            r = arc.grid_radius(n, ALPHA, F(1, 2))
            self.assertLessEqual(arc.tail_upper_2(n, r),
                                 ALPHA * F(1, 2) / (n * (n + 1)))

    def test_radii_tighten_monotonically(self):
        radii = [arc.grid_radius(n, ALPHA, F(1, 2)) for n in (8, 32, 128, 512)]
        for lo, hi in zip(radii, radii[1:]):
            self.assertGreaterEqual(lo, hi)

    def test_unbounded_creation_breaks_fixed_budget(self):
        w = F(1, 4)
        self.assertEqual(arc.hostile_budget_spend(w, 5), F(5, 4))
        self.assertGreater(arc.hostile_budget_spend(w, 5), F(1))

    def test_summable_budget_stays_bounded(self):
        partial = sum(arc.summable_weights(20))
        self.assertLess(partial, F(1))
        self.assertGreater(partial, F(0))

    def test_summable_tail_is_auditable(self):
        weights = arc.summable_weights(6)
        self.assertEqual(weights[0], F(1, 4))
        self.assertEqual(weights[-1], F(1, 128))
        self.assertLess(sum(weights), F(1))

    def test_interfaces_refuse_bad_inputs(self):
        with self.assertRaises(ValueError):
            arc.tail_upper_2(0, F(1, 2))
        with self.assertRaises(ValueError):
            arc.grid_radius(-1, ALPHA, F(1, 2))
        with self.assertRaises(ValueError):
            arc.hostile_budget_spend(F(0), 3)
        with self.assertRaises(ValueError):
            arc.summable_weights(0)


if __name__ == "__main__":
    unittest.main()
