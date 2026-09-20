"""Replay arbitrary reconstruction proofs and independent finite operational checks."""
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RESULTS = {
    "S1": "Two-sided local units, strong partial associativity and coherence derive unique endpoints, exact matching and an actual typed category.",
    "S2": "Actual bundled category arrows give a partial algebra; both object-changing roundtrips preserve and reflect operations.",
    "S3": "Actual raw words and unit-anchored empty histories are preserved; their full responses and the partial table contain equivalent recoverable information.",
    "S4": "Isolated finite law and information-loss witnesses delimit the construction, including the minimum three-element unital associativity failure.",
}
BOUNDARIES = [
    "no original requirement closes and no new qualified replacement is authorized",
    "arbitrary small carriers and empty categories; laws are explicit assumptions",
    "units require both-sided conditional neutrality and self-composition",
    "strong associativity includes definedness; coherence is separately necessary",
    "roundtrip maps preserve and reflect partial multiplication; arbitrary multiplicative maps need not preserve units",
    "classical choice and equality may support abstract reconstruction; no general effective algorithm",
    "information sufficiency is relative to all raw words and unit-anchored empty histories",
    "retaining named symbols differs from retaining their reconstructible information",
    "finite tables supplement arbitrary-carrier and arbitrary-word kernel proofs",
    "classical parent mathematics and integration; no originality or empirical prediction claimed",
    "20 original fulfilled and 202 unresolved; two qualified replacements separately leave 200 active",
    "no signature-independent minimum, canonical prior, universal ontology or full intelligence theory",
]


def load(name):
    spec = importlib.util.spec_from_file_location(name, HERE / (name + ".py"))
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def evaluate():
    for name in ("CORE.md", "THEORY_V19.md", "ROUNDTRIPS_V19.md", "CONTROLS_V19.md",
                 "PARENTS_V19.json", "THEOREM_LEDGER_V19.json",
                 "ADJUDICATION_V19.md", "REVIEW_V19.md", "FORMAL_REVIEW_V19.md", "FORMAL_SCOPE_V19.md"):
        if not (HERE / name).read_text().strip():
            raise ValueError("required theory/review artifact is empty: " + name)
    custody = load("custody_v19").verify(ROOT)
    for name in ("partial_v19", "categories_v19", "responses_v19", "proof_contract_v19"):
        load(name)
    kernel = load("check_lean_v19").evaluate()
    guard = load("coverage_v19")
    modules = [load(name) for name in sorted(guard.REQUIRED)]
    suite = unittest.TestSuite(unittest.defaultTestLoader.loadTestsFromModule(m) for m in modules)
    result = unittest.TextTestRunner(verbosity=1).run(suite)
    if not result.wasSuccessful() or result.testsRun == 0:
        raise ValueError("verification failed or collected no tests")
    coverage = {m.__name__: m.COVERAGE for m in modules}
    guard.validate_coverage(coverage)
    files = sorted(p for p in HERE.iterdir() if p.is_file()
                   and p.suffix in {".py", ".md", ".lean", ".json"} and p.name != "RESULT_V19.json")
    return {
        "schema": "GMI_1068_ARROWS_ONLY_V19",
        "tests_run": result.testsRun, "kernel": kernel, "coverage": coverage,
        "atoms": {},
        "registered_results": {key: {"status": "VERIFIED_AT_REGISTERED_SCOPE", "scope": scope}
                               for key, scope in RESULTS.items()},
        **custody,
        "inputs": {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in files},
        "overall_closure": "OPEN", "scientific_truth_certified": False,
        "claim_boundaries": BOUNDARIES,
    }


def main():
    if sys.argv[1:] not in ([], ["--write"]):
        raise ValueError("only --write accepted")
    encoded = json.dumps(evaluate(), indent=2, sort_keys=True) + "\n"
    output = HERE / "RESULT_V19.json"
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
