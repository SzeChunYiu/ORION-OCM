"""Replay foundation mathematics and original governance without promotion."""
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def load(name):
    spec = importlib.util.spec_from_file_location(name, HERE / (name + ".py"))
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def evaluate():
    load("semantic_v9")
    audit = load("r0_audit_v9")
    r0 = audit.evaluate(ROOT)
    load("independent_semantic_v9")
    math_tests = load("test_semantic_v9")
    audit_tests = load("test_r0_audit_v9")
    review_tests = load("test_independent_review_v9")
    suite = unittest.TestSuite(
        unittest.defaultTestLoader.loadTestsFromModule(module)
        for module in (math_tests, audit_tests, review_tests))
    result = unittest.TextTestRunner(verbosity=1).run(suite)
    if not result.wasSuccessful() or result.testsRun == 0:
        raise ValueError("verification failed or no tests collected")
    files = sorted(p for p in HERE.iterdir() if p.is_file()
                   and p.name != "RESULT_V9.json"
                   and p.suffix in {".py", ".md", ".lean", ".json"})
    return {
        "schema": "GMI_1068_FOUNDATION_RECOVERY_V9",
        "tests_run": result.testsRun,
        "semantic_coverage": math_tests.COVERAGE,
        "independent_audit_coverage": review_tests.COVERAGE,
        "r0": r0,
        "inputs": {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in files},
        "overall_closure": "OPEN",
        "scientific_truth_certified": False,
        "claim_boundaries": [
            "only original eight R0 governance requirements are candidates for closure",
            "semantic independence is relative to the declared model/reduct class",
            "shared ambient typed histories prevent evaluator-domain leakage",
            "invertible presentation transport does not establish primitive-count minimality",
            "classical decoder existence is not a generally effective learning method",
            "no novel empirical prediction or all-family derivation is claimed",
        ],
    }


def main():
    value = evaluate()
    encoded = json.dumps(value, indent=2, sort_keys=True) + "\n"
    if sys.argv[1:] == ["--write"]:
        (HERE / "RESULT_V9.json").write_text(encoded)
    elif sys.argv[1:]:
        raise ValueError("only --write is accepted")
    elif (HERE / "RESULT_V9.json").read_text() != encoded:
        raise ValueError("receipt drift")
    print(encoded, end="")


if __name__ == "__main__":
    try:
        main()
    except OSError as exc:
        print("CANNOT_CHECK:" + str(exc), file=sys.stderr)
        sys.exit(2)
    except RuntimeError as exc:
        audit = sys.modules.get("r0_audit_v9")
        if audit is None or not isinstance(exc, audit.CannotCheck):
            raise
        print("CANNOT_CHECK:" + str(exc), file=sys.stderr)
        sys.exit(2)
    except ValueError as exc:
        print("CHECKED_INVALID:" + str(exc), file=sys.stderr)
        sys.exit(1)
