"""Validate the verifier against real source mutations on disposable laptop copies."""
import hashlib
import json
import os
from pathlib import Path
import py_compile
import shutil
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parent


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(path, freeze=False):
    command = [sys.executable, "-I", "-B", str(path / "verify_unit.py")]
    if freeze:
        command.append("--freeze")
    result = subprocess.run(command, text=True, capture_output=True, timeout=120)
    return result.returncode, result.stdout, result.stderr


def main():
    original = {str(p.relative_to(ROOT)): digest(p) for p in ROOT.rglob("*")
                if p.is_file() and "__pycache__" not in p.parts}
    receipt = []

    def control(name, mutate, expected, freeze=False):
        with tempfile.TemporaryDirectory(prefix="gmi-formal-control-", dir=ROOT.parent) as temp:
            target = Path(temp)
            shutil.copytree(ROOT, target, dirs_exist_ok=True,
                            ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
            before = {n: (target / n).read_bytes() for n in ("FREEZE.json", "SHA256SUMS")}
            mutate(target)
            after_mutation = {n: (target / n).read_bytes() for n in before}
            code, stdout, stderr = run(target, freeze)
            require(code == expected, f"{name}: expected {expected}, got {code}: {stdout} {stderr}")
            if freeze:
                require(all((target/n).read_bytes() == after_mutation[n] for n in before),
                        f"{name}: failed freeze overwrote evidence")
            receipt.append({"control": name, "returncode": code})

    def no_change(path):
        pass

    def theorem_mutation(path):
        with (path / "AXIOMS.md").open("a") as stream:
            stream.write("\nMutation control.\n")

    def false_bellman(path, stale=False):
        source = path / "tests_composition.py"
        original_stat = source.stat()
        text = source.read_text()
        require(text.count("values = [max(") == 1, "Bellman mutation target changed")
        if stale:
            py_compile.compile(str(source), doraise=True)
        source.write_text(text.replace("values = [max(", "values = [min("))
        if stale:
            os.utime(source, ns=(original_stat.st_atime_ns, original_stat.st_mtime_ns))

    def expected_failure(path):
        (path / "tests_sacrificial.py").write_text(
            "import unittest\nclass Masked(unittest.TestCase):\n"
            "    @unittest.expectedFailure\n    def test_false(self):\n"
            "        self.assertEqual(0,1)\n")

    def execution_mutation(path):
        (path / "tests_sacrificial.py").write_text(
            "import unittest\nfrom pathlib import Path\n"
            "class Mutation(unittest.TestCase):\n    def test_mutate(self):\n"
            "        p=Path(__file__).with_name('AXIOMS.md')\n"
            "        p.write_text(p.read_text()+'\\nChanged during execution.\\n')\n")

    def malformed(path):
        manifest = path / "FREEZE.json"
        manifest.write_text("[]\n")
        (path / "SHA256SUMS").write_text(digest(manifest) + "  FREEZE.json\n")

    def execution_freeze_mutation(path):
        (path / "tests_sacrificial.py").write_text(
            "import unittest\nfrom pathlib import Path\nimport hashlib\n"
            "class Mutation(unittest.TestCase):\n    def test_mutate(self):\n"
            "        p=Path(__file__).with_name('FREEZE.json')\n"
            "        p.write_bytes(p.read_bytes()+b' ')\n"
            "        p.with_name('SHA256SUMS').write_text(\n"
            "            hashlib.sha256(p.read_bytes()).hexdigest()+'  FREEZE.json\\n')\n")
        # Bind the added test so normal replay reaches the execution mutation.
        manifest = path / "FREEZE.json"
        frozen = json.loads(manifest.read_text())
        frozen["source_sha256"]["tests_sacrificial.py"] = digest(path / "tests_sacrificial.py")
        frozen["tests"].append("tests_sacrificial.Mutation.test_mutate")
        frozen["tests"].sort()
        frozen["tests_run"] += 1
        manifest.write_text(json.dumps(frozen, indent=2, sort_keys=True) + "\n")
        (path / "SHA256SUMS").write_text(digest(manifest) + "  FREEZE.json\n")

    def wrong_transport(path):
        source = path / "tests_state_discovery.py"
        text = source.read_text()
        target = "_, transported = learned_table[2*learned_state]"
        require(text.count(target) == 1, "transport mutation target changed")
        source.write_text(text.replace(target, "_, transported = learned_table[2]"))

    control("unmodified_real_unit", no_change, 0)
    control("changed_theorem_bytes", theorem_mutation, 2)
    control("false_bellman_maximum", false_bellman, 1, True)
    control("stale_bytecode_equal_size_mtime", lambda p: false_bellman(p, True), 1, True)
    control("expected_failure_cannot_pass", expected_failure, 1, True)
    control("source_changed_during_tests", execution_mutation, 2, True)
    control("malformed_bound_manifest", malformed, 2)
    control("freeze_changed_during_tests", execution_freeze_mutation, 2)
    control("reset_instead_of_transport", wrong_transport, 1, True)
    code, stdout, stderr = run(ROOT)
    require(code == 0, f"final no-alarm replay failed: {stdout} {stderr}")
    final = {str(p.relative_to(ROOT)): digest(p) for p in ROOT.rglob("*")
             if p.is_file() and "__pycache__" not in p.parts}
    require(final == original, "hostile controls changed the original unit")
    print(json.dumps({"status": "CHECKED", "controls": receipt,
                      "original_unchanged": True, "final_no_alarm": True}, indent=2))


if __name__ == "__main__":
    main()
