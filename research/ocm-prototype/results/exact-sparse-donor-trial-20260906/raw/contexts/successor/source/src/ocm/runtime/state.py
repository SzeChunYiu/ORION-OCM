from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "ocm.runtime.state.v1"
RUNTIME_VERSION = "0.1.0"
GENESIS_HASH = "0" * 64


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_json(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def _evidence_id(value: int | str) -> str:
    text = str(value)
    if not text:
        raise ValueError("evidence_id must be non-empty")
    return text


@dataclass(frozen=True, slots=True)
class ProcedureRecord:
    name: str
    table: tuple[int, int, int, int]
    evidence_id: str
    channel: str

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("procedure name must be non-blank")
        if len(self.table) != 4 or any(v not in (0, 1) for v in self.table):
            raise ValueError("M0 controlled procedure table must contain four binary outputs")
        if not self.evidence_id:
            raise ValueError("procedure evidence_id must be non-empty")
        if not self.channel.strip():
            raise ValueError("procedure channel must be non-blank")

    @property
    def object_id(self) -> str:
        return f"procedure:{self.name}"

    @property
    def content_hash(self) -> str:
        return sha256_json({"name": self.name, "table": list(self.table), "evidence_id": self.evidence_id, "channel": self.channel})

    def as_dict(self) -> dict[str, Any]:
        return {"name": self.name, "table": list(self.table), "evidence_id": self.evidence_id, "channel": self.channel, "content_hash": self.content_hash}


@dataclass(slots=True)
class RuntimeState:
    schema_version: str = SCHEMA_VERSION
    runtime_version: str = RUNTIME_VERSION
    sequence: int = 0
    head_hash: str = GENESIS_HASH
    objects: dict[str, str] = field(default_factory=dict)
    warrants: dict[str, tuple[str, ...]] = field(default_factory=dict)
    revoked: set[str] = field(default_factory=set)
    dependencies: dict[str, set[str]] = field(default_factory=dict)
    procedures: dict[str, ProcedureRecord] = field(default_factory=dict)

    def apply(self, event: dict[str, Any]) -> None:
        kind = str(event["kind"])
        payload = event["payload"]
        if kind == "LEARN_PROCEDURE":
            rec = ProcedureRecord(str(payload["name"]), tuple(int(v) for v in payload["table"]), _evidence_id(payload["evidence_id"]), str(payload["channel"]))
            self.procedures[rec.name] = rec
            self.objects[rec.object_id] = rec.content_hash
            self.warrants[rec.object_id] = (rec.evidence_id,)
        elif kind == "ADMIT_OBJECT":
            object_id = str(payload["object_id"]); content_hash = str(payload["content_hash"])
            if not object_id or len(content_hash) != 64: raise ValueError("invalid object admission")
            evidence = tuple(sorted({_evidence_id(v) for v in payload.get("evidence_ids", [])}))
            self.objects[object_id] = content_hash; self.warrants[object_id] = evidence
        elif kind == "REVOKE_EVIDENCE": self.revoked.add(_evidence_id(payload["evidence_id"]))
        elif kind == "REINSTATE_EVIDENCE": self.revoked.discard(_evidence_id(payload["evidence_id"]))
        elif kind == "LINK_DEPENDENCY":
            dependent = str(payload["dependent"]); prerequisite = str(payload["prerequisite"])
            if not dependent or not prerequisite: raise ValueError("dependency identities must be non-blank")
            self.dependencies.setdefault(dependent, set()).add(prerequisite)
        else: raise ValueError(f"unknown runtime event kind: {kind}")
        self.sequence = int(event["sequence"]); self.head_hash = str(event["event_hash"])

    def snapshot(self) -> dict[str, Any]:
        return {"schema_version": self.schema_version, "runtime_version": self.runtime_version, "sequence": self.sequence, "head_hash": self.head_hash, "object_identities": sorted(self.objects), "warrants": {k: list(self.warrants[k]) for k in sorted(self.warrants)}, "revoked_set": sorted(self.revoked), "dependency_links": {k: sorted(self.dependencies[k]) for k in sorted(self.dependencies)}, "learned_procedures": {k: self.procedures[k].as_dict() for k in sorted(self.procedures)}, "content_hashes": {k: self.objects[k] for k in sorted(self.objects)}}

    @property
    def state_hash(self) -> str: return sha256_json(self.snapshot())


class EventStore:
    """Append-only, hash-chained JSONL event store with deterministic replay."""
    def __init__(self, path: str | Path): self.path = Path(path)
    def replay(self) -> RuntimeState:
        state = RuntimeState()
        if not self.path.exists(): return state
        previous = GENESIS_HASH; expected_sequence = 1
        for line_no, raw in enumerate(self.path.read_text(encoding="utf-8").splitlines(), start=1):
            if not raw.strip(): continue
            event = json.loads(raw)
            if event.get("schema_version") != SCHEMA_VERSION: raise ValueError(f"unsupported event schema at line {line_no}")
            if int(event.get("sequence", -1)) != expected_sequence: raise ValueError(f"event sequence gap at line {line_no}")
            if event.get("prev_hash") != previous: raise ValueError(f"event hash chain broken at line {line_no}")
            body = {k: event[k] for k in ("schema_version", "sequence", "kind", "payload", "prev_hash")}
            calculated = sha256_json(body)
            if event.get("event_hash") != calculated: raise ValueError(f"event content hash mismatch at line {line_no}")
            state.apply(event); previous = calculated; expected_sequence += 1
        return state
    def append(self, state: RuntimeState, kind: str, payload: dict[str, Any]) -> dict[str, Any]:
        event = {"schema_version": SCHEMA_VERSION, "sequence": state.sequence + 1, "kind": kind, "payload": payload, "prev_hash": state.head_hash}
        event["event_hash"] = sha256_json(event)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8", newline="\n") as fh:
            fh.write(canonical_json(event) + "\n"); fh.flush(); os.fsync(fh.fileno())
        state.apply(event); return event


class OCMRuntime:
    """Minimal M0 custody runtime; this is not the later M2 unified KSO runtime claim."""
    def __init__(self, event_log: str | Path): self.store = EventStore(event_log); self.state = self.store.replay()
    def learn_procedure(self, name: str, table: tuple[int, int, int, int], evidence_id: int | str, *, channel: str = "INSTRUCTION") -> ProcedureRecord:
        self.store.append(self.state, "LEARN_PROCEDURE", {"name": name, "table": list(table), "evidence_id": _evidence_id(evidence_id), "channel": channel}); return self.state.procedures[name]
    def admit_object(self, object_id: str, content: bytes, evidence_ids: tuple[int | str, ...] = ()) -> str:
        digest = hashlib.sha256(content).hexdigest(); self.store.append(self.state, "ADMIT_OBJECT", {"object_id": object_id, "content_hash": digest, "evidence_ids": [_evidence_id(v) for v in evidence_ids]}); return digest
    def revoke(self, evidence_id: int | str) -> None: self.store.append(self.state, "REVOKE_EVIDENCE", {"evidence_id": _evidence_id(evidence_id)})
    def reinstate(self, evidence_id: int | str) -> None: self.store.append(self.state, "REINSTATE_EVIDENCE", {"evidence_id": _evidence_id(evidence_id)})
    def link_dependency(self, dependent: str, prerequisite: str) -> None: self.store.append(self.state, "LINK_DEPENDENCY", {"dependent": dependent, "prerequisite": prerequisite})
    def run(self, name: str, x: tuple[int, int]) -> tuple[str, int | None]:
        rec = self.state.procedures.get(name)
        if rec is None: return "GAP_UNKNOWN_PROCEDURE", None
        if rec.evidence_id in self.state.revoked: return "GAP_REVOKED_PROCEDURE", None
        if len(x) != 2 or any(v not in (0, 1) for v in x): return "CANNOT_CHECK_INPUT_OUTSIDE_REGISTERED_DOMAIN", None
        return "PASS", rec.table[x[0] * 2 + x[1]]
    def snapshot(self) -> dict[str, Any]: return self.state.snapshot()
    @property
    def state_hash(self) -> str: return self.state.state_hash
