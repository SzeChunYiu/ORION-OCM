from __future__ import annotations

from fractions import Fraction
import unittest

from resource_lifecycle_ledger_v1 import (
    COORDINATES,
    FrozenPriceVector,
    LifecycleEvent,
    ResourceVector,
    dominates,
    pareto_frontier,
    scalarize,
    total,
    totals_by_stage,
    validate_registry,
)


def vector(**overrides: int) -> ResourceVector:
    values = {name: 0 for name in COORDINATES}
    values.update(overrides)
    return ResourceVector.from_mapping(values)


class ResourceLifecycleLedgerTests(unittest.TestCase):
    def test_registry_and_exact_order_certificate(self):
        result = validate_registry()
        self.assertEqual(result["coordinates"], 14)
        self.assertEqual(result["unordered_pairs"], 351)
        self.assertEqual(result["dominance_pairs"], 189)
        self.assertEqual(result["price_reversible_incomparable_pairs"], 162)
        self.assertEqual(result["physical_metering"], "OPEN")
        self.assertEqual(result["energy_metering"], "OPEN")

    def test_lifecycle_partition_conserves_every_charge(self):
        events = (
            LifecycleEvent("BUILD", vector(build_acquisition=7, human_ai_design_input=2), "build-1"),
            LifecycleEvent("SEARCH", vector(search_discovery=5, failed_candidates=4, verification=5), "search-1"),
            LifecycleEvent("SERVE", vector(serving_execution=3, retrieval_index=1), "serve-1"),
            LifecycleEvent("REVISE", vector(revision_unlearning=2, update=1), "revise-1"),
        )
        direct = total(events)
        staged = total(LifecycleEvent(stage, charges, f"stage-{stage}") for stage, charges in totals_by_stage(events).items())
        self.assertEqual(direct, staged)
        self.assertEqual(direct.as_dict()["failed_candidates"], "4")

    def test_complete_vectors_and_nonnegative_types_fail_closed(self):
        with self.assertRaises(ValueError):
            ResourceVector.from_mapping({"build_acquisition": 1})
        with self.assertRaises(ValueError):
            vector(update=-1)
        with self.assertRaises(TypeError):
            vector(update=True)
        with self.assertRaises(ValueError):
            LifecycleEvent("UNKNOWN", vector(), "evidence")
        with self.assertRaises(ValueError):
            LifecycleEvent("BUILD", vector(), "")

    def test_pareto_and_prospective_scalarization(self):
        rows = {
            "cheap_build": vector(build_acquisition=1, serving_execution=5),
            "cheap_serve": vector(build_acquisition=5, serving_execution=1),
            "dominated": vector(build_acquisition=6, serving_execution=6),
        }
        self.assertEqual(pareto_frontier(rows), ("cheap_build", "cheap_serve"))
        self.assertTrue(dominates(rows["cheap_build"], rows["dominated"]))
        prices = {name: 1 for name in COORDINATES}
        frozen = FrozenPriceVector.freeze(prices, registration_id="freeze-before-outcomes-1", registered_before_outcomes=True)
        self.assertEqual(scalarize(rows["cheap_build"], frozen), Fraction(6))
        posthoc = FrozenPriceVector.freeze(prices, registration_id="posthoc", registered_before_outcomes=False)
        with self.assertRaises(ValueError):
            scalarize(rows["cheap_build"], posthoc)
        forged = FrozenPriceVector(frozen.prices, frozen.registration_id, True, "0" * 64)
        with self.assertRaises(ValueError):
            scalarize(rows["cheap_build"], forged)
        prices["verification"] = 0
        with self.assertRaises(ValueError):
            FrozenPriceVector.freeze(prices, registration_id="bad", registered_before_outcomes=True)


if __name__ == "__main__":
    unittest.main()
