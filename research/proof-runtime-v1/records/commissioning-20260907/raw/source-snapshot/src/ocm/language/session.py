"""Dialogue session over the M2 runtime (M3 §7, §12): the discourse record as ledger events.

Every utterance is interpreted; the outcome is *recorded*, never guessed:

* INTERPRETED statement → `said(speaker, meaning)` admitted as OBSERVATION evidence (speaker
  authority, conversation scope) — the machine now knows *that it was said*, not that it is true.
* INTERPRETED yes/no question → answered from the discourse record and the machine store: YES /
  NO / UNKNOWN (never a guess); the answer cites the evidence it rests on.
* AMBIGUOUS → a clarification question listing the retained candidates; the reply is INTERACTION
  evidence that collapses the set (the collapse is an evidence event, MEG-26).
* UNKNOWN_LEXEME / UNKNOWN_CONSTRUCTION → a LEARN request; a demonstration (utterance, meaning)
  reaches the version-space learner (M3 §5) and, on PASS, the construction is admitted with the
  demonstrations' evidence as its warrant.
* Retraction ("I was wrong about …") revokes the said-evidence; dependent answers reopen exactly
  (KS-T22), nothing else.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Hashable, Iterable, Mapping, Sequence

from ocm.kso.types import Authority, Scope
from ocm.kso.warrant import Liveness, WarrantProfile
from ocm.runtime.ocm_runtime import OCMRuntime
from ocm.store.evidence import Channel

from . import acquisition as AQ
from .constructions import CandidateMeaning, Construction
from .interpret import Interpretation, Verdict, interpret
from .lexicon import Lexicon
from .meaning import MeaningGraph, canonical, isomorphic


class ReplyKind(str, Enum):
    RECORDED = "RECORDED"            # statement recorded as said(...)
    ANSWER = "ANSWER"                # YES / NO / UNKNOWN with evidence
    CLARIFY = "CLARIFY"              # ambiguity retained; candidates listed
    LEARN = "LEARN"                  # unknown lexeme/construction; demonstration requested
    NEEDS_CONTEXT = "NEEDS_CONTEXT"
    CONTRADICTION = "CONTRADICTION"
    RETRACTED = "RETRACTED"
    CANNOT_CHECK = "CANNOT_CHECK"


@dataclass(frozen=True)
class Reply:
    kind: ReplyKind
    text: str
    evidence: tuple[str, ...] = ()
    candidates: tuple[CandidateMeaning, ...] = ()
    interpretation: Interpretation | None = None
    meaning_digest: str | None = None


@dataclass
class SaidEntry:
    evidence_id: str
    speaker: str
    utterance: str
    meaning: MeaningGraph
    digest: str
    negated: bool


def _is_question(m: MeaningGraph) -> bool:
    return any(e.relation == "ASKS" for e in m.edges)


def _strip_question(m: MeaningGraph) -> MeaningGraph:
    nodes = tuple(n for n in m.nodes if n.node_type != "question_variable")
    edges = tuple(e for e in m.edges if e.relation != "ASKS")
    return MeaningGraph(nodes, edges, m.root)


def _is_negated(m: MeaningGraph) -> bool:
    return any(e.relation == "NEGATES" for e in m.edges)


def _strip_negation(m: MeaningGraph) -> MeaningGraph:
    return MeaningGraph(m.nodes, tuple(e for e in m.edges if e.relation != "NEGATES"), m.root)


@dataclass
class DialogueSession:
    runtime: OCMRuntime
    lexicon: Lexicon
    constructions: list[Construction]
    conversation: str = "conv"
    said: list[SaidEntry] = field(default_factory=list)
    pending_clarification: Interpretation | None = None
    pending_learn: str | None = None
    families: dict[str, AQ.ConstructionFamily] = field(default_factory=dict)
    demonstrations: dict[str, list[AQ.Demonstration]] = field(default_factory=dict)

    # ------------------------------------------------------------------ helpers
    def _revoked(self) -> frozenset:
        return frozenset(self.runtime.state.revoked)

    def _live_said(self) -> list[SaidEntry]:
        rv = self._revoked()
        return [s for s in self.said if s.evidence_id not in rv]

    def _lookup(self, m: MeaningGraph) -> tuple[list[SaidEntry], list[SaidEntry]]:
        """said entries asserting m (positive) and asserting ¬m (negative), live only."""
        d = canonical(m)[1]
        pos = [s for s in self._live_said() if not s.negated and s.digest == d]
        neg = [s for s in self._live_said() if s.negated and s.digest == d]
        return pos, neg

    # ------------------------------------------------------------------ main entry
    def hear(self, utterance: str, speaker: str = "user") -> Reply:
        if self.pending_clarification is not None:
            return self._resolve_clarification(utterance, speaker)
        r = interpret(utterance, self.lexicon, self.constructions, speaker=speaker, conversation=self.conversation, revoked=self._revoked())
        if r.verdict is Verdict.INTERPRETED:
            m = r.meaning
            if _is_question(m):
                return self._answer(_strip_question(m), r)
            return self._record(utterance, speaker, m, r)
        if r.verdict is Verdict.AMBIGUOUS:
            self.pending_clarification = r
            options = "; ".join(f"({i + 1}) {self._describe(c)}" for i, c in enumerate(r.candidates))
            return Reply(ReplyKind.CLARIFY, f"Which did you mean: {options}?", candidates=r.candidates, interpretation=r)
        if r.verdict in (Verdict.UNKNOWN_LEXEME, Verdict.UNKNOWN_CONSTRUCTION):
            self.pending_learn = utterance
            return Reply(ReplyKind.LEARN, f"I cannot interpret this yet ({r.verdict.value}: {r.reason}). Show me what it means.", interpretation=r)
        if r.verdict is Verdict.NEEDS_CONTEXT:
            return Reply(ReplyKind.NEEDS_CONTEXT, f"I need to know what you refer to: {r.reason}", candidates=r.candidates, interpretation=r)
        if r.verdict is Verdict.CONTRADICTION:
            return Reply(ReplyKind.CONTRADICTION, f"Every reading contradicts what is registered: {r.reason}", candidates=r.candidates, interpretation=r)
        return Reply(ReplyKind.CANNOT_CHECK, r.reason, interpretation=r)

    # ------------------------------------------------------------------ statements
    def _record(self, utterance: str, speaker: str, m: MeaningGraph, r: Interpretation) -> Reply:
        neg = _is_negated(m)
        base = _strip_negation(m) if neg else m
        digest = canonical(base)[1]
        pos, negs = self._lookup(base)
        conflicting = negs if not neg else pos
        outcome, eid = self.runtime.admit_evidence(
            {"said": True, "utterance": utterance, "meaning": base.as_dict(), "digest": digest, "negated": neg, "speaker": speaker},
            Channel.OBSERVATION, speaker, scope=Scope.of(self.conversation), authority=Authority.of(speaker=1),
            contradicts=tuple(s.evidence_id for s in conflicting),
        )
        self.said.append(SaidEntry(eid, speaker, utterance, base, digest, neg))
        text = f"Recorded: {speaker} said {'not ' if neg else ''}{self._describe_meaning(base)}."
        if conflicting:
            text += f" This contradicts what was said before ({', '.join(s.evidence_id for s in conflicting)}); both are kept, neither is promoted."
        return Reply(ReplyKind.RECORDED, text, evidence=(eid,), interpretation=r, meaning_digest=digest)

    # ------------------------------------------------------------------ questions
    def _answer(self, asked: MeaningGraph, r: Interpretation) -> Reply:
        pos, neg = self._lookup(asked)
        if pos and not neg:
            return Reply(ReplyKind.ANSWER, f"Yes — {pos[0].speaker} said so ({pos[0].evidence_id}); I have no independent warrant.", evidence=tuple(s.evidence_id for s in pos), interpretation=r, meaning_digest=canonical(asked)[1])
        if neg and not pos:
            return Reply(ReplyKind.ANSWER, f"No — {neg[0].speaker} said it did not ({neg[0].evidence_id}); I have no independent warrant.", evidence=tuple(s.evidence_id for s in neg), interpretation=r, meaning_digest=canonical(asked)[1])
        if pos and neg:
            return Reply(ReplyKind.ANSWER, "Unknown — contradictory statements are on record: " + ", ".join(s.evidence_id for s in pos + neg), evidence=tuple(s.evidence_id for s in pos + neg), interpretation=r)
        return Reply(ReplyKind.ANSWER, "Unknown — nothing on record supports or denies it.", interpretation=r, meaning_digest=canonical(asked)[1])

    # ------------------------------------------------------------------ clarification
    def _resolve_clarification(self, utterance: str, speaker: str) -> Reply:
        pending, self.pending_clarification = self.pending_clarification, None
        tok = utterance.strip().lower().strip(".!?")
        chosen: CandidateMeaning | None = None
        if tok.isdigit() and 1 <= int(tok) <= len(pending.candidates):
            chosen = pending.candidates[int(tok) - 1]
        else:
            hits = [c for c in pending.candidates if tok in self._describe(c).lower()]
            chosen = hits[0] if len(hits) == 1 else None
        if chosen is None:
            self.pending_clarification = pending
            return Reply(ReplyKind.CLARIFY, "I still cannot tell which; answer with the number.", candidates=pending.candidates, interpretation=pending)
        # the collapse is an INTERACTION evidence event; the other candidates are not deleted, they are
        # simply not the reading this utterance was resolved to
        _, eid = self.runtime.admit_evidence({"clarification": pending.utterance, "chosen": chosen.construction_id, "digest": canonical(chosen.meaning)[1]}, Channel.INTERACTION, speaker, scope=Scope.of(self.conversation))
        m = chosen.meaning
        if _is_question(m):
            return self._answer(_strip_question(m), pending)
        rep = self._record(pending.utterance, speaker, m, pending)
        return Reply(rep.kind, rep.text + f" (resolved by {eid})", evidence=rep.evidence + (eid,), interpretation=pending, meaning_digest=rep.meaning_digest)

    # ------------------------------------------------------------------ learning
    def register_family(self, family: AQ.ConstructionFamily) -> None:
        self.families[family.family] = family

    def demonstrate(self, family: str, utterance: str, meaning: MeaningGraph, speaker: str = "teacher") -> Reply:
        fam = self.families[family]
        _, eid = self.runtime.admit_evidence({"demonstration": utterance, "meaning": meaning.as_dict(), "family": family}, Channel.DEMONSTRATION, speaker, scope=Scope.of(self.conversation))
        self.demonstrations.setdefault(family, []).append(AQ.Demonstration(utterance, meaning, eid, speaker))
        p = AQ.acquire(fam, self.lexicon, self.demonstrations[family])
        if p.status.value != "PASS":
            return Reply(ReplyKind.LEARN, f"Demonstration recorded ({eid}); the {family} construction is still {p.status.value}: {p.detail}", evidence=(eid,))
        cid = f"{fam.language}:{family}:learned"
        self.constructions = [c for c in self.constructions if c.construction_id != cid] + [AQ.construction_from_proposal(fam, p, cid)]
        self.pending_learn = None
        return Reply(ReplyKind.RECORDED, f"Learned the {family} construction ({p.payload['hypothesis']}) from {len(p.warrant.evidence)} demonstration(s).", evidence=tuple(sorted(p.warrant.evidence)))

    # ------------------------------------------------------------------ retraction
    def retract(self, evidence_id: str, speaker: str = "user") -> Reply:
        if evidence_id not in {s.evidence_id for s in self.said}:
            return Reply(ReplyKind.CANNOT_CHECK, f"{evidence_id} is not a statement on record.")
        report = self.runtime.revoke([evidence_id])
        return Reply(ReplyKind.RETRACTED, f"Retracted {evidence_id}; reopened {sorted(report.reopen)}, rechecked {sorted(report.recheck)}.", evidence=(evidence_id,))

    # ------------------------------------------------------------------ rendering
    @staticmethod
    def _describe_meaning(m: MeaningGraph) -> str:
        parts = []
        for e in m.edges:
            if e.relation.startswith("ROLE:"):
                parts.append(f"{e.relation[5:]}={m.node(e.heads[0]).label}")
        ev = m.node(m.root).label if m.root else "?"
        return f"{ev}({', '.join(parts)})"

    def _describe(self, c: CandidateMeaning) -> str:
        labels = sorted({n.label for n in c.meaning.nodes if n.label})
        return f"{self._describe_meaning(c.meaning)} [{', '.join(labels)}]"
