"""Successor custody for the 2026-09-05 runtime revision.

Original milestone receipts remain immutable historical evidence. Current verification binds
the revised engine, checks the old recipe with its historical artifact reads labelled, and
separately records supplied engineering replays. It does not rerun a protected experiment.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path, PurePosixPath
from typing import Callable

REVISION = "runtime_revision_20260905"
PARENT_COMMIT = "f2b83e2849b1afb79c45f12bebc3c929080352c9"
CONFIG_PATH = f"docs/provenance/{REVISION}/REVISION_V1.json"
CONFIG_SHA256 = "cf8bd8785fb1faa2c60ce7b3d44e5a1e9bb420a0a6b0a6cc93ea392602897e8a"


class ReceiptError(ValueError):
    """Missing, changed or mislabelled evidence cannot verify a current revision."""


def path_in(root: Path, relative: str) -> Path:
    rel = PurePosixPath(relative)
    if rel.is_absolute() or ".." in rel.parts:
        raise ReceiptError(f"non-repository evidence path: {relative}")
    path = root / relative
    if not path.resolve().is_relative_to(root.resolve()):
        raise ReceiptError(f"evidence path leaves repository: {relative}")
    return path


def sha(root: Path, relative: str) -> str:
    path = path_in(root, relative)
    if not path.is_file():
        raise ReceiptError(f"MISSING required evidence: {relative}")
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_json(root: Path, relative: str) -> dict:
    sha(root, relative)  # enforce presence and path confinement before parsing
    try:
        value = json.loads(path_in(root, relative).read_text(encoding="utf-8"))
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise ReceiptError(f"invalid JSON evidence: {relative}") from exc
    if not isinstance(value, dict):
        raise ReceiptError(f"evidence must be an object: {relative}")
    return value


class CurrentReceipts:
    def __init__(self, root: Path):
        self.root = root
        if sha(root, CONFIG_PATH) != CONFIG_SHA256:
            raise ReceiptError("immutable runtime revision config changed")
        self.config = read_json(root, CONFIG_PATH)
        if self.config.get("revision") != REVISION or self.config.get("historical_parent_commit") != PARENT_COMMIT:
            raise ReceiptError("runtime revision identity or parent changed")
        self._verified: set[int] = set()
        self._visiting: set[int] = set()

    def _spec(self, milestone: int) -> dict:
        try:
            return self.config["milestones"][str(milestone)]
        except KeyError as exc:
            raise ReceiptError(f"milestone has no declared successor: M{milestone}") from exc

    def _recipe(self, milestone: int) -> tuple[Callable[[], dict], tuple[str, ...]]:
        path = path_in(self.root, f"tools/m{milestone}_receipt.py")
        module_spec = importlib.util.spec_from_file_location(f"runtime_revision_m{milestone}", path)
        if module_spec is None or module_spec.loader is None:
            raise ReceiptError(f"cannot load M{milestone} receipt recipe")
        module = importlib.util.module_from_spec(module_spec)
        module_spec.loader.exec_module(module)
        return module.fresh, tuple(module.BOUND_FILES if milestone == 1 else module.BOUND)

    def _replay(self, milestone: int, spec: dict) -> dict:
        rel = spec["replay_path"]
        if rel is None:
            return {"status": "NO_NEW_EXPERIMENT_EXECUTED_BY_THIS_RECEIPT",
                    "protected_reevaluation": "NOT_RUN"}
        replay = read_json(self.root, rel)
        if milestone == 11:
            engineering = replay.get("engineering_revalidation", {})
            if engineering.get("status") != "CONTROLLED_ENGINEERING_REPLAY_ONLY" or engineering.get("scientific_terminal") != "NO_NEW_ADMISSION_OR_PROMOTION":
                raise ReceiptError("M11 successor replay lost its engineering-only scope")
            for p, digest in engineering.get("bound_files", {}).items():
                if sha(self.root, p) != digest:
                    raise ReceiptError(f"M11 recorded replay source/test drift: {p}")
            results = {k: replay[k] for k in ("summary", "scenarios", "parents", "engineering_revalidation")}
        else:
            if replay.get("study_status") != "REFERENCE_REPLAY_AFTER_RUNTIME_REVISION":
                raise ReceiptError(f"M{milestone} replay is not labelled as a current reference replay")
            if milestone == 12:
                if replay.get("revalidation", {}).get("terminal") != spec["terminal"]:
                    raise ReceiptError("M12 replay terminal claims more than this revision")
                results = {k: replay[k] for k in ("deterministic", "exit_gate_before_replication", "cannot_check", "revalidation")}
            else:
                results = {k: value for k, value in replay.items()
                           if k not in {"cost", "latency_s", "legacy_harness_authority_text", "authority"}}
        return {"status": "REFERENCE_REPLAY_AFTER_RUNTIME_REVISION", "artifact": rel,
                "sha256": sha(self.root, rel), "reference_results": results,
                "protected_reevaluation": "NOT_RUN", "new_replication": "NOT_RUN",
                "scope": "Same authored scenarios; outcome equality does not validate historical input bindings."}

    def build(self, milestone: int, recipe: Callable[[], dict] | None = None,
              declared_bound: tuple[str, ...] | None = None) -> dict:
        if sha(self.root, CONFIG_PATH) != CONFIG_SHA256:
            raise ReceiptError("immutable runtime revision config changed")
        spec = self._spec(milestone)
        historical_path = spec["historical_path"]
        if sha(self.root, historical_path) != spec["historical_sha256"]:
            raise ReceiptError(f"immutable historical receipt changed: {historical_path}")
        historical = read_json(self.root, historical_path)
        if recipe is None:
            recipe, declared_bound = self._recipe(milestone)
        if set(declared_bound or ()) != set(historical["bound_files"]):
            raise ReceiptError(f"M{milestone} historical binding recipe changed")

        aliases = {}
        historical_assets = {}
        bound = {}
        by_historical_path = {v["historical_path"]: int(k) for k, v in self.config["milestones"].items()}
        for rel, old_digest in historical["bound_files"].items():
            actual = sha(self.root, rel)
            if not rel.startswith("src/"):
                if actual != old_digest:
                    raise ReceiptError(f"immutable historical artifact changed: {rel}")
                historical_assets[rel] = old_digest
            elif actual != old_digest and rel not in self.config["affected_sources"]:
                raise ReceiptError(f"source change not declared in immutable revision config: {rel}")
            if rel in by_historical_path:
                dependency = by_historical_path[rel]
                self.verify(dependency)
                target = self._spec(dependency)["successor_path"]
                aliases[rel] = target
                bound[target] = sha(self.root, target)
            else:
                bound[rel] = actual

        source_changes = {}
        for rel, previous_digest in self.config["affected_sources"].items():
            current = sha(self.root, rel)
            bound[rel] = current
            source_changes[rel] = {"at_historical_parent": previous_digest, "current": current}
        for rel in self.config["revision_files"]:
            bound[rel] = sha(self.root, rel)
        replay = self._replay(milestone, spec)
        if spec["replay_path"]:
            bound[spec["replay_path"]] = sha(self.root, spec["replay_path"])

        # Some original recipes execute finite checkers; others only read old result JSON.
        # Keep that mixture visibly historical rather than calling it a new protected run.
        observed = recipe()
        if set(observed["bound_files"]) != set(declared_bound or ()):
            raise ReceiptError(f"M{milestone} recipe returned a different binding set")
        excluded = {"bound_files", "git_head_at_generation", "commands", "missing_bound_files"}
        payload = {k: v for k, v in observed.items() if k not in excluded}
        previous_payload = {k: v for k, v in historical.items() if k not in excluded}
        return {
            "receipt": f"M{milestone}_RECEIPT_RUNTIME_20260905_V1",
            "revision": REVISION, "schema": "ocm.runtime-successor-receipt.v1",
            "terminal": spec["terminal"],
            "authority": self.config["authority"],
            "revision_config": {"path": CONFIG_PATH, "sha256": CONFIG_SHA256},
            "historical_reference": {"path": historical_path, "sha256": spec["historical_sha256"],
                                     "parent_commit": PARENT_COMMIT, "terminal_at_that_revision": historical["terminal"],
                                     "status": "IMMUTABLE_HISTORICAL_OUTCOME; NOT_PROMOTED_TO_CURRENT_CODE"},
            "historical_artifact_bindings": historical_assets,
            "source_changes": source_changes, "bound_files": bound,
            "dependency_aliases": aliases,
            "legacy_recipe_recheck": {"status": "CURRENT_RECIPE_WITH_EXPLICIT_HISTORICAL_ARTIFACT_READS",
                                      "scope": "Finite checker execution and/or old result reads; not a protected experiment rerun.",
                                      "payload": payload, "matches_historical_payload": payload == previous_payload},
            "current_replay": replay,
        }

    def verify(self, milestone: int, recipe: Callable[[], dict] | None = None,
               declared_bound: tuple[str, ...] | None = None) -> None:
        if not self._visiting:
            # Memoization is local to one dependency traversal, never across file changes.
            self._verified.clear()
        if milestone in self._verified:
            return
        if milestone in self._visiting:
            raise ReceiptError("cyclic successor dependency")
        # Fail before executing a historical recipe when the active successor is missing.
        recorded = read_json(self.root, self._spec(milestone)["successor_path"])
        self._visiting.add(milestone)
        try:
            expected = self.build(milestone, recipe, declared_bound)
            if recorded != expected:
                differences = sorted(k for k in recorded.keys() | expected.keys() if recorded.get(k) != expected.get(k))
                raise ReceiptError(f"M{milestone} successor DRIFT: {', '.join(differences)}")
            self._verified.add(milestone)
        finally:
            self._visiting.remove(milestone)

    def write(self, milestone: int, recipe: Callable[[], dict] | None = None,
              declared_bound: tuple[str, ...] | None = None) -> Path:
        target = path_in(self.root, self._spec(milestone)["successor_path"])
        if target.exists():
            # Idempotence is safe; changed evidence requires a new revision, not an overwrite.
            self.verify(milestone, recipe, declared_bound)
            return target
        result = self.build(milestone, recipe, declared_bound)
        with target.open("x", encoding="utf-8") as stream:
            stream.write(json.dumps(result, indent=2, sort_keys=True) + "\n")
        return target


def revision_main(root: Path, argv: list[str], milestone: int,
                  recipe: Callable[[], dict], declared_bound: tuple[str, ...]) -> int:
    if argv not in (["--verify"], ["--write-current"]):
        print("Historical receipts are immutable. Use --verify or --write-current for the declared successor revision.")
        return 2
    try:
        current = CurrentReceipts(root)
        if argv == ["--verify"]:
            current.verify(milestone, recipe, declared_bound)
            print(f"M{milestone} successor verified: historical custody + current bindings; no protected promotion")
        else:
            print("current receipt:", current.write(milestone, recipe, declared_bound))
        return 0
    except (ReceiptError, OSError, KeyError, TypeError) as exc:
        print(f"CURRENT RECEIPT REFUSED: {exc}")
        return 1
