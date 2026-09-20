"""Replay source-specific parent translations with exact scoped proof and finite evidence."""
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ATOM_SPECS = {'GMI2-R1-009': ['translate to parent process formalisms',
                 'At the declared seven-parent scope, actual relations, LTS/powerset roundtrips, '
                 'whole-system coalgebras, finite classical events/tests and declared task-interface bridges '
                 'retain their source-specific observations and premises; generic enriched and physical '
                 'interpretations remain explicitly separate from constructed kernel models.']}
RESULTS = {'AA1': 'Actual relation-LTS and powerset coalgebra roundtrips identify the homomorphism equation with '
        'forward preservation plus successor lifting; actual V11 free paths map and lift the same supplied '
        'target path.',
 'AA2': 'The actual category of whole coalgebra systems follows from primitive endofunctor laws; faithful '
        'underlying-set forgetting can collapse objects and lose failed raw joins, while retaining '
        'structured object tags restores the registered response transport.',
 'AA3': 'Arbitrary relations form an actual category and receive faithful TotalRel inclusion; actual '
        'normalized-matrix and support examples retain their precise parent scope, while enriched-source '
        'sequential reduct interpretation remains parent-owned paper evidence.',
 'AA4': 'Under the explicit ordered commutative extension of actual V14 Weight, subnormalized events compose '
        'and normalized channels embed; finite labelled tests retain outcome pairs and derive aggregate '
        'normalization, and basis experiments separate classical event coefficients.',
 'AA5': 'Ambient tasks decode exactly through legitimate subtype interfaces and explicit regular inclusion '
        'bridges; inferred exact-range regularity fails strong partial associativity, while declared '
        'total-relation interfaces compose lawfully and chosen possibility restrictions remain conditional '
        'on closure.'}
BOUNDARIES = ['only original R1-009 closes at its registered seven-parent scope; whole R1 stays OPEN, every other '
 'original record and both qualified replacements stay unchanged, and accounting is 34 fulfilled/188 '
 'unresolved originals with two qualified replacements/186 active unresolved',
 'the seven-family source ledger is a declared parent set, not every possible process formalism or a unique '
 'absolute process ontology',
 'sequential reducts retain supplied source category laws and forget enrichment; standard-definition '
 'extraction is parent-owned paper evidence and does not reconstruct tensor or symmetry',
 'relation-LTS transition triples do not retain duplicate multigraph-edge identities; richer edge provenance '
 'requires a different declared interface',
 'generator-labelled paths retain complete histories; reachability or trace-language quotients need not '
 'recover transitions or branching',
 'same-target-path lifts require both forward preservation and successor lifting and are finite existential '
 'results, not canonical computable selectors or global infinite-path choices',
 'whole coalgebra systems and their homomorphisms are distinct from states, transitions and within-system '
 'execution paths',
 'faithful forgetting of underlying sets can collapse structured objects and revive failed raw joins; the '
 'tag-retaining repair concerns the registered literal-object observer',
 'arbitrary Rel permits an input without a related output, while TotalRel forbids that case; empty input '
 'sets remain valid for both and their inclusion is not a converse equivalence',
 'finite normalized stochastic channels are neither all subnormalized events nor all measurable kernels; '
 'general measure-theoretic integration is outside the constructed kernel scope',
 'labelled tests retain zero events and nested outcome-pair identities; pair closure is not an '
 'adaptive-test, global strict test-category or general ancilla-equivalence theorem',
 'ordered weights retain actual V14 nontriviality, zero-sum and zero-product premises plus commutative '
 'multiplication and primitive nonnegative monotone order; Nat consistency and exact Fraction calibration do '
 'not fabricate a general Real/Rat Lean instance',
 'inferred exact task ranges can violate strong partial associativity; the repair retains declared '
 'interfaces and explicit inclusions instead of silently shrinking endpoints',
 'physical possibility, inclusion feasibility, approximate repeatability and resource laws remain supplied '
 'premises; a possible composite does not imply possible factors',
 'classical parents own the mechanisms; actual kernel statements and bounded independent correspondence are '
 'distinct evidence levels and establish neither novel mathematics, all-machine derivation nor complete GMI']

def load(name):
    spec = importlib.util.spec_from_file_location(name, HERE / (name + ".py"))
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def evaluate():
    for name in ("CORE.md", "THEORY_V27.md", "LTS_V27.md", "COALGEBRA_V27.md",
                 "EVENTS_V27.md", "TASKS_V27.md", "CONTROLS_V27.md", "PARENTS_V27.json",
                 "PARENT_TRANSLATIONS_V27.json", "THEOREM_LEDGER_V27.json",
                 "ADJUDICATION_V27.md", "REVIEW_V27.md", "FORMAL_REVIEW_V27.md", "FORMAL_SCOPE_V27.md"):
        if not (HERE / name).read_text().strip():
            raise ValueError("required theory/review artifact is empty: " + name)
    custody = load("custody_v27").verify(ROOT)
    parents = load("audit_parents_v27").verify(ROOT)
    for name in ("core_v27", "lts_v27", "events_v27", "tests_v27", "tasks_v27", "proof_contract_v27"):
        load(name)
    kernel = load("check_lean_v27").evaluate()
    guard = load("coverage_v27")
    modules = [load(name) for name in sorted(guard.REQUIRED)]
    suite = unittest.TestSuite(unittest.defaultTestLoader.loadTestsFromModule(m) for m in modules)
    result = unittest.TextTestRunner(verbosity=1).run(suite)
    if not result.wasSuccessful() or result.testsRun != 15:
        raise ValueError("verification failed or registered test count changed")
    coverage = {m.__name__: m.COVERAGE for m in modules}
    guard.validate_coverage(coverage)
    registry = json.loads((ROOT / "research/gmi-1068-grand-unified-v2-r0/ATOMIC_CHECKLIST_V1.json").read_text())
    rows = {row["id"]: row for row in registry["rows"]}
    if any(rows[key]["title"] != title for key, (title, _) in ATOM_SPECS.items()):
        raise ValueError("original requirement identity changed")
    files = sorted(p for p in HERE.iterdir() if p.is_file()
                   and p.suffix in {".py", ".md", ".lean", ".json"} and p.name != "RESULT_V27.json")
    return {
        "schema": "GMI_1068_PARENT_TRANSLATIONS_V27",
        "tests_run": result.testsRun, "kernel": kernel, "coverage": coverage,
        "parent_reconciliation": parents,
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
    output = HERE / "RESULT_V27.json"
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
