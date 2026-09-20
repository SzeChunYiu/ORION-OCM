"""Replay exact distribution-free decision evidence, preserving its assumptions."""
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
    decision = load("decision_v7")
    load("independent_oracle_v7")
    tests = load("test_decision_v7")
    suite = unittest.defaultTestLoader.loadTestsFromModule(tests)
    result = unittest.TextTestRunner(verbosity=1).run(suite)
    if not result.wasSuccessful() or result.testsRun == 0:
        raise ValueError("verification failed or no tests collected")
    losses, coarse, fine = ((0, 1), (1, 0), (0, 1)), (0, 0, 0), (0, 1, 0)
    before, after = decision.minimax(losses, coarse), decision.minimax(losses, fine)
    counterexample = decision.separation_witness((0, 0, 1), (0, 1, 1))
    witness_losses = counterexample["losses"]
    counterexample["fine_value"] = str(decision.minimax(witness_losses, (0, 0, 1))["value"])
    counterexample["coarse_value"] = str(decision.minimax(witness_losses, (0, 1, 1))["value"])
    files = sorted(p for p in HERE.iterdir() if p.is_file()
                   and p.name != "RESULT_V7.json"
                   and p.suffix in {".py", ".md", ".lean", ".json"})
    return {
        "schema": "GMI_1068_DETERMINISTIC_INFORMATION_ORDER_V7",
        "scope": "DECLARED_WORLDS_ACTIONS_LOSSES_SIGNALS_AND_POLICIES",
        "tests_run": result.testsRun,
        "finite_coverage": tests.COVERAGE,
        "matching_example": {
            "losses": losses, "coarse_signal": coarse, "fine_signal": fine,
            "coarse_value": str(before["value"]), "fine_value": str(after["value"]),
            "coarse_policies": before["policy_evaluations"],
            "fine_policies": after["policy_evaluations"],
        },
        "constructed_nonrefinement_witness": counterexample,
        "inputs": {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in files},
        "overall_closure": "OPEN",
        "scientific_truth_certified": False,
        "claim_boundaries": [
            "no probability prior on worlds; other assumptions remain",
            "full loss tables are supplied; no inference from sampled data",
            "deterministic signal and policy theorem; no stochastic garbling promotion",
            "Python correspondence tested; not extracted from Lean",
            "real-valued finite minimax and randomization boundary have paper proofs",
        ],
    }


if __name__ == "__main__":
    value = evaluate()
    encoded = json.dumps(value, indent=2, sort_keys=True) + "\n"
    if sys.argv[1:] == ["--write"]:
        (HERE / "RESULT_V7.json").write_text(encoded)
    elif sys.argv[1:]:
        raise ValueError("only --write is accepted")
    elif (HERE / "RESULT_V7.json").read_text() != encoded:
        raise ValueError("receipt drift")
    print(encoded, end="")
