"""Replay actual permission gating, target incidence and relative blockers."""
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ATOM_SPECS = {'GMI2-R3-007': ['derive impossibility and barriers',
                 'Actual permission-gated execution and fixed partial contexts derive target '
                 'impossibility, relative enabling deficits and deletion blockers. Minimal '
                 'blockers require blocking plus private eligible witnesses; the generic '
                 'history-admission specialization preserves the original one-step relief scope.']}
RESULTS = {'V1': 'Actual state/action-sensitive edge gating succeeds exactly when the physical history '
       'succeeds and its accumulated permissions are enabled, preserving complete successful V8 '
       'Responses.',
 'V2': 'Actual fixed V15 contexts derive target capability and impossibility from eligible '
       'physical history requirements, with history identities and partial evaluation retained.',
 'V3': 'Relative additions are characterized by available witness deficits; deletion blockers are '
       'hitting sets of currently available target supports, with exact minimality/private-witness '
       'certificates and explicit finite enumeration scope.'}
BOUNDARIES = ['only original R3-007 closes; R3 remains stale overall and R3-008/009 remain unresolved',
 'optional positive edge permissions preserve observations, physical edges, payloads, costs and '
 'fixed evaluator meanings',
 'raw finite histories retain their identities; equal endpoints, supports or values do not make '
 'histories identical',
 'gated success preserves full responses; failed gated and unrestricted responses need not agree',
 'generic incidence requires exact admission semantics; actual edge gating earns that bridge',
 'relative additions range over all subsets of available permissions outside the baseline; '
 'arbitrary restricted intervention families need separate constraints',
 'blockers concern currently available eligible target histories; off-universe supports do not '
 'impose deletion constraints',
 'private witnesses certify minimality only together with actual blocking',
 'minimal by inclusion does not mean least cardinality, least cost or unique',
 'finite roster impossibility is not all-word impossibility; infinite witness families need '
 'separate completeness or computability premises',
 '28 fulfilled and 194 unresolved originals; two unchanged qualified replacements separately leave '
 '192 active unresolved',
 'classical parent integration; no identified physical cause, universal intervention family, '
 'novelty or complete GMI claim']

def load(name):
    spec = importlib.util.spec_from_file_location(name, HERE / (name + ".py"))
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def evaluate():
    for name in ("CORE.md", "THEORY_V22.md", "CONTEXTS_V22.md", "BLOCKERS_V22.md",
                 "CONTROLS_V22.md", "PARENTS_V22.json", "THEOREM_LEDGER_V22.json",
                 "ADJUDICATION_V22.md", "REVIEW_V22.md", "FORMAL_REVIEW_V22.md", "FORMAL_SCOPE_V22.md"):
        if not (HERE / name).read_text().strip():
            raise ValueError("required theory/review artifact is empty: " + name)
    custody = load("custody_v22").verify(ROOT)
    for name in ("core_v22", "execution_v22", "contexts_v22", "families_v22", "proof_contract_v22"):
        load(name)
    kernel = load("check_lean_v22").evaluate()
    guard = load("coverage_v22")
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
                   and p.suffix in {".py", ".md", ".lean", ".json"} and p.name != "RESULT_V22.json")
    return {
        "schema": "GMI_1068_PERMISSION_BARRIERS_V22",
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
    output = HERE / "RESULT_V22.json"
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
