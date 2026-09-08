"""Fail closed on a declared source inventory, without importing donor code."""
import hashlib
import json
from pathlib import Path


EXPECTED_INVENTORY_SHA256 = "511966073b83f4de3cb9f7fef1b8dfea776a23e7866be157dc0f84e0fa3c4921"
DEFAULT_INVENTORY = Path(__file__).with_name("DONOR_SOURCE_PINS.json")


def verify_inventory(repository_root, inventory=DEFAULT_INVENTORY,
                     expected_sha256=EXPECTED_INVENTORY_SHA256):
    root = Path(repository_root).resolve(strict=True)
    raw = Path(inventory).read_bytes()
    if hashlib.sha256(raw).hexdigest() != expected_sha256:
        raise ValueError("SOURCE_INVENTORY_DRIFT")
    document = json.loads(raw)
    if document.get("schema") != "paid-drd.declared-source-inventory.v1":
        raise ValueError("SOURCE_INVENTORY_SCHEMA")
    rows = document.get("files")
    if not isinstance(rows, list) or not rows:
        raise ValueError("SOURCE_INVENTORY_EMPTY")
    checked, seen = [], set()
    for row in rows:
        name = row["path"]
        relative = Path(name)
        if relative.is_absolute() or ".." in relative.parts or name in seen:
            raise ValueError("SOURCE_INVENTORY_PATH")
        seen.add(name)
        path = (root / relative).resolve(strict=True)
        if not path.is_relative_to(root) or not path.is_file():
            raise ValueError("SOURCE_INVENTORY_PATH")
        data = path.read_bytes()
        digest = hashlib.sha256(data).hexdigest()
        blob = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
        if (len(data), digest, blob) != (row["bytes"], row["sha256"], row["git_blob_sha1"]):
            raise ValueError("DONOR_SOURCE_DRIFT:" + name)
        checked.append({"path": name, "bytes": len(data), "sha256": digest,
                        "git_blob_sha1": blob})
    return {"inventory_sha256": expected_sha256, "checked_files": checked,
            "scope": document["scope"], "complete_study_requalification": False}


def require_module_path(module, repository_root, relative_path):
    expected = (Path(repository_root) / relative_path).resolve(strict=True)
    actual = Path(module.__file__).resolve(strict=True)
    if actual != expected:
        raise ValueError("DONOR_MODULE_PATH_DRIFT:" + relative_path)
