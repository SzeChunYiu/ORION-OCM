"""Replay partial contexts and actual fixed-process ranking separation."""
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ATOM_SPECS = {
 "GMI2-R2-001": ("formalize context/preorder",
  "Partial evaluation on admitted histories is constructed by restricting an ambient evaluator to the admission/evaluation intersection. Its pullback comparison is a preorder on that defined domain, and mutual comparison yields a partial-order quotient."),
 "GMI2-R2-004": ("generalize AJ7 countermodel",
  "For two distinct admitted/evaluated histories, a strict result pair and a permitted evaluator class containing the constructed separating functions, the same full process admits opposite rankings. Actual ordering functions differ, so the V9 collision theorem rules out recovery from that full process."),
}

SOURCE_PATHS = (
 "research/gmi-1068-grand-unified-v2-r0/ATOMIC_CHECKLIST_V1.json",
 "research/gmi-1068-r2-context-irreducibility-v1/FREEZE_V1.md",
 "research/gmi-1068-recursive-audit-v14/SCOPE_SNAPSHOT_V14.json",
 "research/gmi-1068-r0-foundation-repair-v9/RecoverabilityV9.lean",
)


def load(name):
    spec = importlib.util.spec_from_file_location(name, HERE / (name + ".py"))
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def evaluate():
    load("proof_contract_v15")
    kernel = load("check_lean_v15").evaluate()
    guard = load("coverage_v15")
    modules = [load(name) for name in sorted(guard.REQUIRED)]
    suite = unittest.TestSuite(
        unittest.defaultTestLoader.loadTestsFromModule(module) for module in modules)
    result = unittest.TextTestRunner(verbosity=1).run(suite)
    if not result.wasSuccessful() or result.testsRun == 0:
        raise ValueError("verification failed or no tests collected")
    coverage = {module.__name__: module.COVERAGE for module in modules}
    guard.validate_coverage(coverage)
    registry = json.loads((ROOT / SOURCE_PATHS[0]).read_text())
    rows = {row["id"]: row for row in registry["rows"]}
    if any(rows[key]["title"] != title for key, (title, _) in ATOM_SPECS.items()):
        raise ValueError("original requirement identity changed")
    sources = {path: hashlib.sha256((ROOT / path).read_bytes()).hexdigest()
               for path in SOURCE_PATHS}
    files = sorted(p for p in HERE.iterdir() if p.is_file()
                   and p.name != "RESULT_V15.json"
                   and p.suffix in {".py", ".md", ".lean", ".json"})
    return {
      "schema": "GMI_1068_PARTIAL_CONTEXT_V15",
      "tests_run": result.testsRun, "kernel": kernel,
      "coverage": coverage,
      "atoms": {key: {"title": title, "status": "VERIFIED_AT_REGISTERED_SCOPE", "scope": scope}
                for key, (title, scope) in ATOM_SPECS.items()},
      "source_bindings": sources,
      "inputs": {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in files},
      "overall_closure": "OPEN", "scientific_truth_certified": False,
      "claim_boundaries": [
        "two original scientific requirements only; R2 remains open",
        "admission and defined evaluation remain distinct",
        "the induced preorder is on the admitted evaluated domain only",
        "contextual comparison equivalence is not behavioral equivalence",
        "reversal requires a strict result pair and both permitted separating evaluators",
        "the same full process is preserved; semantic nonrecovery is not statistical independence",
        "204 original requirements retain their unresolved statuses",
        "no reverse-admission recovery closure, universal value rule or empirical novelty",
      ],
    }


def main():
    if sys.argv[1:] not in ([], ["--write"]):
        raise ValueError("only --write is accepted")
    encoded = json.dumps(evaluate(), indent=2, sort_keys=True) + "\n"
    if sys.argv[1:] == ["--write"]:
        (HERE / "RESULT_V15.json").write_text(encoded)
    elif (HERE / "RESULT_V15.json").read_text() != encoded:
        raise ValueError("receipt drift")
    print(encoded, end="")


if __name__ == "__main__":
    try:
        main()
    except OSError as exc:
        print("CANNOT_CHECK:" + str(exc), file=sys.stderr)
        sys.exit(2)
    except RuntimeError as exc:
        modules = [sys.modules.get(name) for name in ("check_lean_v15",)]
        if not any(module and isinstance(exc, module.CannotCheck) for module in modules):
            raise
        print("CANNOT_CHECK:" + str(exc), file=sys.stderr)
        sys.exit(2)
    except (ValueError, KeyError, TypeError) as exc:
        print("CHECKED_INVALID:" + str(exc), file=sys.stderr)
        sys.exit(1)
