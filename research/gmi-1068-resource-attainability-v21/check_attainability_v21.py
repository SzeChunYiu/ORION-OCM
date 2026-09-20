"""Replay actual execution, resource accounting and fixed partial-context attainability."""
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ATOM_SPECS = {'GMI2-R3-001': ('formalize contextual attainability',
                 'Actual fixed partial contexts evaluate selected physically successful finite histories; the '
                 'unrestricted finite-history image is the union of bounded-length images. Infinite traces and '
                 'unattained limits are excluded.'),
 'GMI2-R3-002': ('formalize budget restriction',
                 'Actual V8 residual execution succeeds exactly when unrestricted finite execution succeeds with '
                 'affordable accumulated Nat cost, preserving endpoint and successful full response; its '
                 'contextual image is an actual restriction.'),
 'GMI2-R3-003': ('prove monotonicity',
                 'Fixed-context image inclusion follows from nested history selectors; actual resource execution '
                 'derives capacity nesting. Changing the evaluator or arbitrarily labelling restrictions does not '
                 'establish the premise.'),
 'GMI2-R3-005': ('derive capability projection',
                 'Capability for a declared target is exactly an admitted evaluated execution witness in the '
                 'attainable image, equivalently an affordable target value in the actual joint cost/value '
                 'relation.'),
 'GMI2-R3-006': ('derive resource response',
                 'Declared value-coordinate projections and resource-indexed admission images are separately '
                 'constructed and related by actual joint cost/value fibers; Nat target response has an attained '
                 'least finite threshold when nonempty.'),
 'GMI2-R3-010': ('mechanize attainability lemmas',
                 'Fresh typed replay of original attain_mono, maximal_is_attainable and '
                 'impossible_means_no_target is bridged to actual partial-context images, alongside operational '
                 'restriction, filtration and capability proofs.')}
RESULTS = {'U1': 'Actual weighted finite execution, concatenation and Nat residual accounting preserve successful complete '
       'V8 Responses.',
 'U2': 'Actual fixed V15 partial-context admission constructs finite-history images, selection monotonicity, '
       'horizon unions and operational capacity filtrations.',
 'U3': 'Joint execution-cost/value fibers determine resource-indexed capability and attained least Nat target '
       'costs; declared coordinate projection remains separate.',
 'U4': 'Noncommutative ordered accumulation supports prefix-based capacity nesting; nonnegative increments '
       'justify final-aggregate affordability, with an actual Nat residual bridge.'}
BOUNDARIES = ['only original R3-001/002/003/005/006/010 close; R3 retains its inherited whole-round stale status',
 'all histories are finite; an unbounded set of lengths is not an infinite trace or limit completion',
 'history selection, process admission and evaluator definedness remain separate',
 'capacity image nesting requires fixed evaluator, domain and interpretation',
 'capability uses a declared target; neither target nor cost/value pairing is inferred from an unlabelled value '
 'image',
 'resource-coordinate projection and resource-indexed admission are different operations',
 'least attained Nat thresholds are semantic and may be noncomputable for arbitrary history-dependent contexts',
 'ordered composition alone supplies neither positivity nor universal subtraction',
 'final-aggregate affordability requires nonnegative increments; generic prefix semantics includes initial '
 'affordability',
 'Python evidence concerns finite rosters and concrete resource operations; arbitrary generality belongs to its '
 'explicitly registered kernel statements',
 '27 original fulfilled and 195 unresolved; two qualified replacements separately leave 193 active',
 'classical parent mathematics and scoped integration; no originality, universal objective or full GMI claimed']


def load(name):
    spec = importlib.util.spec_from_file_location(name, HERE / (name + ".py"))
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def evaluate():
    for name in ("CORE.md", "THEORY_V21.md", "CONTEXTS_V21.md", "RESOURCES_V21.md",
                 "CONTROLS_V21.md", "PARENTS_V21.json", "THEOREM_LEDGER_V21.json",
                 "ADJUDICATION_V21.md", "REVIEW_V21.md", "FORMAL_REVIEW_V21.md", "FORMAL_SCOPE_V21.md"):
        if not (HERE / name).read_text().strip():
            raise ValueError("required theory/review artifact is empty: " + name)
    custody = load("custody_v21").verify(ROOT)
    for name in ("core_v21", "execution_v21", "images_v21", "resources_v21", "proof_contract_v21"):
        load(name)
    kernel = load("check_lean_v21").evaluate()
    guard = load("coverage_v21")
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
                   and p.suffix in {".py", ".md", ".lean", ".json"} and p.name != "RESULT_V21.json")
    return {
        "schema": "GMI_1068_RESOURCE_ATTAINABILITY_V21",
        "tests_run": result.testsRun, "kernel": kernel, "coverage": coverage,
        "atoms": {key: {"title": title, "status": "VERIFIED_AT_REGISTERED_SCOPE", "scope": scope}
                  for key, (title, scope) in ATOM_SPECS.items()},
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
    output = HERE / "RESULT_V21.json"
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
