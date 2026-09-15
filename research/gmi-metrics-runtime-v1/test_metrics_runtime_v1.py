"""
test_metrics_runtime_v1.py — 20+ tests for metrics_runtime_v1.

Python 3.8 safe. No network. Exact arithmetic via fractions.Fraction.
Run: python3 -I -B research/gmi-metrics-runtime-v1/test_metrics_runtime_v1.py -v
"""

from __future__ import annotations

import sys
import os
import unittest
from fractions import Fraction

# Import via importlib for -I safety
import importlib.util

_spec = importlib.util.spec_from_file_location(
    'metrics_runtime_v1',
    os.path.join(os.path.dirname(__file__), 'metrics_runtime_v1.py'),
)
_mod = importlib.util.module_from_spec(_spec)
assert sys.version_info >= (3, 8)
sys.modules['metrics_runtime_v1'] = _mod  # register so dataclass introspection works
_spec.loader.exec_module(_mod)

Coordinates = _mod.Coordinates
CapabilityRuntime = _mod.CapabilityRuntime
BudgetFlipDetector = _mod.BudgetFlipDetector
BudgetFlip = _mod.BudgetFlip
check_subadditivity = _mod.check_subadditivity
combine_coordinates = _mod.combine_coordinates
build_finite_world = _mod.build_finite_world
build_finite_world_coords = _mod.build_finite_world_coords


class TestCoordinates(unittest.TestCase):
    """Tests for the Coordinates dataclass."""

    def test_non_negativity_all_zero(self):
        """All-zero coordinates are valid."""
        c = Coordinates(
            wall_clock=Fraction(0), memory_bytes=Fraction(0),
            energy_joules=Fraction(0), description_length=Fraction(0),
            update_cost=Fraction(0), execution_cost=Fraction(0),
            generalization_gap=Fraction(0), retention_rate=Fraction(0),
            plasticity=Fraction(0), stability=Fraction(0),
            information_required=Fraction(0),
        )
        # G contributes 0; (1-R)+(1-P)+(1-S) = 3
        self.assertEqual(c.aggregate_cost, Fraction(3))

    def test_non_negativity_positive(self):
        """All-positive coordinates are valid."""
        c = Coordinates(
            wall_clock=Fraction(1), memory_bytes=Fraction(2),
            energy_joules=Fraction(3), description_length=Fraction(4),
            update_cost=Fraction(5), execution_cost=Fraction(6),
            generalization_gap=Fraction(7), retention_rate=Fraction(8),
            plasticity=Fraction(9), stability=Fraction(10),
            information_required=Fraction(11),
        )
        self.assertGreater(c.aggregate_cost, Fraction(0))

    def test_negative_rejected(self):
        """Negative coordinate raises ValueError."""
        with self.assertRaises(ValueError):
            Coordinates(
                wall_clock=Fraction(-1), memory_bytes=Fraction(0),
                energy_joules=Fraction(0), description_length=Fraction(0),
                update_cost=Fraction(0), execution_cost=Fraction(0),
                generalization_gap=Fraction(0), retention_rate=Fraction(0),
                plasticity=Fraction(0), stability=Fraction(0),
                information_required=Fraction(0),
            )

    def test_wrong_type_rejected(self):
        """Non-Fraction coordinate raises TypeError."""
        with self.assertRaises(TypeError):
            Coordinates(
                wall_clock=0.5, memory_bytes=Fraction(0),
                energy_joules=Fraction(0), description_length=Fraction(0),
                update_cost=Fraction(0), execution_cost=Fraction(0),
                generalization_gap=Fraction(0), retention_rate=Fraction(0),
                plasticity=Fraction(0), stability=Fraction(0),
                information_required=Fraction(0),
            )

    def test_as_tuple_length(self):
        """as_tuple returns exactly 11 elements."""
        c = Coordinates(
            wall_clock=Fraction(1), memory_bytes=Fraction(2),
            energy_joules=Fraction(3), description_length=Fraction(4),
            update_cost=Fraction(5), execution_cost=Fraction(6),
            generalization_gap=Fraction(7), retention_rate=Fraction(8),
            plasticity=Fraction(9), stability=Fraction(10),
            information_required=Fraction(11),
        )
        self.assertEqual(len(c.as_tuple()), 11)

    def test_to_dict_from_dict_roundtrip(self):
        """to_dict -> from_dict preserves coordinates exactly."""
        original = Coordinates(
            wall_clock=Fraction('0.5'), memory_bytes=Fraction(1048576),
            energy_joules=Fraction('0.25'), description_length=Fraction(64),
            update_cost=Fraction('0.01'), execution_cost=Fraction('0.10'),
            generalization_gap=Fraction('0.05'), retention_rate=Fraction('0.95'),
            plasticity=Fraction('0.80'), stability=Fraction('0.90'),
            information_required=Fraction(128),
        )
        d = original.to_dict()
        restored = Coordinates.from_dict(d)
        self.assertEqual(original, restored)


class TestAggregateCost(unittest.TestCase):
    """Tests for aggregate cost computation."""

    def test_aggregate_cost_formula(self):
        """Verify aggregate cost formula: G + (1-R) + (1-P) + (1-S) + others."""
        c = Coordinates(
            wall_clock=Fraction(1), memory_bytes=Fraction(1),
            energy_joules=Fraction(1), description_length=Fraction(1),
            update_cost=Fraction(1), execution_cost=Fraction(1),
            generalization_gap=Fraction(1), retention_rate=Fraction(1),
            plasticity=Fraction(1), stability=Fraction(1),
            information_required=Fraction(1),
        )
        # cost-boosting coords T,M,E,D,U,X,G,I = 8; (1-R)=(1-P)=(1-S)=0
        expected = Fraction(8)
        self.assertEqual(c.aggregate_cost, expected)

    def test_aggregate_cost_perfect_retention(self):
        """Perfect retention/plasticity/stability minimize cost."""
        c = Coordinates(
            wall_clock=Fraction(0), memory_bytes=Fraction(0),
            energy_joules=Fraction(0), description_length=Fraction(0),
            update_cost=Fraction(0), execution_cost=Fraction(0),
            generalization_gap=Fraction(0), retention_rate=Fraction(1),
            plasticity=Fraction(1), stability=Fraction(1),
            information_required=Fraction(0),
        )
        self.assertEqual(c.aggregate_cost, Fraction(0))

    def test_aggregate_cost_zero_retention(self):
        """Zero retention/plasticity/stability maximize cost."""
        c = Coordinates(
            wall_clock=Fraction(0), memory_bytes=Fraction(0),
            energy_joules=Fraction(0), description_length=Fraction(0),
            update_cost=Fraction(0), execution_cost=Fraction(0),
            generalization_gap=Fraction(0), retention_rate=Fraction(0),
            plasticity=Fraction(0), stability=Fraction(0),
            information_required=Fraction(0),
        )
        # (1-0) + (1-0) + (1-0) = 3
        self.assertEqual(c.aggregate_cost, Fraction(3))


class TestCapabilityRuntime(unittest.TestCase):
    """Tests for CapabilityRuntime."""

    def test_create_default_values(self):
        """Default values produce a valid capability."""
        cap = CapabilityRuntime.create(name='test')
        self.assertEqual(cap.name, 'test')
        self.assertEqual(cap.coords.wall_clock, Fraction(0))

    def test_create_with_values(self):
        """Custom values are stored correctly."""
        cap = CapabilityRuntime.create(
            name='inference', wall_clock=0.5, memory_bytes=1048576,
        )
        self.assertEqual(cap.coords.wall_clock, Fraction('0.5'))
        self.assertEqual(cap.coords.memory_bytes, Fraction(1048576))


class TestSubadditivity(unittest.TestCase):
    """Tests for subadditivity checking."""

    def test_subadditivity_holds(self):
        """Subadditivity holds when combined <= sum of parts."""
        a = Coordinates(
            wall_clock=Fraction(1), memory_bytes=Fraction(0),
            energy_joules=Fraction(0), description_length=Fraction(0),
            update_cost=Fraction(0), execution_cost=Fraction(0),
            generalization_gap=Fraction(0), retention_rate=Fraction(1),
            plasticity=Fraction(1), stability=Fraction(1),
            information_required=Fraction(0),
        )
        b = Coordinates(
            wall_clock=Fraction(1), memory_bytes=Fraction(0),
            energy_joules=Fraction(0), description_length=Fraction(0),
            update_cost=Fraction(0), execution_cost=Fraction(0),
            generalization_gap=Fraction(0), retention_rate=Fraction(1),
            plasticity=Fraction(1), stability=Fraction(1),
            information_required=Fraction(0),
        )
        # combined via max: wall_clock = max(1,1) = 1
        ab = combine_coordinates(a, b)
        self.assertTrue(check_subadditivity(a, b, ab))

    def test_subadditivity_strict(self):
        """Strict subadditivity when shared resources reduce cost."""
        a = Coordinates(
            wall_clock=Fraction(2), memory_bytes=Fraction(0),
            energy_joules=Fraction(0), description_length=Fraction(0),
            update_cost=Fraction(0), execution_cost=Fraction(0),
            generalization_gap=Fraction(0), retention_rate=Fraction(1),
            plasticity=Fraction(1), stability=Fraction(1),
            information_required=Fraction(0),
        )
        b = Coordinates(
            wall_clock=Fraction(3), memory_bytes=Fraction(0),
            energy_joules=Fraction(0), description_length=Fraction(0),
            update_cost=Fraction(0), execution_cost=Fraction(0),
            generalization_gap=Fraction(0), retention_rate=Fraction(1),
            plasticity=Fraction(1), stability=Fraction(1),
            information_required=Fraction(0),
        )
        # combined: wall_clock = max(2,3) = 3 < 2+3 = 5
        ab = combine_coordinates(a, b)
        self.assertTrue(check_subadditivity(a, b, ab))
        self.assertLess(ab.wall_clock, a.wall_clock + b.wall_clock)

    def test_subadditivity_finite_world(self):
        """Subadditivity holds across all finite-world capability pairs."""
        fw = build_finite_world_coords()
        caps = list(fw.keys())
        for i in range(len(caps)):
            for j in range(i + 1, len(caps)):
                a_coords = fw[caps[i]][Fraction(1)]
                b_coords = fw[caps[j]][Fraction(1)]
                ab = combine_coordinates(a_coords, b_coords)
                self.assertTrue(
                    check_subadditivity(a_coords, b_coords, ab),
                    f"Subadditivity failed for {caps[i]} + {caps[j]}",
                )


class TestBudgetFlipDetector(unittest.TestCase):
    """Tests for budget-flip detection."""

    def test_no_flip(self):
        """No flip when ROI is always positive."""
        detector = BudgetFlipDetector()
        profiles = {
            'cap_a': [
                (Fraction(1), Fraction(50)),
                (Fraction(2), Fraction(60)),
                (Fraction(3), Fraction(70)),
            ],
        }
        flips = detector.detect(profiles)
        self.assertEqual(len(flips), 0)

    def test_single_flip(self):
        """Detect a single budget flip."""
        detector = BudgetFlipDetector()
        profiles = {
            'cap_a': [
                (Fraction(1), Fraction(50)),
                (Fraction(2), Fraction(60)),
                (Fraction(3), Fraction(55)),  # flip: ROI < 0
            ],
        }
        flips = detector.detect(profiles)
        self.assertEqual(len(flips), 1)
        self.assertEqual(flips[0].capability, 'cap_a')
        self.assertEqual(flips[0].budget_from, Fraction(2))
        self.assertEqual(flips[0].budget_to, Fraction(3))
        self.assertLess(flips[0].roi, Fraction(0))

    def test_multiple_capabilities(self):
        """Detect flips across multiple capabilities."""
        detector = BudgetFlipDetector()
        profiles = {
            'cap_a': [
                (Fraction(1), Fraction(50)),
                (Fraction(2), Fraction(55)),
                (Fraction(3), Fraction(58)),
            ],
            'cap_b': [
                (Fraction(1), Fraction(40)),
                (Fraction(2), Fraction(50)),
                (Fraction(3), Fraction(45)),  # flip
            ],
            'cap_c': [
                (Fraction(1), Fraction(30)),
                (Fraction(2), Fraction(25)),  # flip
                (Fraction(3), Fraction(20)),  # another flip
            ],
        }
        flips = detector.detect(profiles)
        self.assertEqual(len(flips), 3)
        caps_with_flips = {f.capability for f in flips}
        self.assertEqual(caps_with_flips, {'cap_b', 'cap_c'})

    def test_detect_single_capability(self):
        """detect_single works for one capability."""
        detector = BudgetFlipDetector()
        pairs = [
            (Fraction(1), Fraction(80)),
            (Fraction(2), Fraction(85)),
            (Fraction(3), Fraction(82)),
        ]
        flips = detector.detect_single('inference', pairs)
        self.assertEqual(len(flips), 1)
        self.assertEqual(flips[0].capability, 'inference')

    def test_roi_computation(self):
        """ROI is computed correctly."""
        detector = BudgetFlipDetector()
        roi = detector.compute_roi(
            Fraction(50), Fraction(60), Fraction(1), Fraction(2),
        )
        self.assertEqual(roi, Fraction(10))

    def test_roi_zero_budget_delta(self):
        """ROI returns 0 for identical budget levels (degenerate)."""
        detector = BudgetFlipDetector()
        roi = detector.compute_roi(
            Fraction(50), Fraction(60), Fraction(1), Fraction(1),
        )
        self.assertEqual(roi, Fraction(0))

    def test_empty_profile(self):
        """Empty profile produces no flips."""
        detector = BudgetFlipDetector()
        flips = detector.detect({})
        self.assertEqual(len(flips), 0)

    def test_single_budget_level(self):
        """Single budget level produces no flips."""
        detector = BudgetFlipDetector()
        profiles = {'cap_a': [(Fraction(1), Fraction(50))]}
        flips = detector.detect(profiles)
        self.assertEqual(len(flips), 0)

    def test_budget_flip_dataclass(self):
        """BudgetFlip stores all fields correctly."""
        flip = BudgetFlip(
            capability='test',
            budget_from=Fraction(1),
            budget_to=Fraction(2),
            roi=Fraction(-5),
            performance_from=Fraction(80),
            performance_to=Fraction(75),
        )
        self.assertEqual(flip.capability, 'test')
        self.assertEqual(flip.roi, Fraction(-5))


class TestFiniteWorld(unittest.TestCase):
    """Tests for the finite world (4 capabilities, 3 budget levels)."""

    def test_build_finite_world_structure(self):
        """Finite world has 4 capabilities with 3 budget levels each."""
        fw = build_finite_world()
        self.assertEqual(len(fw), 4)
        for cap, pairs in fw.items():
            self.assertEqual(len(pairs), 3)

    def test_build_finite_world_coords_structure(self):
        """Finite world coords has 4 capabilities with 3 budget levels."""
        fw = build_finite_world_coords()
        self.assertEqual(len(fw), 4)
        for cap, levels in fw.items():
            self.assertEqual(len(levels), 3)
            for budget, coords in levels.items():
                self.assertIsInstance(coords, Coordinates)

    def test_finite_world_subadditivity(self):
        """All coordinate pairs in finite world satisfy subadditivity."""
        fw = build_finite_world_coords()
        caps = list(fw.keys())
        for i in range(len(caps)):
            for j in range(i + 1, len(caps)):
                for budget in [Fraction(1), Fraction(2), Fraction(3)]:
                    a = fw[caps[i]][budget]
                    b = fw[caps[j]][budget]
                    ab = combine_coordinates(a, b)
                    self.assertTrue(
                        check_subadditivity(a, b, ab),
                        f"Subadditivity failed: {caps[i]}+{caps[j]} at budget {budget}",
                    )

    def test_finite_world_non_negative_coords(self):
        """All coordinates in finite world are non-negative."""
        fw = build_finite_world_coords()
        for cap, levels in fw.items():
            for budget, coords in levels.items():
                self.assertGreaterEqual(coords.wall_clock, Fraction(0))
                self.assertGreaterEqual(coords.memory_bytes, Fraction(0))
                self.assertGreaterEqual(coords.energy_joules, Fraction(0))
                self.assertGreaterEqual(coords.description_length, Fraction(0))
                self.assertGreaterEqual(coords.update_cost, Fraction(0))
                self.assertGreaterEqual(coords.execution_cost, Fraction(0))
                self.assertGreaterEqual(coords.generalization_gap, Fraction(0))
                self.assertGreaterEqual(coords.retention_rate, Fraction(0))
                self.assertGreaterEqual(coords.plasticity, Fraction(0))
                self.assertGreaterEqual(coords.stability, Fraction(0))
                self.assertGreaterEqual(coords.information_required, Fraction(0))

    def test_budget_flip_detection_in_finite_world(self):
        """Budget flip detector catches the manufactured negative-ROI case."""
        profiles = build_finite_world()
        detector = BudgetFlipDetector()
        flips = detector.detect(profiles)
        # inference should have a flip at budget 2->3
        inference_flips = [f for f in flips if f.capability == 'inference']
        self.assertEqual(len(inference_flips), 1)
        self.assertEqual(inference_flips[0].budget_from, Fraction(2))
        self.assertEqual(inference_flips[0].budget_to, Fraction(3))
        self.assertLess(inference_flips[0].roi, Fraction(0))


if __name__ == '__main__':
    unittest.main()
