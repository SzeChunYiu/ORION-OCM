"""Replay prospective resource checks without scientific promotion."""
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
    for name in ("threshold_v10", "certificate_v10", "independent_oracle_v10"):
        load(name)
    guard = load("coverage_v10")
    modules = [load(name) for name in sorted(guard.REQUIRED)]
    suite = unittest.TestSuite(
        unittest.defaultTestLoader.loadTestsFromModule(module) for module in modules)
    result = unittest.TextTestRunner(verbosity=1).run(suite)
    if not result.wasSuccessful() or result.testsRun == 0:
        raise ValueError("verification failed or no tests collected")
    coverage = {module.__name__: getattr(module, "COVERAGE", {}) for module in modules}
    guard.validate_coverage(coverage)
    files = sorted(p for p in HERE.iterdir() if p.is_file()
                   and p.name != "RESULT_V10.json"
                   and p.suffix in {".py", ".md", ".lean", ".json"})
    return {
        "schema": "GMI_1068_RESOURCE_DISTINCTION_V10",
        "tests_run": result.testsRun,
        "coverage": coverage,
        "inputs": {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in files},
        "overall_closure": "OPEN",
        "scientific_truth_certified": False,
        "claim_boundaries": [
            "declared finite partial deterministic visible-cost model only",
            "classical parent-owned methods adapted, no priority claim",
            "mathematical consequences, not new empirical discovery",
            "exploratory diagnostics precede the expanded production check",
            "fixed known resource snapshot codes, not total online memory",
            "distinction resource is not directed transformation burden",
            "all 214 scientific obligations retain previous status",
        ],
    }


def main():
    value = evaluate()
    encoded = json.dumps(value, indent=2, sort_keys=True) + "\n"
    if sys.argv[1:] == ["--write"]:
        (HERE / "RESULT_V10.json").write_text(encoded)
    elif sys.argv[1:]:
        raise ValueError("only --write is accepted")
    elif (HERE / "RESULT_V10.json").read_text() != encoded:
        raise ValueError("receipt drift")
    print(encoded, end="")


if __name__ == "__main__":
    try:
        main()
    except OSError as exc:
        print("CANNOT_CHECK:" + str(exc), file=sys.stderr)
        sys.exit(2)
    except ValueError as exc:
        print("CHECKED_INVALID:" + str(exc), file=sys.stderr)
        sys.exit(1)
