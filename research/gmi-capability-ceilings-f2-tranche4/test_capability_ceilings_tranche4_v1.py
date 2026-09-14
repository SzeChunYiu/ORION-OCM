"""Exact and hostile controls for #602 F2 tranche 4."""

from pathlib import Path
import copy
import importlib.util
import unittest

path = Path(__file__).with_name("capability_ceilings_tranche4_v1.py")
spec = importlib.util.spec_from_loader("f2_tranche4_checked", loader=None)
mod = importlib.util.module_from_spec(spec)
mod.__file__ = str(path)
exec(compile(path.read_bytes(), str(path), "exec"), mod.__dict__)


class RegistryControls(unittest.TestCase):
    def test_registry_exact_and_valid(self):
        self.assertEqual(mod.validate_registry(), [])
        self.assertEqual(len(mod.EXPECTED_IDS), 2)

    def test_missing_row_rejected(self):
        data = copy.deepcopy(mod.load_registry())
        data["ceilings"].pop()
        self.assertTrue(any("id/order mismatch" in e for e in mod.validate_registry(data)))

    def test_claim_escalation_rejected(self):
        data = copy.deepcopy(mod.load_registry())
        data["claim_ceiling"] = "G6"
        self.assertTrue(any("claim ceiling must be G2" in e for e in mod.validate_registry(data)))

    def test_empty_parent_rejected(self):
        data = copy.deepcopy(mod.load_registry())
        data["ceilings"][1]["strongest_parent"] = ""
        self.assertTrue(any("empty strongest_parent" in e for e in mod.validate_registry(data)))


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
