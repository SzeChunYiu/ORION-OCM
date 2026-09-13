import importlib.util
import json
from fractions import Fraction as F
from itertools import product
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "reuse_invalidation", HERE / "grand_gmi_reuse_invalidation_checks_v1.py")
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)


class ReuseInvalidationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.receipt = MOD.run()

    def test_policy_enumeration_and_receipt_binding(self):
        self.assertTrue(self.receipt["all_checks_green"])
        self.assertEqual(self.receipt["census"]["instances"], 45)
        self.assertEqual(self.receipt["census"]["expected_and_worstcase_matches"], 45)
        frozen = json.loads((HERE / "GRAND_GMI_REUSE_INVALIDATION_RECEIPT_V1.json").read_text())
        self.assertEqual(self.receipt, frozen)

    def test_expectation_is_not_guaranteed_gain(self):
        row = self.receipt["witnesses"][0]
        self.assertEqual(row["repair_expected_gain"], "1/2")
        self.assertEqual(row["repair_worstcase_gain"], "-1")
        self.assertEqual(row["optimal_expected_cost"], "15/2")
        self.assertEqual(row["optimal_worstcase_cost"], "8")
        self.assertEqual((row["policies"], row["histories"]), (6633, 8))

    def test_every_invalidation_and_residual_holding_is_charged(self):
        costs = (2, 1, 2, 1, F(1, 8))
        policy = ((1, 1, 2),)*4
        self.assertEqual(MOD.execute(costs, policy, (0, 0, 0), True), F(51, 8))
        self.assertEqual(MOD.execute(costs, policy, (1, 1, 1), True), F(75, 8))
        self.assertEqual(self.receipt["witnesses"][1]["repair_expected_gain"], "1/8")

    def test_holding_damaged_scaffold_and_abandonment_are_distinct(self):
        costs = (2, 1, 2, 1, 3)
        keep = ((1, 1, 1), (0, 1, 1), (0, 1, 0))
        abandon = ((1, 1, 1), (0, 1, 0), (0, 1, 0))
        self.assertEqual(MOD.execute(costs, keep, (1, 0), True), 13)
        self.assertEqual(MOD.execute(costs, abandon, (1, 0), True), 10)
        self.assertEqual(MOD.bellman(3, costs+(F(1, 2),), True)["cold"], 6)

    def test_unadmitted_cheap_repair_is_not_a_legal_mechanism(self):
        model = (2, 0, 2, 1, 0, F(1, 2))
        self.assertEqual(MOD.bellman(3, model, False)["cold"], 6)
        self.assertLess(MOD.bellman(3, model, True)["cold"], 6)
        with self.assertRaises(ValueError):
            MOD.execute(model[:5], ((1, 1, 2),)*2, (1,), False)
        with self.assertRaises(ValueError):
            MOD.fixed_repair_gain(3, model, False)

    def test_full_rebuild_remains_a_matched_alternative(self):
        model = (0, 10, 2, 1, 0, F(1, 2))
        self.assertEqual(MOD.bellman(1, model, True)["damaged"], 1)
        self.assertEqual(MOD.bellman(1, model, False)["damaged"], 1)

    def test_support_ignores_impossible_hazard_events(self):
        for q in (0, 1):
            model = (2, 1, 2, 1, 0, q)
            oracle = MOD.policy_oracle(2, model, True)
            self.assertEqual(oracle["positive_probability_histories"], 1)
            self.assertEqual(oracle["expected"], oracle["worstcase"])

    def test_failed_certificate_attempt_is_rejected_and_paid(self):
        control = MOD.safety_control()
        self.assertEqual(control["stale_certificates_rejected"], 2)
        self.assertEqual(control["transported_accepted"], 2)
        self.assertEqual(control["failed_attempt_cost"], "1")
        self.assertEqual(control["failed_then_fresh_cost"], "3")

    def test_zero_horizon_never_acquires_or_stores(self):
        model = (2, 1, 2, 1, 1, F(1, 2))
        self.assertEqual(MOD.bellman(0, model, True), dict.fromkeys(("cold", "damaged", "valid"), 0))
        self.assertEqual(MOD.policy_oracle(0, model, True)["expected"], 0)
        with self.assertRaises(ValueError):
            MOD.fixed_repair_gain(0, model, True)

    def test_no_invalidation_recovers_pvr_without_double_derivation(self):
        # C=3,U=1,S=2 gives A=C+S-U=4, four requests, actual retained cost 8.
        costs = (4, 4, 3, 1, 0)
        actual = MOD.execute(costs, ((1, 1, 2),)*4, (0, 0, 0), True)
        self.assertEqual(actual, 8)
        self.assertEqual(12-actual, MOD.fixed_repair_gain(4, costs+(0,), True))

    def test_reuse_then_release_beats_abandon_before_service(self):
        model = (3, 1, 2, 1, 100, F(1, 2))
        self.assertEqual(MOD.bellman(2, model, True)["valid"], 3)
        for bit in (0, 1):
            self.assertEqual(MOD.execute(model[:5], ((0, 2, 0),)*2,
                                         (bit,), True, initial_state=1), 3)
        # Acquisition and repair/rebuild can also serve before logical release.
        self.assertEqual(MOD.execute((0, 0, 2, 1, 100), ((2, 2, 4),)*2, (1,), True), 2)
        for action in (4, 5):
            self.assertEqual(MOD.execute((0, 0, 2, 1, 100), ((2, 2, action),)*2,
                                         (1,), True, initial_state=2), 2)

    def test_reachable_pruning_matches_full_table_enumeration(self):
        choices = tuple(product((0, 1, 2), (1, 2), (0, 1, 2, 3, 4, 5)))
        for start, q in product(range(3), (F(0), F(1, 2), F(1))):
            model = (2, 1, 2, 1, F(1, 4), q)
            expected, worst = [], []
            for policy in product(choices, repeat=2):
                bills = [(MOD.execute(model[:5], policy, (b,), True, start), p)
                         for b, p in ((0, 1-q), (1, q)) if p]
                expected.append(sum(c*p for c, p in bills))
                worst.append(max(c for c, _ in bills))
            oracle = MOD.policy_oracle(2, model, True, start)
            self.assertEqual((oracle["expected"], oracle["worstcase"]),
                             (min(expected), min(worst)))

    def test_malformed_registers_are_rejected(self):
        model = (2, 1, 2, 1, 0, F(1, 2))
        for horizon in (-1, True, 1.5):
            with self.assertRaises(ValueError):
                MOD.bellman(horizon, model, True)
        for i, value in ((0, -1), (1, float("inf")), (2, True),
                         (4, float("nan")), (5, F(3, 2)), (3, 3)):
            bad = list(model)
            bad[i] = value
            with self.subTest(index=i, value=value):
                with self.assertRaises(ValueError):
                    MOD.bellman(2, tuple(bad), True)
        with self.assertRaises(ValueError):
            MOD.bellman(2, model, "certified")
        with self.assertRaises(ValueError):
            MOD.bellman(2, model, True, "unspecified")


if __name__ == "__main__":
    unittest.main()
