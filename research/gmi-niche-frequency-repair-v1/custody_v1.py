"""Complete content custody for this standalone unit, with fixed before/after anchors."""
from pathlib import Path
import hashlib
import json
import os
import stat

HERE = Path(__file__).resolve().parent


def encoded(value):
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def verify(root=HERE):
    root = Path(root)
    anchor = (root / "MANIFEST_V1.json").read_bytes()
    expected = json.loads(anchor)["files"]
    observed = {}
    def walk(directory):
        with os.scandir(directory) as entries:
            for entry in entries:
                path = Path(entry.path)
                mode = entry.stat(follow_symlinks=False).st_mode
                if stat.S_ISLNK(mode):
                    raise ValueError("symlink in bound unit")
                if stat.S_ISDIR(mode):
                    walk(path)
                elif stat.S_ISREG(mode):
                    name = path.relative_to(root).as_posix()
                    if name != "MANIFEST_V1.json":
                        data = path.read_bytes()
                        observed[name] = {"bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}
                else:
                    raise ValueError("nonregular member")
    walk(root)
    if observed != expected:
        raise ValueError("complete unit membership/content mismatch")
    return anchor


def replay(root=HERE):
    root = Path(root)
    if root.resolve() != HERE.resolve():
        raise ValueError("replay requires this imported source root")
    anchor = verify(root)
    expected = (root / "RECEIPT_V1.json").read_bytes()
    from check_v1 import run
    actual = encoded(run())
    if verify(root) != anchor:
        raise ValueError("manifest changed during worker")
    if (root / "RECEIPT_V1.json").read_bytes() != expected:
        raise ValueError("receipt changed during worker")
    if actual != expected:
        raise ValueError("complete payload mismatch")
    return actual
