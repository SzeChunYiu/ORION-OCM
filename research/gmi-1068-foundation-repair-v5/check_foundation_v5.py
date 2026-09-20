"""Replay finite repair evidence; hashes establish custody, not theorem truth."""
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parent


def load(name):
    spec = importlib.util.spec_from_file_location(name, HERE / (name + ".py"))
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def evaluate():
    load("foundation_v5")
    load("independent_oracle_v5")
    tests = load("test_foundation_v5")
    suite = unittest.defaultTestLoader.loadTestsFromModule(tests)
    result = unittest.TextTestRunner(verbosity=1).run(suite)
    if not result.wasSuccessful() or result.testsRun == 0:
        raise ValueError("finite verification failed or no tests collected")
    files = sorted(p for p in HERE.iterdir()
                   if p.is_file() and p.name not in {"RESULT_V5.json"}
                   and p.suffix in {".py", ".md", ".lean", ".json"})
    return {
        "schema": "GMI_1068_FOUNDATION_REPAIR_V5",
        "scope": "CONDITIONAL_ADMISSIBILITY_AND_DECLARED_AGGREGATION",
        "tests_run": result.testsRun,
        "finite_coverage": tests.COVERAGE,
        "overall_closure": "OPEN",
        "scientific_truth_certified": False,
        "inputs": {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in files},
        "claim_boundaries": [
            "finite replay does not prove universal theorems",
            "Lean kernel check is a separate CI step",
            "resource-state lifting assumes additive nonnegative costs",
            "scalar objective does not require a probability prior",
            "R0-R17 whole-round closure remains unearned",
        ],
    }


if __name__ == "__main__":
    value = evaluate()
    encoded = json.dumps(value, indent=2, sort_keys=True) + "\n"
    if sys.argv[1:] == ["--write"]:
        (HERE / "RESULT_V5.json").write_text(encoded)
    elif sys.argv[1:]:
        raise ValueError("only --write is accepted")
    elif (HERE / "RESULT_V5.json").read_text() != encoded:
        raise ValueError("receipt drift")
    print(encoded, end="")
