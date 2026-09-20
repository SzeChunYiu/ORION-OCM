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
    "GMI2-R2-008": ("relate Legg-Hutter and intelligence measures",
        "Legg-Hutter scores instantiate declared evaluation contexts with a chosen environment class, coding, rewards and reference machine. Actual prefix wrappers expose reference dependence; the full bounded-profile score envelope equals pointwise order at paper-proof scope. Declared expectation, lower-envelope and free-conversion target contexts recover their parent constructions with explicit dynamic-consistency and completeness boundaries."),
}
BOUNDARIES = [
    "only original R2-008 closes; R2 remains OPEN",
    "fixed countable environment class, injective coding and bounded reward semantics",
    "unnormalized shortest-description weights; no inferred probability simplex",
    "the full reference-machine family must contain arbitrary target/padding wrappers",
    "Option-machine kernel semantics is not a universal Turing-machine implementation",
    "TM realizability, infinite Kraft and Real score-envelope proofs are paper-level",
    "finite prefix books are calibration models, never universal reference machines",
    "lower-envelope recursion requires additional assumptions; the example tests rectangular repair only",
    "complete resource signatures require every target and full observed object domain",
    "classical parent constructions and elementary adaptations; no originality or empirical prediction claimed",
    "20 original fulfilled and 202 unresolved; two qualified replacements separately leave 200 active",
    "no canonical prior, unique intelligence scalar, efficient selector or full-family derivation",
]


def load(name):
    spec = importlib.util.spec_from_file_location(name, HERE / (name + ".py"))
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def evaluate():
    for name in ("CORE.md", "THEORY_V18.md", "CONTEXTS_V18.md", "PARENTS_V18.json",
                 "THEOREM_LEDGER_V18.json", "ADJUDICATION_V18.md",
                 "REVIEW_V18.md", "FORMAL_REVIEW_V18.md", "FORMAL_SCOPE_V18.md"):
        if not (HERE / name).read_text().strip():
            raise ValueError("required theory/review artifact is empty: " + name)
    custody = load("custody_v18").verify(ROOT)
    for name in ("core_v18", "prefix_v18", "measures_v18", "resources_v18",
                 "interaction_v18", "proof_contract_v18"):
        load(name)
    kernel = load("check_lean_v18").evaluate()
    guard = load("coverage_v18")
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
                   and p.suffix in {".py", ".md", ".lean", ".json"} and p.name != "RESULT_V18.json")
    return {
        "schema": "GMI_1068_REFERENCE_ENVELOPE_V18",
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
    output = HERE / "RESULT_V18.json"
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
