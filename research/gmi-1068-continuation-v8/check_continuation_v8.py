"""Replay frozen continuation tests and bind the exact package contents."""
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
    load("continuation_v8")
    load("independent_oracle_v8")
    tests = load("test_continuation_v8")
    suite = unittest.defaultTestLoader.loadTestsFromModule(tests)
    result = unittest.TextTestRunner(verbosity=1).run(suite)
    if not result.wasSuccessful() or result.testsRun == 0:
        raise ValueError("verification failed or no tests collected")
    files = sorted(p for p in HERE.iterdir() if p.is_file()
                   and p.name != "RESULT_V8.json"
                   and p.suffix in {".py", ".md", ".lean", ".json"})
    return {
        "schema": "GMI_1068_COMPLETE_CONTINUATION_V8",
        "scope": "DECLARED_DETERMINISTIC_PARTIAL_MACHINES_WITH_FULL_PREFIX_OBSERVATIONS",
        "tests_run": result.testsRun,
        "finite_coverage": tests.COVERAGE,
        "inputs": {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in files},
        "overall_closure": "OPEN",
        "scientific_truth_certified": False,
        "claim_boundaries": [
            "classical parent-owned behavioral minimization; no novelty claim",
            "Python is not extracted from Lean; correspondence is independently tested",
            "finite machines compute a quotient; no universal effective infinite-state algorithm",
            "edgewise observations include resource cost; cost erasure changes semantics",
            "resource-rejected and physically absent actions both count as not admitted",
            "known model input; no claim of learning the transition law from data",
        ],
    }


if __name__ == "__main__":
    value = evaluate()
    encoded = json.dumps(value, indent=2, sort_keys=True) + "\n"
    if sys.argv[1:] == ["--write"]:
        (HERE / "RESULT_V8.json").write_text(encoded)
    elif sys.argv[1:]:
        raise ValueError("only --write is accepted")
    elif (HERE / "RESULT_V8.json").read_text() != encoded:
        raise ValueError("receipt drift")
    print(encoded, end="")
