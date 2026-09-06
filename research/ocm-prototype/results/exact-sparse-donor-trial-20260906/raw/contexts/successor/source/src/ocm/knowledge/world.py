"""Bounded knowledge world with provenance (M6 §4–§5).

Every fact is a `Fact`: a proposition (meaning graph) plus *source records*.  Ingestion keeps the
four statements apart (M6 §5):

    source document exists              → SourceDocument (id, title, licence, hash, revision)
    source asserts proposition P        → SourceAssertion evidence (channel IMPORTED, authority source=1)
    OCM has parsed candidate meaning P  → the Fact's meaning graph (digest)
    P is corroborated / warranted       → a Verification evidence (channel PROOF/OBSERVATION, declared
                                          authority) — the machine layer's warrant is the ⊗ of
                                          assertion and verification; repetition of assertions never
                                          raises authority (majority mutant)

The world is loaded from a manifest (hand-authored controlled facts for exact adversarial cases;
Wikidata / Simple Wikipedia subsets by custody script) and admitted into the runtime ledger so that
revoking one source reopens exactly the answers that depended on it (KS-T22).
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from ocm.kso.types import Authority, Scope
from ocm.kso.warrant import Liveness, WarrantProfile
from ocm.runtime.ocm_runtime import OCMRuntime
from ocm.store.evidence import Channel

from ocm.language.meaning import MEdge, MNode, MeaningGraph, canonical


@dataclass(frozen=True)
class SourceDocument:
    source_id: str
    title: str
    licence: str
    content_hash: str
    revision: str = ""
    kind: str = "hand_authored"           # hand_authored | wikidata | simple_wikipedia | dictionary


@dataclass
class Fact:
    fact_id: str
    meaning: MeaningGraph
    digest: str
    topic: str
    sources: list[str]                    # source ids asserting it
    assertion_evidence: list[str] = field(default_factory=list)
    verification_evidence: list[str] = field(default_factory=list)
    verified_by: str | None = None        # declared verifier authority ("curator", "checker")
    gloss: str = ""                       # canonical English rendering for realisation fallback


def triple(subject: str, relation: str, obj: str, *, subject_type: str = "entity", obj_type: str = "entity", value: str | None = None) -> MeaningGraph:
    """A simple relational fact as a meaning graph: subject —relation→ object (or value)."""
    nodes = (MNode("s", subject_type, subject), MNode("o", obj_type, obj))
    return MeaningGraph(nodes, (MEdge(relation, ("s",), ("o",), value),), root="s")


@dataclass
class KnowledgeWorld:
    runtime: OCMRuntime
    documents: dict[str, SourceDocument] = field(default_factory=dict)
    facts: dict[str, Fact] = field(default_factory=dict)
    by_digest: dict[str, str] = field(default_factory=dict)
    manifest_hash: str | None = None

    # ------------------------------------------------------------------ ingestion
    def add_document(self, doc: SourceDocument) -> None:
        self.documents[doc.source_id] = doc

    def assert_fact(self, fact_id: str, meaning: MeaningGraph, topic: str, source_id: str, *, gloss: str = "") -> Fact:
        """'source asserts P' — IMPORTED evidence with authority source=1 (never world_truth)."""
        if source_id not in self.documents:
            raise KeyError(f"unknown source {source_id}")
        digest = canonical(meaning)[1]
        f = self.facts.get(fact_id)
        if f is None:
            f = Fact(fact_id, meaning, digest, topic, [], gloss=gloss)
            self.facts[fact_id] = f
            self.by_digest[digest] = fact_id
        _, eid = self.runtime.admit_evidence({"asserts": digest, "fact": fact_id, "source": source_id}, Channel.IMPORTED, f"source:{source_id}", scope=Scope.of(topic))
        f.sources.append(source_id)
        f.assertion_evidence.append(eid)
        return f

    def verify_fact(self, fact_id: str, verifier: str, *, channel: Channel = Channel.PROOF) -> str:
        """'P is corroborated under declared authority' — a separate evidence record."""
        f = self.facts[fact_id]
        _, eid = self.runtime.admit_evidence({"verifies": f.digest, "fact": fact_id, "verifier": verifier}, channel, f"verifier:{verifier}", scope=Scope.of(f.topic))
        f.verification_evidence.append(eid)
        f.verified_by = verifier
        return eid

    # ------------------------------------------------------------------ queries
    def warrant(self, fact_id: str) -> WarrantProfile:
        """⊕ over assertions ⊗ (verification if any): an asserted-but-unverified fact is a *source
        claim*, LIVE at source authority only."""
        f = self.facts[fact_id]
        w = WarrantProfile.zero()
        for e in f.assertion_evidence:
            w = w.join(WarrantProfile.of({e}))
        if f.verification_evidence:
            v = WarrantProfile.zero()
            for e in f.verification_evidence:
                v = v.join(WarrantProfile.of({e}))
            w = w.meet(v)
        return w

    def authority(self, fact_id: str) -> Authority:
        f = self.facts[fact_id]
        a = Authority.of(source=1)
        if f.verification_evidence and self.runtime.state.evidence.liveness(f.verification_evidence) is Liveness.LIVE:
            a = Authority.of(source=1, verified=1)
        return a

    def liveness(self, fact_id: str) -> Liveness:
        return self.warrant(fact_id).liveness(self.runtime.state.revoked)

    def lookup(self, meaning: MeaningGraph) -> tuple[Fact | None, Liveness]:
        d = canonical(meaning)[1]
        fid = self.by_digest.get(d)
        if fid is None:
            return None, Liveness.UNKNOWN
        return self.facts[fid], self.liveness(fid)

    def about(self, label: str) -> list[Fact]:
        """Live facts whose meaning mentions the label (for explanation / comparison / summary)."""
        out = []
        for f in self.facts.values():
            if any(n.label == label for n in f.meaning.nodes) and self.liveness(f.fact_id) is Liveness.LIVE:
                out.append(f)
        return out

    def relations_of(self, label: str) -> dict[str, list[tuple[str, str | None]]]:
        rel: dict[str, list[tuple[str, str | None]]] = {}
        for f in self.about(label):
            for e in f.meaning.edges:
                tail = f.meaning.node(e.tails[0]).label
                head = f.meaning.node(e.heads[0]).label
                if tail == label:
                    rel.setdefault(e.relation, []).append((head, e.value))
        return rel

    def revoke_source(self, source_id: str) -> dict[str, Any]:
        """Remove one source: its assertion evidence is revoked; facts asserted only by it die."""
        ev = [e for f in self.facts.values() for e, s in zip(f.assertion_evidence, f.sources) if s == source_id]
        report = self.runtime.revoke(ev)
        dead = sorted(fid for fid in self.facts if self.liveness(fid) is Liveness.DEAD)
        return {"revoked_evidence": ev, "facts_dead": dead, "reopen": sorted(report.reopen), "recheck": sorted(report.recheck)}

    # ------------------------------------------------------------------ manifest
    def load_manifest(self, path: str | Path) -> dict[str, Any]:
        raw = Path(path).read_bytes()
        self.manifest_hash = hashlib.sha256(raw).hexdigest()
        m = json.loads(raw.decode("utf-8"))
        for d in m["documents"]:
            self.add_document(SourceDocument(d["source_id"], d["title"], d["licence"], d.get("content_hash", ""), d.get("revision", ""), d.get("kind", "hand_authored")))
        for fct in m["facts"]:
            g = triple(fct["subject"], fct["relation"], fct["object"], subject_type=fct.get("subject_type", "entity"), obj_type=fct.get("object_type", "entity"), value=fct.get("value"))
            for s in fct["sources"]:
                self.assert_fact(fct["fact_id"], g, fct["topic"], s, gloss=fct.get("gloss", ""))
            if fct.get("verified_by"):
                self.verify_fact(fct["fact_id"], fct["verified_by"])
        return {"manifest_sha256": self.manifest_hash, "documents": len(self.documents), "facts": len(self.facts), "verified": sum(1 for f in self.facts.values() if f.verification_evidence)}


def mutant_repetition_raises_authority(world: KnowledgeWorld, fact_id: str, k: int) -> Authority:
    """Planted (M6 §5): k source assertions treated as verification."""
    f = world.facts[fact_id]
    return Authority.of(source=1, verified=1) if len(f.assertion_evidence) >= k else Authority.of(source=1)
