"""Replay actual affine contexts, exact interval regimes and all winning identities."""
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ATOM_SPECS = {'GMI2-R3-008': ['derive phase/frontier change',
                 'Actual affine families of partial contexts admit a common decoded value space '
                 'and preserve all winning identities. Whole-interval endpoint laws hold under '
                 'explicit ordered-ring assumptions; exact rational root/cell diagrams and '
                 'independent interval certificates establish the registered finite affine '
                 'regimes, including ties.']}
RESULTS = {'W1': 'Actual V15 code and common-value contexts, explicit injective decoders and V20 full '
       'maximality preserve all active winning identities and partial-evaluation tags.',
 'W2': 'Primitive ordered-ring laws derive affine whole-interval weak and strict endpoint '
       'dominance, universal weak-winner intersection and the exact universal-unique criterion, '
       'without division or density.',
 'W3': 'Exact rational boundary/open-cell diagrams retain all winner identities and admit '
       'independent whole-interval inequality certificates; existential and universal parameter '
       'claims remain distinct.'}
BOUNDARIES = ['only original R3-008 closes at registered affine context-family scope; R3 remains stale and '
 'R3-009 remains unresolved',
 'candidate identities, affine coefficients, admission and evaluator domain are fixed across the '
 'parameter interval',
 'actual values inhabit a common identity/scalar space; parameter-indexed integer codes require '
 'their explicit decoder',
 'all ties and distinct equal-score identities are retained; a preorder quotient or tie breaker '
 'does not give the same winner set',
 'whole-interval endpoint laws require lo<=hi and primitive ordered-ring structure; they do not '
 'require density or division',
 'singleton universal weak-winner intersection does not imply uniqueness everywhere; the exact '
 'unique criterion retains strict comparisons to all other active identities',
 'general rational root existence and full cell/sample completeness are paper plus exact Fraction '
 'evidence, not a claimed ordered-field kernel construction',
 'only winner identities are constant on open cells; numeric attainable values may vary',
 'all-pair roots refine the envelope, and nonwinning crossings need not change winners',
 'explicit-roster root counts are not efficient compact-graph path-envelope bounds or universal '
 'nonlinear regime algorithms',
 '29 fulfilled and 193 unresolved originals; two unchanged qualified replacements separately leave '
 '191 active unresolved',
 'classical parent integration; no thermodynamic transition, universal objective, originality or '
 'complete GMI claimed']

def load(name):
    spec = importlib.util.spec_from_file_location(name, HERE / (name + ".py"))
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def evaluate():
    for name in ("CORE.md", "THEORY_V23.md", "CONTEXTS_V23.md", "DIAGRAMS_V23.md",
                 "CONTROLS_V23.md", "PARENTS_V23.json", "THEOREM_LEDGER_V23.json",
                 "ADJUDICATION_V23.md", "REVIEW_V23.md", "FORMAL_REVIEW_V23.md", "FORMAL_SCOPE_V23.md"):
        if not (HERE / name).read_text().strip():
            raise ValueError("required theory/review artifact is empty: " + name)
    custody = load("custody_v23").verify(ROOT)
    for name in ("core_v23", "contexts_v23", "regimes_v23", "proof_contract_v23"):
        load(name)
    kernel = load("check_lean_v23").evaluate()
    guard = load("coverage_v23")
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
                   and p.suffix in {".py", ".md", ".lean", ".json"} and p.name != "RESULT_V23.json")
    return {
        "schema": "GMI_1068_AFFINE_REGIMES_V23",
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
    output = HERE / "RESULT_V23.json"
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
