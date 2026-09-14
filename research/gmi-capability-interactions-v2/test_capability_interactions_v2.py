import importlib.util
import json
import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("capability_interactions_v2", ROOT / "capability_interactions_v2.py")
mod = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = mod
assert SPEC.loader is not None
SPEC.loader.exec_module(mod)


class RegistryTests(unittest.TestCase):
    def setUp(self):
        self.registry = json.loads((ROOT / "INTERACTIONS_TRANCHE2_V1.json").read_text())

    def test_exact_five_rows(self):
        self.assertEqual(5, len(self.registry["rows"]))
        self.assertEqual(
            {
                "Communication × teaching interaction.",
                "Teaching × cultural accumulation interaction.",
                "Metacognition × resource allocation interaction.",
                "Causal model × planning interaction.",
                "Tool routing × verification interaction.",
            },
            {row["ledger_row"] for row in self.registry["rows"]},
        )

    def test_required_claim_fields(self):
        for row in self.registry["rows"]:
            for field in (
                "scope", "assumptions", "theorem", "strongest_parent",
                "negative_twin", "nearest_counterexample", "falsifier", "status",
            ):
                self.assertTrue(row[field], (row["id"], field))
        self.assertEqual("G2", self.registry["claim_ceiling"])


class CommunicationTeachingTests(unittest.TestCase):
    def test_product_capacity(self):
        self.assertEqual(12, mod.teaching_cells(prior_classes=3, transcript_symbols=4))

    def test_each_factor_load_bearing(self):
        self.assertEqual(4, mod.teaching_cells(prior_classes=1, transcript_symbols=4))
        self.assertEqual(3, mod.teaching_cells(prior_classes=3, transcript_symbols=1))

    def test_free_zero_channel_refused(self):
        with self.assertRaises(ValueError):
            mod.teaching_cells(prior_classes=3, transcript_symbols=0)


class TeachingCultureTests(unittest.TestCase):
    def test_exact_recurrence(self):
        self.assertEqual(11, mod.next_cultural_repertoire(current=10, teaching_capacity=8, novel_discoveries=3))
        self.assertTrue(mod.cultural_growth_possible(current=10, teaching_capacity=8, novel_discoveries=3))

    def test_replacement_before_growth(self):
        self.assertEqual(10, mod.next_cultural_repertoire(current=10, teaching_capacity=8, novel_discoveries=2))
        self.assertFalse(mod.cultural_growth_possible(current=10, teaching_capacity=8, novel_discoveries=2))

    def test_no_discovery_twin(self):
        self.assertEqual(8, mod.next_cultural_repertoire(current=10, teaching_capacity=8, novel_discoveries=0))
        self.assertFalse(mod.cultural_growth_possible(current=10, teaching_capacity=8, novel_discoveries=0))


class MetacognitionAllocationTests(unittest.TestCase):
    def test_top_k_positive(self):
        self.assertEqual((1, 3), mod.allocate_equal_cost_evc((0.5, 3.0, -1.0, 2.0), 2))

    def test_no_scarcity_selects_all_positive(self):
        self.assertEqual((1, 3, 0), mod.allocate_equal_cost_evc((0.5, 3.0, -1.0, 2.0), 10))

    def test_equal_value_tie_is_deterministic(self):
        self.assertEqual((0, 1), mod.allocate_equal_cost_evc((1.0, 1.0, 1.0), 2))


class CausalPlanningTests(unittest.TestCase):
    def test_alias_with_common_optimum_is_sufficient(self):
        classes = (0, 0)
        values = ((3.0, 1.0), (2.0, 1.0))
        self.assertTrue(mod.planning_sufficient(classes, values))

    def test_alias_with_conflicting_interventions_is_insufficient(self):
        classes = (0, 0)
        values = ((3.0, 1.0), (1.0, 3.0))
        self.assertFalse(mod.planning_sufficient(classes, values))

    def test_ties_can_preserve_common_action(self):
        classes = (0, 0)
        values = ((3.0, 3.0), (1.0, 3.0))
        self.assertTrue(mod.planning_sufficient(classes, values))


class ToolVerificationTests(unittest.TestCase):
    def test_safe_success(self):
        status = mod.verified_route_status(
            routed=("a", "b", "c"),
            correct=frozenset({"b"}),
            accepted=frozenset({"b"}),
            verification_budget=2,
        )
        self.assertEqual("SAFE_SUCCESS", status)

    def test_correct_beyond_budget_does_not_help(self):
        status = mod.verified_route_status(
            routed=("a", "b", "c"),
            correct=frozenset({"c"}),
            accepted=frozenset({"c"}),
            verification_budget=2,
        )
        self.assertEqual("NO_VERIFIED_SOLUTION", status)

    def test_false_accept_is_unsafe(self):
        status = mod.verified_route_status(
            routed=("a", "b"),
            correct=frozenset({"b"}),
            accepted=frozenset({"a", "b"}),
            verification_budget=2,
        )
        self.assertEqual("UNSAFE_VERIFIER", status)

    def test_zero_budget_twin(self):
        status = mod.verified_route_status(
            routed=("a",),
            correct=frozenset({"a"}),
            accepted=frozenset({"a"}),
            verification_budget=0,
        )
        self.assertEqual("NO_VERIFIED_SOLUTION", status)


if __name__ == "__main__":
    unittest.main()
