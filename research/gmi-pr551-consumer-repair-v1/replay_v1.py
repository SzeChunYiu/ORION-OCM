"""Whole static receipt replay with a fixed pre-worker manifest and payload."""
from pathlib import Path
import hashlib
import json
import os
import stat
import subprocess
import sys
HERE = Path(__file__).resolve().parent


def verify(base=HERE):
    anchor = (base / "MANIFEST_V1.json").read_bytes()
    expected = json.loads(anchor)["files"]
    actual = {}
    def walk(folder):
        with os.scandir(folder) as entries:
            for entry in entries:
                mode = entry.stat(follow_symlinks=False).st_mode
                path = Path(entry.path)
                if stat.S_ISDIR(mode):
                    walk(path)
                elif stat.S_ISREG(mode):
                    relative = path.relative_to(base).as_posix()
                    if relative != "MANIFEST_V1.json":
                        raw = path.read_bytes()
                        actual[relative] = {"bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}
                else:
                    raise ValueError("nonregular unit entry")
    if (base / "MANIFEST_V1.json").is_symlink():
        raise ValueError("linked manifest")
    walk(base)
    if actual != expected:
        raise ValueError("complete unit membership/content differs")
    return anchor, (base / "REPAIR_RECEIPT_V1.json").read_bytes()


def replay(base=HERE, worker=subprocess.run):
    before, expected = verify(base)
    command = [sys.executable, "-I", "-B"] + (["-O"] if sys.flags.optimize else [])
    result = worker(command + [str(base / "check_consumer_repair_v1.py")],
                    capture_output=True, check=True)
    after, _ = verify(base)
    if after != before:
        raise ValueError("worker changed manifest authority")
    if result.stderr or result.stdout != expected:
        raise ValueError("whole static receipt differs")
    return result.stdout


if __name__ == "__main__":
    sys.stdout.buffer.write(replay())
