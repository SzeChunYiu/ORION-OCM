"""Replay actual anchored histories, carrier census and named-interface information."""
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ATOM_SPECS = {'GMI2-R1-001': ['minimize typed process structure',
                 'Actual anchored typed histories and partial operations determine the same registered '
                 'sequential observations; least retained information is the lawful ambient-labelled '
                 'table for canonical unit anchors and the table plus identity encoder for fixed '
                 'external object names, relative to the declared observer requirements.'],
 'GMI2-R1-007': ['give loss witness per survivor',
                 'Each original TYPE, PROCESS, COMPOSITION, IDENTITY, ASSOCIATIVITY and IDENTITY_LAWS '
                 'row is reconciled to an actual information-loss or law-omission witness, preserving '
                 'stated other premises and distinguishing reconstructible fields from necessary '
                 'information; coherence is separately retained.']}
RESULTS = {'Y1': 'Actual arbitrary bracketed category observations agree with nonempty identity-guarded V19 word '
       'evaluation and actual V11 typed-path interpretation, including failed joins.',
 'Y2': 'Actual presented subtype multiplication derives ambient carrier membership and canonical raw '
       'observations; attained-image recoverability of the observer, carrier/table core and lawful '
       'padded table is equivalent.',
 'Y3': 'All six original survivor rows have precise information/law-loss witnesses and valid-encoding '
       'controls; table-defined type and identity information does not require independent named '
       'fields.',
 'Y4': 'Actual object/arrow roundtrip maps transport tree responses, while fixed external names require '
       'exactly the lawful padded table plus their supplied identity map.'}
BOUNDARIES = ['only original R1-001 and R1-007 close at their original requirement-relative ceiling; R1-006, R1-009 '
 'and all other original records remain unchanged',
 'least retained information is relative to declared ambient input/output labels and full sequential '
 'observations; it is not absolute ontology, literal primitive count, shortest encoding or independent '
 'necessity of every table cell',
 'actual canonical carrier membership is derived from the lawful padded table using local units; the '
 'padded table need not be a lawful algebra on absent ambient labels',
 'fixed external object names require their actual identity encoder; canonical unit anchors do not '
 'license erasing independently supplied names',
 'generic named recovery requires unit-valued identity maps; full category presentation additionally '
 'requires a bijection onto all units, as enforced by the concrete NamedPresented API',
 'each nested empty anchor survives guarded flattening; no empty-word default arrow, untyped carrier '
 'equality or hidden reassociation assumption is used',
 'whole-tree structural validation precedes semantic evaluation; absent-label or nonunit failure may '
 'short-circuit only afterward',
 'lawless raw-table experiments are separate weakened-law controls and are not admitted as lawful '
 'Presented models',
 'the six historical survivor rows distinguish information loss from omission of laws; explicit TYPE '
 'and IDENTITY fields can reconstruct, and isolated coherence remains a separate requirement',
 'faithful computation uses actual immutable V19 tables, category constructions and words; independent '
 'finite certificates calibrate Python refinement, while arbitrary-tree and decoder statements are '
 'separately kernel checked',
 'all named finite strata and supplementary review remain bounded calibration, not empirical '
 'machine-intelligence validation or originality evidence',
 '32 fulfilled and 190 unresolved original requirements; two unchanged qualified replacements '
 'separately leave 188 active unresolved',
 'only R0 remains whole-round earned; R1/R2 remain open and dependent closure retains inherited stale '
 'status',
 'classical parent assimilation and foundation repair only; no prior-independent objective, universal '
 'physical adequacy, all-machine derivation, novel mathematics or complete GMI is claimed']


def load(name):
    spec = importlib.util.spec_from_file_location(name, HERE / (name + ".py"))
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def evaluate():
    for name in ("CORE.md", "THEORY_V25.md", "HISTORIES_V25.md", "INFORMATION_V25.md",
                 "ENCODINGS_V25.md", "CONTROLS_V25.md", "PARENTS_V25.json",
                 "SURVIVOR_LEDGER_V25.json", "THEOREM_LEDGER_V25.json",
                 "ADJUDICATION_V25.md", "REVIEW_V25.md", "FORMAL_REVIEW_V25.md", "FORMAL_SCOPE_V25.md"):
        if not (HERE / name).read_text().strip():
            raise ValueError("required theory/review artifact is empty: " + name)
    custody = load("custody_v25").verify(ROOT)
    survivors = load("audit_survivors_v25").verify(ROOT)
    for name in ("core_v25", "syntax_v25", "trees_v25", "presentations_v25",
                 "transports_v25", "information_v25", "named_v25", "proof_contract_v25"):
        load(name)
    kernel = load("check_lean_v25").evaluate()
    guard = load("coverage_v25")
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
                   and p.suffix in {".py", ".md", ".lean", ".json"} and p.name != "RESULT_V25.json")
    return {
        "schema": "GMI_1068_GUARDED_FOUNDATIONS_V25",
        "tests_run": result.testsRun, "kernel": kernel, "coverage": coverage,
        "survivor_reconciliation": survivors,
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
    output = HERE / "RESULT_V25.json"
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
