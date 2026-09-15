from __future__ import annotations

import importlib.util
import json
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("development_amortization_v1", ROOT / "development_amortization_v1.py")
mod = importlib.util.module_from_spec(SPEC)
if SPEC.loader is None:
    raise RuntimeError("cannot load amortization module")
SPEC.loader.exec_module(mod)


class LifecycleTheoremTests(unittest.TestCase):
    def test_exact_crossover_and_reset_reversal(self):
        # Per-task saving = 3, maintenance/revision = 9.
        # H=3 ties; H>=4 continued wins; H<=2 reset wins.
        self.assertEqual(mod.RESET, mod.lifecycle_costs(horizon=2, reset_per_task=8, continued_per_task=5, maintenance_revision=9)["verdict"])
        self.assertEqual(mod.TIE, mod.lifecycle_costs(horizon=3, reset_per_task=8, continued_per_task=5, maintenance_revision=9)["verdict"])
        self.assertEqual(mod.CONTINUE, mod.lifecycle_costs(horizon=4, reset_per_task=8, continued_per_task=5, maintenance_revision=9)["verdict"])
        self.assertEqual(4, mod.strict_continue_break_even(reset_per_task=8, continued_per_task=5, maintenance_revision=9))

    def test_no_break_even_without_positive_per_task_saving(self):
        self.assertEqual(mod.NO_FINITE_BREAK_EVEN, mod.strict_continue_break_even(reset_per_task=5, continued_per_task=5, maintenance_revision=0))
        self.assertEqual(mod.NO_FINITE_BREAK_EVEN, mod.strict_continue_break_even(reset_per_task=4, continued_per_task=5, maintenance_revision=0))

    def test_exhaustive_small_integer_verdicts(self):
        checked = 0
        for horizon in range(1, 7):
            for reset_per_task in range(0, 6):
                for continued_per_task in range(0, 6):
                    for maintenance in range(0, 11):
                        result = mod.lifecycle_costs(
                            horizon=horizon,
                            reset_per_task=reset_per_task,
                            continued_per_task=continued_per_task,
                            maintenance_revision=maintenance,
                        )
                        reset = horizon * reset_per_task
                        continued = maintenance + horizon * continued_per_task
                        expected = mod.CONTINUE if continued < reset else mod.RESET if continued > reset else mod.TIE
                        self.assertEqual(expected, result["verdict"])
                        checked += 1
        self.assertEqual(2376, checked)


class RepresentationTests(unittest.TestCase):
    def test_obligation_preserving_compression_can_reduce_future_acquisition(self):
        costs = mod.representation_future_cost(raw_distinctions=10, quotient_classes=4, representation_use_cost=1)
        self.assertTrue(costs["future_acquisition_cheaper"])
        self.assertEqual(5, costs["per_task_saving"])

    def test_representation_negative_twin_no_net_saving(self):
        costs = mod.representation_future_cost(raw_distinctions=5, quotient_classes=4, representation_use_cost=1)
        self.assertFalse(costs["future_acquisition_cheaper"])
        self.assertEqual(0, costs["per_task_saving"])

    def test_maintenance_can_reverse_representation_benefit_at_short_horizon(self):
        short = mod.representation_lifecycle_verdict(
            horizon=1,
            raw_distinctions=10,
            quotient_classes=4,
            representation_use_cost=1,
            maintenance_revision=8,
        )
        long = mod.representation_lifecycle_verdict(
            horizon=2,
            raw_distinctions=10,
            quotient_classes=4,
            representation_use_cost=1,
            maintenance_revision=8,
        )
        self.assertEqual(mod.RESET, short["verdict"])
        self.assertEqual(mod.CONTINUE, long["verdict"])


class OperatorTests(unittest.TestCase):
    def test_learned_operator_can_reduce_future_search(self):
        costs = mod.operator_future_search_cost(base_expansions=12, learned_expansions=5, verification_cost=2)
        self.assertTrue(costs["future_search_cheaper"])
        self.assertEqual(5, costs["per_task_saving"])

    def test_verification_can_erase_operator_gain(self):
        costs = mod.operator_future_search_cost(base_expansions=8, learned_expansions=5, verification_cost=3)
        self.assertFalse(costs["future_search_cheaper"])
        self.assertEqual(0, costs["per_task_saving"])


class PriorTests(unittest.TestCase):
    def test_search_prior_improves_discovery_when_rank_saving_pays_inference(self):
        costs = mod.prior_future_discovery_cost(base_rank=20, prior_rank=5, prior_inference_cost=2)
        self.assertTrue(costs["future_discovery_cheaper"])
        self.assertEqual(13, costs["per_task_saving"])

    def test_misranked_prior_is_harmful(self):
        costs = mod.prior_future_discovery_cost(base_rank=5, prior_rank=8, prior_inference_cost=1)
        self.assertFalse(costs["future_discovery_cheaper"])
        self.assertEqual(-4, costs["per_task_saving"])


class RegistryAndHostileTests(unittest.TestCase):
    def test_registry_rows_and_claim_gate(self):
        registry = json.loads((ROOT / "DEVELOPMENT_AMORTIZATION_V1.json").read_text())
        self.assertEqual(5, len(registry["rows"]))
        self.assertEqual("G2", registry["claim_ceiling"])
        for field in ("scope", "assumptions", "evidence_class", "strongest_parent", "negative_twin", "nearest_counterexample", "falsifier", "claim_boundary"):
            self.assertTrue(registry[field], field)
        for row in registry["rows"]:
            for field in ("ledger_row", "law", "strongest_parent", "negative_twin", "falsifier"):
                self.assertTrue(row[field], (row["id"], field))

    def test_boolean_smuggling_refused(self):
        with self.assertRaises(ValueError):
            mod.lifecycle_costs(horizon=True, reset_per_task=1, continued_per_task=0, maintenance_revision=0)
        with self.assertRaises(ValueError):
            mod.representation_future_cost(raw_distinctions=True, quotient_classes=1, representation_use_cost=0)
        with self.assertRaises(ValueError):
            mod.operator_future_search_cost(base_expansions=1, learned_expansions=False, verification_cost=0)
        with self.assertRaises(ValueError):
            mod.prior_future_discovery_cost(base_rank=1, prior_rank=True, prior_inference_cost=0)


if __name__ == "__main__":
    unittest.main()
