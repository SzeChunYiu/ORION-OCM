"""A missing experiment or corrupted counter must block adjudication."""
from copy import deepcopy
import unittest
import coverage_v11 as guard

COVERAGE = {}


class CoverageTests(unittest.TestCase):
    def test_omissions_and_corruptions(self):
        baseline = deepcopy(guard.REQUIRED)
        self.assertTrue(guard.validate_coverage(baseline))
        rejected = 0
        for module in baseline:
            bad = deepcopy(baseline)
            del bad[module]
            with self.assertRaises(ValueError):
                guard.validate_coverage(bad)
            rejected += 1
            for key, value in baseline[module].items():
                for mutation in (value + 1, True, None, "missing"):
                    bad = deepcopy(baseline)
                    if mutation == "missing":
                        del bad[module][key]
                    else:
                        bad[module][key] = mutation
                    with self.assertRaises(ValueError):
                        guard.validate_coverage(bad)
                    rejected += 1
        bad = deepcopy(baseline)
        bad["undeclared_experiment"] = {}
        with self.assertRaises(ValueError):
            guard.validate_coverage(bad)
        rejected += 1
        COVERAGE["coverage_guard_rejections"] = rejected


if __name__ == "__main__":
    unittest.main()
