"""Portable lossless-archive/source custody audit; no native execution or external paths."""
import argparse
import gzip
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import re
import tarfile

MAX_ARCHIVE_BYTES = 32 * 1024 * 1024
MAX_TAR_BYTES = 128 * 1024 * 1024
MAX_MEMBER_BYTES = 64 * 1024 * 1024

def safe_name(name):
    if not isinstance(name, str) or not name or "\\" in name or "\x00" in name:
        raise ValueError("PATH")
    p = PurePosixPath(name)
    if p.is_absolute() or ".." in p.parts or str(p) != name or name == ".":
        raise ValueError("PATH")
    return name

def pairs(items):
    value = {}
    for key, item in items:
        if key in value: raise ValueError("DUPLICATE_JSON_KEY")
        value[key] = item
    return value

def parse(raw):
    return json.loads(raw, object_pairs_hook=pairs,
                      parse_constant=lambda _: (_ for _ in ()).throw(ValueError("NONFINITE_JSON")))

def checked(raw, expected, reason):
    if set(expected) != {"bytes", "sha256"} or type(expected["bytes"]) is not int:
        raise ValueError("BINDING_SCHEMA")
    if len(raw) != expected["bytes"] or hashlib.sha256(raw).hexdigest() != expected["sha256"]:
        raise ValueError(reason)
    return raw

def read_file(path, limit):
    if path.is_symlink() or not path.is_file() or path.stat().st_size > limit:
        raise ValueError("FILE_KIND_OR_SIZE")
    with path.open("rb") as stream: raw = stream.read(limit + 1)
    if len(raw) > limit: raise ValueError("FILE_SIZE")
    return raw

def audit_archive(path, members):
    for name in members: safe_name(name)
    compressed = read_file(Path(path), MAX_ARCHIVE_BYTES)
    with gzip.GzipFile(fileobj=io.BytesIO(compressed), mode="rb") as stream:
        raw = stream.read(MAX_TAR_BYTES + 1)
    if len(raw) > MAX_TAR_BYTES: raise ValueError("TAR_SIZE")
    seen = set()
    total = 0
    with tarfile.open(fileobj=io.BytesIO(raw), mode="r:", ignore_zeros=True) as tar:
        for item in tar:
            name = safe_name(item.name)
            if not item.isreg(): raise ValueError("FILE_TYPE")
            if name in seen: raise ValueError("DUPLICATE_MEMBER")
            if name not in members: raise ValueError("MEMBER_SET")
            if item.size > MAX_MEMBER_BYTES: raise ValueError("MEMBER_SIZE")
            seen.add(name)
            stream = tar.extractfile(item)
            if stream is None: raise ValueError("MEMBER_STREAM")
            data = stream.read(MAX_MEMBER_BYTES + 1)
            checked(data, members[name], "MEMBER_HASH")
            total += len(data)
    if seen != set(members): raise ValueError("MEMBER_SET")
    return {"members": len(seen), "bytes": total}

def audit_package(root, expected_seal, research_root):
    root = Path(root)
    if not re.fullmatch("[0-9a-f]{64}", expected_seal): raise ValueError("SEAL_HASH_FORMAT")
    seal_raw = read_file(root / "SEAL.json", MAX_ARCHIVE_BYTES)
    if hashlib.sha256(seal_raw).hexdigest() != expected_seal: raise ValueError("SEAL_HASH")
    seal = parse(seal_raw)
    if set(seal) != {"schema", "files"} or seal["schema"] != "ocm.coverage.native-archive-seal.v1":
        raise ValueError("SEAL_SCHEMA")
    expected_files = set(seal["files"])
    actual_files = {p.name for p in root.iterdir()}
    if actual_files != expected_files | {"SEAL.json"}: raise ValueError("PACKAGE_SET")
    values = {}
    for name, binding in seal["files"].items():
        safe_name(name)
        if len(PurePosixPath(name).parts) != 1: raise ValueError("PACKAGE_PATH")
        values[name] = checked(read_file(root / name, MAX_ARCHIVE_BYTES), binding, "FILE_HASH")
    index = parse(values["INDEX.json"])
    if index["schema"] != "ocm.coverage.native-archives.v1": raise ValueError("INDEX_SCHEMA")
    seen_archives = set()
    members_total = bytes_total = 0
    for row in index["archives"]:
        name = safe_name(row["archive"])
        inventory = safe_name(row["members"])
        if name in seen_archives: raise ValueError("DUPLICATE_ARCHIVE")
        seen_archives.add(name)
        if name not in values or inventory not in values: raise ValueError("UNSEALED_ARCHIVE")
        result = audit_archive(root / name, parse(values[inventory]))
        if result != {"members": row["count"], "bytes": row["raw_bytes"]}: raise ValueError("ARCHIVE_COUNTS")
        members_total += result["members"]; bytes_total += result["bytes"]
    declared_archives = {name for name in values if name.endswith(".tar.gz")}
    if declared_archives != seen_archives: raise ValueError("ARCHIVE_SET")
    bindings = parse(values["SOURCE_BINDINGS.json"])
    for relative, binding in bindings.items():
        safe_name(relative)
        checked(read_file(Path(research_root) / relative, MAX_MEMBER_BYTES), binding, "CURRENT_SOURCE_HASH")
    return {"terminal": "ARCHIVE_CUSTODY_PASS", "archive_members": members_total,
            "raw_bytes": bytes_total, "current_sources": len(bindings),
            "scope": "Byte custody and current registered source identity; no native or semantic rerun"}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent / "native-records")
    parser.add_argument("--seal-sha256", required=True)
    args = parser.parse_args()
    try:
        result = audit_package(args.root, args.seal_sha256, Path(__file__).resolve().parent.parent)
        code = 0
    except (OSError, ValueError, KeyError, TypeError, tarfile.TarError, EOFError) as exc:
        result = {"terminal": "CANNOT_CHECK_ARCHIVE_CUSTODY", "reason": str(exc)}; code = 2
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))
    return code

if __name__ == "__main__": raise SystemExit(main())
