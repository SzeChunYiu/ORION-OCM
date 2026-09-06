"""One immutable, source-only V4 predecessor anchor; no historical recipe executes."""
from __future__ import annotations
import base64
import hashlib
import io
import json
from pathlib import Path
import subprocess
import zipfile
import runtime_revision_receipts_v4 as V4

DIRECTORY = "docs/provenance/engineering_revisions"
MANIFEST = DIRECTORY + "/PREDECESSOR_V4.json"
MANIFEST_SHA256 = "180431efb091899a4ae95ad21204587b9d4ffa2a24080f1f40adaf844929a931"
ARCHIVE = DIRECTORY + "/V4_SOURCE_EVIDENCE.zip"
PROTECTED = "docs/provenance/M12_PAIRED_RECEIPT_V5.json"


def encoded(value):
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode()


def tree_files(manifest):
    commit = base64.b64decode(manifest["commit_object"], validate=True)
    if V4.git_hash("commit", commit) != manifest["baseline_commit"]:
        raise V4.ReceiptError("predecessor commit proof changed")
    root = commit.split(b"\n", 1)[0].split()[1].decode()
    found = {}
    def walk(oid, prefix=""):
        data = base64.b64decode(manifest["tree_objects"][oid], validate=True)
        if V4.git_hash("tree", data) != oid:
            raise V4.ReceiptError("predecessor tree proof changed")
        cursor = 0
        while cursor < len(data):
            stop = data.index(b"\0", cursor)
            mode, name = data[cursor:stop].split(b" ", 1)
            child = data[stop + 1:stop + 21].hex()
            path = prefix + name.decode()
            V4.relative_path(path)
            cursor = stop + 21
            if mode == b"40000": walk(child, path + "/")
            else: found[path] = child
    walk(root)
    return found


def _verify(root, manifest):
    current = V4.CurrentReceipts(root)
    V4.ParentSnapshot(root, current.config)
    for path, expected in manifest["frozen_files"].items():
        if V4.sha(root, path) != expected:
            raise V4.ReceiptError("frozen predecessor changed: " + path)
    archive = V4.raw(root, ARCHIVE)
    if V4.digest(archive) != manifest["archive_sha256"]:
        raise V4.ReceiptError("predecessor source archive changed")
    membership = tree_files(manifest)
    contents = {}
    inventory = manifest["source_inventory"]
    with zipfile.ZipFile(io.BytesIO(archive)) as stream:
        names = stream.namelist()
        if len(names) != len(set(names)) or set(names) != set(inventory):
            raise V4.ReceiptError("predecessor source inventory mismatch")
        for path in names:
            V4.relative_path(path)
            data = stream.read(path)
            if (V4.digest(data) != inventory[path]
                    or V4.git_hash("blob", data) != membership.get(path)):
                raise V4.ReceiptError("predecessor source binding changed: " + path)
            contents[path] = data
    replay = current._replay(inventory)
    by_path = {s["predecessor_path"]: s for s in current.config["milestones"].values()}
    for number, spec in current.config["milestones"].items():
        receipt = V4.read_json(root, spec["successor_path"])
        old = V4.read_json(root, spec["predecessor_path"])
        aliases = {p: by_path[p]["successor_path"] for p in old["current_dependencies"] if p in by_path}
        required = {"schema": "ocm.runtime-successor-receipt.v4", "revision": V4.REVISION,
            "terminal": spec["terminal"], "authority": current.config["authority"],
            "current_source_inventory": inventory, "current_engineering_replay": replay,
            "legacy_recipe_execution": "NOT_EXECUTED", "dependency_aliases": aliases,
            "current_dependencies": {p: V4.sha(root, p) for p in aliases.values()}}
        if any(receipt.get(k) != v for k, v in required.items()):
            raise V4.ReceiptError("V4 predecessor semantics changed: M" + number)
    if PROTECTED in manifest["frozen_files"]:
        record = V4.read_json(root, PROTECTED)
        for path, expected in record["bound_files"].items():
            data = contents[path] if path in contents else V4.raw(root, path)
            if V4.digest(data) != expected:
                raise V4.ReceiptError("archived protected binding changed: " + path)
    return {"manifest": MANIFEST, "sha256": V4.sha(root, MANIFEST),
            "source_files": len(inventory), "legacy_recipe_execution": "NOT_EXECUTED",
            "current_scientific_promotion": "NOT_ESTABLISHED"}


def verify(root):
    if V4.sha(root, MANIFEST) != MANIFEST_SHA256:
        raise V4.ReceiptError("immutable predecessor anchor changed")
    return _verify(root, V4.read_json(root, MANIFEST))


def create(root, baseline):
    """One-time capture from an explicit Git ref; writes new files exclusively."""
    root = Path(root)
    def git(*args):
        return subprocess.check_output(["/usr/bin/git", "-C", str(root), *args])
    config = V4.CurrentReceipts(root).config
    inventory = V4.read_json(root, config["engineering_replay_path"])["current_source_inventory"]
    commit = git("rev-parse", baseline).decode().strip()
    commit_object = git("cat-file", "commit", commit)
    trees = {}
    def descend(oid):
        data = git("cat-file", "tree", oid)
        trees[oid] = base64.b64encode(data).decode()
        cursor = 0
        while cursor < len(data):
            stop = data.index(b"\0", cursor)
            mode, _ = data[cursor:stop].split(b" ", 1)
            child = data[stop + 1:stop + 21].hex()
            cursor = stop + 21
            if mode == b"40000": descend(child)
    descend(commit_object.split(b"\n", 1)[0].split()[1].decode())
    contents = {p: git("show", commit + ":" + p) for p in inventory}
    if any(V4.digest(data) != inventory[p] for p, data in contents.items()):
        raise V4.ReceiptError("explicit baseline does not match recorded V4 source")
    root.joinpath(DIRECTORY).mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(root / ARCHIVE, "x", compression=zipfile.ZIP_DEFLATED) as stream:
        for path, data in sorted(contents.items()):
            info = zipfile.ZipInfo(path, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            stream.writestr(info, data)
    frozen = {p.relative_to(root).as_posix(): V4.digest(p.read_bytes())
              for p in (root / "docs/provenance" / V4.REVISION).rglob("*") if p.is_file()}
    if (root / PROTECTED).is_file():
        frozen[PROTECTED] = V4.sha(root, PROTECTED)
        for path in V4.read_json(root, PROTECTED)["bound_files"]:
            if path not in inventory: frozen[path] = V4.sha(root, path)
    manifest = {"schema": "ocm.engineering-predecessor.v1", "baseline_commit": commit,
        "commit_object": base64.b64encode(commit_object).decode(), "tree_objects": trees,
        "source_inventory": inventory, "archive_sha256": V4.sha(root, ARCHIVE),
        "frozen_files": frozen, "scope": "Exact archived bindings only; no historical recipe or scientific promotion"}
    with (root / MANIFEST).open("xb") as output: output.write(encoded(manifest))
    _verify(root, manifest)
    return V4.sha(root, MANIFEST)
