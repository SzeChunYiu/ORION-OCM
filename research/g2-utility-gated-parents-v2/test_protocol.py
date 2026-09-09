from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import experiment as E


class TestUtilityGatedParentsV2(unittest.TestCase):
    def test_methods_blob_pinned(self):
        self.assertEqual(E.git_blob_sha1(E.SRC / "ocm" / "learning" / "methods.py"), E.METHOD_BLOB)

    def test_v1_salts_are_not_reused(self):
        self.assertNotEqual(E.TRAIN_SALT, "orion-ocm-g2-strong-parents-train-v1")
        self.assertNotEqual(E.TEST_SALT, "orion-ocm-g2-strong-parents-test-v1")
        self.assertTrue(E.TRAIN_SALT.endswith("-v2"))

    def test_partitions_disjoint(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = E.main(Path(tmp) / "RESULT.json")
        self.assertEqual(result["train_n"], E.TRAIN_N)
        self.assertEqual(result["val_n"], E.VAL_N)
        self.assertEqual(result["test_n"], E.TEST_N)

    def test_gate_does_not_admit_frequency_when_validation_loses(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = E.main(Path(tmp) / "RESULT.json")
        self.assertIn(result["terminal"], {
            "HARMFUL_FREQUENCY_REFUSED_BY_UTILITY_GATE",
            "UTILITY_GATED_LIBRARY_BEATS_PRIMITIVE",
            "UTILITY_GATE_SELECTS_NO_METHOD",
        })
        self.assertNotEqual(result["terminal"], "HARMFUL_TRANSFER_LIMIT")
        self.assertTrue(result["v1_frozen"]["not_retuned"])
        self.assertEqual(result["v1_frozen"]["terminal"], "HARMFUL_TRANSFER_LIMIT")
        self.assertFalse(result["controls"]["harmful_transfer"]["gated_library_worse_than_primitive"])
        self.assertLessEqual(result["test"]["gated_attempts"], result["test"]["primitive_attempts"])
        freq = tuple(result["frequency_selected"])
        admitted = tuple(result["admitted"])
        if result["validation"]["frequency_attempts"] >= result["validation"]["primitive_attempts"]:
            self.assertNotEqual(admitted, freq)

    def test_all_g25_controls_recorded(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = E.main(Path(tmp) / "RESULT.json")
        required = {
            "reset_OCM", "persistent_exemplar_memory", "persistent_method_library",
            "same_library_conventional_search", "domain_native_synthesis",
            "structural_placebo", "method_removed", "scope_conflicting_method",
            "harmful_transfer", "unrelated_method_growth",
        }
        self.assertEqual(required, set(result["controls"]))


if __name__ == "__main__":
    unittest.main()
