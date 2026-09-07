"""Portable resource archive/source custody; never run resource or native controls."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import types

SEAL_SHA256 = "2457516e82e1b07062360655dc0dfbce772f3b72aa16379bcfadb23eb6ae00e0"
HELPER_SHA256 = "630179d7dd4076ef2c859f54047de88f5ded164e185c5dc23bd146413065dd54"

def shared():
    path = Path(__file__).resolve().parent / "native_evidence.py"
    source = path.read_bytes()
    if hashlib.sha256(source).hexdigest() != HELPER_SHA256:
        raise ValueError("RESOURCE_AUDIT_HELPER_IDENTITY")
    module = types.ModuleType("resource_archive_shared")
    module.__file__ = str(path)
    # Execute exactly verified source bytes; ignore ambient imports and cached bytecode.
    exec(compile(source, str(path), "exec"), module.__dict__)
    return module

def binding(record):
    return {key: record[key] for key in ("bytes", "sha256")}

def audit_resource(root, expected_seal=SEAL_SHA256, source_root=None):
    audit = shared()
    root = Path(root)
    source_root = Path(source_root) if source_root is not None else Path(__file__).resolve().parent
    if not re.fullmatch("[0-9a-f]{64}", expected_seal): raise ValueError("RESOURCE_SEAL_FORMAT")
    seal_bytes = audit.read_file(root / "SEAL.json", audit.MAX_ARCHIVE_BYTES)
    if hashlib.sha256(seal_bytes).hexdigest() != expected_seal: raise ValueError("RESOURCE_SEAL_HASH")
    seal = audit.parse(seal_bytes)
    if (set(seal) != {"schema", "terminal", "files"} or seal["terminal"] != "COMPLETE"
            or seal["schema"] != "ocm.f1.resource-evidence-seal.v1"):
        raise ValueError("RESOURCE_SEAL_SCHEMA")
    if {p.name for p in root.iterdir()} != set(seal["files"]) | {"SEAL.json"}:
        raise ValueError("RESOURCE_PACKAGE_SET")
    values = {}
    for name, expected in seal["files"].items():
        audit.safe_name(name)
        if "/" in name: raise ValueError("RESOURCE_PACKAGE_PATH")
        values[name] = audit.checked(audit.read_file(root / name, audit.MAX_ARCHIVE_BYTES),
                                     expected, "RESOURCE_FILE_HASH")
    index = audit.parse(values["INDEX.json"])
    if index["schema"] != "ocm.f1.resource-evidence-archive.v1": raise ValueError("RESOURCE_INDEX_SCHEMA")
    audit.checked(values["SOURCE_FREEZE.json"], index["source_freeze"], "RESOURCE_SOURCE_FREEZE_HASH")
    audit.checked(values["RESULT.json"], index["result"], "RESOURCE_RESULT_HASH")
    seen = set(); members = total = 0
    for row in index["archives"]:
        name = audit.safe_name(row["archive"]); member_map = row["member_map"]
        inventory = audit.safe_name(member_map["file"])
        if name in seen: raise ValueError("DUPLICATE_RESOURCE_ARCHIVE")
        seen.add(name)
        if name not in values or inventory not in values: raise ValueError("RESOURCE_UNSEALED_ARCHIVE")
        if type(row["members"]) is not int or type(row["raw_bytes"]) is not int:
            raise ValueError("RESOURCE_COUNT_TYPE")
        audit.checked(values[name], binding(row), "RESOURCE_ARCHIVE_HASH")
        audit.checked(values[inventory], binding(member_map), "RESOURCE_MEMBER_MAP_HASH")
        result = audit.audit_archive(root / name, audit.parse(values[inventory]))
        if result != {"members": row["members"], "bytes": row["raw_bytes"]}: raise ValueError("RESOURCE_COUNTS")
        members += result["members"]; total += result["bytes"]
    if seen != {name for name in values if name.endswith(".tar.gz")}: raise ValueError("RESOURCE_ARCHIVE_SET")
    freeze = audit.parse(values["SOURCE_FREEZE.json"])
    if type(freeze["count"]) is not int or freeze["count"] != len(freeze["files"]):
        raise ValueError("RESOURCE_SOURCE_COUNT")
    for name, record in freeze["files"].items():
        audit.safe_name(name)
        if "/" in name: raise ValueError("RESOURCE_SOURCE_PATH")
        source = source_root / name
        try: source.resolve().relative_to(source_root.resolve())
        except ValueError as exc: raise ValueError("RESOURCE_SOURCE_PATH") from exc
        audit.checked(audit.read_file(source, audit.MAX_MEMBER_BYTES), binding(record), "CURRENT_RESOURCE_SOURCE")
    return {"terminal": "RESOURCE_ARCHIVE_CUSTODY_PASS", "archive_members": members, "raw_bytes": total,
            "current_sources": len(freeze["files"]), "omitted_host_inputs_revalidated": False,
            "scope": "Archive bytes and current registered sources only; no resource/native/corpus execution"}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent / "resource-records")
    parser.add_argument("--seal-sha256", default=SEAL_SHA256)
    args = parser.parse_args()
    try:
        result = audit_resource(args.root, args.seal_sha256); code = 0
    except Exception as exc:
        result = {"terminal": "CANNOT_CHECK_RESOURCE_ARCHIVE_CUSTODY", "reason": str(exc)}; code = 2
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))
    return code

if __name__ == "__main__": raise SystemExit(main())
