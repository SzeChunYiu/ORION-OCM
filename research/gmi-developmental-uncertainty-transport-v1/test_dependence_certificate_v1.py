import importlib.util
import json
from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("dep", HERE / "dependence_certificate_v1.py")
MOD = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MOD
SPEC.loader.exec_module(MOD)


class DependenceCertificateTests(unittest.TestCase):
    def test_certificate_reproduces_committed_json(self):
        committed = json.loads((HERE / "DEPENDENCE_CERTIFICATE_V1.json").read_text())
        self.assertEqual(MOD.build_certificate(), committed)

    def test_union_bound_is_tight_without_independence(self):
        cert = MOD.build_certificate()
        self.assertEqual(cert["actual_joint_good_probability"], "187/200")
        self.assertEqual(cert["union_bound_good_lower_bound"], "187/200")
        self.assertTrue(cert["bound_is_tight"])
        self.assertFalse(cert["independence_used"])
        self.assertFalse(cert["success_events_are_independent"])
        self.assertNotEqual(cert["actual_joint_good_probability"], cert["product_if_independent"])

    def test_registered_failure_sum_matches_union_failure(self):
        cert = MOD.build_certificate()
        self.assertTrue(cert["failure_sets_pairwise_disjoint"])
        self.assertEqual(cert["sum_registered_failure_budgets"], "13/200")
        self.assertEqual(cert["union_failure_probability"], "13/200")


if __name__ == "__main__":
    unittest.main()
