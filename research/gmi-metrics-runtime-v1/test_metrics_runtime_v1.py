"""Controls for GMI Metrics Runtime V1.

CPython 3.8+ safe.  unittest.  No network.
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from metrics_runtime_v1 import (
    ALL_COORDINATES,
    BURDEN_COORDINATES,
    DEFAULT_PRICE_VECTOR,
    DEVELOPMENT_COORDINATES,
    EnergyProxy,
    MemoryTracker,
    ResourceCounter,
    WallClock,
    budget_flip_check,
    reject_negative_budget,
)


class CoordinateRegistrationTests(unittest.TestCase):
    """Test that all 11 coordinates are properly registered."""

    def test_all_coordinates_count(self):
        self.assertEqual(len(ALL_COORDINATES), 11)

    def test_burden_coordinates_count(self):
        self.assertEqual(len(BURDEN_COORDINATES), 7)

    def test_development_coordinates_count(self):
        self.assertEqual(len(DEVELOPMENT_COORDINATES), 4)

    def test_burden_and_development_cover_all(self):
        self.assertEqual(
            set(BURDEN_COORDINATES) | set(DEVELOPMENT_COORDINATES),
            set(ALL_COORDINATES),
        )

    def test_specific_coordinates_present(self):
        required = {
            "build", "storage", "serve", "update", "verify",
            "history", "search", "capability", "plasticity",
            "retention", "information_required",
        }
        self.assertEqual(set(ALL_COORDINATES), required)


class PriceVectorTests(unittest.TestCase):
    """Test price vector is frozen and consistent."""

    def test_default_prices_all_ones(self):
        for coord in ALL_COORDINATES:
            self.assertEqual(DEFAULT_PRICE_VECTOR[coord], 1.0)

    def test_price_vector_frozen_on_copy(self):
        rc = ResourceCounter()
        pv = rc.price_vector
        pv["build"] = 999.0
        self.assertEqual(rc.price_vector["build"], 1.0)

    def test_custom_price_vector(self):
        prices = {c: 2.0 for c in ALL_COORDINATES}
        prices["build"] = 5.0
        rc = ResourceCounter(price_vector=prices)
        self.assertEqual(rc.price_vector["build"], 5.0)

    def test_missing_coordinate_raises(self):
        bad_prices = {c: 1.0 for c in ALL_COORDINATES if c != "build"}
        with self.assertRaises(ValueError):
            ResourceCounter(price_vector=bad_prices)


class ResourceCounterTests(unittest.TestCase):
    """Test coordinate independence and counting."""

    def test_increment_and_get(self):
        rc = ResourceCounter()
        rc.increment("build", 3)
        self.assertEqual(rc.get("build"), 3)

    def test_increment_unknown_raises(self):
        rc = ResourceCounter()
        with self.assertRaises(ValueError):
            rc.increment("nonexistent")

    def test_decrement_raises(self):
        rc = ResourceCounter()
        with self.assertRaises(ValueError):
            rc.increment("build", -1)

    def test_vector_returns_all_zeros(self):
        rc = ResourceCounter()
        v = rc.vector()
        self.assertEqual(len(v), 11)
        self.assertTrue(all(v[c] == 0 for c in ALL_COORDINATES))

    def test_independence_build_vs_storage(self):
        rc = ResourceCounter()
        self.assertTrue(rc.are_independent("build", "storage"))

    def test_independence_serve_vs_verify(self):
        rc = ResourceCounter()
        rc.increment("serve", 5)
        self.assertTrue(rc.are_independent("serve", "verify"))

    def test_independence_all_pairs(self):
        rc = ResourceCounter()
        for a in ALL_COORDINATES:
            for b in ALL_COORDINATES:
                if a != b:
                    self.assertTrue(
                        rc.are_independent(a, b),
                        f"Coordinates {a} and {b} are not independent",
                    )

    def test_scalarization_zero(self):
        rc = ResourceCounter()
        self.assertEqual(rc.scalarized_cost(), 0.0)

    def test_scalarization_known_prices(self):
        prices = {c: 1.0 for c in ALL_COORDINATES}
        prices["build"] = 3.0
        prices["serve"] = 2.0
        rc = ResourceCounter(price_vector=prices)
        rc.increment("build", 4)  # 3.0 * 4 = 12.0
        rc.increment("serve", 5)  # 2.0 * 5 = 10.0
        self.assertAlmostEqual(rc.scalarized_cost(), 22.0)


class WallClockTests(unittest.TestCase):
    """Test monotonic and non-negative elapsed time."""

    def test_elapsed_non_negative(self):
        clock = WallClock()
        clock.start()
        clock.stop()
        self.assertGreaterEqual(clock.elapsed_ns(), 0)

    def test_not_started_raises(self):
        clock = WallClock()
        with self.assertRaises(RuntimeError):
            clock.elapsed_ns()

    def test_stop_without_start_raises(self):
        clock = WallClock()
        with self.assertRaises(RuntimeError):
            clock.stop()

    def test_running_clock_positive(self):
        clock = WallClock()
        clock.start()
        elapsed = clock.elapsed_ns()
        self.assertGreaterEqual(elapsed, 0)

    def test_reset_clears_state(self):
        clock = WallClock()
        clock.start()
        clock.stop()
        clock.reset()
        with self.assertRaises(RuntimeError):
            clock.elapsed_ns()


class MemoryTrackerTests(unittest.TestCase):
    """Test peak allocation tracking."""

    def test_initial_peak_zero(self):
        mt = MemoryTracker()
        self.assertEqual(mt.peak, 0)

    def test_allocate_updates_peak(self):
        mt = MemoryTracker()
        mt.allocate(100)
        self.assertEqual(mt.current, 100)
        self.assertEqual(mt.peak, 100)

    def test_deallocate_reduces_current_not_peak(self):
        mt = MemoryTracker()
        mt.allocate(200)
        mt.deallocate(50)
        self.assertEqual(mt.current, 150)
        self.assertEqual(mt.peak, 200)

    def test_peak_non_decreasing(self):
        mt = MemoryTracker()
        mt.allocate(100)
        mt.deallocate(80)
        mt.allocate(50)
        self.assertEqual(mt.peak, 100)
        self.assertEqual(mt.current, 70)

    def test_negative_allocate_raises(self):
        mt = MemoryTracker()
        with self.assertRaises(ValueError):
            mt.allocate(-10)

    def test_over_deallocate_raises(self):
        mt = MemoryTracker()
        mt.allocate(10)
        with self.assertRaises(ValueError):
            mt.deallocate(20)


class EnergyProxyTests(unittest.TestCase):
    """Test linear compute x time energy model."""

    def test_zero_compute_zero_energy(self):
        ep = EnergyProxy()
        self.assertEqual(ep.compute(0, 1000), 0.0)

    def test_zero_time_zero_energy(self):
        ep = EnergyProxy()
        self.assertEqual(ep.compute(1000, 0), 0.0)

    def test_linear_proportionality(self):
        ep = EnergyProxy()
        e1 = ep.compute(10, 100)
        e2 = ep.compute(10, 200)
        self.assertAlmostEqual(e2, 2.0 * e1)

    def test_intensity_scaling(self):
        ep1 = EnergyProxy(intensity=1.0)
        ep2 = EnergyProxy(intensity=2.5)
        e1 = ep1.compute(10, 100)
        e2 = ep2.compute(10, 100)
        self.assertAlmostEqual(e2, 2.5 * e1)

    def test_additive(self):
        ep = EnergyProxy()
        e1 = ep.compute(5, 100)
        e2 = ep.compute(3, 200)
        self.assertAlmostEqual(ep.add(e1, e2), e1 + e2)

    def test_negative_intensity_raises(self):
        with self.assertRaises(ValueError):
            EnergyProxy(intensity=-1.0)


class BudgetFlipTests(unittest.TestCase):
    """Test budget-flip detection."""

    def test_no_flip_same_prices(self):
        x = {c: 5 for c in ALL_COORDINATES}
        y = {c: 10 for c in ALL_COORDINATES}
        prices = dict(DEFAULT_PRICE_VECTOR)
        self.assertFalse(budget_flip_check(x, y, prices, prices))

    def test_flip_detected(self):
        x = {"build": 10}
        y = {"build": 1}
        for c in ALL_COORDINATES:
            if c != "build":
                x[c] = 1
                y[c] = 10
        # Under uniform prices, y is more expensive (higher on 10 coords)
        # Under build-heavy prices, x is more expensive
        prices_b1 = {c: 1.0 for c in ALL_COORDINATES}
        prices_b2 = {c: 0.1 for c in ALL_COORDINATES}
        prices_b2["build"] = 10.0
        self.assertTrue(budget_flip_check(x, y, prices_b1, prices_b2))


class NegativeBudgetTests(unittest.TestCase):
    """Test negative budget rejection."""

    def test_positive_accepted(self):
        ok, reason = reject_negative_budget(100.0, 1000)
        self.assertTrue(ok)
        self.assertIsNone(reason)

    def test_zero_accepted(self):
        ok, reason = reject_negative_budget(0.0, 0)
        self.assertTrue(ok)

    def test_negative_energy_rejected(self):
        ok, reason = reject_negative_budget(-1.0, 100)
        self.assertFalse(ok)
        self.assertIn("energy", reason)

    def test_negative_memory_rejected(self):
        ok, reason = reject_negative_budget(100.0, -1)
        self.assertFalse(ok)
        self.assertIn("memory", reason)


if __name__ == "__main__":
    unittest.main()
