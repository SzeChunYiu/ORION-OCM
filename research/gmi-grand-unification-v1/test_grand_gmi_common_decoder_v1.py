import importlib.util
import json
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "grand_gmi_common_decoder_checks_v1", HERE / "grand_gmi_common_decoder_checks_v1.py")
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)


class CommonDecoderTests(unittest.TestCase):
    def test_hidden_ecology_cannot_be_given_to_decoder(self):
        result = MOD.hidden_ecology_witness()
        self.assertFalse(result["oracle_jointly_attainable"])
        self.assertEqual(result["randomized_robust_minimum"], MOD.F(1, 2))

    def test_randomized_decoder_closure_is_load_bearing(self):
        result = MOD.deterministic_class_boundary()
        self.assertTrue(result["stochastic_garbling_requires_randomized_emulation"])

    def test_additive_receipt_reproduces_exact_hostile_checks(self):
        actual = json.loads(json.dumps(MOD.run(), default=MOD.json_value))
        expected = json.loads((HERE / "GRAND_GMI_COMMON_DECODER_RECEIPT_V1.json").read_text())
        self.assertEqual(actual, expected)
        self.assertEqual(actual["argmin_criterion"]["instances"], 2304)
        self.assertGreater(actual["argmin_criterion"]["oracle_envelope_unattainable_instances"], 0)
        self.assertEqual(actual["garbling"]["joint_profile_identities"], 6561)
        self.assertEqual(actual["convex_hull"]["decoder_mixture_identities"], 81)


if __name__ == "__main__":
    unittest.main()
