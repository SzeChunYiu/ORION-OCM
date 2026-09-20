"""Replay typed stochastic and nondeterministic process constructions."""
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ATOM_SPECS = {
 "GMI2-R1-008": ("formalize stochastic/nondeterministic optional structure",
  "Finite stochastic kernels and total relations supply lawful optional process instances with faithful deterministic embeddings; support preserves composition but loses probabilities. Generic scalar-law and actual finite rational proofs are distinguished from paper-level rational/real specialization."),
}

SOURCE_PATHS = (
 "research/gmi-1068-grand-unified-v2-r0/ATOMIC_CHECKLIST_V1.json",
 "research/gmi-1068-r1-minimal-process-core-v1/FREEZE_V1.md",
 "research/gmi-1068-recursive-audit-v13/SCOPE_SNAPSHOT_V13.json",
)


def load(name):
    spec = importlib.util.spec_from_file_location(name, HERE / (name + ".py"))
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def evaluate():
    load("proof_contract_v14")
    kernel = load("check_lean_v14").evaluate()
    guard = load("coverage_v14")
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
                   and p.name != "RESULT_V14.json"
                   and p.suffix in {".py", ".md", ".lean", ".json"})
    return {
      "schema": "GMI_1068_STOCHASTIC_PROCESS_V14",
      "tests_run": result.testsRun, "kernel": kernel,
      "coverage": coverage,
      "atoms": {key: {"title": title, "status": "VERIFIED_AT_REGISTERED_SCOPE", "scope": scope}
                for key, (title, scope) in ATOM_SPECS.items()},
      "source_bindings": sources,
      "inputs": {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in files},
      "overall_closure": "OPEN", "scientific_truth_certified": False,
      "claim_boundaries": [
        "one original scientific requirement only; R1 remains open",
        "generic nonnegative-weight semiring laws are explicit assumptions",
        "general rational/real scalar instantiation remains paper-level",
        "the actual finite rational model uses kernel-checked arithmetic",
        "support loses probabilities; uniformization does not preserve composition",
        "206 original requirements retain their unresolved statuses",
        "no canonical probability assignment, architecture recovery or empirical novelty",
      ],
    }


def main():
    if sys.argv[1:] not in ([], ["--write"]):
        raise ValueError("only --write is accepted")
    encoded = json.dumps(evaluate(), indent=2, sort_keys=True) + "\n"
    if sys.argv[1:] == ["--write"]:
        (HERE / "RESULT_V14.json").write_text(encoded)
    elif (HERE / "RESULT_V14.json").read_text() != encoded:
        raise ValueError("receipt drift")
    print(encoded, end="")


if __name__ == "__main__":
    try:
        main()
    except OSError as exc:
        print("CANNOT_CHECK:" + str(exc), file=sys.stderr)
        sys.exit(2)
    except RuntimeError as exc:
        modules = [sys.modules.get(name) for name in ("check_lean_v14",)]
        if not any(module and isinstance(exc, module.CannotCheck) for module in modules):
            raise
        print("CANNOT_CHECK:" + str(exc), file=sys.stderr)
        sys.exit(2)
    except (ValueError, KeyError, TypeError) as exc:
        print("CHECKED_INVALID:" + str(exc), file=sys.stderr)
        sys.exit(1)
