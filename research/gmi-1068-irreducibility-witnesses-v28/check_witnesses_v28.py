"""Replay original finite witnesses and their observer boundaries with exact scoped proof and finite evidence."""
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ATOM_SPECS = {'GMI2-R2-009': ['mechanize irreducibility',
                 'The five original finite witness statements are freshly mechanized with actual '
                 'fixed-process, weak-state observer, generated-admission and positive-scalar bindings; full '
                 'tagged/source recovery and the limits of the original stronger readings remain explicit, '
                 'with immutable V16 replacements unchanged.']}
RESULTS = {'AB1': 'Actual original action generators remain distinct in the same complete V11 free process; actual '
        'partial contexts have the same one-step evaluation domain and opposite original rankings, with '
        'separate context-value and induced-order nonrecoverability.',
 'AB2': 'Actual original reachability predicates derive lawful thin categories with the same stateValue '
        'observation and different admitted transitions; generated raw-history domains differ, so the '
        'weak-state collision is not equality of full context/source observations.',
 'AB3': 'Actual three-tag observations recover admission for arbitrary partial evaluation through an '
        'explicit attained-image decoder; fixed-graph generated raw domains recover primitive edge '
        'admission, while active-domain or tag-collapsed observations can lose it.',
 'AB4': 'The original two scalar score reversals bind to actual V12 finite Int sums with explicit '
        'incomparable profiles and strictly positive weights; exact Fraction calibration retains the '
        'zero/negative-weight boundaries.'}
BOUNDARIES = ['only original R2-009 closes at its five-witness scope; whole R2 stays OPEN and all other original records '
 'remain unchanged; accounting is 35 fulfilled/187 unresolved originals, two unchanged qualified '
 'replacements and 185 active unresolved',
 'original R2-003 and R2-007 remain UNKNOWN and the immutable V16 revised readings retain their separate '
 'authority; mechanizing a literal witness does not prove an unsupported stronger theorem name',
 'the forward process is the complete free category on two labelled generators with a distinct empty '
 'identity, not a quotient identifying repeated histories or identical state effects',
 'the two-history forward executable roster and nine reward contexts do not enumerate the infinite free '
 'process or every permitted context class',
 'evaluation is defined exactly at one generator in the forward witness; admitted empty and longer histories '
 'remain UNDEFINED and off-domain implementation values do not become observations',
 'fixed-process context-value recovery and induced-order recovery have different fibers and retain fixed '
 'history labels, value decoder and comparison relation',
 'the reverse collision observes only the ambient stateValue rule; it does not equate full admitted '
 'contexts, full generated raw sources or complete three-tag observations',
 'complete ILLEGAL/UNDEFINED/VALUE observations recover admission even with empty evaluation domains; this '
 'does not recover every process composition law',
 'singleton decoding requires a fixed labelled graph and an actual generated-admission domain; agreement of '
 'an arbitrary callback on sampled paths is not that general premise',
 'the 30-history reverse roster is a singleton-complete separating signature for the declared generated '
 'models, not an enumeration of their infinite raw-history domains',
 'active-domain observations retain P intersection E and may hide admission; collapsing ILLEGAL and '
 'UNDEFINED can recreate ambiguity that complete tags resolve',
 'the scalar witness uses explicit strictly positive weights and incomparable profiles; it does not force '
 'arbitrary aggregation to be linear or select a universal objective or world-probability prior',
 'actual V12 Int kernel bindings and exact Fraction executable calibration are distinct evidence, with no '
 'fabricated general Real scalar instance',
 'original statement/header custody and ledger shape do not certify the truth of added prose; source review, '
 'exact typed registrations and finite correspondence are separate checks',
 'classical parents own these finite-witness and observer-factorization mechanisms; this round establishes '
 'no novel mathematics, all-intelligence derivation, empirical breakthrough or complete GMI']

def load(name):
    spec = importlib.util.spec_from_file_location(name, HERE / (name + ".py"))
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def evaluate():
    for name in ("CORE.md", "THEORY_V28.md", "FORWARD_V28.md", "REVERSE_V28.md",
                 "OBSERVERS_V28.md", "SCALAR_V28.md", "CONTROLS_V28.md", "PARENTS_V28.json",
                 "WITNESS_TRANSLATIONS_V28.json", "THEOREM_LEDGER_V28.json",
                 "ADJUDICATION_V28.md", "REVIEW_V28.md", "FORMAL_REVIEW_V28.md", "FORMAL_SCOPE_V28.md"):
        if not (HERE / name).read_text().strip():
            raise ValueError("required theory/review artifact is empty: " + name)
    custody = load("custody_v28").verify(ROOT)
    witnesses = load("audit_witnesses_v28").verify(ROOT)
    for name in ("core_v28", "forward_v28", "reverse_v28", "recovery_v28", "scalar_v28", "proof_contract_v28"):
        load(name)
    kernel = load("check_lean_v28").evaluate()
    guard = load("coverage_v28")
    modules = [load(name) for name in sorted(guard.REQUIRED)]
    suite = unittest.TestSuite(unittest.defaultTestLoader.loadTestsFromModule(m) for m in modules)
    result = unittest.TextTestRunner(verbosity=1).run(suite)
    if not result.wasSuccessful() or result.testsRun != 11:
        raise ValueError("verification failed or registered test count changed")
    coverage = {m.__name__: m.COVERAGE for m in modules}
    guard.validate_coverage(coverage)
    registry = json.loads((ROOT / "research/gmi-1068-grand-unified-v2-r0/ATOMIC_CHECKLIST_V1.json").read_text())
    rows = {row["id"]: row for row in registry["rows"]}
    if any(rows[key]["title"] != title for key, (title, _) in ATOM_SPECS.items()):
        raise ValueError("original requirement identity changed")
    files = sorted(p for p in HERE.iterdir() if p.is_file()
                   and p.suffix in {".py", ".md", ".lean", ".json"} and p.name != "RESULT_V28.json")
    return {
        "schema": "GMI_1068_IRREDUCIBILITY_WITNESSES_V28",
        "tests_run": result.testsRun, "kernel": kernel, "coverage": coverage,
        "witness_reconciliation": witnesses,
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
    output = HERE / "RESULT_V28.json"
    if sys.argv[1:] == ["--write"]:
        output.write_text(encoded)
    elif output.read_text() != encoded:
        raise ValueError("scientific receipt drift")
    print(encoded, end="")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ModuleNotFoundError) as exc:
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
