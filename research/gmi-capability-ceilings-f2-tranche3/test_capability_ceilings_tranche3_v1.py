"""Exact and hostile controls for #602 F2 tranche 3 capability ceilings."""

from fractions import Fraction
from pathlib import Path
import copy
import importlib.util
import unittest

path = Path(__file__).with_name("capability_ceilings_tranche3_v1.py")
spec = importlib.util.spec_from_loader("f2_tranche3_checked", loader=None)
mod = importlib.util.module_from_spec(spec)
mod.__file__ = str(path)
exec(compile(path.read_bytes(), str(path), "exec"), mod.__dict__)


class RegistryControls(unittest.TestCase):
    def test_registry_exact_and_valid(self):
        self.assertEqual(mod.validate_registry(), [])
        self.assertEqual(len(mod.EXPECTED_IDS), 3)

    def test_missing_row_rejected(self):
        data = copy.deepcopy(mod.load_registry())
        data["ceilings"].pop()
        self.assertTrue(any("id/order mismatch" in e for e in mod.validate_registry(data)))

    def test_g6_escalation_rejected(self):
        data = copy.deepcopy(mod.load_registry())
        data["claim_ceiling"] = "G6"
        self.assertTrue(any("claim ceiling must be G2" in e for e in mod.validate_registry(data)))

    def test_empty_falsifier_rejected(self):
        data = copy.deepcopy(mod.load_registry())
        data["ceilings"][0]["falsifier"] = ""
        self.assertTrue(any("empty falsifier" in e for e in mod.validate_registry(data)))


class PlanningControls(unittest.TestCase):
    def test_exact_binary_tree_counts(self):
        self.assertEqual(mod.complete_tree_nodes(2, 0), 1)
        self.assertEqual(mod.complete_tree_nodes(2, 2), 7)
        self.assertEqual(mod.complete_tree_nodes(2, 3), 15)

    def test_binary_horizon_boundary_is_tight(self):
        self.assertFalse(mod.planning_budget_allows(2, 3, 14))
        self.assertTrue(mod.planning_budget_allows(2, 3, 15))
        self.assertEqual(mod.max_exhaustive_horizon(2, 14), 2)
        self.assertEqual(mod.max_exhaustive_horizon(2, 15), 3)

    def test_chain_special_case(self):
        self.assertEqual(mod.complete_tree_nodes(1, 4), 5)
        self.assertEqual(mod.max_exhaustive_horizon(1, 5), 4)

    def test_uninspected_node_supports_adversary(self):
        self.assertTrue(mod.planning_uninspected_adversary(2, 3, 14))
        self.assertFalse(mod.planning_uninspected_adversary(2, 3, 15))

    def test_shortcuts_are_scope_changes(self):
        errors = mod.validate_planning_scope({
            "full_tree": True,
            "heuristic_oracle": True,
            "pruning_certificate": True,
            "transposition_merging": True,
            "structural_dominance": True,
            "worst_case_complete": True,
        })
        self.assertEqual(len(errors), 4)


class SearchControls(unittest.TestCase):
    def test_five_candidates_need_five_worst_case_queries(self):
        self.assertFalse(mod.search_budget_allows(5, 4))
        self.assertTrue(mod.search_budget_allows(5, 5))
        self.assertEqual(mod.max_guaranteed_unstructured_candidates(4), 4)

    def test_adversary_uses_unqueried_index(self):
        self.assertEqual(mod.unstructured_search_adversary(5, [0, 1, 2, 3]), 4)
        self.assertIsNone(mod.unstructured_search_adversary(5, [0, 1, 2, 3, 4]))

    def test_query_order_does_not_change_unstructured_lower_bound(self):
        self.assertEqual(mod.unstructured_search_adversary(5, [4, 2, 0, 1]), 3)

    def test_duplicate_query_rejected(self):
        with self.assertRaises(ValueError):
            mod.unstructured_search_adversary(5, [0, 0])

    def test_structured_shortcuts_rejected_by_scope(self):
        errors = mod.validate_search_scope({
            "unstructured_candidates": False,
            "ordering_promise": True,
            "heuristic_oracle": True,
            "side_information": True,
            "perfect_membership_verifier": True,
            "worst_case_zero_error": True,
        })
        self.assertEqual(len(errors), 4)


class VerificationControls(unittest.TestCase):
    def test_single_defect_floor(self):
        self.assertEqual(mod.hypergeom_false_adoption(10, 1, 8), Fraction(1, 5))
        self.assertEqual(mod.hypergeom_false_adoption(10, 1, 10), Fraction(0, 1))

    def test_multiple_defect_formula_matches_enumeration(self):
        expected = mod.hypergeom_false_adoption(6, 2, 2)
        observed = mod.exhaustive_uniform_defect_miss(6, 2, [0, 1])
        self.assertEqual(expected, Fraction(2, 5))
        self.assertEqual(observed, expected)

    def test_checked_coordinate_identity_is_irrelevant_under_exchangeability(self):
        self.assertEqual(
            mod.exhaustive_uniform_defect_miss(6, 2, [0, 1]),
            mod.exhaustive_uniform_defect_miss(6, 2, [2, 5]),
        )

    def test_target_false_adoption_implies_minimum_checks(self):
        self.assertEqual(mod.minimum_checks_for_false_adoption(10, 1, Fraction(1, 5)), 8)
        self.assertEqual(mod.minimum_checks_for_false_adoption(10, 1, Fraction(0, 1)), 10)

    def test_adversarial_zero_false_adoption_requires_full_coverage(self):
        self.assertFalse(mod.adversarial_zero_false_adoption_possible(10, 9))
        self.assertTrue(mod.adversarial_zero_false_adoption_possible(10, 10))

    def test_side_information_and_imperfect_checks_are_scope_changes(self):
        errors = mod.validate_verification_scope({
            "exchangeable_defects": False,
            "defect_location_side_info": True,
            "distinct_checks_without_replacement": False,
            "perfect_check_detection": False,
            "adopt_iff_all_checked_pass": False,
        })
        self.assertEqual(len(errors), 5)

    def test_bad_domains_rejected(self):
        with self.assertRaises(ValueError):
            mod.hypergeom_false_adoption(5, 6, 1)
        with self.assertRaises(ValueError):
            mod.hypergeom_false_adoption(5, 1, 6)
        with self.assertRaises(ValueError):
            mod.exhaustive_uniform_defect_miss(5, 1, [0, 0])


class EndToEndControls(unittest.TestCase):
    def test_run_passes(self):
        result = mod.run()
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["claim_ceiling"], "G2")
        self.assertEqual(result["ceiling_ids"], list(mod.EXPECTED_IDS))
        self.assertTrue(all(result["checks"].values()))


if __name__ == "__main__":
    unittest.main()
