"""Create the fourth revision's immutable parent snapshot and declared test gates.

One-time engineering setup, not a test runner or a scientific approval mechanism.
The parent is pinned; existing artifacts are never overwritten.
"""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import subprocess
import zipfile

PARENT = "ddc2be3104f4f9ac5e476eee96245007c89b0369"
REVISION = "runtime_revision_20260905_v4"
FOCUSED = ["tests/test_evaluation_integrity_v3.py", "tests/m2/test_action_recovery_v3.py",
           "tests/m9/test_method_contract_integrity_v3.py", "tests/test_method_learning_v1.py",
           "tests/test_distribution.py", "tests/test_runtime_revision_receipts_v4.py", "tests/m6/test_chat_learning_spelling_v4.py", "tests/m11/test_batch6_obligations.py"]


def snapshot(root, out, parent):
    def git(*args):
        return subprocess.check_output(["git", "-C", str(root), *args])
    def digest(data):
        return hashlib.sha256(data).hexdigest()
    def write(path, data):
        with path.open("x", encoding="utf-8") as stream:
            json.dump(data, stream, indent=2, sort_keys=True)
            stream.write("\n")
    commit = git("cat-file", "commit", parent)
    tree = commit.split(b"\n", 1)[0].split()[1].decode()
    entries, contents, trees = {}, {}, {}
    for row in git("ls-tree", "-rz", parent).split(b"\0"):
        if not row:
            continue
        metadata, path = row.split(b"\t")
        mode, kind, blob = metadata.decode().split()
        if kind != "blob" or mode not in ("100644", "100755"):
            raise ValueError("unsupported parent object")
        path = path.decode()
        data = git("cat-file", "blob", blob)
        contents[path] = data
        entries[path] = {"mode": mode, "git_blob": blob, "sha256": digest(data), "bytes": len(data)}
    def descend(oid):
        data = git("cat-file", "tree", oid)
        trees[oid] = base64.b64encode(data).decode()
        pos = 0
        while pos < len(data):
            end = data.index(b"\0", pos)
            mode, _ = data[pos:end].split(b" ", 1)
            child = data[end + 1:end + 21].hex()
            pos = end + 21
            if mode == b"40000":
                descend(child)
    descend(tree)
    archive = out / ("PARENT_" + parent[:7] + "_SOURCE_EVIDENCE.zip")
    with zipfile.ZipFile(archive, "x", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as stream:
        for path, data in sorted(contents.items()):
            info = zipfile.ZipInfo(path, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = int(entries[path]["mode"], 8) << 16
            stream.writestr(info, data)
    manifest = {"schema": "ocm.parent-source-evidence.v4", "parent_commit": parent,
                "git_commit_object_base64": base64.b64encode(commit).decode(), "git_root_tree": tree,
                "git_tree_objects_base64": trees, "archive": {"path": archive.relative_to(root).as_posix(),
                "sha256": digest(archive.read_bytes())}, "entries": entries,
                "scope": "Complete exact parent Git tree, including all previous source and evidence. No historical recipe reexecution."}
    manifest_path = out / ("PARENT_" + parent[:7] + "_MANIFEST_V4.json")
    write(manifest_path, manifest)
    return contents, entries, manifest_path


def build(root, full_count, focused_count):
    if min(full_count, focused_count) < 1:
        raise ValueError("declared gates must contain tests")
    def git(*args):
        return subprocess.check_output(["git", "-C", str(root), *args])
    def digest(data):
        return hashlib.sha256(data).hexdigest()
    def write(path, data):
        with path.open("x", encoding="utf-8") as stream:
            json.dump(data, stream, indent=2, sort_keys=True)
            stream.write("\n")
    out = root / "docs/provenance" / REVISION
    out.mkdir(parents=True, exist_ok=True)
    contents, entries, manifest_path = snapshot(root, out, PARENT)
    upstream = "5352984bd0c80260c9c0d9fafc3c78f94c025e39"
    other, other_entries, other_manifest = snapshot(root, out, upstream)
    old = json.loads(contents["docs/provenance/runtime_revision_20260905_v3/REVISION_V3.json"])
    config = {"schema": "ocm.runtime-revision.v4", "revision": REVISION, "parent_commit": PARENT,
              "parent_manifest": {"path": manifest_path.relative_to(root).as_posix(), "sha256": digest(manifest_path.read_bytes())},
              "engineering_replay_path": f"docs/provenance/{REVISION}/ENGINEERING_REPLAY_V4.json",
              "authority": "Historical outcomes remain historical; current engineering tests do not establish protected results, independent replication or scientific promotion.",
              "milestones": {key: {"predecessor_path": spec["successor_path"],
                  "predecessor_sha256": digest(contents[spec["successor_path"]]),
                  "successor_path": f"docs/provenance/{REVISION}/M{key}_RECEIPT_RUNTIME_20260905_V4.json",
                  "terminal": f"M{key}_HISTORICAL_CUSTODY__CURRENT_ENGINEERING_ONLY"} for key, spec in old["milestones"].items()}}
    config["upstream_commit"] = upstream
    config["upstream_manifest"] = {"path": other_manifest.relative_to(root).as_posix(), "sha256": digest(other_manifest.read_bytes())}
    config["historical_path_replacements"] = {p: {"from_sha256": digest(data), "to_sha256": digest(other[p])}
        for p, data in contents.items() if p.startswith(("docs/", "research/")) and p in other and data != other[p]}
    gates = {}
    for label, paths, count, name in (("full_suite", ["tests"], full_count, "FULL_SUITE.xml"),
                                      ("focused_suite", FOCUSED, focused_count, "FOCUSED_SUITE.xml")):
        path = f"docs/provenance/{REVISION}/{name}"
        gates[label] = {"argv": ["python", "-m", "pytest", *paths, "-q", f"--junitxml={path}"],
                        "artifact_path": path, "minimum_tests": count}
    config["validation_requirements"] = gates
    config_path = out / "REVISION_V4.json"
    write(config_path, config)
    return {"parent_files": len(entries), "config_sha256": digest(config_path.read_bytes())}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--full-count", required=True, type=int)
    parser.add_argument("--focused-count", required=True, type=int)
    args = parser.parse_args()
    print(json.dumps(build(Path(__file__).resolve().parents[1], args.full_count, args.focused_count)))
