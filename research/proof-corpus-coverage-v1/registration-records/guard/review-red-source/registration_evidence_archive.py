"""Read and hash regular archive members without extracting or executing them."""
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import stat
import tarfile


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def identity(raw):
    return {"sha256": hashlib.sha256(raw).hexdigest(), "bytes": len(raw)}


def canonical(value):
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False) + "\n").encode()


def decode(raw):
    def pairs(items):
        result = {}
        for key, value in items:
            require(key not in result, "duplicate JSON key")
            result[key] = value
        return result
    def invalid(value):
        raise ValueError("nonfinite JSON: " + value)
    return json.loads(raw, object_pairs_hook=pairs, parse_constant=invalid)


def safe_name(name):
    require(isinstance(name, str) and bool(name), "empty archive name")
    p = PurePosixPath(name)
    require(bool(p.parts) and not p.is_absolute() and ".." not in p.parts and str(p) == name
            and "\\" not in name and "\0" not in name, "ambiguous archive name")


def checked_file(path, expected):
    path = Path(path)
    require(not path.is_symlink(), "symlink bound file")
    require(stat.S_ISREG(path.stat().st_mode), "nonregular bound file")
    raw = path.read_bytes()
    require(identity(raw) == expected, "bound file identity differs: " + str(path))
    return raw


def read_archive(path, members):
    require(isinstance(members, dict), "member map must be an object")
    for name, record in members.items():
        safe_name(name)
        require(isinstance(record, dict) and set(record) == {"sha256", "bytes"}, "member identity shape")
        require(type(record["bytes"]) is int and record["bytes"] >= 0 and
                isinstance(record["sha256"], str) and re.fullmatch("[0-9a-f]{64}", record["sha256"]), "member identity values")
    output = {}
    with tarfile.open(path, "r:gz") as archive:
        for member in archive:
            safe_name(member.name)
            require(member.isfile() and member.name not in output, "nonregular or duplicate archive member")
            require(member.name in members, "unexpected archive member")
            expected = members[member.name]
            require(member.size == expected["bytes"], "member size differs")
            raw = archive.extractfile(member).read()
            require(identity(raw) == expected, "member hash differs")
            output[member.name] = raw
    require(set(output) == set(members), "missing archive members")
    return output
