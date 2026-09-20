"""Replay actual admission restrictions, functor boundaries and resource-path lifting."""
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ATOM_SPECS = {'GMI2-R1-006': ['eliminate redundant primitives',
                 'Relative to the registered sequential observer, actual optional-structure '
                 'examples and substrate-relative Hom restrictions reconcile all six original '
                 'removed-component rows; lawful wide inclusion preserves all anchored responses, '
                 'resource projection preserves successful histories with exact same-path '
                 'affordability, and arbitrary predicates, enriched information and physical '
                 'adequacy are not inferred or erased.']}
RESULTS = {'Z1': 'Actual V5/V11 adapters and closed same-object Hom restrictions give injective bundled '
       'inclusion, arbitrary V25 tree-response preservation/reflection and actual typed-path '
       'interpretation.',
 'Z2': 'For actual identity/composition-preserving functors, object-map injectivity is equivalent '
       'to all partial-product and raw-tree Option-response transport; every functor preserves '
       'successful histories, while output equality reflection additionally needs homwise '
       'faithfulness.',
 'Z3': 'Actual additive Nat-resource categories lift precisely the same typed base path iff its '
       'edge-cost sum fits the initial balance, with exact residual; forgetting balances preserves '
       'successful histories but can revive failed raw joins.',
 'Z4': 'All six original removed-component rows have actual category constructions, inherited '
       'optional-structure witnesses and explicit information/scope boundaries; locally discrete '
       'higher data leave the actual sequential observer unchanged.'}
BOUNDARIES = ['only original R1-006 closes at its original requirement-relative ceiling; R1-009 and all other '
 'original records remain unchanged',
 'optional here means not universally required by the registered sequential observer; arbitrary '
 'stochastic, branching, tensor or higher-cell information is not erased',
 'wide restriction retains every object and original identity and uses actual inherited '
 'composition; arbitrary nonclosed predicates do not form the registered restriction',
 'absorbing an explicitly chosen predicate into Hom is a representation theorem and does not '
 'derive admission, physical adequacy or the correct substrate',
 'the sharp functor equivalence concerns all raw trees with literal anchored object names; it is '
 'not invariant under arbitrary equivalence of categories',
 'object injectivity alone guarantees mapped-response commutation, not recovery of distinct '
 'arrows; homwise faithfulness supplies the additional successful-output distinction',
 'resource projection may collapse objects and revive failed raw joins despite homwise '
 'faithfulness; only successful raw trees and actual typed paths always project',
 'exact resource lifting assumes nonnegative additive natural costs and preserves the literal '
 'supplied path; no shortest-path substitution, subadditive extension or arbitrary infinite-state '
 'compression is claimed',
 'finite resource balances form a declared full subcategory of the Nat-resource construction; the '
 'affordability criterion applies only to successfully typed base paths',
 'the reset-category monoidal obstruction retains its standard-to-weak extraction boundary; the '
 'nonbraided example concerns its registered tensor, not every alternative tensor',
 'matrix weights and relation branches remain arrow data; full Weight/support premises and the '
 'support collision remain; no canonical relation selector or unrestricted uniformization '
 'impossibility follows',
 'locally discrete equality 2-cells give a concrete example with unchanged sequential '
 'observations; they do not reconstruct arbitrary higher data',
 'exact kernel declarations and constructor equations prove their stated arbitrary-carrier '
 'results; exhaustive finite cases and independent Python correspondence remain bounded '
 'calibration, not empirical intelligence or originality evidence',
 '33 fulfilled and 189 unresolved original requirements; two unchanged qualified replacements '
 'separately leave 187 active unresolved; only R0 is whole-round earned',
 'classical parent assimilation and foundation repair only; no prior-independent objective, '
 'universal physical adequacy, all-machine derivation, novel mathematics or complete GMI is '
 'claimed']


def load(name):
    spec = importlib.util.spec_from_file_location(name, HERE / (name + ".py"))
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def evaluate():
    for name in ("CORE.md", "THEORY_V26.md", "RESTRICTIONS_V26.md", "FUNCTORS_V26.md",
                 "RESOURCES_V26.md", "OPTIONAL_V26.md", "CONTROLS_V26.md", "PARENTS_V26.json",
                 "OPTIONAL_LEDGER_V26.json", "THEOREM_LEDGER_V26.json",
                 "ADJUDICATION_V26.md", "REVIEW_V26.md", "FORMAL_REVIEW_V26.md", "FORMAL_SCOPE_V26.md"):
        if not (HERE / name).read_text().strip():
            raise ValueError("required theory/review artifact is empty: " + name)
    custody = load("custody_v26").verify(ROOT)
    optional = load("audit_optional_v26").verify(ROOT)
    for name in ("core_v26", "functors_v26", "restrictions_v26", "resource_v26", "proof_contract_v26"):
        load(name)
    kernel = load("check_lean_v26").evaluate()
    guard = load("coverage_v26")
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
                   and p.suffix in {".py", ".md", ".lean", ".json"} and p.name != "RESULT_V26.json")
    return {
        "schema": "GMI_1068_ADMISSION_STRUCTURE_V26",
        "tests_run": result.testsRun, "kernel": kernel, "coverage": coverage,
        "optional_reconciliation": optional,
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
    output = HERE / "RESULT_V26.json"
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
