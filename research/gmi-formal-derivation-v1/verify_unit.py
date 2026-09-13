"""Source-bound finite proof witnesses; not a proof-assistant formalization.

Run on the verification host. --freeze records successful current witnesses.
Exit 0 = checked; 1 = mathematical witness failed; 2 = source/contract not checked.
"""
import argparse
import hashlib
import io
import json
from pathlib import Path
import re
import sys
import types
import unittest


ROOT = Path(__file__).resolve().parent
BASE = "c0344314805b60e7c1c1aec2f5635ee98cfb2951"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inventory():
    files = sorted(p for p in ROOT.rglob("*") if p.is_file()
                   and p.suffix in {".md", ".py"})
    return {str(p.relative_to(ROOT)): sha(p) for p in files}


def contracts():
    problems = []
    for path in sorted(ROOT.glob("*.md")):
        text = path.read_text()
        lines = len(text.splitlines())
        if lines > 180 or (path.name == "CORE.md" and lines > 70):
            problems.append(f"overlong module: {path.name} ({lines})")
        for target in re.findall(r"\]\(([^)]+)\)", text):
            if target.startswith(("https://", "http://", "#")):
                continue
            target = target.split("#", 1)[0]
            if target and not (path.parent / target).exists():
                problems.append(f"missing local link in {path.name}: {target}")
    return problems


def flattened(suite):
    for item in suite:
        if isinstance(item, unittest.TestSuite):
            yield from flattened(item)
        else:
            yield item.id()


def run_witnesses(source):
    # Compile the bound bytes directly: -B alone does not prevent stale .pyc reads.
    # Test modules are self-contained except for standard-library imports.
    suite = unittest.TestSuite()
    for path in sorted(ROOT.glob("tests_*.py")):
        data = path.read_bytes()
        if hashlib.sha256(data).hexdigest() != source[path.name]:
            raise ValueError("test source changed before execution")
        module = types.ModuleType(path.stem)
        module.__file__ = str(path)
        sys.modules[path.stem] = module
        exec(compile(data, str(path), "exec"), module.__dict__)
        suite.addTests(unittest.defaultTestLoader.loadTestsFromModule(module))
    names = sorted(flattened(suite))
    stream = io.StringIO()
    result = unittest.TextTestRunner(stream=stream, verbosity=2).run(suite)
    return result, names, stream.getvalue()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--freeze", action="store_true")
    args = parser.parse_args()
    source = inventory()
    problems = contracts()
    manifest_path = ROOT / "FREEZE.json"
    binding_path = ROOT / "SHA256SUMS"
    evidence_paths = (manifest_path, binding_path)
    evidence_before = tuple(p.read_bytes() if p.is_file() else None
                            for p in evidence_paths)
    frozen = None
    if not args.freeze:
        if not manifest_path.is_file() or not binding_path.is_file():
            problems.append("missing source freeze or manifest binding")
        else:
            try:
                frozen = json.loads(evidence_before[0])
                if not isinstance(frozen, dict):
                    raise ValueError("freeze root must be an object")
                if (frozen.get("schema") != "GMI_FORMAL_DERIVATION_FINITE_UNIT_V1"
                        or frozen.get("scientific_base") != BASE
                        or not isinstance(frozen.get("tests"), list)
                        or not all(isinstance(x, str) for x in frozen["tests"])
                        or type(frozen.get("tests_run")) is not int):
                    raise ValueError("freeze schema or lineage mismatch")
                if frozen.get("source_sha256") != source:
                    problems.append("source inventory differs from frozen content")
                expected_binding = hashlib.sha256(evidence_before[0]).hexdigest() + "  FREEZE.json\n"
                if evidence_before[1] != expected_binding.encode():
                    problems.append("manifest binding differs")
            except (ValueError, OSError) as exc:
                problems.append(f"unreadable freeze: {type(exc).__name__}")
    if problems:
        print(json.dumps({"status": "NOT_CHECKED", "problems": problems}, indent=2))
        return 2
    result, names, output = run_witnesses(source)
    if inventory() != source:
        print(json.dumps({"status": "NOT_CHECKED", "problems": ["source changed during execution"]}))
        return 2
    evidence_after = tuple(p.read_bytes() if p.is_file() else None
                           for p in evidence_paths)
    if evidence_after != evidence_before:
        print(json.dumps({"status": "NOT_CHECKED", "problems": ["freeze changed during execution"]}))
        return 2
    if not names or not result.wasSuccessful() or result.skipped or result.expectedFailures:
        print(output, file=sys.stderr)
        print(json.dumps({"status": "WITNESS_FAILED", "tests_run": result.testsRun}))
        return 1
    if args.freeze:
        frozen = {"schema": "GMI_FORMAL_DERIVATION_FINITE_UNIT_V1",
                  "scientific_base": BASE,
                  "scope": "exact finite witnesses plus separately reviewed analytic proofs",
                  "source_sha256": source, "tests": names, "tests_run": result.testsRun}
        manifest_path.write_text(json.dumps(frozen, indent=2, sort_keys=True) + "\n")
        binding_path.write_text(sha(manifest_path) + "  FREEZE.json\n")
    elif names != frozen.get("tests") or result.testsRun != frozen.get("tests_run"):
        print(json.dumps({"status": "NOT_CHECKED", "problems": ["test inventory differs"]}))
        return 2
    reported_manifest = manifest_path.read_bytes() if args.freeze else evidence_before[0]
    print(json.dumps({"status": "CHECKED", "source_files": len(source),
                      "tests_run": result.testsRun, "tests": names,
                      "manifest_sha256": hashlib.sha256(reported_manifest).hexdigest(),
                      "scope": "finite witnesses; no universal or physical completion claim"},
                     indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        result_code = main()
    except (OSError, ValueError, UnicodeError, SyntaxError, KeyError) as exc:
        print(json.dumps({"status": "NOT_CHECKED", "problems": [type(exc).__name__]}))
        result_code = 2
    raise SystemExit(result_code)
