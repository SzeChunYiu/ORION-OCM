import importlib.util
import pathlib
import unittest

HERE = pathlib.Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "run_gmi_operational_closure_v1", HERE / "run_gmi_operational_closure_v1.py"
)
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)


class OperationalClosureV1Tests(unittest.TestCase):
    def test_rv135(self):
        r = MOD.rv135()
        self.assertTrue(r["all_checks_green"])
        self.assertEqual(r["observed_capability"], r["predicted_capability"])

    def test_rv136(self):
        r = MOD.rv136()
        self.assertTrue(r["all_checks_green"])
        self.assertEqual(r["example"]["observed_capability"], r["example"]["predicted_capability"])

    def test_rv137(self):
        r = MOD.rv137()
        self.assertTrue(r["all_checks_green"])
        self.assertEqual(r["conditional_top_k_checks"], 540)

    def test_rv138(self):
        r = MOD.rv138()
        self.assertTrue(r["all_checks_green"])
        self.assertGreater(r["top_k_posterior_checks"], 1000)

    def test_neural_compiler(self):
        r = MOD.neural_compile_check()
        self.assertTrue(r["all_checks_green"])
        self.assertEqual(r["trace_checks"], 192)

    def test_finite_frontier(self):
        r = MOD.finite_operational_closure_check()
        self.assertTrue(r["all_checks_green"])
        self.assertEqual(r["best_accuracy"], "3/4")


if __name__ == "__main__":
    unittest.main()
