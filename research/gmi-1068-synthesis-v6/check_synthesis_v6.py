"""Replay generated witnesses, independent tests and source-bound evidence."""
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
    synthesis = load("synthesis_v6")
    machine = load("machine_v6")
    load("independent_oracle_v6")
    load("score_intervals_v6")
    tests, scores = load("test_synthesis_v6"), load("test_score_v6")
    suite = unittest.TestSuite(unittest.defaultTestLoader.loadTestsFromModule(m)
                               for m in (tests, scores))
    result = unittest.TextTestRunner(verbosity=1).run(suite)
    if not result.wasSuccessful() or result.testsRun == 0:
        raise ValueError("replay failed or no tests collected")
    stats = {}
    candidates = synthesis.synthesize(stats=stats)
    synthesis.validate_certificate(candidates)
    witnesses = {
        str(k): {"ast": v["ast"], "cost": v["cost"],
                 "program": machine.compile_ast(v["ast"])}
        for k, v in sorted(candidates.items())
    }
    files = sorted(p for p in HERE.iterdir() if p.is_file()
                   and p.name != "RESULT_V6.json"
                   and p.suffix in {".py", ".md", ".lean", ".json"})
    return {
        "schema": "GMI_1068_CONSTRUCTIVE_SYNTHESIS_V6",
        "scope": "BINARY_BOOLEAN_AST_SYNTHESIS_AND_STACK_COMPILATION",
        "tests_run": result.testsRun,
        "finite_coverage": tests.COVERAGE,
        "score_coverage": scores.COVERAGE,
        "search_operations": stats,
        "witnesses": witnesses,
        "inputs": {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in files},
        "overall_closure": "OPEN",
        "scientific_truth_certified": False,
        "claim_boundaries": [
            "exact finite Boolean instance; no neural architecture recovery",
            "general compiler and certificate schemas kernel checked separately",
            "Python implementation correspondence is tested, not kernel proved",
            "node cost excludes search and compilation acquisition costs",
            "no claim of probability-free or assumption-free universal optimality",
        ],
    }


if __name__ == "__main__":
    value = evaluate()
    encoded = json.dumps(value, indent=2, sort_keys=True) + "\n"
    if sys.argv[1:] == ["--write"]:
        (HERE / "RESULT_V6.json").write_text(encoded)
    elif sys.argv[1:]:
        raise ValueError("only --write is accepted")
    elif (HERE / "RESULT_V6.json").read_text() != encoded:
        raise ValueError("receipt drift")
    print(encoded, end="")
