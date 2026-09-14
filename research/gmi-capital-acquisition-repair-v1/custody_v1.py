"""Complete source/receipt custody under a declared trusted process."""
import hashlib
import json
import math
from pathlib import Path
import stat
import subprocess
import sys

HERE = Path(__file__).absolute().parent
MANIFEST = "MANIFEST_V1.json"
RECEIPT = "RECEIPT_V1.json"


def finite_json(data):
    def pairs(items):
        out = {}
        for k, v in items:
            if k in out:
                raise ValueError("duplicate JSON key")
            out[k] = v
        return out
    value = json.loads(data, object_pairs_hook=pairs)
    def walk(x):
        if isinstance(x, float) and not math.isfinite(x):
            raise ValueError("nonfinite JSON")
        if isinstance(x, dict):
            for v in x.values():
                walk(v)
        if isinstance(x, list):
            for v in x:
                walk(v)
    walk(value)
    return value


def verify(root=HERE):
    root = Path(root)
    if not stat.S_ISDIR(root.lstat().st_mode):
        raise ValueError("unit must be a regular directory")
    original = (root / MANIFEST).read_bytes()
    manifest = finite_json(original)
    if set(manifest) != {"schema", "files"} or manifest["schema"] != "GMI_CAPITAL_ACQUISITION_MANIFEST_V1":
        raise ValueError("manifest schema")
    rows = manifest["files"]
    actual = {}
    def descend(directory):
        for p in directory.iterdir():
            kind = p.lstat().st_mode
            if stat.S_ISDIR(kind):
                descend(p)
            elif stat.S_ISREG(kind):
                actual[p.relative_to(root).as_posix()] = p
            else:
                raise ValueError("nonregular unit member")
    descend(root)
    if set(actual) != set(rows) | {MANIFEST}:
        raise ValueError("complete manifest membership mismatch")
    for name, binding in rows.items():
        if Path(name).is_absolute() or any(x in (".", "..") for x in name.split("/")):
            raise ValueError("noncanonical member")
        if set(binding) != {"bytes", "sha256"} or type(binding["bytes"]) is not int:
            raise ValueError("member schema")
        data = actual[name].read_bytes()
        if len(data) != binding["bytes"] or hashlib.sha256(data).hexdigest() != binding["sha256"]:
            raise ValueError("content binding mismatch: " + name)
    expected = (root / RECEIPT).read_bytes()
    finite_json(expected)
    source = finite_json((root / "raw/SOURCE_BINDINGS_V1.json").read_bytes())
    for name, binding in source.items():
        if rows[name] != {k: binding[k] for k in ("bytes", "sha256")}:
            raise ValueError("source authority mismatch")
    return original, expected


def replay(root=HERE, worker=None):
    root = Path(root)
    if root.resolve() != HERE.resolve():
        raise ValueError("replay must execute this imported unit")
    manifest, expected = verify(root)
    if worker is None:
        def worker():
            process = subprocess.run([sys.executable, "-I", "-B"] + (["-O"] if sys.flags.optimize else []) + [str(root / "check_v1.py")],
                                     capture_output=True, check=True, timeout=30)
            if process.stderr:
                raise ValueError("worker stderr is nonempty")
            return process.stdout
    actual = worker()
    if (root / MANIFEST).read_bytes() != manifest:
        raise ValueError("manifest changed during replay")
    verify(root)
    if actual != expected:
        raise ValueError("complete original payload mismatch")
    return finite_json(actual)
