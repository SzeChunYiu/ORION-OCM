import importlib.util
import json
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("real_regime_v1", ROOT / "real_regime_v1.py")
mod = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(mod)


class RegistryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry = json.loads((ROOT / "REAL_REGIME_PROTOCOL_V1.json").read_text())

    def test_exact_four_domains(self):
        self.assertEqual(4, len(self.registry["domains"]))
        self.assertEqual(
            {
                "FACTUAL_SCIENCE_RETRIEVAL",
                "MATH_PROOF_CHAIN",
                "CODE_PATCH_VERIFICATION",
                "SENSOR_ACTUATOR_CONTROL",
            },
            {row["id"] for row in self.registry["domains"]},
        )

    def test_claim_gate_metadata(self):
        for field in (
            "scope",
            "assumptions",
            "evidence_class",
            "claim_ceiling",
            "strongest_parent",
            "negative_twin",
            "nearest_counterexample",
            "falsifier",
        ):
            self.assertTrue(self.registry[field], field)
        self.assertEqual("G3", self.registry["claim_ceiling"])


class ExecutableTaskTests(unittest.TestCase):
    def test_science_retrieval_threshold(self):
        self.assertTrue(mod.factual_science_task(0))
        self.assertFalse(mod.factual_science_task(-1))
        self.assertEqual("299792458", mod.SCIENCE_FACTS["speed_of_light_m_per_s"])

    def test_proof_threshold(self):
        self.assertTrue(mod.math_proof_task(0, 0))
        self.assertFalse(mod.math_proof_task(0, -1))
        self.assertFalse(mod.math_proof_task(-1, 0))

    def test_code_verifier_executes_candidates(self):
        self.assertTrue(mod.code_patch_task(0, 0))
        self.assertFalse(mod.code_patch_task(0, -1))
        self.assertFalse(mod.code_patch_task(-1, 0))

    def test_control_communication_threshold(self):
        self.assertTrue(mod.sensor_actuator_control_task(0))
        self.assertFalse(mod.sensor_actuator_control_task(-1))


class PredictorReplicationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry = json.loads((ROOT / "REAL_REGIME_PROTOCOL_V1.json").read_text())

    def test_every_positive_and_twin_is_determinate_and_correct(self):
        for row in self.registry["domains"]:
            positive = mod.evaluate_case(row["id"], row["target"], row["positive"])
            twin = mod.evaluate_case(row["id"], row["target"], row["negative_twin"])
            self.assertEqual(1, positive["prediction"], row["id"])
            self.assertEqual(1, positive["executable_truth"], row["id"])
            self.assertTrue(positive["agree"], row["id"])
            self.assertEqual(0, twin["prediction"], row["id"])
            self.assertEqual(0, twin["executable_truth"], row["id"])
            self.assertTrue(twin["agree"], row["id"])

    def test_twins_change_only_registered_load_bearing_axis(self):
        expected_axis = {
            "FACTUAL_SCIENCE_RETRIEVAL": "memory_margin",
            "MATH_PROOF_CHAIN": "planning_margin",
            "CODE_PATCH_VERIFICATION": "verification_margin",
            "SENSOR_ACTUATOR_CONTROL": "communication_margin",
        }
        for row in self.registry["domains"]:
            changed = {
                key
                for key in row["positive"]
                if row["positive"][key] != row["negative_twin"][key]
            }
            self.assertEqual({expected_axis[row["id"]]}, changed)

    def test_hidden_extra_margin_is_rejected(self):
        bad = dict(mod.BASE)
        bad["external_memory_margin"] = 100
        with self.assertRaises(ValueError):
            mod.executable_truth("FACTUAL_SCIENCE_RETRIEVAL", bad)

    def test_unknown_domain_is_rejected(self):
        with self.assertRaises(ValueError):
            mod.executable_truth("OPAQUE_UNKNOWN", mod.BASE)


if __name__ == "__main__":
    unittest.main()
