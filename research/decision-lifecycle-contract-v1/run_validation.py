"""Record only this exposed finite capsule; never upgrade programme gates."""
import argparse
from datetime import datetime, timezone
from hashlib import sha256
import io
import json
import os
from pathlib import Path
import platform
import sys
import unittest

import test_contracts


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    here = Path(__file__).resolve().parent
    paths = [here / name for name in ("contracts.py", "test_contracts.py", "run_validation.py")]
    paths.append(test_contracts.PARENT_PATH)
    def hashes():
        return {p.parent.name + "/" + p.name: sha256(p.read_bytes()).hexdigest() for p in paths}
    before = hashes()
    stream = io.StringIO()
    suite = unittest.defaultTestLoader.loadTestsFromModule(test_contracts)
    result = unittest.TextTestRunner(stream=stream, verbosity=2).run(suite)
    after = hashes()
    passed = result.wasSuccessful() and not result.skipped and before == after
    report = {
        "schema": "OCM_EXPOSED_VALIDATION_V1",
        "terminal": "FINITE_TABLE_CONTROLS_PASS" if passed else "FINITE_TABLE_CONTROLS_FAIL",
        "evidence": "SELF_AUTHORED_ENGINEERING_AND_FINITE_ENUMERATION",
        "runtime_qualification": False,
        "independent_review": False,
        "protected_evaluation": False,
        "full_repository_suite_run": False,
        "base_commit": "4c5d3ec35cfa694572b968b4a85bd03321b0cf8d",
        "parent_blob": test_contracts.PARENT_BLOB,
        "utc": datetime.now(timezone.utc).isoformat(),
        "python": sys.version,
        "platform": platform.platform(),
        "optimize": sys.flags.optimize,
        "pid": os.getpid(),
        "tests": result.testsRun,
        "failures": len(result.failures),
        "errors": len(result.errors),
        "skips": len(result.skipped),
        "census": getattr(test_contracts.ContractsTests, "census", None),
        "sha256_before": before,
        "sha256_after": after,
    }
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "validation.json").write_text(json.dumps(report, indent=2) + "\n")
    (args.out / "tests.txt").write_text(stream.getvalue())
    print(json.dumps(report, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
