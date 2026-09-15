from __future__ import annotations

from fractions import Fraction
import json
from pathlib import Path
import unittest

import scaling_bottleneck_v1 as u2

ROOT = Path(__file__).resolve().parent


class ScalingBottleneckV1Tests(unittest.TestCase):
    def test_registered_resource_laws(self):
        self.assertEqual(u2.resources("Q", 11), (121, 22, 11))
        self.assertEqual(u2.resources("L", 11), (111, 15, 22))

    def test_exact_work_crossover_exhaustive_1_to_128(self):
        winners = [u2.winner(n, u2.P_WORK) for n in range(1, 129)]
        self.assertEqual(winners[:10], ["Q"] * 10)
        self.assertEqual(winners[10:], ["L"] * 118)
        self.assertNotIn("TIE", winners)
        switches = [n for n in range(1, 128) if winners[n - 1] != winners[n]]
        self.assertEqual(switches, [10])
        self.assertEqual(u2.work_delta(10), -2)
        self.assertEqual(u2.work_delta(11), 10)

    def test_finite_size_correction_and_failed_n10_extrapolation(self):
        self.assertEqual(u2.finite_relative_correction(26), Fraction(2, 39))
        self.assertGreater(u2.finite_relative_correction(26), Fraction(1, 20))
        self.assertEqual(u2.finite_relative_correction(27), Fraction(4, 81))
        self.assertLessEqual(u2.finite_relative_correction(27), Fraction(1, 20))
        self.assertEqual(u2.first_tolerance_n(Fraction(1, 20)), 27)
        self.assertEqual(u2.winner(10, u2.P_WORK), "Q")
        self.assertEqual(u2.resources("Q", 10)[0], 100)
        self.assertEqual(u2.resources("L", 10)[0], 102)
        self.assertEqual(u2.zero_intercept_l_work(10), 90)

    def test_bottleneck_theorem_exhaustive_small_grid(self):
        for q1 in range(1, 4):
            for q2 in range(1, 4):
                for b1 in range(5):
                    for b2 in range(5):
                        status = u2.bottleneck_status((b1, b2), (q1, q2), ("a", "b"))
                        self.assertEqual(status["feasible"], b1 >= q1 and b2 >= q2)
                        self.assertEqual(status["sigma"] >= 1, status["feasible"])
                        self.assertTrue(status["bottlenecks"])

    def test_registered_threshold_and_negative_twin(self):
        req = u2.resources("L", 11)
        fail = u2.bottleneck_status((110, 15, 22), req, u2.RESOURCE_NAMES)
        self.assertFalse(fail["feasible"])
        self.assertEqual(fail["sigma"], Fraction(110, 111))
        self.assertEqual(fail["bottlenecks"], ["work"])

        passed = u2.bottleneck_status((111, 15, 22), req, u2.RESOURCE_NAMES)
        self.assertTrue(passed["feasible"])
        self.assertEqual(passed["sigma"], 1)

        for work in (111, 1110, 111000, 10**9):
            twin = u2.bottleneck_status((work, 14, 22), req, u2.RESOURCE_NAMES)
            self.assertFalse(twin["feasible"])
            self.assertEqual(twin["sigma"], Fraction(14, 15))
            self.assertEqual(twin["bottlenecks"], ["memory"])

    def test_binary_saturation_is_only_binary(self):
        req = u2.resources("L", 11)
        base = u2.bottleneck_status((111, 15, 22), req, u2.RESOURCE_NAMES)
        more_work = u2.bottleneck_status((10**6, 15, 22), req, u2.RESOURCE_NAMES)
        self.assertTrue(base["feasible"])
        self.assertTrue(more_work["feasible"])
        self.assertEqual(int(base["feasible"]), int(more_work["feasible"]))

    def test_price_coordinate_reversal_and_pareto_incomparability(self):
        q = u2.resources("Q", 11)
        l = u2.resources("L", 11)
        self.assertEqual(u2.winner(11, u2.P_WORK), "L")
        self.assertEqual(u2.winner(11, u2.P_VERIFY), "Q")
        self.assertFalse(u2.pareto_dominates(q, l))
        self.assertFalse(u2.pareto_dominates(l, q))

    def test_smooth_no_crossover_control(self):
        for n in range(1, 129):
            self.assertLess(3 * n + 1, 5 * n + 7)

    def test_malformed_inputs_fail_closed(self):
        for bad_n in (0, -1, 1.5, True):
            with self.assertRaises(ValueError):
                u2.resources("Q", bad_n)  # type: ignore[arg-type]
        with self.assertRaises(ValueError):
            u2.resources("UNKNOWN", 1)
        with self.assertRaises(ValueError):
            u2.charged_cost((1, 2), (1,))
        with self.assertRaises(ValueError):
            u2.bottleneck_status((1,), (0,), ("x",))
        with self.assertRaises(ValueError):
            u2.bottleneck_status((-1,), (1,), ("x",))
        with self.assertRaises(ValueError):
            u2.bottleneck_status((1, 1), (1, 1), ("x", "x"))
        with self.assertRaises(ValueError):
            u2.first_tolerance_n(Fraction(0))

    def test_receipt_matches_committed_result_and_contains_no_floats(self):
        actual = u2.build_receipt()
        committed = json.loads((ROOT / "RESULT_V1.json").read_text(encoding="utf-8"))
        self.assertEqual(actual, committed)

        def walk(value):
            if isinstance(value, dict):
                for child in value.values():
                    yield from walk(child)
            elif isinstance(value, list):
                for child in value:
                    yield from walk(child)
            else:
                yield value

        self.assertFalse(any(isinstance(value, float) for value in walk(actual)))
        self.assertFalse(actual["smooth_vs_crossover"]["thermodynamic_phase_transition_claimed"])
        self.assertTrue(actual["finite_size_correction"]["exact_finite_extrapolation_failure_at_n10"])


if __name__ == "__main__":
    unittest.main()
