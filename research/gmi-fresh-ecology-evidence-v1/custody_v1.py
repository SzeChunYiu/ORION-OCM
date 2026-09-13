"""Whole-unit custody with an immutable manifest anchor across the static worker."""
import hashlib
import json
import os
from pathlib import Path

HERE = Path(__file__).resolve().parent
MANIFEST = "MANIFEST_V1.json"


def files(root):
    result = set()
    def walk(directory):
        with os.scandir(directory) as entries:
            for item in entries:
                path = Path(item.path)
                if item.is_symlink():
                    raise ValueError("symlink")
                if item.is_dir(follow_symlinks=False):
                    walk(path)
                elif item.is_file(follow_symlinks=False):
                    result.add(path.relative_to(root).as_posix())
                else:
                    raise ValueError("nonregular file")
    walk(root)
    return result


def verify(root=HERE):
    raw = (root / MANIFEST).read_bytes()
    manifest = json.loads(raw)
    entries = manifest["files"]
    actual = files(root)
    if actual != set(entries) | {MANIFEST}:
        raise ValueError("complete membership differs")
    for name, expected in entries.items():
        parts = Path(name)
        if parts.is_absolute() or ".." in parts.parts or not parts.parts:
            raise ValueError("unsafe path")
        content = (root / name).read_bytes()
        if expected != {"sha256": hashlib.sha256(content).hexdigest(), "bytes": len(content)}:
            raise ValueError("payload differs: " + name)
    return raw


def replay(worker=None, root=HERE):
    anchor = verify(root)
    expected = (root / "RECEIPT_V1.json").read_bytes()
    if worker is None:
        from check_v1 import run
        worker = run
    payload = worker()
    if (root / MANIFEST).read_bytes() != anchor:
        raise ValueError("manifest changed during worker")
    verify(root)
    encoded = (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode()
    if encoded != expected:
        raise ValueError("complete receipt differs")
    return payload
