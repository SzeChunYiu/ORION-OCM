"""Replay the integrated original R1 requirements with separate evidence levels."""
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import time
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RUN_COSTS = {}


def load(name):
    path = HERE / (name + ".py")
    if name in sys.modules:
        if Path(sys.modules[name].__file__).resolve() != path:
            raise ValueError("same-name local module collision")
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def evaluate():
    for name in ("CORE.md", "THEORY_V29.md", "PRESENTATION_V29.md", "OBSERVERS_V29.md",
                 "INFORMATION_V29.md", "CONTROLS_V29.md", "PARENTS_V29.json",
                 "THEOREM_LEDGER_V29.json", "ADJUDICATION_V29.md", "REVIEW_V29.md",
                 "FORMAL_REVIEW_V29.md", "FORMAL_SCOPE_V29.md"):
        if not (HERE / name).read_text().strip():
            raise ValueError("required theory/review artifact is empty:" + name)
    custody = load("custody_v29").verify(ROOT)
    rollup = load("audit_rollup_v29").verify(ROOT)
    for name in ("core_v29", "presentation_v29", "named_v29", "information_v29", "proof_contract_v29",
                 "oracle_v29", "support_v29", "hostile_cases_v29"):
        load(name)
    kernel_started = time.perf_counter()
    kernel = load("check_lean_v29").evaluate()
    RUN_COSTS["kernel_seconds"] = time.perf_counter() - kernel_started
    guard = load("coverage_v29")
    modules = [load(name) for name in sorted(guard.REQUIRED)]
    suite = unittest.TestSuite(unittest.defaultTestLoader.loadTestsFromModule(m) for m in modules)
    test_started = time.perf_counter()
    result = unittest.TextTestRunner(verbosity=1).run(suite)
    RUN_COSTS["test_seconds"] = time.perf_counter() - test_started
    if not result.wasSuccessful() or result.testsRun != 13:
        raise ValueError("verification failed or registered test count changed")
    coverage = {m.__name__: m.COVERAGE for m in modules}
    guard.validate_coverage(coverage)
    codecs = {"named": load("test_named_v29").CODEC_COSTS,
              "information": load("test_information_v29").CODEC_COSTS}
    if len(codecs["named"]["models"]) != 2 or len(codecs["information"]["family_reports"]) != 180:
        raise ValueError("registered interface-cost inventory changed")
    crosswalk = json.loads((HERE / "ORIGINAL_CROSSWALK_V29.json").read_text())
    pins = json.loads((HERE / "SOURCE_PINS_V29.json").read_text())
    proofs = json.loads((HERE / "INHERITED_PROOFS_V29.json").read_text())
    specs = load("integration_specs_v29")
    files = sorted(p for p in HERE.iterdir() if p.is_file()
                   and p.suffix in {".py", ".md", ".lean", ".json"}
                   and p.name not in {"RESULT_V29.json", "RUN_TIMINGS_V29.json"})
    RUN_COSTS["python_version"] = sys.version.split()[0]
    return {
        "schema": "GMI_1068_R1_INTEGRATED_CORE_V29", "tests_run": result.testsRun,
        "kernel": kernel, "coverage": coverage, "rollup_reconciliation": rollup,
        "round_adjudication": {"R1": {"status": "VERIFIED_AT_REGISTERED_SCOPE",
            "scope": crosswalk["original_scope"]["proposed_scope"]}},
        "registered_results": {key: {"status": "VERIFIED_AT_REGISTERED_SCOPE", "scope": scope}
                               for key, scope in specs.RESULTS.items()},
        "codec_costs": codecs,
        "source_costs": {"direct_pinned_records": len(pins["sources"]),
            "direct_pinned_bytes": sum((ROOT / p).stat().st_size for p in pins["sources"]),
            "inherited_lean_sources": proofs["source_count"],
            "inherited_lean_source_bytes": proofs["source_bytes"],
            "python_parents": len(pins["python_load_order"]),
            "python_parent_bytes": sum((ROOT / p).stat().st_size for p in pins["python_load_order"]),
            "new_python_modules": sum(p.suffix == ".py" for p in files),
            "new_python_bytes": sum(p.stat().st_size for p in files if p.suffix == ".py"),
            "new_lean_modules": sum(p.suffix == ".lean" for p in files),
            "new_lean_bytes": sum(p.stat().st_size for p in files if p.suffix == ".lean"),
            "deterministic_package_files": len(files),
            "deterministic_package_bytes": sum(p.stat().st_size for p in files)},
        **custody,
        "inputs": {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in files},
        "overall_closure": "OPEN", "scientific_truth_certified": False,
        "claim_boundaries": specs.BOUNDARIES,
    }


def main():
    if sys.argv[1:] not in ([], ["--write"]):
        raise ValueError("only --write accepted")
    started = time.perf_counter()
    receipt = evaluate()
    RUN_COSTS["evaluation_seconds"] = time.perf_counter() - started
    encoded = json.dumps(receipt, indent=2, sort_keys=True) + "\n"
    output = HERE / "RESULT_V29.json"
    if sys.argv[1:] == ["--write"]:
        output.write_text(encoded)
        (HERE / "RUN_TIMINGS_V29.json").write_text(json.dumps(
            {"normal": RUN_COSTS, "scope": "Observed checker execution; not an efficiency optimum."},
            indent=2, sort_keys=True) + "\n")
    elif output.read_text() != encoded:
        raise ValueError("scientific receipt drift")
    print("RUN_TIMINGS_V29 " + json.dumps(RUN_COSTS, sort_keys=True), file=sys.stderr)
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
