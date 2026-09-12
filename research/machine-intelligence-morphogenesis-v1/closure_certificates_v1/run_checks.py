"""Reproduce local mathematical/control checks; no beacons, network or HPC work."""
from pathlib import Path
import hashlib
import io
import json
import os
import platform
import unittest

import gmi_closure_microscope as microscope
import target_witness_gap as gap
from execution_controls import certify_finite_frontier


def main():
    root = Path(__file__).resolve().parent
    evidence = root / "evidence"
    evidence.mkdir(exist_ok=True)
    log = io.StringIO()
    result = unittest.TextTestRunner(stream=log, verbosity=2).run(
        unittest.defaultTestLoader.discover(str(root), pattern="test_*.py"))
    (evidence / "unit-tests.log").write_text(log.getvalue())
    print(log.getvalue())
    frontier = microscope.exhaustive_frontier_check()
    bound = gap.finite_bound_check()
    finite = certify_finite_frontier([(x, x) for x in range(-2, 3)], target_uses_multiplication=True)
    receipt = {
        "schema": "GMIClosureCertificateValidationV1", "python": platform.python_version(),
        "environment_revision": os.environ.get("GITHUB_SHA"),
        "unit_tests": result.testsRun, "failures": len(result.failures),
        "errors": len(result.errors), "skipped": len(result.skipped),
        "frontier": frontier, "target_class_bound_checks": bound,
        "executed_finite_class": finite,
        "source_derived_legacy_projection": gap.source_derived_receipt(),
        "source_sha256": {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                          for p in sorted(root.glob("*.py"))},
        "legacy_integration": "SEPARATE_LEGACY_CLASS_BOUND_JOB_NOT_ASSERTED_HERE",
        "protected_evidence": False, "independent_authorship": False,
        "full_GMI_closure": False,
    }
    (evidence / "validation.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps(receipt, indent=2))
    if not result.wasSuccessful() or result.skipped or frontier["failures"] or bound["failures"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
