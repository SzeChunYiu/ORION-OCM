"""Replay kernel proofs and independent witnesses before three-atom adjudication."""
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
TITLES = {"GMI2-R1-002": "prove typing/associativity",
          "GMI2-R1-003": "prove identities",
          "GMI2-R2-002": "prove context not derived from process law"}


def load(name):
    spec = importlib.util.spec_from_file_location(name, HERE / (name + ".py"))
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def evaluate():
    load("proof_contract_v11")
    kernel = load("check_lean_v11").evaluate()
    for name in ("paths_v11", "independent_paths_v11", "independent_context_v11"):
        load(name)
    context = sys.modules["independent_context_v11"].audit(ROOT)
    guard = load("coverage_v11")
    modules = [load(name) for name in sorted(guard.REQUIRED)]
    suite = unittest.TestSuite(
        unittest.defaultTestLoader.loadTestsFromModule(module) for module in modules)
    result = unittest.TextTestRunner(verbosity=1).run(suite)
    if not result.wasSuccessful() or result.testsRun == 0:
        raise ValueError("verification failed or no tests collected")
    coverage = {module.__name__: module.COVERAGE for module in modules}
    guard.validate_coverage(coverage)
    registry = json.loads((ROOT / "research/gmi-1068-grand-unified-v2-r0/ATOMIC_CHECKLIST_V1.json").read_text())
    rows = {row["id"]: row for row in registry["rows"]}
    if any(rows[key]["title"] != title for key, title in TITLES.items()):
        raise ValueError("original requirement identity changed")
    scopes = {
      "GMI2-R1-002": "Constructed typed path concatenation and congruence quotient laws, with a general lawful-category presentation isomorphism; substrate adequacy remains conditional.",
      "GMI2-R1-003": "Constructed typed empty paths and both unit laws, inherited by typed congruence quotients; no independent physical no-op assumption is eliminated.",
      "GMI2-R2-002": "Same full process and admitted history domain, opposite actual evaluator rankings: no uniform context recovery over any model class containing these two expansions.",
    }
    atoms = {key: {"title": TITLES[key], "status": "VERIFIED_AT_REGISTERED_SCOPE",
                   "scope": scopes[key]} for key in TITLES}
    files = sorted(p for p in HERE.iterdir() if p.is_file()
                   and p.name != "RESULT_V11.json"
                   and p.suffix in {".py", ".md", ".lean", ".json"})
    return {
      "schema": "GMI_1068_TYPED_FOUNDATION_V11",
      "tests_run": result.testsRun, "kernel": kernel, "coverage": coverage,
      "context": context, "atoms": atoms,
      "inputs": {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in files},
      "overall_closure": "OPEN", "scientific_truth_certified": False,
      "claim_boundaries": [
        "three original scientific requirements only; R1 and R2 remain open",
        "lawful target categories and typed congruences are explicit premises",
        "no claim every physical substrate already has these laws",
        "whole-round dependencies and 211 remaining requirements stay unresolved",
        "no primitive-count minimality, all-family derivation or empirical novelty",
      ],
    }


def main():
    if sys.argv[1:] not in ([], ["--write"]):
        raise ValueError("only --write is accepted")
    value = evaluate()
    encoded = json.dumps(value, indent=2, sort_keys=True) + "\n"
    if sys.argv[1:] == ["--write"]:
        (HERE / "RESULT_V11.json").write_text(encoded)
    elif (HERE / "RESULT_V11.json").read_text() != encoded:
        raise ValueError("receipt drift")
    print(encoded, end="")


if __name__ == "__main__":
    try:
        main()
    except OSError as exc:
        print("CANNOT_CHECK:" + str(exc), file=sys.stderr)
        sys.exit(2)
    except RuntimeError as exc:
        module = sys.modules.get("check_lean_v11")
        if module is None or not isinstance(exc, module.CannotCheck):
            raise
        print("CANNOT_CHECK:" + str(exc), file=sys.stderr)
        sys.exit(2)
    except (ValueError, KeyError, TypeError) as exc:
        print("CHECKED_INVALID:" + str(exc), file=sys.stderr)
        sys.exit(1)
