"""Exact and hostile controls for #602 F2 capability ceilings, tranches 1-2."""

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
        self.assertEqual(len(mod.EXPECTED_IDS), 6)

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


class EndToEndControls(unittest.TestCase):
    def test_run_passes(self):
        result = mod.run()
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["claim_ceiling"], "G2")
        self.assertEqual(result["ceiling_ids"], list(mod.EXPECTED_IDS))
        self.assertTrue(all(result["checks"].values()))


if __name__ == "__main__":
    unittest.main()
