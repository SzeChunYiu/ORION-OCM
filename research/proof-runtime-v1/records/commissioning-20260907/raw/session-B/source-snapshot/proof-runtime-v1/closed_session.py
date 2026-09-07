"""Fresh host-issued proof handles over a closed proposer and separate kernel check.

Host Python and filesystem remain trusted. This is not whole-OCM isolation or a
persistent authenticity store; the adapter must persist verified issuer bindings.
"""
import math
from pathlib import Path
import time
from uuid import uuid4
import session_dependencies as D
import session_dispatch as dispatch
from session_bindings import (canonical, detached, digest, fixed_task, inventory, runtime_check,
                              source_inventory, source_paths, write_bytes, write_json)
import json


class ProofSession:
    def __init__(self, runtime_manifest, expected_sha256, attempts_root, *, task=None, timeout_s=30):
        started = time.monotonic()
        self.root = Path(attempts_root).resolve(); self.root.mkdir(exist_ok=False)
        self._closed = False; self._proposals = {}; self._handles = {}; self._artifacts = {}
        self._manifest = Path(runtime_manifest); self._runtime = None
        self._task = detached(D.f0_fixture()); self._bindings = {}; self._environment_id = ""
        self._readiness = {"terminal": "CANNOT_CHECK", "reason": ""}
        self.timeout_s = timeout_s
        try:
            write_json(self.root / "requested-descriptor.json", self._task if task is None else task)
            self._task = fixed_task(task)
            if (isinstance(timeout_s, bool) or not isinstance(timeout_s, (int, float)) or
                    not math.isfinite(timeout_s) or not 0 < timeout_s <= 30):
                raise ValueError("timeout exceeds registered envelope")
            raw = self._manifest.read_bytes()
            write_bytes(self.root / "runtime-manifest.json", raw)
            if digest(raw) != expected_sha256: raise ValueError("runtime manifest differs from registered SHA256")
            self._runtime = json.loads(raw)
            sources = source_inventory()
            self._bindings = {"runtime_sha256": expected_sha256, "source_files": sources,
                              "target_sha256": D.TARGET_SHA256, "foundation_sha256": D.FOUNDATION_SHA256}
            for name, path in source_paths().items():
                dest = self.root / "source-snapshot" / name; dest.parent.mkdir(parents=True, exist_ok=True)
                write_bytes(dest, path.read_bytes())
            self._environment_id = digest(canonical(self._bindings))
            self._verify()
            self._readiness.update(terminal="READY")
        except (ValueError, TypeError, KeyError, OSError, RecursionError) as exc:
            self._readiness["reason"] = type(exc).__name__ + ": " + str(exc)
        self._readiness.update(wall_s=time.monotonic() - started, bindings=self.bindings,
            task_sha256=self.task_sha256, environment_id=self.environment_id,
            cost_scope="Readiness includes validation and source/runtime binding; final serialization and sealing require outer lifecycle accounting. Not native executable qualification.",
            runtime_cost={k: (self._runtime or {}).get(k) for k in ("preparation_wall_s", "acquisition",
                "preparation_including_failed_attempts_wall_s", "prior_development_preparations")})
        write_json(self.root / "registered-task.json", self._task)
        write_json(self.root / "session.json", self._readiness)
        self._root_records = {n: D.file_hash(self.root / n) for n in ("session.json", "registered-task.json", "requested-descriptor.json")
                              if (self.root / n).is_file()}

    @property
    def task(self): return detached(self._task)
    @property
    def task_sha256(self): return digest(canonical(self._task))
    @property
    def environment_id(self): return self._environment_id
    @property
    def bindings(self): return detached(self._bindings)
    @property
    def readiness(self): return detached(self._readiness)

    def _verify(self):
        if self._closed: raise ValueError("session closed; stale handles")
        if not self._runtime or not self._bindings: raise ValueError("session environment unavailable")
        expected = self._bindings["runtime_sha256"]
        if D.file_hash(self._manifest) != expected or D.file_hash(self.root / "runtime-manifest.json") != expected:
            raise ValueError("runtime manifest custody changed")
        if source_inventory() != self._bindings["source_files"]:
            raise ValueError("session or commissioned source changed")
        if inventory(self.root / "source-snapshot") != self._bindings["source_files"]:
            raise ValueError("source snapshot changed")
        for name, expected in getattr(self, "_root_records", {}).items():
            if D.file_hash(self.root / name) != expected: raise ValueError("session record changed")
        runtime_check(self._runtime)

    def _attempt(self, kind):
        token = uuid4().hex; dest = self.root / (kind + "-" + token); dest.mkdir()
        return token, dest, time.monotonic()

    def _finish(self, result, dest, started):
        result.update(wall_s=time.monotonic() - started, record_path=str(dest / "result.json"),
            cost_scope="Phase wall includes validation, copying and dispatch before final record serialization/sealing. Native envelopes overlap; outer lifecycle wall must include sealing. Runtime preparation separate; CPU/RSS/energy unmeasured.")
        write_json(dest / "result.json", result)
        result["record_sha256"] = D.file_hash(dest / "result.json")
        self._artifacts[str(dest)] = inventory(dest)
        return detached(result)

    def _custody(self, value, issued, key):
        if type(value) is not dict or type(value.get(key)) is not str:
            raise ValueError("issued data handle required")
        saved = issued.get(value[key])
        if saved is None or canonical(saved) != canonical(value): raise ValueError("unissued or changed handle")
        dest = str(Path(saved["record_path"]).parent)
        if inventory(dest) != self._artifacts[dest]: raise ValueError("issued artifact custody changed")
        return saved

    def propose(self, task_bytes, registered_sha256):
        token, dest, started = self._attempt("proposal")
        result = {"status": "CANNOT_CHECK", "candidate": None, "reason": "", "proposal_id": token,
                  "task_sha256": self.task_sha256, "environment_id": self.environment_id}
        try:
            if type(task_bytes) is not bytes or len(task_bytes) > 262144:
                raise ValueError("registered task byte bound")
            write_bytes(dest / "requested-task.json", task_bytes)
            write_json(dest / "request-binding.json", {"registered_sha256": registered_sha256})
            if registered_sha256 != self.task_sha256 or task_bytes != canonical(self._task):
                raise ValueError("task differs from registered descriptor")
            if self._readiness["terminal"] != "READY": raise ValueError(self._readiness["reason"])
            self._verify()
            proposal = dispatch.propose(task_bytes, self._runtime, dest, self._bindings["source_files"], self.timeout_s)
            if not set(proposal["used_constants"]) <= {int(k) for k in self._task["constants"]}:
                raise ValueError("candidate dependencies exceed permitted input")
            self._verify(); result.update(proposal)
        except (ValueError, TypeError, KeyError, OSError, RecursionError) as exc:
            result.update(status="CANNOT_CHECK", candidate=None, reason=type(exc).__name__ + ": " + str(exc))
        result = self._finish(result, dest, started)
        if result["status"] == "FOUND": self._proposals[token] = detached(result)
        return result

    def check(self, candidate_data):
        token, dest, started = self._attempt("check")
        result = {"terminal": "CANNOT_CHECK", "reason": "", "run_id": token,
                  "task_sha256": self.task_sha256, "environment_id": self.environment_id}
        try:
            write_json(dest / "requested-proposal.json", candidate_data)
            self._verify(); proposal = self._custody(candidate_data, self._proposals, "proposal_id")
            result["candidate_sha256"] = digest(canonical(proposal["candidate"]))
            result["proposal_id"] = proposal["proposal_id"]
            checked = dispatch.check(proposal["candidate"], self._runtime, dest, self.timeout_s)
            self._verify(); self._custody(candidate_data, self._proposals, "proposal_id")
            result.update(terminal=checked["terminal"], reason=checked.get("reason", ""), checker=checked)
        except (ValueError, TypeError, KeyError, OSError, RecursionError) as exc:
            result.update(terminal="CANNOT_CHECK", reason=type(exc).__name__ + ": " + str(exc))
        result = self._finish(result, dest, started)
        if result["terminal"] == "KERNEL_PASS": self._handles[token] = detached(result)
        return result

    def authentic_for(self, handle, task_digest, candidate_digest, environment_id):
        _, dest, started = self._attempt("authenticate")
        result = {"terminal": "CANNOT_CHECK", "reason": ""}
        try:
            self._verify(); saved = self._custody(handle, self._handles, "run_id")
            if (task_digest, candidate_digest, environment_id) != (
                    saved["task_sha256"], saved["candidate_sha256"], saved["environment_id"]):
                raise ValueError("task/candidate/environment differs from issued check")
            self._custody(self._proposals[saved["proposal_id"]], self._proposals, "proposal_id")
            result["terminal"] = "AUTHENTIC"
        except (ValueError, TypeError, KeyError, OSError, RecursionError) as exc:
            result["reason"] = type(exc).__name__ + ": " + str(exc)
        self._finish(result, dest, started)
        return result["terminal"] == "AUTHENTIC"

    def close(self):
        if not self._closed: write_json(self.root / "closed.json", {"closed": True})
        self._closed = True; self._handles.clear(); self._proposals.clear()
