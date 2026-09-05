"""DialogueWorkspace.v1 (M4 §1–§2, §5, §10): scoped, persistent working cognition for a conversation.

Three epistemic layers for every proposition (M4 §2):
  utterance content  — the turn log (immutable history; `turns`)
  speaker commitment — `Commitment` records (ACTIVE / SUPERSEDED / RETRACTED), each backed by the
                       runtime's OBSERVATION evidence with `speaker` authority and conversation scope
  machine warrant    — the runtime's own liveness of the proposition (never derived from commitments
                       without a bridge; B1 / MEG-05)

Persistence: the workspace writes its state atomically to ``<runtime.root>/dialogue/<conversation>.json``
after every mutation and reloads it on restart; every evidence id it references must exist in the
runtime's evidence registry, otherwise the load is CANNOT_CHECK (never a silent partial state).
Correction = supersession (B5 / MEG-03): the old commitment's evidence is revoked in the runtime
(dependents reopen exactly, KS-T22) and linked ``superseded_by``; history is never edited.
Nothing here is world knowledge: promotion is `propose_promote` (M4 §10) under the authority meet.
"""
from __future__ import annotations

import hashlib
import json
import os
from dataclasses import asdict, dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from ocm.kso.types import Authority, Scope
from ocm.kso.warrant import Liveness
from ocm.runtime.ocm_runtime import OCMRuntime
from ocm.store.evidence import Channel

from ocm.language.meaning import MeaningGraph, canonical


class CommitmentStatus(str, Enum):
    ACTIVE = "ACTIVE"
    SUPERSEDED = "SUPERSEDED"
    RETRACTED = "RETRACTED"


class WorkspaceRefusal(RuntimeError):
    def __init__(self, code: str, detail: str = "") -> None:
        super().__init__(f"{code}: {detail}")
        self.code = code
        self.detail = detail


@dataclass
class Entity:
    entity_id: str
    kind: str                                  # registry node type (entity, event, value, …)
    descriptions: list[str] = field(default_factory=list)   # "the robot", "it"
    aliases: list[str] = field(default_factory=list)        # names
    introduced_turn: int = 0
    mentions: list[int] = field(default_factory=list)       # turn ids
    features: dict[str, str] = field(default_factory=dict)
    kso_atom: str | None = None                # link to a long-term KSO object, if any


@dataclass
class Commitment:
    commitment_id: str
    turn_id: int
    speaker: str
    digest: str                                # canonical meaning digest of the (positive) proposition
    negated: bool
    evidence_id: str                           # runtime evidence backing this commitment
    meaning: dict[str, Any]
    status: CommitmentStatus = CommitmentStatus.ACTIVE
    superseded_by: str | None = None
    supersedes: str | None = None
    topic: str | None = None


@dataclass
class Turn:
    turn_id: int
    speaker: str
    utterance: str
    act: str                                   # dialogue act (M4 §9)
    verdict: str
    evidence: list[str] = field(default_factory=list)
    meaning_digest: str | None = None
    topic: str | None = None


@dataclass
class OpenItem:
    item_id: str
    kind: str                                  # question | obligation | reference | ambiguity
    turn_id: int
    detail: dict[str, Any]
    resolved_turn: int | None = None


@dataclass
class DialogueWorkspace:
    runtime: OCMRuntime
    conversation_id: str
    participants: list[str] = field(default_factory=list)
    turns: list[Turn] = field(default_factory=list)
    entities: dict[str, Entity] = field(default_factory=dict)
    commitments: dict[str, Commitment] = field(default_factory=dict)
    open_items: dict[str, OpenItem] = field(default_factory=dict)
    topics: list[str] = field(default_factory=list)          # focus stack; last = current
    preferences: dict[str, Any] = field(default_factory=dict)  # conversation-scoped only
    assumptions: list[str] = field(default_factory=list)
    machine_commitments: list[dict[str, Any]] = field(default_factory=list)
    _counter: int = 0

    # ------------------------------------------------------------------ persistence
    @property
    def path(self) -> Path:
        return Path(self.runtime.root) / "dialogue" / f"{self.conversation_id}.json"

    def snapshot(self) -> dict[str, Any]:
        return {
            "conversation_id": self.conversation_id, "participants": self.participants,
            "turns": [asdict(t) for t in self.turns], "entities": {k: asdict(v) for k, v in self.entities.items()},
            "commitments": {k: {**asdict(v), "status": v.status.value} for k, v in self.commitments.items()},
            "open_items": {k: asdict(v) for k, v in self.open_items.items()}, "topics": self.topics,
            "preferences": self.preferences, "assumptions": self.assumptions, "machine_commitments": self.machine_commitments,
            "counter": self._counter,
        }

    def state_hash(self) -> str:
        return hashlib.sha256(json.dumps(self.snapshot(), sort_keys=True).encode()).hexdigest()

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.path.with_suffix(".tmp")
        tmp.write_text(json.dumps(self.snapshot(), sort_keys=True, indent=1), encoding="utf-8")
        os.replace(tmp, self.path)

    @classmethod
    def load(cls, runtime: OCMRuntime, conversation_id: str) -> "DialogueWorkspace":
        ws = cls(runtime, conversation_id)
        if not ws.path.exists():
            return ws
        d = json.loads(ws.path.read_text(encoding="utf-8"))
        ws.participants = list(d["participants"])
        ws.turns = [Turn(**t) for t in d["turns"]]
        ws.entities = {k: Entity(**v) for k, v in d["entities"].items()}
        ws.commitments = {k: Commitment(**{**v, "status": CommitmentStatus(v["status"])}) for k, v in d["commitments"].items()}
        ws.open_items = {k: OpenItem(**v) for k, v in d["open_items"].items()}
        ws.topics = list(d["topics"])
        ws.preferences = dict(d["preferences"])
        ws.assumptions = list(d["assumptions"])
        ws.machine_commitments = list(d["machine_commitments"])
        ws._counter = int(d["counter"])
        # every referenced evidence id must exist in the runtime registry; a missing one is CANNOT_CHECK
        known = set(runtime.state.evidence.records)
        missing = sorted({c.evidence_id for c in ws.commitments.values()} - known)
        if missing:
            raise WorkspaceRefusal("CANNOT_CHECK", f"workspace references evidence absent from the ledger: {missing}")
        return ws

    # ------------------------------------------------------------------ ids
    def _next(self, prefix: str) -> str:
        self._counter += 1
        return f"{prefix}:{self.conversation_id}:{self._counter}"

    @property
    def current_topic(self) -> str | None:
        return self.topics[-1] if self.topics else None

    # ------------------------------------------------------------------ turns
    def record_turn(self, speaker: str, utterance: str, act: str, verdict: str, *, evidence: Iterable[str] = (), meaning_digest: str | None = None) -> Turn:
        if speaker not in self.participants:
            self.participants.append(speaker)
        t = Turn(len(self.turns) + 1, speaker, utterance, act, verdict, list(evidence), meaning_digest, self.current_topic)
        self.turns.append(t)
        self.save()
        return t

    # ------------------------------------------------------------------ entities
    def introduce(self, kind: str, description: str | None = None, alias: str | None = None, *, features: Mapping[str, str] | None = None, turn_id: int | None = None, kso_atom: str | None = None) -> Entity:
        e = Entity(self._next("ent"), kind, [description] if description else [], [alias] if alias else [], turn_id or len(self.turns), [turn_id or len(self.turns)], dict(features or {}), kso_atom)
        self.entities[e.entity_id] = e
        self.save()
        return e

    def mention(self, entity_id: str, *, description: str | None = None, alias: str | None = None, turn_id: int | None = None) -> None:
        e = self.entities[entity_id]
        e.mentions.append(turn_id or len(self.turns))
        if description and description not in e.descriptions:
            e.descriptions.append(description)
        if alias and alias not in e.aliases:
            e.aliases.append(alias)
        self.save()

    # ------------------------------------------------------------------ commitments (speaker layer)
    def commit(self, speaker: str, meaning: MeaningGraph, *, negated: bool = False, turn_id: int | None = None, supersedes: str | None = None, utterance: str = "") -> Commitment:
        """Record a speaker commitment backed by OBSERVATION evidence.  Supersession revokes the old
        commitment's evidence (dependents reopen), links both ways, and keeps the old record."""
        digest = canonical(meaning)[1]
        old = self.commitments.get(supersedes) if supersedes else None
        if supersedes and old is None:
            raise WorkspaceRefusal("UNKNOWN_COMMITMENT", supersedes)
        conflicting = [c for c in self.active_commitments() if c.digest == digest and c.negated != negated and c.commitment_id != supersedes]
        _, eid = self.runtime.admit_evidence(
            {"dialogue": self.conversation_id, "said": True, "speaker": speaker, "utterance": utterance, "digest": digest, "negated": negated, "supersedes": old.evidence_id if old else None},
            Channel.OBSERVATION, speaker, scope=Scope.of(self.conversation_id), contradicts=tuple(c.evidence_id for c in conflicting),
            supersedes=old.evidence_id if old else None,
        )
        c = Commitment(self._next("cmt"), turn_id or len(self.turns), speaker, digest, negated, eid, meaning.as_dict(), supersedes=supersedes, topic=self.current_topic)
        self.commitments[c.commitment_id] = c
        if old is not None:
            old.status = CommitmentStatus.SUPERSEDED
            old.superseded_by = c.commitment_id
            self.runtime.revoke([old.evidence_id])          # dependents of the old commitment reopen exactly (KS-T22)
        self.save()
        return c

    def retract(self, commitment_id: str) -> Commitment:
        c = self.commitments.get(commitment_id)
        if c is None:
            raise WorkspaceRefusal("UNKNOWN_COMMITMENT", commitment_id)
        if c.status is not CommitmentStatus.ACTIVE:
            raise WorkspaceRefusal("NOT_ACTIVE", f"{commitment_id} is {c.status.value}")
        c.status = CommitmentStatus.RETRACTED
        self.runtime.revoke([c.evidence_id])
        self.save()
        return c

    def active_commitments(self, speaker: str | None = None) -> list[Commitment]:
        rv = self.runtime.state.revoked
        return [c for c in self.commitments.values() if c.status is CommitmentStatus.ACTIVE and c.evidence_id not in rv and (speaker is None or c.speaker == speaker)]

    def commitments_on(self, meaning: MeaningGraph) -> tuple[list[Commitment], list[Commitment]]:
        """(asserting, denying) active commitments on the proposition."""
        d = canonical(meaning)[1]
        act = self.active_commitments()
        return [c for c in act if c.digest == d and not c.negated], [c for c in act if c.digest == d and c.negated]

    # ------------------------------------------------------------------ machine layer
    def machine_liveness(self, evidence_ids: Iterable[str]) -> Liveness:
        return self.runtime.state.evidence.liveness(evidence_ids)

    def propose_promote(self, commitment_id: str, target_scope: Scope, *, bridge_evidence: Sequence[str] = (), bridge_authority: Authority | None = None) -> dict[str, Any]:
        """M4 §10: promotion of a dialogue object to longer-lived knowledge needs a bridge (independent
        evidence with authority) — the result authority is the meet; no bridge ⇒ refused."""
        c = self.commitments.get(commitment_id)
        if c is None:
            raise WorkspaceRefusal("UNKNOWN_COMMITMENT", commitment_id)
        if c.status is not CommitmentStatus.ACTIVE:
            return {"promoted": False, "reason": f"commitment is {c.status.value}"}
        if not bridge_evidence or bridge_authority is None:
            return {"promoted": False, "reason": "NO_BRIDGE: speaker commitment alone never becomes machine knowledge"}
        live = self.machine_liveness(bridge_evidence)
        if live is not Liveness.LIVE:
            return {"promoted": False, "reason": f"bridge evidence is {live.value}"}
        authority = Authority.of(speaker=1).meet(bridge_authority)
        _, eid = self.runtime.admit_evidence({"promoted_from": commitment_id, "digest": c.digest, "bridge": list(bridge_evidence)}, Channel.IMPORTED, "dialogue.promote", scope=target_scope)
        self.machine_commitments.append({"commitment_id": commitment_id, "evidence_id": eid, "scope": target_scope.as_dict(), "authority": authority.as_dict() if hasattr(authority, "as_dict") else str(authority)})
        self.save()
        return {"promoted": True, "evidence_id": eid, "authority": authority}

    # ------------------------------------------------------------------ open items / topics
    def open(self, kind: str, detail: Mapping[str, Any], turn_id: int | None = None) -> OpenItem:
        it = OpenItem(self._next(kind), kind, turn_id or len(self.turns), dict(detail))
        self.open_items[it.item_id] = it
        self.save()
        return it

    def resolve(self, item_id: str, turn_id: int | None = None) -> None:
        self.open_items[item_id].resolved_turn = turn_id or len(self.turns)
        self.save()

    def unresolved(self, kind: str | None = None) -> list[OpenItem]:
        return [i for i in self.open_items.values() if i.resolved_turn is None and (kind is None or i.kind == kind)]

    def push_topic(self, topic: str) -> None:
        if topic in self.topics:
            self.topics.remove(topic)              # return to an earlier topic: re-focus, never clip
        self.topics.append(topic)
        self.save()

    def set_preference(self, key: str, value: Any) -> None:
        self.preferences[key] = value              # conversation scope only; never global
        self.save()


def mutant_correction_overwrites_history(ws: DialogueWorkspace, commitment_id: str, new_meaning: MeaningGraph) -> None:
    """Planted (M4 §5 hostile): edit the old commitment in place instead of superseding it."""
    c = ws.commitments[commitment_id]
    c.meaning = new_meaning.as_dict()
    c.digest = canonical(new_meaning)[1]


def mutant_promote_all_assertions(ws: DialogueWorkspace) -> list[str]:
    """Planted (M4 §14 hostile): every active speaker commitment becomes machine knowledge."""
    out = []
    for c in ws.active_commitments():
        _, eid = ws.runtime.admit_evidence({"promoted_from": c.commitment_id, "digest": c.digest, "bridge": []}, Channel.IMPORTED, "dialogue.promote#mutant", scope=Scope.universal())
        out.append(eid)
    return out
