"""Validate fail-closed source checks on actual frozen unit copies, on laptop."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import py_compile
import shutil
import subprocess
import sys
import tempfile


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--receipt", required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parent
    records = []
    with tempfile.TemporaryDirectory(prefix="gmi-neutral-controls-") as temporary:
        temp = Path(temporary)
        cases = ("unchanged", "stale_pyc", "changed_source", "missing_source", "extra_source",
                 "changed_registration", "changed_binding", "bad_freeze_root", "receipt_collision",
                 "mutation_during_replay")
        for case in cases:
            unit = temp / case / "research" / root.name
            unit.parent.mkdir(parents=True)
            shutil.copytree(root, unit, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
            for sibling in root.parent.iterdir():
                if sibling.name != root.name:
                    (unit.parent / sibling.name).symlink_to(sibling, target_is_directory=sibling.is_dir())
            if case == "stale_pyc":
                source = unit / "orbit_compiler.py"
                original, stat = source.read_bytes(), source.stat()
                forged = b'raise RuntimeError("stale compiled source loaded")\n'
                source.write_bytes(forged + b" " * (len(original) - len(forged)))
                os.utime(source, ns=(stat.st_atime_ns, stat.st_mtime_ns))
                py_compile.compile(str(source), doraise=True)
                source.write_bytes(original)
                os.utime(source, ns=(stat.st_atime_ns, stat.st_mtime_ns))
            elif case == "changed_source":
                with (unit / "orbit_compiler.py").open("a") as stream:
                    stream.write("\n# deliberate control mutation\n")
            elif case == "missing_source":
                (unit / "orbit_compiler.py").unlink()
            elif case == "extra_source":
                (unit / "unregistered_extra.py").write_text("pass\n")
            elif case == "changed_registration":
                with (unit / "orbit_registration.json").open("a") as stream:
                    stream.write("\n")
            elif case == "changed_binding":
                (unit / "SHA256SUMS").write_text("0" * 64 + "  UNIT_FREEZE.json\n")
            elif case == "bad_freeze_root":
                raw = b"[]\n"
                (unit / "UNIT_FREEZE.json").write_bytes(raw)
                (unit / "SHA256SUMS").write_text(hashlib.sha256(raw).hexdigest() + "  UNIT_FREEZE.json\n")
            elif case == "mutation_during_replay":
                source = unit / "proof_runtime.py"
                with source.open("a") as stream:
                    stream.write('\ndef run(root, inventory):\n'
                                 '    path = root / "orbit_registration.json"\n'
                                 '    path.write_bytes(path.read_bytes() + b"\\n")\n'
                                 '    raise ValueError("deliberate after-start mutation")\n')
                freeze = json.loads((unit / "UNIT_FREEZE.json").read_text())
                freeze["source_sha256"][source.name] = hashlib.sha256(source.read_bytes()).hexdigest()
                raw = (json.dumps(freeze, sort_keys=True, indent=2) + "\n").encode()
                (unit / "UNIT_FREEZE.json").write_bytes(raw)
                (unit / "SHA256SUMS").write_text(hashlib.sha256(raw).hexdigest() + "  UNIT_FREEZE.json\n")
            replay = temp / (case + "-replay.json")
            original = (unit / "orbit_compiler.py").read_bytes() if case == "receipt_collision" else None
            if case == "receipt_collision":
                replay = unit / "orbit_compiler.py"
            proc = subprocess.run([sys.executable, "-B", str(unit / "verify_unit.py"),
                                   "--receipt", str(replay)], capture_output=True, text=True)
            try:
                output = json.loads(proc.stdout)
            except ValueError as error:
                raise RuntimeError(case + " did not produce structured status: " + proc.stderr) from error
            positive = case in ("unchanged", "stale_pyc")
            expected = 0 if positive else 2
            status = "CHECKED" if positive else "NOT_CHECKED"
            if proc.returncode != expected or output.get("status") != status:
                raise RuntimeError(case + " has wrong status: " + proc.stdout + proc.stderr)
            if positive:
                if not replay.is_file() or json.loads(replay.read_text())["status"] != "CHECKED":
                    raise RuntimeError("unchanged control failed to execute the actual unit")
            elif case == "receipt_collision":
                if replay.read_bytes() != original:
                    raise RuntimeError("receipt collision altered protected source")
            elif replay.exists():
                raise RuntimeError(case + " emitted success evidence without checking")
            records.append({"case": case, "returncode": proc.returncode, "status": status})
    result = {"status": "CHECKED", "controls": records}
    Path(args.receipt).write_text(json.dumps(result, sort_keys=True, indent=2) + "\n")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
