"""Replay actual source-keyed profile, preference and plan contexts."""
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ATOM_SPECS = {'GMI2-R3-009': ['retire Gamma/Pref/SEL as foundations',
                 'Source-keyed profile, full candidate-ID preference and common-plan constructions '
                 'conservatively replace the registered legacy foundation symbols using actual partial '
                 'contexts and explicit projections, while preserving source premises, selected/full '
                 'histories, ties and distinct unrelated uses.']}
RESULTS = {'X1': 'Actual AF BFS records and full edge-history profile contexts are distinguished by an explicit '
       'erasure. Generic active-domain image coverage exactly characterizes which projected observations a '
       'selected roster preserves.',
 'X2': 'Actual resource and declared positive-price contexts reproduce full legacy candidate-ID frontiers '
       'and argmins, with strict-price Pareto efficiency and retained ties.',
 'X3': 'Actual partial-loss contexts and common plan identities recover source feasible-plan sets by '
       'explicit specialization; mapped-universe intersections preserve empty-family semantics.',
 'X4': 'Registered source-specific equalities permit conservative substitution within their fixed signatures '
       'and premises; shared spellings do not identify different objects or transport every historical '
       'theorem.'}
BOUNDARIES = ['only original R3-009 closes at registered source-specific conservative-notation scope; R3 and dependent '
 'closure remain stale',
 'AF full edge histories and old BFS terminal/action-word records are different carriers linked by explicit '
 'erasure, not an assumed injective decoder',
 'the old AF helper retains capability strings, provenance set union and Boolean presence resource '
 'indicators, not additive event counts or general resource/horizon/verifier arguments',
 'repeated action labels remain valid and share action-keyed provenance; no deterministic source/action map '
 'replaces the ordered graph relation',
 'BFS path-lift and finite-graph horizon coverage are paper plus finite executable evidence; generic actual '
 'context/image/frontier/plan transports are separately kernel checked',
 'finite-horizon full profile enumeration is a declared extension; terminal coverage does not imply '
 'preservation of all path profiles or unbounded histories',
 'candidate identities and all ties survive coordinate and scalar orders; faithful concrete resource '
 'comparison requires positive dimension and strictly positive declared prices',
 'strict new parsing validates unused data; it does not attribute those validation rules to historical '
 'early-return behavior',
 'the source rooted-plan definition has total loss; partial admission/evaluation is an explicit extension '
 'with a stated specialization back to that source',
 'plan intersections require a common declared universe, and injective transport intersects within its '
 'mapped universe, including an empty history family',
 'source-symbol retirement neither removes the conditional SEL opcode nor identifies AF profiles, rooted '
 'plans and adequate outputs',
 '30 fulfilled and 192 unresolved originals; two unchanged qualified replacements separately leave 190 '
 'active unresolved',
 'classical parent assimilation and conservative integration only; no universal preferred prior or '
 'objective, causal provenance discovery, new mathematics or complete GMI claimed']


def load(name):
    spec = importlib.util.spec_from_file_location(name, HERE / (name + ".py"))
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def evaluate():
    for name in ("CORE.md", "THEORY_V24.md", "PROFILES_V24.md", "PREFERENCES_V24.md", "PLANS_V24.md",
                 "TRANSPORT_LEDGER_V24.json",
                 "CONTROLS_V24.md", "PARENTS_V24.json", "THEOREM_LEDGER_V24.json",
                 "ADJUDICATION_V24.md", "REVIEW_V24.md", "FORMAL_REVIEW_V24.md", "FORMAL_SCOPE_V24.md"):
        if not (HERE / name).read_text().strip():
            raise ValueError("required theory/review artifact is empty: " + name)
    custody = load("custody_v24").verify(ROOT)
    for name in ("core_v24", "af_model_v24", "profiles_v24", "preferences_v24", "plans_v24", "proof_contract_v24"):
        load(name)
    kernel = load("check_lean_v24").evaluate()
    guard = load("coverage_v24")
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
                   and p.suffix in {".py", ".md", ".lean", ".json"} and p.name != "RESULT_V24.json")
    return {
        "schema": "GMI_1068_LEGACY_TRANSPORTS_V24",
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
    output = HERE / "RESULT_V24.json"
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
