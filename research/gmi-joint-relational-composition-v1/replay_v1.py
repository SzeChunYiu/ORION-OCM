#!/usr/bin/env python3
"""Verify frozen packet bytes and replay the complete derived receipt."""
from hashlib import sha256
from pathlib import Path
import json

HERE = Path(__file__).resolve().parent


def verify_manifest(root=HERE):
    manifest = json.loads((root/"MANIFEST.json").read_text())
    if manifest.get("schema") != "joint-relational-composition-manifest-v1":
        raise ValueError("manifest schema")
    for name, binding in manifest["files"].items():
        path = root/name
        if Path(name).is_absolute() or ".." in Path(name).parts or not path.is_file():
            raise ValueError("manifest path")
        raw = path.read_bytes()
        if len(raw) != binding["bytes"] or sha256(raw).hexdigest() != binding["sha256"]:
            raise ValueError("binding mismatch: "+name)
    return len(manifest["files"])


def main():
    files = verify_manifest()
    from joint_relation_checks_v1 import run
    expected = json.loads((HERE/"JOINT_RELATIONAL_COMPOSITION_RECEIPT_V1.json").read_text())
    actual = run()
    if actual != expected:
        raise ValueError("full receipt mismatch")
    print(json.dumps(dict(bound_files=files, full_payload_equal=True,
                         terminal="JOINT_RELATIONAL_COMPOSITION_REPLAY_GREEN"), sort_keys=True))


if __name__ == "__main__":
    main()
