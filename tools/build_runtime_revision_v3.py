"""Create the third revision's immutable parent snapshot and declared test gates.

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

PARENT = "f59e5d8e39db592c9643ef51c4252f743f7ec091"
REVISION = "runtime_revision_20260905_v3"
FOCUSED = ["tests/test_evaluation_integrity_v3.py", "tests/m2/test_action_recovery_v3.py",
           "tests/m9/test_method_contract_integrity_v3.py", "tests/test_method_learning_v1.py",
           "tests/test_distribution.py", "tests/test_runtime_revision_receipts_v3.py"]


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
    commit = git("cat-file", "commit", PARENT)
    tree = commit.split(b"\n", 1)[0].split()[1].decode()
    entries, contents, trees = {}, {}, {}
    for row in git("ls-tree", "-rz", PARENT).split(b"\0"):
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
    archive = out / "PARENT_f59e5d8_SOURCE_EVIDENCE.zip"
    with zipfile.ZipFile(archive, "x", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as stream:
        for path, data in sorted(contents.items()):
            info = zipfile.ZipInfo(path, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = int(entries[path]["mode"], 8) << 16
            stream.writestr(info, data)
    manifest = {"schema": "ocm.parent-source-evidence.v3", "parent_commit": PARENT,
                "git_commit_object_base64": base64.b64encode(commit).decode(), "git_root_tree": tree,
                "git_tree_objects_base64": trees, "archive": {"path": archive.relative_to(root).as_posix(),
                "sha256": digest(archive.read_bytes())}, "entries": entries,
                "scope": "Complete exact parent Git tree, including all previous source and evidence. No historical recipe reexecution."}
    manifest_path = out / "PARENT_MANIFEST_V3.json"
    write(manifest_path, manifest)
    old = json.loads(contents["docs/provenance/runtime_revision_20260905_v2/REVISION_V2.json"])
    config = {"schema": "ocm.runtime-revision.v3", "revision": REVISION, "parent_commit": PARENT,
              "parent_manifest": {"path": manifest_path.relative_to(root).as_posix(), "sha256": digest(manifest_path.read_bytes())},
              "engineering_replay_path": f"docs/provenance/{REVISION}/ENGINEERING_REPLAY_V3.json",
              "authority": "Historical outcomes remain historical; current engineering tests do not establish protected results, independent replication or scientific promotion.",
              "milestones": {key: {"predecessor_path": spec["successor_path"],
                  "predecessor_sha256": digest(contents[spec["successor_path"]]),
                  "successor_path": f"docs/provenance/{REVISION}/M{key}_RECEIPT_RUNTIME_20260905_V3.json",
                  "terminal": f"M{key}_HISTORICAL_CUSTODY__CURRENT_ENGINEERING_ONLY"} for key, spec in old["milestones"].items()}}
    gates = {}
    for label, paths, count, name in (("full_suite", ["tests"], full_count, "FULL_SUITE.xml"),
                                      ("focused_suite", FOCUSED, focused_count, "FOCUSED_SUITE.xml")):
        path = f"docs/provenance/{REVISION}/{name}"
        gates[label] = {"argv": ["python", "-m", "pytest", *paths, "-q", f"--junitxml={path}"],
                        "artifact_path": path, "minimum_tests": count}
    config["validation_requirements"] = gates
    config_path = out / "REVISION_V3.json"
    write(config_path, config)
    return {"parent_files": len(entries), "config_sha256": digest(config_path.read_bytes())}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--full-count", required=True, type=int)
    parser.add_argument("--focused-count", required=True, type=int)
    args = parser.parse_args()
    print(json.dumps(build(Path(__file__).resolve().parents[1], args.full_count, args.focused_count)))
