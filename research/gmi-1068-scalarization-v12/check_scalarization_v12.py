"""Replay general scalarization proofs and calibrations before original-atom closure."""
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ATOM = "GMI2-R2-006"
TITLE = "prove scalarization boundaries"
SCOPE = ("General finite-vector weighted-order preservation, constructive reversal for every "
         "incomparable pair, and scalar/Pareto converse boundaries; real proofs are mathematical, "
         "generic ordered-ring proofs and the Int instance are kernel checked.")
SOURCE_PATHS = (
    "research/gmi-1068-grand-unified-v2-r0/ATOMIC_CHECKLIST_V1.json",
    "research/gmi-1068-r2-context-irreducibility-v1/FREEZE_V1.md",
    "research/gmi-1068-recursive-audit-v11/SCOPE_SNAPSHOT_V11.json",
)


def load(name):
    spec = importlib.util.spec_from_file_location(name, HERE / (name + ".py"))
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def evaluate():
    load("proof_contract_v12")
    kernel = load("check_lean_v12").evaluate()
    guard = load("coverage_v12")
    modules = [load(name) for name in sorted(guard.REQUIRED)]
    suite = unittest.TestSuite(
        unittest.defaultTestLoader.loadTestsFromModule(module) for module in modules)
    result = unittest.TextTestRunner(verbosity=1).run(suite)
    if not result.wasSuccessful() or result.testsRun == 0:
        raise ValueError("verification failed or no tests collected")
    coverage = {module.__name__: module.COVERAGE for module in modules}
    guard.validate_coverage(coverage)
    registry = json.loads((ROOT / SOURCE_PATHS[0]).read_text())
    matches = [row for row in registry["rows"] if row["id"] == ATOM]
    if len(matches) != 1 or matches[0]["title"] != TITLE:
        raise ValueError("original requirement identity changed")
    sources = {path: hashlib.sha256((ROOT / path).read_bytes()).hexdigest()
               for path in SOURCE_PATHS}
    files = sorted(p for p in HERE.iterdir() if p.is_file()
                   and p.name != "RESULT_V12.json"
                   and p.suffix in {".py", ".md", ".lean", ".json"})
    return {
      "schema": "GMI_1068_SCALARIZATION_V12",
      "tests_run": result.testsRun, "kernel": kernel, "coverage": coverage,
      "atoms": {ATOM: {"title": TITLE, "status": "VERIFIED_AT_REGISTERED_SCOPE", "scope": SCOPE}},
      "source_bindings": sources,
      "inputs": {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in files},
      "overall_closure": "OPEN", "scientific_truth_certified": False,
      "claim_boundaries": [
        "one original scientific requirement only; R2 remains open",
        "explicit primitive ordered-ring laws; Int instance kernel checked; real instance paper-only",
        "all positive scalarizations characterize order; no single scalar reflects incomparables",
        "positive weighted sums need not select every Pareto-efficient point",
        "210 remaining original requirements retain their unresolved statuses",
        "no derived objective or preferred weights, architecture recovery or empirical novelty",
      ],
    }


def main():
    if sys.argv[1:] not in ([], ["--write"]):
        raise ValueError("only --write is accepted")
    value = evaluate()
    encoded = json.dumps(value, indent=2, sort_keys=True) + "\n"
    if sys.argv[1:] == ["--write"]:
        (HERE / "RESULT_V12.json").write_text(encoded)
    elif (HERE / "RESULT_V12.json").read_text() != encoded:
        raise ValueError("receipt drift")
    print(encoded, end="")


if __name__ == "__main__":
    try:
        main()
    except OSError as exc:
        print("CANNOT_CHECK:" + str(exc), file=sys.stderr)
        sys.exit(2)
    except RuntimeError as exc:
        module = sys.modules.get("check_lean_v12")
        if module is None or not isinstance(exc, module.CannotCheck):
            raise
        print("CANNOT_CHECK:" + str(exc), file=sys.stderr)
        sys.exit(2)
    except (ValueError, KeyError, TypeError) as exc:
        print("CHECKED_INVALID:" + str(exc), file=sys.stderr)
        sys.exit(1)
