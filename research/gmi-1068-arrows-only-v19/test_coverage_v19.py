"""No-alarm baseline and exact omission/type/count corruption controls."""
from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("coverage_v19", HERE / "coverage_v19.py")
guard = importlib.util.module_from_spec(spec)
spec.loader.exec_module(guard)
COVERAGE = {}


class CoverageTests(unittest.TestCase):
    def test_omissions_aliases_and_corruptions(self):
        baseline = deepcopy(guard.REQUIRED)
        self.assertTrue(guard.validate_coverage(baseline))
        rejected = 0
        for module in baseline:
            bad = deepcopy(baseline)
            del bad[module]
            with self.assertRaises(ValueError):
                guard.validate_coverage(bad)
            rejected += 1
            bad = deepcopy(baseline)
            bad[module]["unexpected_counter"] = 1
            with self.assertRaises(ValueError):
                guard.validate_coverage(bad)
            rejected += 1
            for key, value in baseline[module].items():
                for mutation in (value + 1, True, None, float(value), "delete"):
                    bad = deepcopy(baseline)
                    if mutation == "delete":
                        del bad[module][key]
                    else:
                        bad[module][key] = mutation
                    with self.subTest(module=module, key=key, value=mutation), self.assertRaises(ValueError):
                        guard.validate_coverage(bad)
                    rejected += 1
        bad = deepcopy(baseline)
        bad["unexpected_experiment"] = {}
        with self.assertRaises(ValueError):
            guard.validate_coverage(bad)
        rejected += 1
        self.assertEqual(rejected, guard.REQUIRED["test_coverage_v19"]["coverage_guard_rejections"])
        self.assertEqual(baseline, guard.REQUIRED)
        COVERAGE["coverage_guard_rejections"] = rejected


if __name__ == "__main__":
    program = unittest.main(exit=False, verbosity=2)
    print(json.dumps(COVERAGE, sort_keys=True))
    raise SystemExit(not program.result.wasSuccessful())
