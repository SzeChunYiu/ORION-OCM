"""Replay actual attainable frontiers, partial-map guards and continuation simulation."""
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ATOM_SPECS = {
    "GMI2-R3-004": ("prove frontier construction conditions",
        "Actual finite attainable images under declared admission and evaluator domains have a constructed maximal frontier, cofinality and equal downward closure. Equivalent maximal values remain distinct unless an explicit representative selector is used. Infinite existence requires additional assumptions; the original finite-frontier requirement alone closes."),
}
RESULTS = {
    "T1": "Construct finite maximal frontiers and class representatives for actual attained images; well-founded strict ascent separately supplies maximal extensions on arbitrary attained preorders.",
    "T2": "Guarded partial maps are exactly those preserving downward output images under every finite cofinal pruning; actual partial context postcomposition preserves admission and updates evaluator definedness.",
    "T3": "Greatest base-contained deterministic forward simulation equals one-sided preservation of all same finite action words and makes continuation pruning safe at the declared endpoint scope.",
    "T4": "Independent finite refinement, distinguishing words, actual residual-budget lifting and guarded endpoint evaluation repair unsafe pruning under explicit observer assumptions.",
}
BOUNDARIES = [
    "only original R3-004 closes; R3 retains its inherited whole-round stale status",
    "finite attained image is required for finite frontier construction; finite individual histories alone do not imply it",
    "preorder-equivalent maximal values remain distinct until an explicit representative choice",
    "representative minimality is among cofinal subsets of the attained set, not absolute encoding size",
    "well-founded strict ascent is sufficient for maximal extensions, not necessary or a finite-frontier guarantee",
    "partial context postcomposition preserves admission and changes evaluator definedness",
    "pruning preserves existential upward goals, not arbitrary targets, probabilities, multiplicities or history identity",
    "greatest simulation concerns one-sided same-word admission for deterministic partial actions",
    "state simulation needs guarded active endpoint evaluation to preserve attained value goals",
    "finite refinement and budget adapter evidence does not certify full V8 output/cost trace equality",
    "21 original fulfilled and 201 unresolved; two qualified replacements separately leave 199 active",
    "classical parent mathematics and scoped integration; no originality, universal objective or full GMI claimed",
]


def load(name):
    spec = importlib.util.spec_from_file_location(name, HERE / (name + ".py"))
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def evaluate():
    for name in ("CORE.md", "THEORY_V20.md", "PARTIAL_MAPS_V20.md", "SIMULATION_V20.md",
                 "CONTROLS_V20.md", "PARENTS_V20.json", "THEOREM_LEDGER_V20.json",
                 "ADJUDICATION_V20.md", "REVIEW_V20.md", "FORMAL_REVIEW_V20.md", "FORMAL_SCOPE_V20.md"):
        if not (HERE / name).read_text().strip():
            raise ValueError("required theory/review artifact is empty: " + name)
    custody = load("custody_v20").verify(ROOT)
    for name in ("core_v20", "frontier_v20", "maps_v20", "simulation_v20",
                 "bridge_v20", "proof_contract_v20"):
        load(name)
    kernel = load("check_lean_v20").evaluate()
    guard = load("coverage_v20")
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
                   and p.suffix in {".py", ".md", ".lean", ".json"} and p.name != "RESULT_V20.json")
    return {
        "schema": "GMI_1068_FRONTIER_SIMULATION_V20",
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
    output = HERE / "RESULT_V20.json"
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
