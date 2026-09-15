from __future__ import annotations

import importlib.util
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("perturbations_v1", ROOT / "perturbations_v1.py")
mod = importlib.util.module_from_spec(SPEC)
if SPEC.loader is None:
    raise RuntimeError("cannot load perturbation calculus")
SPEC.loader.exec_module(mod)


def base_point(**updates):
    point = {axis: 0 for axis in mod.AXES}
    point.update(updates)
    return point


class RepricingTests(unittest.TestCase):
    def test_price_increase_can_cross_capability_boundary(self):
        # spend=6, requirement=2: old price 2 -> capacity 3 -> margin +1;
        # new price 4 -> capacity 1 -> margin -1.
        before = base_point(communication_margin=1)
        after = mod.reprice_fixed_spend(
            before,
            axis="communication_margin",
            spend=6,
            old_price=2,
            new_price=4,
            requirement=2,
        )
        self.assertEqual(-1, after["communication_margin"])
        self.assertEqual(1, mod.independent_oracle(before)["coordination_exact"])
        self.assertEqual(0, mod.predict(after)["coordination_exact"])

    def test_equal_price_negative_twin_is_identity(self):
        before = base_point(memory_margin=1)
        after = mod.reprice_fixed_spend(
            before, axis="memory_margin", spend=6, old_price=2, new_price=2, requirement=2
        )
        self.assertEqual(before, after)

    def test_inconsistent_baseline_refused(self):
        with self.assertRaises(ValueError):
            mod.reprice_fixed_spend(
                base_point(memory_margin=0),
                axis="memory_margin",
                spend=6,
                old_price=2,
                new_price=3,
                requirement=2,
            )


class AblationTests(unittest.TestCase):
    def test_memory_ablation_can_break_planning_joint_gate(self):
        before = base_point(memory_margin=1, planning_margin=0)
        after = mod.ablate_capacity(before, axis="memory_margin", lost_capacity=2)
        self.assertEqual(1, mod.independent_oracle(before)["planning_exact"])
        self.assertEqual(0, mod.predict(after)["planning_exact"])

    def test_zero_ablation_negative_twin_is_identity(self):
        before = base_point(routing_margin=1)
        self.assertEqual(before, mod.ablate_capacity(before, axis="routing_margin", lost_capacity=0))

    def test_negative_ablation_refused(self):
        with self.assertRaises(ValueError):
            mod.ablate_capacity(base_point(), axis="memory_margin", lost_capacity=-1)


class DriftTests(unittest.TestCase):
    def test_harder_verification_requirement_breaks_verified_tool_gate(self):
        before = base_point(routing_margin=0, verification_margin=1)
        after = mod.drift_requirement(before, axis="verification_margin", requirement_delta=2)
        self.assertEqual(1, mod.independent_oracle(before)["verified_tool_exact"])
        self.assertEqual(0, mod.predict(after)["verified_tool_exact"])

    def test_zero_drift_negative_twin_is_identity(self):
        before = base_point(planning_margin=1)
        self.assertEqual(before, mod.drift_requirement(before, axis="planning_margin", requirement_delta=0))

    def test_relaxation_can_restore_capability(self):
        before = base_point(communication_margin=-1)
        after = mod.drift_requirement(before, axis="communication_margin", requirement_delta=-1)
        self.assertEqual(0, mod.independent_oracle(before)["coordination_exact"])
        self.assertEqual(1, mod.predict(after)["coordination_exact"])


class CalibrationTests(unittest.TestCase):
    def test_radius_two_probe_exact_counts(self):
        receipt = mod.calibration_probe(radius=2)
        self.assertEqual(12500, receipt["total_cells"])
        self.assertEqual(5248, receipt["determinate_cells"])
        self.assertEqual(7252, receipt["abstention_cells"])
        self.assertEqual(0, receipt["incorrect_determinate_cells"])

    def test_abstention_is_not_coerced(self):
        point = {
            "memory_margin": 2,
            "planning_margin": -2,
            "communication_margin": 0,
            "routing_margin": 0,
            "verification_margin": 0,
        }
        self.assertEqual(mod.CANNOT_IDENTIFY, mod.predict(point)["planning_exact"])

    def test_unknown_axis_refused(self):
        with self.assertRaises(ValueError):
            mod.ablate_capacity(base_point(), axis="architecture_name", lost_capacity=1)


if __name__ == "__main__":
    unittest.main()
