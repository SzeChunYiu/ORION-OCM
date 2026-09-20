"""Freshly replay proof evidence, then validate the additive amendment ledger."""
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SCIENCE = ROOT / "research/gmi-1068-corrected-targets-v16"
CHECKPOINT = {
    "freeze": "ef27aa6373403d3e9add7571bb97635320d63c50",
    "contract_sha256": "faa8f83c0af7a2f0a042e84deb7be191b09a281c08f287c5e986397124177902",
}


def load(name, directory=HERE):
    spec = importlib.util.spec_from_file_location(name, directory / (name + ".py"))
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def evaluate_repository(root, trusted_checkpoint=CHECKPOINT):
    if trusted_checkpoint != CHECKPOINT:
        raise ValueError("unrecognized repository trust checkpoint")
    load("ledger_structure_v16")
    contract = load("custody_v16").read_contract(root)
    science_dir = root / "research/gmi-1068-corrected-targets-v16"
    science = load("check_targets_v16", science_dir).evaluate()
    encoded = json.dumps(science, indent=2, sort_keys=True) + "\n"
    if (science_dir / "RESULT_V16.json").read_text() != encoded:
        raise ValueError("scientific receipt is not freshly reproducible")
    ledger = json.loads((root / HERE.relative_to(ROOT) / "AMENDMENT_LEDGER_V16.json").read_text())
    review = hashlib.sha256((science_dir / "REVIEW_V16.md").read_bytes()).hexdigest()
    accounting = load("ledger_evidence_v16").validate_evidence(ledger, contract, science, review)
    return {"accounting": accounting,
            "science_receipt_sha256": hashlib.sha256(encoded.encode()).hexdigest(),
            "original_snapshot_sha256": ledger["original_snapshot"]["sha256"],
            "ledger_sha256": hashlib.sha256((root / HERE.relative_to(ROOT) / "AMENDMENT_LEDGER_V16.json").read_bytes()).hexdigest(),
            "checkpoint": CHECKPOINT}


def evaluate():
    result = evaluate_repository(ROOT)
    guard = load("governance_coverage_v16")
    actual_modules = {path.stem for path in HERE.glob("test_*.py")}
    if actual_modules != set(guard.REQUIRED):
        raise ValueError("governance test inventory changed")
    modules = [load(name) for name in sorted(guard.REQUIRED)]
    if not modules:
        raise ValueError("no independent governance tests")
    suite = unittest.TestSuite(unittest.defaultTestLoader.loadTestsFromModule(m) for m in modules)
    tests = unittest.TextTestRunner(verbosity=1).run(suite)
    if not tests.wasSuccessful() or tests.testsRun == 0:
        raise ValueError("governance hostile/positive controls failed")
    coverage = {m.__name__: m.COVERAGE for m in modules}
    guard.validate_coverage(coverage)
    files = sorted(p for p in HERE.iterdir() if p.is_file()
                   and p.suffix in {".py", ".md", ".json"} and p.name != "RESULT_V16.json")
    return dict(result, schema="GMI_1068_AMENDMENT_GOVERNANCE_V16",
                tests_run=tests.testsRun, coverage=coverage,
                inputs={p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in files})


def main():
    if sys.argv[1:] not in ([], ["--write"]):
        raise ValueError("only --write accepted")
    encoded = json.dumps(evaluate(), indent=2, sort_keys=True) + "\n"
    output = HERE / "RESULT_V16.json"
    if sys.argv[1:] == ["--write"]:
        output.write_text(encoded)
    elif output.read_text() != encoded:
        raise ValueError("governance receipt drift")
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
