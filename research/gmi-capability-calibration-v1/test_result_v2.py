from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


RESULT = load("capability_calibration_result_v2", HERE / "result_v2.py")


class ResultV2ReplayTests(unittest.TestCase):
    def test_result_reproduces_committed_object(self):
        committed = json.loads((HERE / "RESULT_V2.json").read_text())
        self.assertEqual(RESULT.build_result(), committed)

    def test_claim_ceiling_stays_bounded(self):
        result = RESULT.build_result()
        self.assertEqual(
            result["claim_ceiling"],
            "EXACT_FINITE_POPULATION_CAPABILITY_ERROR_CALIBRATION_AT_REGISTERED_SCOPE",
        )
        self.assertEqual(
            result["section_m_disposition"],
            "CALIBRATE_CAPABILITY_PREDICTION_UNCERTAINTY_SUPPORTED_AT_REGISTERED_FINITE_SCOPE",
        )
        self.assertIn("IID_GENERALIZATION", result["nonclaims"])
        self.assertIn("REAL_WORLD_CAPABILITY_CALIBRATION", result["nonclaims"])
        self.assertIn("COMPLETE_GMI", result["nonclaims"])

    def test_v1_failure_remains_visible(self):
        result = RESULT.build_result()
        self.assertEqual(
            result["v1_disposition"],
            "CANNOT_EXECUTE_FROZEN_SAMPLE_DETERMINATE_POPULATION_TOO_SMALL",
        )
        self.assertTrue(result["v1_outcome_free_sample_preserved_but_invalid"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
