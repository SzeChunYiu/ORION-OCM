"""Verify all 20 immutable source records without importing any old script."""
import hashlib
import json
from pathlib import Path

BINDING_SHA = "2dd33f577f370bde9e950a2418ef0758690be23fddebc432f37738e226eafab6"

def sha(data):
    return hashlib.sha256(data).hexdigest()

def verify_sources(root):
    root = Path(root)
    raw = (root/"SOURCE_BINDINGS_V1.json").read_bytes()
    if sha(raw) != BINDING_SHA:
        raise ValueError("source authority changed")
    rows = json.loads(raw)
    if len(rows) != 20 or len({r["copy"] for r in rows}) != 20:
        raise ValueError("source coverage")
    result = {}
    for row in rows:
        path = root/row["copy"]
        data = path.read_bytes()
        if len(data) != row["bytes"] or sha(data) != row["sha256"]:
            raise ValueError("source mismatch: "+row["path"])
        result[(row["kind"], row["path"])] = data
    return result
