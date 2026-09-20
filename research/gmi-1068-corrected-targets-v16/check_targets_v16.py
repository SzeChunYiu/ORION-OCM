"""Replay the registered correction theorems and independent finite calibration."""
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
GOV = ROOT / "research/gmi-1068-amendment-governance-v16"


def load(name, directory=HERE):
    spec = importlib.util.spec_from_file_location(name, directory / (name + ".py"))
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def evaluate():
    for name in ("CORE.md", "THEORY_V16.md", "PARENTS_V16.json", "ADJUDICATION_V16.md",
                 "REVIEW_V16.md", "FORMAL_REVIEW_V16.md", "FORMAL_SCOPE_V16.md"):
        if not (HERE / name).read_text().strip():
            raise ValueError("empty required review/theory artifact: " + name)
    load("ledger_structure_v16", GOV)
    contract = load("custody_v16", GOV).read_contract(ROOT)
    load("proof_contract_v16")
    kernel = load("check_lean_v16").evaluate()
    guard = load("coverage_v16")
    modules = [load(name) for name in sorted(guard.REQUIRED)]
    suite = unittest.TestSuite(unittest.defaultTestLoader.loadTestsFromModule(m) for m in modules)
    result = unittest.TextTestRunner(verbosity=1).run(suite)
    if not result.wasSuccessful() or result.testsRun == 0:
        raise ValueError("scientific verification failed or collected no tests")
    coverage = {m.__name__: m.COVERAGE for m in modules}
    guard.validate_coverage(coverage)
    files = sorted(p for p in HERE.iterdir() if p.is_file()
                   and p.suffix in {".py", ".md", ".lean", ".json"}
                   and p.name != "RESULT_V16.json")
    sources = dict(contract["source_bindings"])
    for path in (GOV / "ledger_structure_v16.py", GOV / "custody_v16.py"):
        sources[str(path.relative_to(ROOT))] = hashlib.sha256(path.read_bytes()).hexdigest()
    return {
        "schema": "GMI_1068_CORRECTED_TARGETS_V16",
        "tests_run": result.testsRun, "kernel": kernel, "coverage": coverage,
        "statements": {s["id"]: {"status": "VERIFIED_AT_REGISTERED_SCOPE", "contract": s}
                       for s in contract["statements"]},
        "source_bindings": sources,
        "inputs": {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in files},
        "original_atoms_closed": [],
        "overall_closure": "OPEN", "scientific_truth_certified": False,
        "claim_boundaries": [
            "qualified frozen readings corrected; both original atoms remain UNKNOWN",
            "raw full-source admission decoding is distinct from composition nonrecovery",
            "singleton extraction does not certify an arbitrary generated path domain",
            "basis extraction and finite probes do not certify arbitrary-function linearity",
            "generic ordered-ring kernel and Int instance; Real interpretation paper-only",
            "nonlinear min/max general Real properties paper-level; exact Nat proofs replayed",
            "classical constructions; no empirical novelty or universal objective derived",
            "18 original fulfilled and 204 original unresolved remain unchanged",
        ],
    }


def main():
    if sys.argv[1:] not in ([], ["--write"]):
        raise ValueError("only --write accepted")
    encoded = json.dumps(evaluate(), indent=2, sort_keys=True) + "\n"
    output = HERE / "RESULT_V16.json"
    if sys.argv[1:] == ["--write"]:
        output.write_text(encoded)
    elif output.read_text() != encoded:
        raise ValueError("scientific receipt drift")
    print(encoded, end="")


if __name__ == "__main__":
    try:
        main()
    except OSError as exc:
        print("CANNOT_CHECK: " + str(exc), file=sys.stderr)
        sys.exit(2)
    except RuntimeError as exc:
        if type(exc).__name__ != "CannotCheck":
            raise
        print("CANNOT_CHECK: " + str(exc), file=sys.stderr)
        sys.exit(2)
    except (ValueError, KeyError, TypeError) as exc:
        print("CHECKED_INVALID: " + str(exc), file=sys.stderr)
        sys.exit(1)
