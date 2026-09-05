"""Immutable third-revision custody; no historical recipe executes on current code.

The exact parent snapshot contains Git commit/tree proofs and selected original blobs.
Verification reads the snapshot in memory, preserves historical evidence, and separately
binds the current code inventory to an explicitly labelled engineering replay.
"""
from __future__ import annotations

import base64
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import sys
import zipfile
import xml.etree.ElementTree as ET

REVISION = "runtime_revision_20260905_v3"
PARENT_COMMIT = "f59e5d8e39db592c9643ef51c4252f743f7ec091"
CONFIG_PATH = f"docs/provenance/{REVISION}/REVISION_V3.json"
CONFIG_SHA256 = "ca861417f8740beb3a8aedfca92b160ce1f54ab0adf1eea527498a4ce0136182"


class ReceiptError(ValueError):
    """Unverifiable custody or current engineering evidence."""


def relative_path(relative: str) -> PurePosixPath:
    if not isinstance(relative, str) or not relative or "\\" in relative:
        raise ReceiptError("invalid evidence path")
    rel = PurePosixPath(relative)
    if rel.is_absolute() or ".." in rel.parts or str(rel) != relative:
        raise ReceiptError(f"non-repository evidence path: {relative}")
    return rel


def path_in(root: Path, relative: str) -> Path:
    rel = relative_path(relative)
    path = root.joinpath(*rel.parts)
    if not path.resolve().is_relative_to(root.resolve()):
        raise ReceiptError(f"evidence path leaves repository: {relative}")
    if path.is_symlink():
        raise ReceiptError(f"symlink evidence is not accepted: {relative}")
    return path


def raw(root: Path, relative: str) -> bytes:
    path = path_in(root, relative)
    if not path.is_file():
        raise ReceiptError(f"MISSING required evidence: {relative}")
    return path.read_bytes()


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha(root: Path, relative: str) -> str:
    return digest(raw(root, relative))


def parse_json(data: bytes, label: str) -> dict:
    try:
        result = json.loads(data)
    except (UnicodeError, ValueError) as exc:
        raise ReceiptError(f"invalid JSON evidence: {label}") from exc
    if not isinstance(result, dict):
        raise ReceiptError(f"evidence must be an object: {label}")
    return result


def read_json(root: Path, relative: str) -> dict:
    return parse_json(raw(root, relative), relative)


def git_hash(kind: str, data: bytes) -> str:
    return hashlib.sha1(kind.encode() + b" " + str(len(data)).encode() + b"\0" + data).hexdigest()


def source_inventory(root: Path) -> dict[str, str]:
    """Exact source/resources and pyproject; exclude generated editable-install metadata."""
    selected = {"pyproject.toml"}
    for base in ("src", "tests", "tools"):
        directory = path_in(root, base)
        if not directory.is_dir():
            raise ReceiptError(f"MISSING source inventory directory: {base}")
        for path in directory.rglob("*"):
            rel = path.relative_to(root)
            if "__pycache__" in rel.parts or path.suffix in {".pyc", ".pyo"}:
                continue
            if path.is_symlink():
                raise ReceiptError(f"source inventory symlink: {rel}")
            if rel.parts[:2] == ("src", "orion_ocm.egg-info"):
                # setuptools derives these installation records from the bound
                # pyproject/source tree. They are not runtime implementation.
                if path.name in {"PKG-INFO", "SOURCES.txt", "dependency_links.txt", "entry_points.txt",
                                 "requires.txt", "top_level.txt", "not-zip-safe"}:
                    continue
            if path.is_file() and (base == "src" or path.suffix == ".py"):
                selected.add(rel.as_posix())
    return {p: sha(root, p) for p in sorted(selected)}


class ParentSnapshot:
    def __init__(self, root: Path, config: dict):
        spec = config["parent_manifest"]
        if sha(root, spec["path"]) != spec["sha256"]:
            raise ReceiptError("parent snapshot manifest changed")
        self.manifest = read_json(root, spec["path"])
        m = self.manifest
        if m["schema"] != "ocm.parent-source-evidence.v3" or m["parent_commit"] != PARENT_COMMIT:
            raise ReceiptError("parent snapshot identity changed")
        commit = base64.b64decode(m["git_commit_object_base64"], validate=True)
        if git_hash("commit", commit) != PARENT_COMMIT:
            raise ReceiptError("parent Git commit proof failed")
        tree_line = commit.split(b"\n", 1)[0]
        if tree_line != b"tree " + m["git_root_tree"].encode():
            raise ReceiptError("parent Git tree identity failed")
        objects = m["git_tree_objects_base64"]
        visited, files = set(), {}

        def walk(oid: str, prefix: str = "") -> None:
            if oid not in objects:
                raise ReceiptError("missing parent Git tree proof")
            data = base64.b64decode(objects[oid], validate=True)
            if git_hash("tree", data) != oid:
                raise ReceiptError("parent Git tree proof failed")
            visited.add(oid)
            cursor = 0
            names = set()
            while cursor < len(data):
                stop = data.find(b"\0", cursor)
                if stop < 0 or len(data) < stop + 21:
                    raise ReceiptError("malformed parent Git tree")
                mode, name = data[cursor:stop].split(b" ", 1)
                name = name.decode("utf-8")
                if name in names or "/" in name or name in {".", ".."}:
                    raise ReceiptError("duplicate or invalid parent Git tree path")
                names.add(name)
                child = data[stop + 1:stop + 21].hex()
                cursor = stop + 21
                path = prefix + name
                relative_path(path)
                if mode == b"40000":
                    walk(child, path + "/")
                elif mode in {b"100644", b"100755"}:
                    files[path] = {"mode": mode.decode(), "git_blob": child}
                else:
                    raise ReceiptError("unsupported parent Git object mode")
        walk(m["git_root_tree"])
        if visited != set(objects):
            raise ReceiptError("extra parent Git tree objects")
        archive_spec = m["archive"]
        archive_bytes = raw(root, archive_spec["path"])
        if digest(archive_bytes) != archive_spec["sha256"]:
            raise ReceiptError("parent source archive changed")
        self.contents = {}
        with zipfile.ZipFile(io.BytesIO(archive_bytes)) as archive:
            entries = archive.infolist()
            names = [x.filename for x in entries]
            if len(names) != len(set(names)) or set(names) != set(m["entries"]):
                raise ReceiptError("missing, extra or duplicate parent archive entries")
            for entry in entries:
                rel = entry.filename
                relative_path(rel)
                spec = m["entries"][rel]
                if rel not in files or any(spec[key] != files[rel][key] for key in ("mode", "git_blob")):
                    raise ReceiptError(f"parent archive has no Git membership proof: {rel}")
                if (entry.is_dir() or entry.file_size != spec["bytes"]
                        or (entry.external_attr >> 16) != int(spec["mode"], 8)):
                    raise ReceiptError(f"parent archive size/type mismatch: {rel}")
                data = archive.read(entry)
                if digest(data) != spec["sha256"] or git_hash("blob", data) != spec["git_blob"]:
                    raise ReceiptError(f"parent source blob proof failed: {rel}")
                self.contents[rel] = data
        if not {p for p in files if p.startswith(("src/", "docs/provenance/"))} <= self.contents.keys():
            raise ReceiptError("incomplete parent runtime or historical evidence inventory")
        # Historical documents/results remain byte-identical in the current tree.
        for rel, data in self.contents.items():
            if rel.startswith(("docs/", "research/")) and raw(root, rel) != data:
                raise ReceiptError(f"immutable predecessor evidence changed: {rel}")
        # Every prior successor binding is verified against archived parent bytes.
        for spec in config["milestones"].values():
            rel = spec["predecessor_path"]
            if rel not in self.contents or digest(self.contents[rel]) != spec["predecessor_sha256"]:
                raise ReceiptError(f"predecessor custody failed: {rel}")
            previous = parse_json(self.contents[rel], rel)
            bindings = {**previous["current_source_inventory"], **previous["current_dependencies"], **previous["current_engineering_replay"]["validation_artifacts"]}
            for bound, expected in bindings.items():
                if bound not in self.contents or digest(self.contents[bound]) != expected:
                    raise ReceiptError(f"predecessor source snapshot missing or changed: {bound}")


class CurrentReceipts:
    def __init__(self, root: Path):
        self.root = root
        if sha(root, CONFIG_PATH) != CONFIG_SHA256:
            raise ReceiptError("immutable third-revision config changed")
        self.config = read_json(root, CONFIG_PATH)
        if (self.config.get("schema") != "ocm.runtime-revision.v3"
                or self.config.get("revision") != REVISION
                or self.config.get("parent_commit") != PARENT_COMMIT
                or set(self.config.get("milestones", {})) != {str(i) for i in range(1, 13)}):
            raise ReceiptError("third-revision identity or milestone inventory changed")
        self._visiting: set[int] = set()
        self._verified: set[int] = set()
        self._snapshot: ParentSnapshot | None = None

    def _spec(self, milestone: int) -> dict:
        if type(milestone) is not int or str(milestone) not in self.config["milestones"]:
            raise ReceiptError("milestone has no declared third successor")
        return self.config["milestones"][str(milestone)]

    def _begin(self) -> None:
        if sha(self.root, CONFIG_PATH) != CONFIG_SHA256:
            raise ReceiptError("immutable third-revision config changed")
        self._verified.clear()
        self._snapshot = ParentSnapshot(self.root, self.config)

    def _replay(self, inventory: dict) -> dict:
        rel = self.config["engineering_replay_path"]
        replay = read_json(self.root, rel)
        required = {"schema": "ocm.engineering-replay.v3", "revision": REVISION,
                    "status": "ENGINEERING_REGRESSION_ONLY", "protected_reevaluation": "NOT_RUN",
                    "scientific_promotion": "NOT_ESTABLISHED", "independent_replication": "NOT_RUN"}
        if any(replay.get(key) != value for key, value in required.items()):
            raise ReceiptError("current replay lost its engineering-only scope")
        if replay.get("current_source_inventory") != inventory:
            raise ReceiptError("engineering replay source inventory DRIFT")
        commands = replay.get("executions")
        if not isinstance(commands, list) or not commands:
            raise ReceiptError("engineering replay has no executed validation")
        artifacts = replay.get("validation_artifacts")
        if not isinstance(artifacts, dict) or not artifacts:
            raise ReceiptError("engineering replay has no validation artifacts")
        requirements = self.config["validation_requirements"]
        by_label = {}
        for command in commands:
            if (not isinstance(command, dict) or type(command.get("exit_code")) is not int
                    or command["exit_code"] != 0 or command.get("label") not in requirements
                    or command["label"] in by_label):
                raise ReceiptError("engineering replay contains unsuccessful, duplicate or undeclared validation")
            label = command["label"]
            spec = requirements[label]
            if command.get("argv") != spec["argv"] or command.get("artifact_path") != spec["artifact_path"]:
                raise ReceiptError(f"engineering validation command or artifact differs from declared gate: {label}")
            by_label[label] = command
        if set(by_label) != set(requirements):
            raise ReceiptError("engineering replay omits a mandatory named validation gate")
        for path, expected in artifacts.items():
            if sha(self.root, path) != expected:
                raise ReceiptError(f"engineering validation artifact DRIFT: {path}")
        summaries = {}
        for label, spec in requirements.items():
            path = spec["artifact_path"]
            if path not in artifacts:
                raise ReceiptError(f"engineering replay omits mandatory JUnit artifact: {label}")
            try:
                report = ET.fromstring(raw(self.root, path))
                suites = list(report.iter("testsuite"))
                cases = list(report.iter("testcase"))
                counts = {key: sum(int(suite.attrib[key]) for suite in suites)
                          for key in ("tests", "failures", "errors", "skipped")}
            except (ET.ParseError, KeyError, TypeError, ValueError) as exc:
                raise ReceiptError(f"invalid required JUnit evidence: {label}") from exc
            skipped = sum(case.find("skipped") is not None for case in cases)
            if (not suites or counts["tests"] != len(cases)
                    or len(cases) < spec["minimum_tests"] or skipped >= len(cases)
                    or counts["skipped"] != skipped or skipped != 0 or counts["failures"] != 0 or counts["errors"] != 0
                    or any(case.find("failure") is not None or case.find("error") is not None for case in cases)):
                raise ReceiptError(f"required JUnit gate did not pass with declared coverage: {label}")
            summaries[label] = counts
        return {"path": rel, "sha256": sha(self.root, rel), **required,
                "executions": commands, "validation_artifacts": artifacts,
                "validated_junit_summaries": summaries,
                "scope": "Recorded-run attestation with required command and JUnit gates; not cryptographic proof of execution or independent evaluation."}

    def build(self, milestone: int) -> dict:
        spec = self._spec(milestone)
        if not self._visiting or self._snapshot is None:
            self._begin()
        snapshot = self._snapshot
        previous = parse_json(snapshot.contents[spec["predecessor_path"]], spec["predecessor_path"])
        by_path = {v["predecessor_path"]: int(k) for k, v in self.config["milestones"].items()}
        aliases, dependencies = {}, {}
        for rel in previous["current_dependencies"]:
            if rel in by_path:
                dependency = by_path[rel]
                self.verify(dependency)
                target = self._spec(dependency)["successor_path"]
                aliases[rel] = target
                dependencies[target] = sha(self.root, target)
        inventory = source_inventory(self.root)
        replay = self._replay(inventory)
        return {"schema": "ocm.runtime-successor-receipt.v3", "revision": REVISION,
                "receipt": f"M{milestone}_RECEIPT_RUNTIME_20260905_V3", "terminal": spec["terminal"],
                "authority": self.config["authority"],
                "revision_config": {"path": CONFIG_PATH, "sha256": CONFIG_SHA256},
                "predecessor": {"path": spec["predecessor_path"], "sha256": spec["predecessor_sha256"],
                                "parent_commit": PARENT_COMMIT,
                                "terminal_at_parent": previous["terminal"],
                                "status": "ARCHIVED_BYTES_AND_SOURCES_VERIFIED__NO_REEXECUTION"},
                "parent_snapshot": self.config["parent_manifest"],
                "current_source_inventory": inventory, "dependency_aliases": aliases,
                "current_dependencies": dependencies, "current_engineering_replay": replay,
                "legacy_recipe_execution": "NOT_EXECUTED"}

    def verify(self, milestone: int) -> None:
        spec = self._spec(milestone)
        if not self._visiting:
            self._begin()
        if milestone in self._verified:
            return
        if milestone in self._visiting:
            raise ReceiptError("cyclic third-successor dependency")
        recorded = read_json(self.root, spec["successor_path"])
        self._visiting.add(milestone)
        try:
            if recorded != self.build(milestone):
                raise ReceiptError(f"M{milestone} third successor DRIFT")
            self._verified.add(milestone)
        finally:
            self._visiting.remove(milestone)

    def write(self, milestone: int) -> Path:
        target = path_in(self.root, self._spec(milestone)["successor_path"])
        if target.exists():
            self.verify(milestone)
            return target
        self._begin()
        self._visiting.add(milestone)
        try:
            receipt = self.build(milestone)
        finally:
            self._visiting.remove(milestone)
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("x", encoding="utf-8") as stream:
            stream.write(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
        return target


def revision_main(root: Path, argv: list[str], milestone: int) -> int:
    if argv not in (["--verify"], ["--write-current"]):
        print("Historical receipts are immutable. Use --verify or --write-current for the explicit V3 successor.")
        return 2
    try:
        current = CurrentReceipts(root)
        if argv == ["--verify"]:
            current.verify(milestone)
            print(f"M{milestone} V3 successor verified: archived parent custody and current engineering only")
        else:
            print("current receipt:", current.write(milestone))
        return 0
    except (ReceiptError, OSError, KeyError, TypeError, ValueError, zipfile.BadZipFile) as exc:
        print(f"CURRENT RECEIPT REFUSED: {exc}")
        return 1


if __name__ == "__main__":
    if len(sys.argv) < 2 or not sys.argv[1].isdigit():
        print("Usage: runtime_revision_receipts_v3.py MILESTONE --verify|--write-current")
        raise SystemExit(2)
    raise SystemExit(revision_main(Path(__file__).resolve().parents[1], sys.argv[2:], int(sys.argv[1])))
