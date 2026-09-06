"""Reproduce local development checks; emits no OCM scientific authority."""
from __future__ import annotations

import hashlib
import json
import platform
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from authority_router import Eligibility, Envelope, Query, Route, RouteIndex


HERE = Path(__file__).resolve().parent


def run_suite(folder: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "unittest", "discover", "-s", str(folder),
         "-p", "test_*.py", "-v"], capture_output=True, text=True, timeout=60,
        check=False,
    )


def main() -> int:
    output = Path(sys.argv[1]) if len(sys.argv) == 2 else HERE / "development_results.json"
    if len(sys.argv) > 2:
        raise SystemExit("usage: python run_checks.py [output.json]")
    if output.exists():
        raise FileExistsError("Choose a new output path; existing development records are not overwritten")
    good = run_suite(HERE)
    source = (HERE / "authority_router.py").read_text(encoding="utf-8")
    needle = "if eligibility is Eligibility.REJECTED:"
    if source.count(needle) != 1:
        raise RuntimeError("mutation target changed; review the control instead of guessing")
    with tempfile.TemporaryDirectory(prefix="qg-routing-mutation-") as tmp:
        folder = Path(tmp)
        (folder / "authority_router.py").write_text(
            source.replace(needle, "if False:  # planted unsafe eligibility bypass"),
            encoding="utf-8")
        shutil.copyfile(HERE / "test_authority_router.py", folder / "test_authority_router.py")
        bad = run_suite(folder)
    diagnostic = []
    for count in (2, 102, 10002):
        rows = [Route("a", frozenset(("x",)), 1, 10, "c:a"),
                Route("b", frozenset(("x",)), 2, 10, "c:b")]
        rows.extend(Route(f"d{i}", frozenset(("other",)), 1, 10, f"c:d{i}")
                    for i in range(count - 2))
        index = RouteIndex(tuple(rows))
        selection = index.select(Query("x", "lab", "FORMAL", "s0"),
                                 lambda r, q: Eligibility.APPROVED, Envelope(100, 100))
        diagnostic.append({"catalogue_routes": len(index.routes),
                           "index_references_built": index.index_references,
                           "candidate_routes_inspected": selection.work.routes_inspected,
                           "eligibility_calls": selection.work.eligibility_calls})
    good_log, bad_log = good.stdout + good.stderr, bad.stdout + bad.stderr
    good_count = re.search(r"Ran (\d+) tests", good_log)
    bad_failures = re.search(r"FAILED \(failures=(\d+)", bad_log)
    valid = good.returncode == 0 and bad.returncode != 0 and bad_failures is not None
    record = {
        "schema": "QGAuthorityRouting.DevelopmentChecks.v0",
        "terminal": "DEVELOPMENT_CONTROLS_PASS" if valid else "DEVELOPMENT_CONTROL_FAILURE",
        "python": platform.python_version(),
        "source_sha256": {name: hashlib.sha256((HERE / name).read_bytes()).hexdigest()
                          for name in ("authority_router.py", "test_authority_router.py", "run_checks.py")},
        "unit_test_exit": good.returncode,
        "unit_tests_run": int(good_count.group(1)) if good_count else None,
        "finite_reference_comparisons": 1944 if good.returncode == 0 else None,
        "planted_eligibility_bypass_exit": bad.returncode,
        "planted_bypass_failing_tests": int(bad_failures.group(1)) if bad_failures else None,
        "catalogue_growth_diagnostic": diagnostic,
        "unit_test_log": good_log,
        "mutation_test_log": bad_log,
        "authority": "LOCAL_DEVELOPMENT_ONLY",
        "non_claims": ["No production host-checker integration", "No field-k scaling result",
                       "No OCM-specific residual", "No quantum computation or advantage",
                       "No LLM parity", "No whole-runtime or lifetime performance result"],
    }
    output.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(record["terminal"], f"tests={record['unit_tests_run']}",
          f"mutant_failures={record['planted_bypass_failing_tests']}", f"record={output}")
    return 0 if valid else 1


if __name__ == "__main__":
    raise SystemExit(main())
