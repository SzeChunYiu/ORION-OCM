import importlib.util
import json
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("capability_interactions_v1", ROOT / "capability_interactions_v1.py")
mod = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(mod)


class RegistryTests(unittest.TestCase):
    def setUp(self):
        self.registry = json.loads((ROOT / "INTERACTIONS_TRANCHE1_V1.json").read_text())

    def test_exact_four_rows(self):
        rows = self.registry["rows"]
        self.assertEqual(4, len(rows))
        self.assertEqual(
            {
                "Memory × planning interaction.",
                "Memory × abstraction interaction.",
                "Search × learned heuristic interaction.",
                "Social modeling × communication interaction.",
            },
            {row["ledger_row"] for row in rows},
        )

    def test_required_claim_fields_present(self):
        for row in self.registry["rows"]:
            for field in (
                "scope",
                "assumptions",
                "theorem",
                "strongest_parent",
                "negative_twin",
                "nearest_counterexample",
                "falsifier",
                "status",
            ):
                self.assertTrue(row[field], (row["id"], field))
        self.assertEqual("G2", self.registry["claim_ceiling"])
        self.assertIn("do not establish the G6", self.registry["claim_boundary"])


class MemoryPlanningTests(unittest.TestCase):
    def test_joint_and_threshold(self):
        self.assertTrue(mod.MemoryPlanningInstance(3, 3, 4, 4).exact_success_possible())
        self.assertFalse(mod.MemoryPlanningInstance(3, 2, 4, 4).exact_success_possible())
        self.assertFalse(mod.MemoryPlanningInstance(3, 3, 4, 3).exact_success_possible())

    def test_truth_table_matches_formula(self):
        for n, k, h, d, verdict in mod.memory_planning_truth_table():
            self.assertEqual((k >= n and d >= h), verdict)

    def test_invalid_free_resource_refused(self):
        with self.assertRaises(ValueError):
            mod.MemoryPlanningInstance(3, 0, 4, 4).exact_success_possible()


class MemoryAbstractionTests(unittest.TestCase):
    def test_obligation_preserving_quotient_saves_states(self):
        raw_to_class = (0, 0, 1, 1, 2, 2)
        obligations = (9, 9, 8, 8, 7, 7)
        self.assertEqual(3, mod.abstraction_required_states(raw_to_class, obligations))

    def test_coarse_alias_is_impossible_not_cheaper(self):
        raw_to_class = (0, 0, 1, 1)
        obligations = (1, 2, 3, 3)
        self.assertIsNone(mod.abstraction_required_states(raw_to_class, obligations))

    def test_negative_twin_no_compression(self):
        raw_to_class = (0, 1, 2, 3)
        obligations = (10, 11, 12, 13)
        self.assertEqual(4, mod.abstraction_required_states(raw_to_class, obligations))


class SearchHeuristicTests(unittest.TestCase):
    def test_break_even(self):
        # Each use saves 6 verified expansions; learning costs 18.
        self.assertEqual("SEARCH_PLAIN", mod.heuristic_verdict(baseline_cost=10, heuristic_cost=4, learn_cost=18, reuse=2))
        self.assertEqual("TIE", mod.heuristic_verdict(baseline_cost=10, heuristic_cost=4, learn_cost=18, reuse=3))
        self.assertEqual("RETAIN_HEURISTIC", mod.heuristic_verdict(baseline_cost=10, heuristic_cost=4, learn_cost=18, reuse=4))

    def test_zero_reduction_twin_never_pays(self):
        for reuse in (1, 2, 8, 64, 1024):
            self.assertEqual(
                "SEARCH_PLAIN",
                mod.heuristic_verdict(baseline_cost=10, heuristic_cost=10, learn_cost=1, reuse=reuse),
            )

    def test_scope_rejects_cost_increasing_heuristic(self):
        with self.assertRaises(ValueError):
            mod.heuristic_net_saving(baseline_cost=4, heuristic_cost=5, learn_cost=0, reuse=10)


class SocialCommunicationTests(unittest.TestCase):
    def test_product_bound(self):
        self.assertEqual(6, mod.social_communication_cells(social_states=2, message_symbols=3))
        self.assertTrue(mod.social_communication_exact_possible(social_states=2, message_symbols=3, obligation_cells=6))
        self.assertFalse(mod.social_communication_exact_possible(social_states=2, message_symbols=3, obligation_cells=7))

    def test_each_factor_is_load_bearing(self):
        full = mod.social_communication_cells(social_states=4, message_symbols=5)
        no_social_distinction = mod.social_communication_cells(social_states=1, message_symbols=5)
        one_message = mod.social_communication_cells(social_states=4, message_symbols=1)
        self.assertEqual(20, full)
        self.assertEqual(5, no_social_distinction)
        self.assertEqual(4, one_message)

    def test_invalid_hidden_side_capacity_not_encoded(self):
        with self.assertRaises(ValueError):
            mod.social_communication_cells(social_states=0, message_symbols=4)


if __name__ == "__main__":
    unittest.main()
