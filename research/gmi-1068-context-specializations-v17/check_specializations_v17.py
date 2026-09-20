"""Replay actual context specializations and independently calibrated viability."""
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ATOM_SPECS = {
    "GMI2-R2-005": ("characterize scalar/vector/viability contexts",
        "Actual partial contexts instantiate scalar utility, Boolean acceptance, finite Pareto vectors, explicitly dual cost preference, nonempty-set information order and existential viability. Codomain maps and products preserve their declared domain and order laws. Viability is the greatest safe postfixed set and, with classical choice, exactly admits an infinite safe trajectory; arbitrary finite-horizon survival is insufficient."),
}
BOUNDARIES = [
    "only original R2-005 closes; R2 remains OPEN",
    "preorders, admission, evaluator domains and evolution are declared",
    "monotonicity preserves comparison; reflection requires its own premise",
    "shared and independent empty products have different declared domains",
    "confidence is nonempty-set information order, not statistical calibration",
    "viability is existential discrete safety with explicit classical choice",
    "no automatic identity stuttering, adversarial safety or continuous-time limit",
    "finite exhaustive calibration is distinct from arbitrary-state kernel proofs",
    "classical parent constructions; no novel mechanism or empirical prediction claimed",
    "19 original fulfilled and 203 unresolved; two qualified replacements separately leave 201 active",
    "no canonical utility, universal scalar, assumption-free theory or full-family derivation",
]


def load(name):
    spec = importlib.util.spec_from_file_location(name, HERE / (name + ".py"))
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def evaluate():
    for name in ("CORE.md", "THEORY_V17.md", "PARENTS_V17.json", "ADJUDICATION_V17.md",
                 "REVIEW_V17.md", "FORMAL_REVIEW_V17.md", "FORMAL_SCOPE_V17.md"):
        if not (HERE / name).read_text().strip():
            raise ValueError("required theory/review artifact is empty: " + name)
    custody = load("custody_v17").verify(ROOT)
    for name in ("core_v17", "ops_v17", "products_v17", "specializations_v17",
                 "viability_v17", "proof_contract_v17"):
        load(name)
    kernel = load("check_lean_v17").evaluate()
    guard = load("coverage_v17")
    modules = [load(name) for name in sorted(guard.REQUIRED)]
    suite = unittest.TestSuite(unittest.defaultTestLoader.loadTestsFromModule(m) for m in modules)
    result = unittest.TextTestRunner(verbosity=1).run(suite)
    if not result.wasSuccessful() or result.testsRun == 0:
        raise ValueError("verification failed or collected no tests")
    coverage = {m.__name__: m.COVERAGE for m in modules}
    guard.validate_coverage(coverage)
    registry = json.loads((ROOT / "research/gmi-1068-grand-unified-v2-r0/ATOMIC_CHECKLIST_V1.json").read_text())
    rows = {row["id"]: row for row in registry["rows"]}
    if any(rows[key]["title"] != title for key, (title, _) in ATOM_SPECS.items()):
        raise ValueError("original requirement identity changed")
    files = sorted(p for p in HERE.iterdir() if p.is_file()
                   and p.suffix in {".py", ".md", ".lean", ".json"} and p.name != "RESULT_V17.json")
    return {
        "schema": "GMI_1068_CONTEXT_SPECIALIZATIONS_V17",
        "tests_run": result.testsRun, "kernel": kernel, "coverage": coverage,
        "atoms": {key: {"title": title, "status": "VERIFIED_AT_REGISTERED_SCOPE", "scope": scope}
                  for key, (title, scope) in ATOM_SPECS.items()},
        **custody,
        "inputs": {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in files},
        "overall_closure": "OPEN", "scientific_truth_certified": False,
        "claim_boundaries": BOUNDARIES,
    }


def main():
    if sys.argv[1:] not in ([], ["--write"]):
        raise ValueError("only --write accepted")
    encoded = json.dumps(evaluate(), indent=2, sort_keys=True) + "\n"
    output = HERE / "RESULT_V17.json"
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
