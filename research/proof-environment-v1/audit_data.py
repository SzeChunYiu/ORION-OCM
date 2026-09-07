"""Portable exact-byte archive inspection. No extraction, imports or native dispatch."""
from hashlib import sha256
import json
import math
from pathlib import Path, PurePosixPath
import tarfile


def require(condition, message):
    if not condition: raise ValueError(message)


def canonical(value):
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False) + "\n").encode()


def same(left, right): return canonical(left) == canonical(right)


def load_json(raw):
    def pairs(items):
        result = {}
        for key, value in items:
            require(key not in result, "duplicate JSON key")
            result[key] = value
        return result
    def floating(value):
        result = float(value)
        require(math.isfinite(result), "nonfinite JSON number")
        return result
    def reject(value): raise ValueError("nonfinite JSON constant: " + value)
    return json.loads(raw, object_pairs_hook=pairs, parse_float=floating, parse_constant=reject)


def record(raw): return {"sha256": sha256(raw).hexdigest(), "bytes": len(raw)}


def bound(raw, binding, label):
    require(type(binding) is dict and type(binding.get("bytes")) is int and binding["bytes"] >= 0,
            label + ": invalid byte count")
    require(same(record(raw), {k: binding[k] for k in ("sha256", "bytes")}), label + ": byte binding differs")
    return raw


def member_name(name):
    require(type(name) is str and name and "\\" not in name, "invalid member name")
    path = PurePosixPath(name)
    require(not path.is_absolute() and path.as_posix() == name and
            all(part not in ("", ".", "..") for part in name.split("/")), "noncanonical member name")
    return name


def file_bytes(path):
    path = Path(path).absolute()
    require(path.resolve(strict=True) == path and path.is_file(), "nonregular or noncanonical file")
    return path.read_bytes()


def inventory(data): return {name: record(raw) for name, raw in sorted(data.items())}


def read_archive(path, expected):
    require(type(expected) is dict, "member inventory required")
    for name, binding in expected.items():
        member_name(name)
        require(type(binding) is dict and set(binding) == {"sha256", "bytes"}, "exact member binding required")
        require(type(binding["bytes"]) is int and binding["bytes"] >= 0, "invalid member size")
    data = {}
    with tarfile.open(path, "r:gz") as archive:
        for item in archive:
            name = member_name(item.name)
            require(item.isfile() and not item.issparse(), "nonregular archive member")
            require(name in expected and name not in data, "unexpected or duplicate archive member")
            require(item.size == expected[name]["bytes"], "archive member size differs")
            stream = archive.extractfile(item)
            require(stream is not None, "missing member bytes")
            with stream: raw = stream.read(item.size + 1)
            data[name] = bound(raw, expected[name], name)
    require(set(data) == set(expected), "archive membership differs")
    return data
