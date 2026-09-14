import importlib.util
import itertools
import json
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("capability_perturbations_v1", ROOT / "capability_perturbations_v1.py")
mod = importlib.util.module_from_spec(SPEC)
if SPEC.loader is None:
    raise RuntimeError("cannot load perturbation module")
SPEC.loader.exec_module(mod)


class PerturbationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.protocol = json.loads((ROOT / "PERTURBATION_PROTOCOL_V1.json").read_text())
        cls.predictor = mod.build_predictor()

    def test_claim_gate_metadata(self):
        for field in ("scope", "assumptions", "evidence_class", "claim_ceiling", "strongest_parent", "negative_twin", "nearest_counterexample", "falsifier", "status"):
            self.assertTrue(self.protocol[field], field)
        self.assertEqual("G2", self.protocol["claim_ceiling"])
        self.assertEqual(6, len(self.protocol["cases"]))
        self.assertIn("Calibrate uncertainty / abstention when capability is not identifiable.", self.protocol["ledger_rows"])

    def test_all_registered_cases_match_transform_predictor_and_oracle(self):
        for case in self.protocol["cases"]:
            before = case["before"]
            params = case["parameters"]
            if case["kind"] == "resource_repricing":
                after = mod.apply_repricing(before, params["axis"], spend=params["spend"], old_price=params["old_price"], new_price=params["new_price"], requirement=params["requirement"])
            elif case["kind"] == "ablation":
                after = mod.ablate(before, params["axis"], params["removed_capacity"])
            elif case["kind"] == "environmental_drift":
                after = mod.drift_requirement(before, params["axis"], params["added_requirement"])
            else:
                self.fail(case["kind"])
            self.assertEqual(case["after"], after, case["id"])
            target = case["target"]
            self.assertEqual(case["expected_target_before"], self.predictor.predict_one(before, target), case["id"])
            self.assertEqual(case["expected_target_after"], self.predictor.predict_one(after, target), case["id"])
            self.assertEqual(case["expected_target_before"], mod.capability_oracle(before)[target], case["id"])
            self.assertEqual(case["expected_target_after"], mod.capability_oracle(after)[target], case["id"])

    def test_repricing_floor_law_and_negative_twin(self):
        self.assertEqual((0, -1), mod.reprice_margin(spend=6, old_price=2, new_price=3, requirement=3))
        self.assertEqual((1, 0), mod.reprice_margin(spend=9, old_price=2, new_price=3, requirement=3))

    def test_ablation_and_drift_are_margin_subtractions(self):
        base = {axis: 1 for axis in mod.AXES}
        self.assertEqual(-1, mod.ablate(base, "memory_margin", 2)["memory_margin"])
        self.assertEqual(-2, mod.drift_requirement(base, "planning_margin", 3)["planning_margin"])

    def test_abstention_has_exact_no_witness_certificate(self):
        point = {
            "memory_margin": 2,
            "planning_margin": -2,
            "communication_margin": 0,
            "routing_margin": 0,
            "verification_margin": 0,
        }
        cert = mod.identification_certificate(point, "planning_exact")
        self.assertFalse(cert["positive_below_witness_exists"])
        self.assertFalse(cert["negative_above_witness_exists"])
        self.assertEqual(mod.CANNOT_IDENTIFY, cert["prediction"])
        self.assertEqual(mod.CANNOT_IDENTIFY, self.predictor.predict_one(point, "planning_exact"))
        # The exact oracle is deliberately hidden from fitting; abstention is not
        # scored as a mistake merely because the oracle happens to be 0.
        self.assertEqual(0, mod.capability_oracle(point)["planning_exact"])

    def test_abstention_calibration_exhaustive_probe_grid(self):
        # 3^5 = 243 probe points, including values outside the development cube.
        # The certificate must match the predictor exactly; determinate outputs
        # must agree with the independent exact oracle.
        for values in itertools.product((-2, 0, 2), repeat=len(mod.AXES)):
            point = dict(zip(mod.AXES, values))
            truth = mod.capability_oracle(point)
            for target in mod.TARGETS:
                cert = mod.identification_certificate(point, target)
                prediction = self.predictor.predict_one(point, target)
                self.assertEqual(cert["prediction"], prediction, (point, target))
                if prediction == mod.CANNOT_IDENTIFY:
                    self.assertFalse(cert["positive_below_witness_exists"])
                    self.assertFalse(cert["negative_above_witness_exists"])
                else:
                    self.assertEqual(truth[target], prediction, (point, target))

    def test_invalid_parameters_refused(self):
        with self.assertRaises(ValueError):
            mod.reprice_margin(spend=1, old_price=0, new_price=1, requirement=0)
        base = {axis: 0 for axis in mod.AXES}
        with self.assertRaises(ValueError):
            mod.ablate(base, "memory_margin", -1)
        with self.assertRaises(ValueError):
            mod.drift_requirement(base, "unknown", 1)
        with self.assertRaises(ValueError):
            mod.identification_certificate(base, "unknown_target")
        bad = dict(base)
        bad["memory_margin"] = True
        with self.assertRaises(ValueError):
            mod.capability_oracle(bad)


if __name__ == "__main__":
    unittest.main()
