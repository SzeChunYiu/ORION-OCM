"""Bounded helper qualification; no corpus, learner, or native verifier."""
from fractions import Fraction as F
from decimal import Decimal
import unittest
import decision_core as D


class ExactCoreTests(unittest.TestCase):
    def model(self, ps, pt, sa=("a",), ta=("a",)):
        states = ("s", "t", "u", "v")
        actions = {"s": sa, "t": ta, "u": ("a", "b"), "v": ("a", "b")}
        contract = {(s, a): int(s == "u") for s in states for a in actions[s]}
        kernels = {"s": ps, "t": pt, "u": ((1, "u"),), "v": ((1, "v"),)}
        transitions = {(s, a): kernels[s] for s in states for a in actions[s]}
        return states, actions, contract, transitions, dict(zip(states, ("B", "B", "U", "V")))

    def dp(self, stop, cost, outcomes, budget=1):
        return D.finite_meta_dp(
            ("s", "t"), {"s": stop, "t": 0}, {"s": ("probe",), "t": ()},
            {("s", "probe"): cost}, {("s", "probe"): outcomes}, budget)

    def test_decision_regions_snapshot_good_action_iterables(self):
        states, actions = ("s",), ("a", "b")
        expected = {"a": frozenset(), "b": frozenset({"s"})}
        for container in (tuple, iter):
            with self.subTest(container=container.__name__):
                regions = D.decision_regions(
                    iter(states), iter(actions), {"s": container(("b",))})
                self.assertEqual(regions, expected)
                common = D.common_actions(states, {"s": container(("b",))})
                self.assertEqual(common, frozenset({"b"}))
                self.assertEqual(D.contained_decision_actions(states, regions), common)

    def test_near_equal_laws_do_not_certify_exact_bisimulation(self):
        delta = F(1, 2**42)
        model = self.model(((F(1, 2) + delta, "u"), (F(1, 2) - delta, "v")),
                           ((F(1, 2), "u"), (F(1, 2), "v")))
        self.assertFalse(D.is_contract_bisimulation(*model))

    def test_exact_equal_laws_and_split_mass_are_accepted(self):
        model = self.model(((F(1, 3), "u"), (F(2, 3), "v")),
                           ((F(1, 6), "u"), (F(1, 6), "u"), (F(2, 3), "v")))
        self.assertTrue(D.is_contract_bisimulation(*model))

    def test_admissible_action_order_is_irrelevant(self):
        model = self.model(((1, "u"),), ((1, "u"),), ("a", "b"), ("b", "a"))
        self.assertTrue(D.is_contract_bisimulation(*model))

    def test_different_action_sets_and_contracts_remain_rejected(self):
        model = self.model(((1, "u"),), ((1, "u"),), ("a",), ("b",))
        self.assertFalse(D.is_contract_bisimulation(*model))
        model = self.model(((1, "u"),), ((1, "u"),))
        model[2]["t", "a"] = 7
        self.assertFalse(D.is_contract_bisimulation(*model))

    def test_integer_stop_margin_survives_above_binary64_precision(self):
        values, policies = self.dp(2**53 + 1, 2**53, ((1, "t"),))
        self.assertEqual(policies[1]["s"], "probe")
        self.assertEqual(values[1]["s"], F(2**53))
        self.assertEqual(values[0]["s"], F(2**53 + 1))

    def test_finite_zero_cost_loop_stops_at_allowance_zero(self):
        values, policies = self.dp(1, 0, ((1, "s"),), budget=3)
        self.assertEqual([v["s"] for v in values], [F(1)] * 4)
        self.assertTrue(all(p["s"] is None for p in policies))

    def test_transition_and_action_iterators_survive_two_steps(self):
        values, policies = D.finite_meta_dp(
            iter(("s", "t")), {"s": 3, "t": 0},
            {"s": iter(("probe",)), "t": iter(())}, {("s", "probe"): 1},
            {("s", "probe"): iter(((1, "t"),))}, 2)
        self.assertEqual(values[2]["s"], F(1))
        self.assertEqual(policies[2]["s"], "probe")

    def test_binary_float_inputs_mean_their_exact_stored_rationals(self):
        values, _ = self.dp(1.0, 0.5, ((0.5, "s"), (0.5, "t")))
        self.assertIsInstance(values[1]["s"], F)
        self.assertEqual(values[1]["s"], 1)

    def test_rational_feature_regret_is_exact_with_iterable_inputs(self):
        costs = {("x", "a"): 0, ("x", "b"): 1,
                 ("y", "a"): 1, ("y", "b"): 0}
        report = D.feature_regret_floor(
            iter(("x", "y")), iter(("a", "b")), costs,
            {"x": F(1, 3), "y": F(2, 3)}, {"x": "z", "y": "z"})
        self.assertEqual(report["regret"], F(1, 3))
        self.assertIsInstance(report["regret"], F)
        self.assertEqual(report["policy"], {"z": "b"})

    def test_zero_regret_control_and_nonempty_common_optimum(self):
        costs = {("x", "a"): 0, ("x", "b"): F(1, 3)}
        result = D.feature_regret_floor(("x",), ("a", "b"), costs, {"x": 1}, {"x": 0})
        self.assertEqual(result["regret"], 0)
        self.assertTrue(D.exact_feature_sufficient(("x",), ("a", "b"), costs, {"x": 0}))

    def test_signed_and_inexactly_normalized_kernels_are_rejected(self):
        for outcomes in (((-1, "s"), (2, "t")),
                         ((1 - F(1, 2**42), "s"),),
                         ((0.1, "s"), (0.9, "t"))):
            with self.subTest(outcomes=outcomes):
                with self.assertRaises(ValueError):
                    self.dp(3, 1, outcomes)
                with self.assertRaises(ValueError):
                    D.is_contract_bisimulation(*self.model(outcomes, outcomes))

    def test_unknown_successors_are_rejected_even_at_zero_probability(self):
        with self.assertRaises(ValueError):
            self.dp(1, 0, ((1, "t"), (0, "outside")))
        with self.assertRaises(ValueError):
            D.is_contract_bisimulation(
                *self.model(((1, "outside"),), ((1, "outside"),)))

    def test_invalid_numeric_inputs_fail_closed(self):
        for bad in (float("nan"), float("inf"), -float("inf")):
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError):
                    self.dp(bad, 0, ((1, "t"),))
        for bad in (True, "1", Decimal("1")):
            with self.subTest(bad=repr(bad)):
                with self.assertRaises(TypeError):
                    self.dp(bad, 0, ((1, "t"),))
        with self.assertRaises(ValueError):
            self.dp(1, -1, ((1, "t"),))

    def test_invalid_probability_weight_and_allowance_domains(self):
        for bad in (True, "1", float("nan")):
            with self.subTest(probability=repr(bad)):
                with self.assertRaises((TypeError, ValueError)):
                    self.dp(1, 0, ((bad, "t"),))
        for bad in (True, F(1), -1):
            with self.subTest(allowance=bad):
                with self.assertRaises((TypeError, ValueError)):
                    self.dp(1, 0, ((1, "t"),), budget=bad)
        for weight in (-1, F(1, 2), float("nan")):
            with self.subTest(weight=weight):
                with self.assertRaises(ValueError):
                    D.best_feature_expected_cost(("x",), ("a",), {("x", "a"): 1},
                                                 {"x": weight}, {"x": "z"})

    def test_numeric_helpers_reject_nonfinite_costs(self):
        calls = (
            lambda: D.optimal_actions("s", ("a",), {("s", "a"): float("nan")}),
            lambda: D.price_independent_dominates((float("nan"),), (1,)),
            lambda: D.local_gain_beats_overhead(0, 0, float("inf"), 0),
            lambda: D.prune_dominated_slopes(((0, float("inf"), "x"),)),
        )
        for call in calls:
            with self.assertRaises(ValueError):
                call()

    def test_adaptive_information_erratum_two_world_control(self):
        # Columns: Theta, P1, Y1, P2, Y2. Two equally likely worlds.
        rows = ((0, "fixed", 0, 0, "constant"), (1, "fixed", 1, 1, "constant"))
        def entropy(columns):
            distinct = {tuple(row[c] for c in columns) for row in rows}
            return int(len(distinct) == 2)  # Exactly 0 or 1 bit in this table.
        def cmi(x, y, z=()):
            return entropy(x + z) + entropy(y + z) - entropy(z) - entropy(x + y + z)
        obsolete_lhs = cmi((0,), (2, 4), (1, 3))
        incremental = cmi((0,), (2,), (1,)) + cmi((0,), (4,), (1, 2, 3))
        corrected_lhs = cmi((0,), (1, 2, 3, 4))
        self.assertEqual(obsolete_lhs, 0)
        self.assertEqual(incremental, 1)
        self.assertEqual(corrected_lhs, incremental)


if __name__ == "__main__":
    unittest.main()
