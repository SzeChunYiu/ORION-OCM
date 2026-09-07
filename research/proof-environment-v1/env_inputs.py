"""Strict, create-only custody records. Hashes bind bytes; the evaluator authorizes them."""
from hashlib import sha256
import json
import os
from pathlib import Path
import re
import shutil
import stat


def canonical(value):
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False, ensure_ascii=False) + "\n").encode()


def _pairs(items):
    value = {}
    for key, item in items:
        if key in value: raise ValueError("duplicate JSON key: " + key)
        value[key] = item
    return value


def parse_json(raw):
    return json.loads(raw, object_pairs_hook=_pairs,
                      parse_constant=lambda value: (_ for _ in ()).throw(ValueError(value)))


def digest(value): return sha256(value).hexdigest()


def valid_hash(value):
    if type(value) is not str or re.fullmatch("[0-9a-f]{64}", value) is None:
        raise ValueError("SHA256 required")
    return value


def regular(path):
    path = Path(path)
    if not path.is_absolute() or path.resolve(strict=True) != path or not path.is_file():
        raise ValueError("canonical regular file required: " + str(path))
    return path


def file_record(path):
    path = regular(path); value = sha256(); size = 0
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(block); size += len(block)
    return {"sha256": value.hexdigest(), "bytes": size}


def verify_file(record):
    if type(record) is not dict or set(record) != {"path", "sha256", "bytes"}:
        raise ValueError("exact file record required")
    valid_hash(record["sha256"])
    if type(record["bytes"]) is not int or record["bytes"] < 0:
        raise ValueError("invalid file size")
    if file_record(record["path"]) != {k: record[k] for k in ("sha256", "bytes")}:
        raise ValueError("file binding differs: " + record["path"])
    return Path(record["path"])


def bound_json(path, expected_sha256):
    valid_hash(expected_sha256)
    raw = regular(path).read_bytes()
    if digest(raw) != expected_sha256: raise ValueError("independently registered digest differs")
    value = parse_json(raw)
    if type(value) is not dict: raise ValueError("JSON object required")
    return value


def write_bytes(path, value):
    with Path(path).open("xb") as stream: stream.write(value)


def write_json(path, value): write_bytes(path, canonical(value))


def snapshot(record, destination):
    source = verify_file(record)
    with source.open("rb") as src, Path(destination).open("xb") as dst:
        shutil.copyfileobj(src, dst, 1024 * 1024)
    copied = {"path": str(Path(destination).absolute()), **file_record(Path(destination).absolute())}
    if copied["sha256"] != record["sha256"] or copied["bytes"] != record["bytes"]:
        raise ValueError("copy differs from authorized file")
    verify_file(record)
    return copied


def relative_name(value):
    if type(value) is not str: raise ValueError("relative file name required")
    path = Path(value)
    if path.is_absolute() or not value or value != path.as_posix() or any(p in ("", ".", "..") for p in value.split("/")):
        raise ValueError("noncanonical relative file name")
    return value


def inventory(root):
    root = Path(root)
    if not root.is_absolute() or root.resolve(strict=True) != root or not root.is_dir():
        raise ValueError("canonical artifact directory required")
    result = {}
    for path in sorted(root.rglob("*")):
        if path.is_symlink(): raise ValueError("artifact symlink")
        if path.is_file(): result[path.relative_to(root).as_posix()] = file_record(path)
        elif not path.is_dir(): raise ValueError("nonregular artifact")
    return result


def verify_inventory(root, expected):
    if type(expected) is not dict: raise ValueError("inventory object required")
    for name in expected: relative_name(name)
    if inventory(root) != expected: raise ValueError("artifact inventory differs")


def artifact_diagnostics(root):
    """Non-following names/kinds only; never substitutes for a verified inventory."""
    result = []
    for current, directories, files in os.walk(root, followlinks=False):
        for name in sorted(directories + files):
            path = Path(current) / name
            try:
                mode = path.lstat().st_mode
                kind = ("symlink" if stat.S_ISLNK(mode) else "file" if stat.S_ISREG(mode)
                        else "directory" if stat.S_ISDIR(mode) else "nonregular")
            except OSError as exc: kind = "unreadable:" + type(exc).__name__
            result.append({"path": path.relative_to(root).as_posix(), "kind": kind})
    return result


def create_root(path):
    path = Path(path).absolute()
    if path.parent.resolve(strict=True) != path.parent:
        raise ValueError("linked output parent")
    path.mkdir(exist_ok=False)
    return path
