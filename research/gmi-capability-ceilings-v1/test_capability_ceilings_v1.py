"""Exact and hostile controls for #602 F2 capability ceilings, all eleven rows."""

from fractions import Fraction
from pathlib import Path
import copy
import importlib.util
import unittest

path = Path(__file__).with_name("capability_ceilings_v1.py")
spec = importlib.util.spec_from_loader("gmi_capability_ceilings_checked", loader=None)
mod = importlib.util.module_from_spec(spec)
mod.__file__ = str(path)
exec(compile(path.read_bytes(), str(path), "exec"), mod.__dict__)


class RegistryControls(unittest.TestCase):
    def test_exact_registry_is_valid(self):
        self.assertEqual(mod.validate_registry(), [])
        self.assertEqual(len(mod.EXPECTED_IDS), 11)

    def test_missing_ceiling_rejected(self):
        data = copy.deepcopy(mod.load_registry())
        data["ceilings"].pop()
        errors = mod.validate_registry(data)
        self.assertTrue(any("ceiling id/order mismatch" in e for e in errors))

    def test_claim_escalation_rejected(self):
        data = copy.deepcopy(mod.load_registry())
        data["claim_ceiling"] = "G6"
        self.assertTrue(any("claim ceiling must be G2" in e for e in mod.validate_registry(data)))

    def test_empty_parent_rejected(self):
        data = copy.deepcopy(mod.load_registry())
        data["ceilings"][0]["strongest_parent"] = ""
        self.assertTrue(any("empty strongest_parent" in e for e in mod.validate_registry(data)))


class StateCapacityControls(unittest.TestCase):
    def test_three_labels_need_three_states(self):
        self.assertFalse(mod.state_capacity_allows(3, 2))
        self.assertFalse(mod.exhaustive_delayed_label_exists(3, 2))
        self.assertTrue(mod.state_capacity_allows(3, 3))
        self.assertTrue(mod.exhaustive_delayed_label_exists(3, 3))

    def test_one_state_handles_one_class(self):
        self.assertTrue(mod.exhaustive_delayed_label_exists(1, 1))

    def test_external_memory_rejected_by_scope(self):
        errors = mod.validate_state_scope({
            "external_memory": True,
            "hidden_side_channel": False,
            "future_observation_reseparates": False,
            "zero_error": True,
        })
        self.assertTrue(any("external memory" in e for e in errors))

    def test_future_reseparation_rejected_by_scope(self):
        errors = mod.validate_state_scope({
            "external_memory": False,
            "hidden_side_channel": False,
            "future_observation_reseparates": True,
            "zero_error": True,
        })
        self.assertTrue(any("re-separates" in e for e in errors))


class ObservationQuotientControls(unittest.TestCase):
    def setUp(self):
        self.observation = {"x0": "z0", "x1": "z0", "x2": "z1"}

    def test_collision_with_different_obligations_impossible(self):
        required = {"x0": "a0", "x1": "a1", "x2": "a0"}
        self.assertFalse(mod.observation_task_realisable(self.observation, required))
        self.assertFalse(mod.exhaustive_observation_policy_exists(self.observation, required))

    def test_negative_twin_collapse_is_realisable(self):
        required = {"x0": "a0", "x1": "a0", "x2": "a1"}
        self.assertTrue(mod.observation_task_realisable(self.observation, required))
        self.assertTrue(mod.exhaustive_observation_policy_exists(self.observation, required))

    def test_later_probe_rejected_by_scope(self):
        errors = mod.validate_observation_scope({
            "later_probe": True,
            "later_intervention_information": False,
            "side_information": False,
            "zero_error": True,
        })
        self.assertTrue(any("later probe" in e for e in errors))

    def test_domain_mismatch_rejected(self):
        with self.assertRaises(ValueError):
            mod.observation_task_realisable({"x0": "z0"}, {"x1": "a0"})


class CommunicationControls(unittest.TestCase):
    def test_two_bits_carry_at_most_four_identity_classes(self):
        self.assertTrue(mod.communication_allows(4, 2))
        self.assertFalse(mod.communication_allows(5, 2))
        self.assertEqual(mod.minimum_fixed_bits(5), 3)

    def test_exhaustive_protocol_boundary(self):
        self.assertFalse(mod.exhaustive_one_way_protocol_exists(3, 1))
        self.assertTrue(mod.exhaustive_one_way_protocol_exists(4, 2))

    def test_zero_bits_handle_one_class_only(self):
        self.assertTrue(mod.exhaustive_one_way_protocol_exists(1, 0))
        self.assertFalse(mod.communication_allows(2, 0))

    def test_receiver_side_information_rejected_by_scope(self):
        errors = mod.validate_communication_scope({
            "receiver_side_information": True,
            "correlated_shared_state": False,
            "deterministic": True,
            "noiseless": True,
            "fixed_length": True,
            "one_way": True,
            "zero_error": True,
        })
        self.assertTrue(any("side information" in e for e in errors))

    def test_randomized_or_noisy_claim_rejected_by_scope(self):
        errors = mod.validate_communication_scope({
            "receiver_side_information": False,
            "correlated_shared_state": False,
            "deterministic": False,
            "noiseless": False,
            "fixed_length": True,
            "one_way": True,
            "zero_error": True,
        })
        self.assertTrue(any("deterministic" in e for e in errors))
        self.assertTrue(any("noiseless" in e for e in errors))


class PrecisionBoundaryControls(unittest.TestCase):
    def test_two_bits_do_not_cover_five_threshold_placements(self):
        self.assertEqual(mod.precision_boundary_capacity(2, 4), 4)
        self.assertFalse(mod.exhaustive_threshold_codebook_covers(4, 2))
        self.assertEqual(mod.minimum_threshold_bits(4), 3)

    def test_two_bits_are_tight_for_four_threshold_placements(self):
        self.assertEqual(mod.precision_boundary_capacity(2, 3), 4)
        self.assertTrue(mod.exhaustive_threshold_codebook_covers(3, 2))

    def test_architecture_growth_scope_is_not_silently_claimed(self):
        errors = mod.validate_precision_scope({
            "architecture_frozen": False,
            "codebook_frozen": True,
            "extra_precision_channel": False,
            "task_specific_decoder_rewrite": False,
            "zero_error": True,
        })
        self.assertTrue(any("architecture must be frozen" in e for e in errors))

    def test_posthoc_codebook_and_side_precision_rejected(self):
        errors = mod.validate_precision_scope({
            "architecture_frozen": True,
            "codebook_frozen": False,
            "extra_precision_channel": True,
            "task_specific_decoder_rewrite": True,
            "zero_error": True,
        })
        self.assertTrue(any("codebook" in e for e in errors))
        self.assertTrue(any("extra precision" in e for e in errors))
        self.assertTrue(any("decoder rewrite" in e for e in errors))


class UpdateChannelControls(unittest.TestCase):
    def test_two_binary_updates_reach_at_most_four_targets(self):
        self.assertEqual(mod.update_transcript_capacity(2, 2), 4)
        self.assertFalse(mod.update_channel_allows(5, 2, 2))
        self.assertTrue(mod.update_channel_allows(4, 2, 2))
        self.assertEqual(mod.minimum_update_steps(5, 2), 3)

    def test_exhaustive_decoder_boundary(self):
        self.assertFalse(mod.exhaustive_update_decoder_covers(5, 2, 2))
        self.assertTrue(mod.exhaustive_update_decoder_covers(4, 2, 2))

    def test_single_update_symbol_cannot_select_multiple_targets(self):
        with self.assertRaises(ValueError):
            mod.minimum_update_steps(2, 1)

    def test_bypass_channels_rejected_by_scope(self):
        errors = mod.validate_update_scope({
            "fixed_initial_state": True,
            "direct_write": True,
            "external_memory_mutation": True,
            "target_correlated_side_channel": True,
            "architecture_growth": True,
            "deterministic": True,
            "zero_error": True,
        })
        self.assertTrue(any("direct write" in e for e in errors))
        self.assertTrue(any("external memory" in e for e in errors))
        self.assertTrue(any("side channel" in e for e in errors))
        self.assertTrue(any("architecture growth" in e for e in errors))


class ProtectedRankControls(unittest.TestCase):
    def test_rank_nullity_frontier_is_exact(self):
        protected = [[1, 0, 0], [0, 1, 0]]
        self.assertEqual(mod.matrix_rank(protected), 2)
        self.assertEqual(mod.protected_nullity(protected, 3), 1)
        self.assertTrue(mod.protected_frontier_allows(protected, 3, 1))
        self.assertFalse(mod.protected_frontier_allows(protected, 3, 2))

    def test_redundant_protected_rows_do_not_consume_extra_rank(self):
        protected = [[1, 0, 0], [2, 0, 0]]
        self.assertEqual(mod.matrix_rank(protected), 1)
        self.assertEqual(mod.protected_nullity(protected, 3), 2)

    def test_exact_fraction_rank_avoids_float_tolerance(self):
        protected = [[1, 1, 0], [2, 2, 0], [0, 0, 1]]
        self.assertEqual(mod.matrix_rank(protected), 2)

    def test_nonlinear_or_growing_scope_rejected(self):
        errors = mod.validate_protected_rank_scope({
            "linear_protected_map": False,
            "fixed_parameter_dim": False,
            "auxiliary_mutable_state": True,
            "architecture_growth": True,
            "exact_retention": True,
        })
        self.assertTrue(any("linear protected-output" in e for e in errors))
        self.assertTrue(any("dimension must be fixed" in e for e in errors))
        self.assertTrue(any("auxiliary mutable state" in e for e in errors))
        self.assertTrue(any("architecture growth" in e for e in errors))

    def test_bad_matrix_shape_rejected(self):
        with self.assertRaises(ValueError):
            mod.protected_nullity([[1, 0], [0, 1]], 3)


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


class AcquisitionControls(unittest.TestCase):
    def test_binary_transcript_capacity(self):
        self.assertEqual(mod.acquisition_transcript_capacity(2, 2), 4)
        self.assertFalse(mod.acquisition_allows(5, 2, 2))
        self.assertTrue(mod.acquisition_allows(4, 2, 2))

    def test_minimum_queries(self):
        self.assertEqual(mod.minimum_queries(1, 2), 0)
        self.assertEqual(mod.minimum_queries(5, 2), 3)
        self.assertEqual(mod.minimum_queries(9, 3), 2)

    def test_uniform_cost_budget(self):
        self.assertEqual(mod.max_queries_from_budget(5, 2), 2)
        self.assertEqual(mod.acquisition_budget_capacity(2, 5, 2), 4)
        self.assertEqual(mod.acquisition_budget_capacity(3, 6, 2), 27)

    def test_exhaustive_code_boundary(self):
        self.assertFalse(mod.exhaustive_separating_code_exists(5, 2, 2))
        self.assertTrue(mod.exhaustive_separating_code_exists(4, 2, 2))

    def test_one_outcome_query_cannot_identify_multiple(self):
        with self.assertRaises(ValueError):
            mod.minimum_queries(2, 1)

    def test_side_channels_and_noise_change_scope(self):
        errors = mod.validate_acquisition_scope({
            "deterministic": False,
            "noiseless": False,
            "bounded_outcome_alphabet": False,
            "free_side_information": True,
            "passive_target_information": True,
            "zero_error": False,
        })
        self.assertEqual(len(errors), 6)


class SocialIdentifiabilityControls(unittest.TestCase):
    def setUp(self):
        self.base, self.heldout, self.diagnostic = mod.social_witness()

    def test_colliding_models_with_different_response_are_not_identifiable(self):
        self.assertFalse(mod.social_response_identifiable(self.base, self.heldout))
        self.assertFalse(mod.exhaustive_social_decoder_exists(self.base, self.heldout))

    def test_diagnostic_probe_restores_identifiability(self):
        self.assertTrue(mod.social_response_identifiable(self.diagnostic, self.heldout))
        self.assertTrue(mod.exhaustive_social_decoder_exists(self.diagnostic, self.heldout))
        self.assertTrue(mod.social_model_identifiable(self.diagnostic))

    def test_full_model_identity_requires_injective_transcript(self):
        self.assertFalse(mod.social_model_identifiable(self.base))
        self.assertEqual(mod.social_transcript_class_count(self.base), 2)
        self.assertEqual(mod.social_transcript_class_count(self.diagnostic), 3)

    def test_response_can_be_identifiable_without_model_identity(self):
        same_response = {
            "goal_left": "same",
            "belief_blocked": "same",
            "goal_stay": "other",
        }
        self.assertFalse(mod.social_model_identifiable(self.base))
        self.assertTrue(mod.social_response_identifiable(self.base, same_response))
        self.assertTrue(mod.exhaustive_social_decoder_exists(self.base, same_response))

    def test_domain_mismatch_rejected(self):
        with self.assertRaises(ValueError):
            mod.social_response_identifiable({"m0": "t"}, {"m1": "r"})

    def test_private_access_and_unregistered_probe_change_scope(self):
        errors = mod.validate_social_scope({
            "hidden_model_label_visible": True,
            "private_state_access": True,
            "unregistered_later_probe": True,
            "deterministic_behavior": False,
            "zero_error": False,
        })
        self.assertEqual(len(errors), 5)


class EndToEndControls(unittest.TestCase):
    def test_run_passes(self):
        result = mod.run()
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["claim_ceiling"], "G2")
        self.assertEqual(result["ceiling_ids"], list(mod.EXPECTED_IDS))
        self.assertTrue(all(result["checks"].values()))


if __name__ == "__main__":
    unittest.main()
