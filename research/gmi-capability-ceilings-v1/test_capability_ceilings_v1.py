"""Exact and hostile controls for #602 F2 capability-ceiling tranche 1."""

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
        self.assertEqual(len(mod.EXPECTED_IDS), 3)

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


class EndToEndControls(unittest.TestCase):
    def test_run_passes(self):
        result = mod.run()
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["claim_ceiling"], "G2")
        self.assertEqual(result["ceiling_ids"], list(mod.EXPECTED_IDS))
        self.assertTrue(all(result["checks"].values()))


if __name__ == "__main__":
    unittest.main()
