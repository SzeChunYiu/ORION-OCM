"""Verify and replay recovered historical sources. Trusted repository/host only."""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import subprocess
import sys
import tarfile
import tempfile
import xml.etree.ElementTree as ET

BASE = "3039e233486252c5092728ab5fbdcdac0aa61ab4"
MANIFEST_SHA256 = "3cc8e20a2525dd542390856823b6815f7c929183d6e2dfd39dce35bc88405278"
PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
TESTS = ["test_recursive_kso_v0.py", "test_kso_exact_checker_sympy_v1.py",
         "test_kso_algebra_quadratic_v1.py", "test_kso_m2b_algebra_population_v1.py"]


class CannotCheck(ValueError):
    pass


def digest(data):
    return hashlib.sha256(data).hexdigest()


def regular(root, relative):
    path = PurePosixPath(relative)
    if path.is_absolute() or ".." in path.parts or not path.parts:
        raise CannotCheck("invalid relative path")
    # The package location is the caller's trusted root. Inspect only its
    # descendants; an unrelated symlink above a checkout is not source drift.
    result = Path(root).resolve()
    for part in path.parts:
        result = result / part
        if result.is_symlink():
            raise CannotCheck("symlink source is unsupported")
    if not result.is_file():
        raise CannotCheck("missing source: " + relative)
    return result


def verify(package=PACKAGE):
    raw = regular(package, "MANIFEST_V1.json").read_bytes()
    if digest(raw) != MANIFEST_SHA256:
        raise CannotCheck("source inventory identity changed")
    manifest = json.loads(raw)
    if manifest["ocm_base"] != BASE or len(manifest["files"]) != 39:
        raise CannotCheck("unexpected source boundary")
    for row in manifest["files"]:
        data = regular(package, row["archive_path"]).read_bytes()
        blob = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
        if digest(data) != row["sha256"] or blob != row["source_blob"]:
            raise CannotCheck("historical source drift: " + row["source_path"])
    adapter = manifest["adapter"]
    if digest(regular(package, adapter["path"]).read_bytes()) != adapter["sha256"]:
        raise CannotCheck("adapter identity changed")
    return manifest


def materialize(destination, manifest):
    # Build from Git bytes, never the working tree or pre-existing bytecode caches.
    git = lambda *args: subprocess.check_output(["git", *args], cwd=ROOT)
    if git("rev-parse", BASE + "^{commit}").decode().strip() != BASE:
        raise CannotCheck("historical OCM base unavailable")
    candidates = ["research/orion-machine", "research/experiments", "src"]
    paths = [p for p in candidates if git("ls-tree", BASE, "--", p)]
    payload = git("archive", BASE, *paths)
    with tarfile.open(fileobj=io.BytesIO(payload)) as archive:
        for member in archive:
            path = PurePosixPath(member.name)
            if path.is_absolute() or ".." in path.parts:
                raise CannotCheck("invalid Git archive path")
            if member.isdir():
                continue
            if not member.isfile():
                raise CannotCheck("nonregular Git archive member")
            target = destination / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(archive.extractfile(member).read())
    for row in manifest["files"]:
        target = destination / row["source_path"]
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(regular(PACKAGE, row["archive_path"]).read_bytes())
    adapter = manifest["adapter"]
    (destination / adapter["source_path"]).write_bytes(regular(PACKAGE, adapter["path"]).read_bytes())


def replay():
    manifest = verify()
    # The original importorskip is not a waiver for this successor gate.
    import pytest
    import sympy
    with tempfile.TemporaryDirectory(prefix="ocm-migration-") as tmp:
        target = Path(tmp)
        materialize(target, manifest)
        env = dict(os.environ, PYTHONPATH=str(target / "src"),
                   PYTHONDONTWRITEBYTECODE="1", PYTEST_DISABLE_PLUGIN_AUTOLOAD="1")
        result = subprocess.run([sys.executable, "-m", "pytest", "-q", "-o", "addopts=",
                                 *["tests/unit/" + name for name in TESTS],
                                 "--junitxml=result.xml"], cwd=target, env=env,
                                capture_output=True, text=True, timeout=180)
        print(result.stdout, file=sys.stderr)
        if result.returncode:
            raise CannotCheck("recovered-source test failure: exit " + str(result.returncode))
        suites = ET.parse(target / "result.xml").getroot()
        cases = list(suites.iter("testcase"))
        failures = list(suites.iter("failure")) + list(suites.iter("error")) + list(suites.iter("skipped"))
        if len(cases) != 35 or failures:
            raise CannotCheck("required denominator is 35 passed with no skip/error/failure")
    verify()  # Reject package drift during execution.
    return {"schema": "OCM_MIGRATION_REPLAY_V1", "status": "ENGINEERING_REPLAY_PASS",
            "source_files": 39, "tests_passed": 35, "manifest_sha256": MANIFEST_SHA256,
            "ocm_base": BASE, "python": sys.version.split()[0],
            "pytest": pytest.__version__, "sympy": sympy.__version__,
            "scientific_adoption": False, "historical_result_rewritten": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify-only", action="store_true")
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    try:
        if args.out and args.out.exists():
            raise CannotCheck("new output path required")
        result = {"status": "SOURCE_CUSTODY_PASS", "source_files": len(verify()["files"])} if args.verify_only else replay()
        text = json.dumps(result, indent=2) + "\n"
        if args.out:
            with args.out.open("x") as handle:
                handle.write(text)
        print(text, end="")
        return 0
    except (CannotCheck, OSError, ValueError, ImportError, subprocess.SubprocessError, ET.ParseError) as exc:
        print(json.dumps({"status": "CANNOT_CHECK", "reason": str(exc)}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
