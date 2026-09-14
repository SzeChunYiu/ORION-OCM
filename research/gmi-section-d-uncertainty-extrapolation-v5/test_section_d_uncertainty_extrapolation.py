import importlib.util
import json
import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parent


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    if spec.loader is None:
        raise RuntimeError(f"unable to load {path}")
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


v5 = load_module("v5", ROOT / "section_d_uncertainty_extrapolation_witness.py")
training = load_module("v5_training", ROOT / "training_measure_v5.py")


class SectionDV5Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.r = v5.build_results()

    def test_all_frozen_predictions(self):
        self.assertTrue(self.r["all_frozen_predictions_pass"])
        self.assertTrue(all(self.r["assertions"].values()))
        self.assertEqual(self.r["authority"]["stage1_freeze_commit"], "ab231d78aae98beb679ca0e0ce8c36c4651dc438")
        self.assertEqual(self.r["authority"]["stage2_freeze_commit"], "0a153e972dd920f61f394ce117d5dfa189ad964f")

    def test_uncertainty_localizes_only_with_full_sample(self):
        u = self.r["uncertainty"]
        full = u["full_sample"]
        small = u["small_sample_negative_control"]
        self.assertEqual(u["sample_custody"]["ones_count"], 14369)
        self.assertEqual(u["sample_custody"]["first_64_ones_count"], 58)
        self.assertEqual(full["possible_first_strict_integer_switches"], [4])
        self.assertEqual(full["q_interval"]["lo"], {"numerator": 65536, "denominator": 19299})
        self.assertEqual(full["q_interval"]["hi"], {"numerator": 65536, "denominator": 17763})
        self.assertEqual(small["possible_first_strict_integer_switches"], [3, 4, 5, 6, 7, 8, 9])
        self.assertEqual(small["q_interval"]["lo"], {"numerator": 8, "denominator": 3})
        self.assertEqual(small["q_interval"]["hi"], {"numerator": 128, "denominator": 15})
        self.assertTrue(full["failure_bound_lt_0_001"])
        self.assertTrue(small["failure_bound_lt_0_001"])

    def test_training_fit_is_tiny_only_and_affine(self):
        self.assertEqual(training.TRAINING_SIZES, (2, 3, 4, 5))
        with self.assertRaises(ValueError):
            training.measure(17)
        fits = self.r["extrapolation"]["fits"]
        expected = {
            "persistent_cells_single_orientation": (1, 0),
            "migration_ops": (2, 0),
            "key_block_ops": (4, 3),
            "value_block_ops": (3, 4),
        }
        for name, (a, b) in expected.items():
            self.assertEqual((fits[name]["a"], fits[name]["b"]), (a, b))
            self.assertEqual(fits[name]["validation_residuals"], {"4": 0, "5": 0})
            self.assertTrue(fits[name]["matches_second_freeze"])

    def test_n17_out_of_scale_prediction(self):
        h = self.r["extrapolation"]["holdouts"]["17"]
        self.assertTrue(h["zero_tolerance_match"])
        self.assertTrue(h["remint_counts_match"])
        self.assertTrue(h["remint_exact"])
        self.assertEqual(h["observed"]["key_checks"], 34)
        self.assertEqual(h["observed"]["value_checks"], 34)
        self.assertEqual(h["observed_crossover"]["continuous_crossover"], {"numerator": 17, "denominator": 8})
        self.assertEqual(h["observed_crossover"]["first_strict_migration_horizon"], 3)
        self.assertLess(h["observed_crossover"]["m2_stay_key"], h["observed_crossover"]["m2_migrate_value"])
        self.assertLess(h["observed_crossover"]["m3_migrate_value"], h["observed_crossover"]["m3_stay_key"])

    def test_n31_out_of_scale_prediction(self):
        h = self.r["extrapolation"]["holdouts"]["31"]
        self.assertTrue(h["zero_tolerance_match"])
        self.assertTrue(h["remint_counts_match"])
        self.assertTrue(h["remint_exact"])
        self.assertEqual(h["observed"]["key_checks"], 62)
        self.assertEqual(h["observed"]["value_checks"], 62)
        self.assertEqual(h["observed_crossover"]["continuous_crossover"], {"numerator": 31, "denominator": 15})
        self.assertEqual(h["observed_crossover"]["first_strict_migration_horizon"], 3)
        self.assertLess(h["observed_crossover"]["m2_stay_key"], h["observed_crossover"]["m2_migrate_value"])
        self.assertLess(h["observed_crossover"]["m3_migrate_value"], h["observed_crossover"]["m3_stay_key"])

    def test_hostile_prediction_mutation_fails_closed(self):
        obs = v5.measure_holdout(17, False)
        hostile = dict(v5.FROZEN_HOLDOUT[17])
        hostile["migration_ops"] += 1
        self.assertFalse(v5.compare_observation_to_frozen(obs, 17, hostile))
        self.assertTrue(v5.compare_observation_to_frozen(obs, 17))

    def test_raw_sample_custody(self):
        meta, bits = v5.unpack_sample()
        self.assertEqual(len(bits), 16384)
        self.assertEqual(sum(bits), 14369)
        self.assertEqual(sum(bits[:64]), 58)
        self.assertEqual(meta["packed_sha256"], "736e589ddcd23903820bbb12b30ccc5b5deb7f6ff377ca0b604db1f4b5c22540")

    def test_committed_receipt_reproduces(self):
        committed = json.loads((ROOT / "RESULT_V5.json").read_text(encoding="utf-8"))
        self.assertEqual(committed, self.r)


if __name__ == "__main__":
    unittest.main()
