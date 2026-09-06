from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any

from .historical import repository_root

SOURCE_REPOSITORY = "SzeChunYiu/ORION-V2"
SOURCE_COMMIT = "42b1b0d1ab5920a69036e1c782c6b84c92c3b4d3"
SOURCE_RESEARCH_TREE = "9f04028706dfc70dad4606491c84eed72bba753c"
MIGRATION_COMMIT = "430708103525f567633e377f015a7113633d709d"
PATH_MANIFEST = "docs/provenance/MIGRATED_FILE_MANIFEST.md"


class ProvenanceError(RuntimeError): pass


def _git(root: Path, *args: str, text: bool = True) -> str | bytes:
    p = subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=text)
    if p.returncode:
        err = p.stderr if text else p.stderr.decode("utf-8", errors="replace")
        raise ProvenanceError(f"git {' '.join(args)} failed: {err.strip()}")
    return p.stdout


def migrated_paths(root: Path) -> list[str]:
    path = root / PATH_MANIFEST
    if not path.exists(): raise ProvenanceError(f"path manifest missing: {PATH_MANIFEST}")
    rows = [line.strip()[3:-1] for line in path.read_text(encoding="utf-8").splitlines() if line.strip().startswith("- `") and line.strip().endswith("`")]
    if not rows or len(rows) != len(set(rows)): raise ProvenanceError("path manifest empty or duplicate")
    return rows


def _role(path: str) -> str:
    low = path.lower()
    if path.startswith("tests/"): return "test"
    if "/parent-space/" in path: return "parent-audit"
    if "failure" in low or "negative" in low: return "negative-history"
    if "/receipts/" in path or "receipt" in low: return "receipt"
    if "/results/" in path or "result" in low: return "result"
    if "/reference/" in path or path.endswith(".py"): return "code"
    return "theory"


def _status(path: str) -> str:
    low = path.lower()
    if any(x in low for x in ("wisdom", "method_kso", "thought_speech")): return "PARKED"
    if "failure" in low or "negative" in low: return "NEGATIVE"
    if "/parent-space/" in path: return "PARENT_OWNED"
    return "HISTORICAL"


def detailed_manifest(root: Path) -> dict[str, Any]:
    tree = str(_git(root, "rev-parse", f"{MIGRATION_COMMIT}:research/orion-machine")).strip()
    if tree != SOURCE_RESEARCH_TREE: raise ProvenanceError(f"migration research tree {tree} != frozen source tree {SOURCE_RESEARCH_TREE}")
    entries=[]; passed=0
    for rel in migrated_paths(root):
        target=root/rel
        if not target.is_file(): raise ProvenanceError(f"migrated file missing: {rel}")
        source=_git(root,"show",f"{MIGRATION_COMMIT}:{rel}",text=False); assert isinstance(source,bytes)
        source_blob=str(_git(root,"rev-parse",f"{MIGRATION_COMMIT}:{rel}")).strip(); dest_blob=str(_git(root,"hash-object",rel)).strip()
        s256=hashlib.sha256(source).hexdigest(); d256=hashlib.sha256(target.read_bytes()).hexdigest(); equal=source_blob==dest_blob and s256==d256; passed+=int(equal)
        entries.append({"path":rel,"source_blob_sha":source_blob,"source_content_sha256":s256,"source_commit":SOURCE_COMMIT,"migration_mirror_commit":MIGRATION_COMMIT,"migrated_path":rel,"destination_blob_sha":dest_blob,"destination_content_sha256":d256,"role":_role(rel),"status":_status(rel),"byte_identity":equal})
    total=len(entries)
    return {"schema_version":"ocm.migrated-file-manifest.v1","source_repository":SOURCE_REPOSITORY,"source_commit":SOURCE_COMMIT,"source_research_tree":SOURCE_RESEARCH_TREE,"migration_mirror_commit":MIGRATION_COMMIT,"migrated_file_count":total,"byte_identity_pass":passed,"byte_identity_total":total,"manifest_drift":total-passed,"entries":entries}


def verify_migration(root: Path) -> dict[str, Any]:
    m=detailed_manifest(root)
    if m["manifest_drift"]: raise ProvenanceError(f"migrated historical byte drift: {[r['path'] for r in m['entries'] if not r['byte_identity']][:8]}")
    return m


def main(argv: list[str] | None = None) -> int:
    p=argparse.ArgumentParser(); p.add_argument("--check",action="store_true"); p.add_argument("--write",type=Path); a=p.parse_args(argv); root=repository_root()
    try: m=verify_migration(root)
    except ProvenanceError as exc: print(json.dumps({"terminal":"M0_PROVENANCE_FAIL","reason":str(exc)},sort_keys=True)); return 1
    if a.write: a.write.parent.mkdir(parents=True,exist_ok=True); a.write.write_text(json.dumps(m,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({"terminal":"M0_PROVENANCE_GREEN","migrated_file_count":m["migrated_file_count"],"byte_identity_pass":m["byte_identity_pass"],"byte_identity_total":m["byte_identity_total"],"manifest_drift":m["manifest_drift"]},sort_keys=True)); return 0


if __name__ == "__main__": raise SystemExit(main())
