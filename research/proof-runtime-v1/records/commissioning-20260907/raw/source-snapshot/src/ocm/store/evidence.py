"""Evidence registry (M2 §3.2–§3.3) with dependence structure (MEG-01).

Every evidence record carries: id (content-bound), channel (the eight-channel enum mapped onto
``admission.CertificateKind``), source/provenance, content hash, scope, authority, status and
revocation state.  The universe splits as ``E = A ⊔ D``: **assumptions** ``A`` are the independent
revocable ids; **derived** evidence ``D`` carries its own warrant interval (its provenance) so a
claim citing ``d`` has warrant ``Λ_claim ⊗ Λ_d`` and revocation is always ``R ⊆ A``.

Behaviours required by M2 §3.3, each a distinct typed outcome, never a majority vote:
  byte-identical duplicate            → DUPLICATE_BYTES (same id returned; provenance appended)
  same content, different provenance  → DUPLICATE_CONTENT (new id; DEPENDS/SAME_CONTENT link)
  direct contradiction                → CONTRADICTION (registered as a nogood on the two ids)
  partial overlap                     → OVERLAP (recorded link; no merge)
  stale superseded evidence           → SUPERSEDED (old id stays; scope epoch closed; link)
  revoked source reappearing          → REVOKED_SOURCE_REAPPEARED (new id shares the assumption;
                                        it is dead while the assumption is revoked)
"""
from __future__ import annotations

from dataclasses import dataclass, field, replace
from enum import Enum
from typing import Any, Hashable, Iterable, Mapping

from ocm.kso.admission import CertificateKind, WARRANTING_KINDS
from ocm.kso.ids import content_hash, evidence_id
from ocm.kso.nogoods import NogoodSet
from ocm.kso.types import Authority, Scope
from ocm.kso.warrant import Liveness, WarrantProfile


class Channel(str, Enum):
    INSTRUCTION = "instruction"
    DEMONSTRATION = "demonstration"
    OBSERVATION = "observation"
    INTERACTION = "interaction"
    EXPERIMENT = "experiment"
    PROOF = "proof"
    FEEDBACK = "feedback"
    IMPORTED = "imported"

    @property
    def certificate(self) -> CertificateKind:
        return _CHANNEL_TO_CERT[self]


_CHANNEL_TO_CERT = {
    Channel.INSTRUCTION: CertificateKind.INSTRUCTION,
    Channel.DEMONSTRATION: CertificateKind.DEMONSTRATION,
    Channel.OBSERVATION: CertificateKind.OBSERVATION,
    Channel.INTERACTION: CertificateKind.INTERACTION,
    Channel.EXPERIMENT: CertificateKind.EXPERIMENTATION,
    Channel.PROOF: CertificateKind.EXACT_CHECKER,
    Channel.FEEDBACK: CertificateKind.FEEDBACK,
    Channel.IMPORTED: CertificateKind.IMPORTED,
}


class Admission(str, Enum):
    ADMITTED = "ADMITTED"
    DUPLICATE_BYTES = "DUPLICATE_BYTES"
    DUPLICATE_CONTENT = "DUPLICATE_CONTENT"
    CONTRADICTION = "CONTRADICTION"
    OVERLAP = "OVERLAP"
    SUPERSEDED = "SUPERSEDED"
    REVOKED_SOURCE_REAPPEARED = "REVOKED_SOURCE_REAPPEARED"


@dataclass(frozen=True)
class EvidenceRecord:
    evidence_id: str
    channel: Channel
    source: str                      # provenance (who/where)
    content_hash: str
    scope: Scope = field(default_factory=Scope.universal)
    authority: Authority = field(default_factory=Authority)
    derived_from: WarrantProfile | None = None   # None ⇒ assumption (A); interval ⇒ derived (D)
    superseded_by: str | None = None
    links: tuple[tuple[str, str], ...] = ()      # (kind, other_id)

    @property
    def is_assumption(self) -> bool:
        return self.derived_from is None

    @property
    def warrant(self) -> WarrantProfile:
        """The interval a citing claim multiplies in (MEG-01): assumptions are their own id."""
        if self.derived_from is None:
            return WarrantProfile.certified([frozenset({self.evidence_id})])
        return self.derived_from

    def as_dict(self) -> dict[str, Any]:
        return {
            "evidence_id": self.evidence_id,
            "channel": self.channel.value,
            "certificate": self.channel.certificate.value,
            "source": self.source,
            "content_hash": self.content_hash,
            "scope": self.scope.as_dict(),
            "authority": self.authority.as_dict(),
            "kind": "assumption" if self.is_assumption else "derived",
            "derived_from": None if self.derived_from is None else self.derived_from.as_dict(),
            "superseded_by": self.superseded_by,
            "links": list(self.links),
        }


@dataclass
class EvidenceRegistry:
    namespace: str = "ocm"
    records: dict[str, EvidenceRecord] = field(default_factory=dict)
    by_content: dict[str, list[str]] = field(default_factory=dict)
    revoked: frozenset = frozenset()
    nogoods: NogoodSet = field(default_factory=NogoodSet)
    log: list[tuple[str, str, str]] = field(default_factory=list)   # (outcome, evidence_id, detail)

    # --- registration ----------------------------------------------------------------------
    def register(
        self,
        payload: Any,
        channel: Channel | str,
        source: str,
        *,
        scope: Scope | None = None,
        authority: Authority | None = None,
        derived_from: WarrantProfile | None = None,
        overlaps: Iterable[str] = (),
        contradicts: Iterable[str] = (),
        supersedes: str | None = None,
    ) -> tuple[Admission, EvidenceRecord]:
        ch = Channel(channel)
        digest = content_hash(payload)
        eid = evidence_id(self.namespace, {"payload": payload, "source": source, "channel": ch.value})
        if eid in self.records:
            rec = self.records[eid]
            self._log(Admission.DUPLICATE_BYTES, eid, source)
            return Admission.DUPLICATE_BYTES, rec
        rec = EvidenceRecord(eid, ch, source, digest, scope or Scope.universal(), authority or Authority(), derived_from)
        outcome = Admission.ADMITTED
        same = self.by_content.get(digest, [])
        if same:
            rec = replace(rec, links=rec.links + tuple(("SAME_CONTENT", o) for o in same))
            outcome = Admission.DUPLICATE_CONTENT
        for o in overlaps:
            self._require(o)
            rec = replace(rec, links=rec.links + (("OVERLAPS", o),))
            outcome = Admission.OVERLAP if outcome is Admission.ADMITTED else outcome
        for o in contradicts:
            self._require(o)
            rec = replace(rec, links=rec.links + (("CONTRADICTS", o),))
            self.nogoods = self.nogoods.add({eid, o})     # they cannot both warrant anything
            outcome = Admission.CONTRADICTION
        if supersedes is not None:
            old = self._require(supersedes)
            self.records[supersedes] = replace(old, superseded_by=eid, scope=Scope(old.scope.contexts, (old.scope.epoch[0], min(old.scope.epoch[1], rec.scope.epoch[0]))))
            rec = replace(rec, links=rec.links + (("SUPERSEDES", supersedes),))
            outcome = Admission.SUPERSEDED
        if derived_from is not None and any(a in self.revoked for w in derived_from.lower for a in w) and not derived_from.is_live(self.revoked):
            outcome = Admission.REVOKED_SOURCE_REAPPEARED
        self.records[eid] = rec
        self.by_content.setdefault(digest, []).append(eid)
        self._log(outcome, eid, source)
        return outcome, rec

    def _require(self, eid: str) -> EvidenceRecord:
        if eid not in self.records:
            raise KeyError(f"unknown evidence id {eid}")
        return self.records[eid]

    def _log(self, outcome: Admission, eid: str, detail: str) -> None:
        self.log.append((outcome.value, eid, detail))

    # --- revocation (assumptions only) ----------------------------------------------------------
    def revoke(self, evidence: Iterable[str]) -> frozenset:
        for e in evidence:
            rec = self._require(e)
            if not rec.is_assumption:
                raise ValueError(f"{e} is derived evidence: revoke its assumptions, not the derivation (R ⊆ A)")
        self.revoked = self.revoked | frozenset(evidence)
        return self.revoked

    def reinstate(self, evidence: Iterable[str]) -> frozenset:
        self.revoked = self.revoked - frozenset(evidence)
        return self.revoked

    # --- warrant of a citation (MEG-01) ---------------------------------------------------------
    def citation_warrant(self, cited: Iterable[str]) -> WarrantProfile:
        """Λ = ⊗ over cited records' intervals; a FEEDBACK record contributes the certified zero."""
        out = WarrantProfile.one()
        for e in cited:
            rec = self._require(e)
            w = WarrantProfile.zero() if rec.channel is Channel.FEEDBACK else rec.warrant
            out = out.meet(w)
        return out

    def liveness(self, cited: Iterable[str]) -> Liveness:
        return self.nogoods.liveness(self.citation_warrant(cited), self.revoked)

    def independent_support_count(self, alternatives: Iterable[Iterable[str]]) -> int:
        """Number of alternatives with pairwise-disjoint assumption sets (MEG-01: shared
        assumptions never count twice).  Conservative: greedy maximal disjoint family."""
        sets = []
        for alt in alternatives:
            assumptions: set = set()
            for e in alt:
                assumptions |= self.citation_warrant([e]).evidence
            sets.append(frozenset(assumptions))
        chosen: list[frozenset] = []
        for s in sorted(sets, key=lambda x: (len(x), sorted(map(repr, x)))):
            if all(not (s & c) for c in chosen):
                chosen.append(s)
        return len(chosen)

    def as_dict(self) -> dict[str, Any]:
        return {"namespace": self.namespace, "records": {k: v.as_dict() for k, v in sorted(self.records.items())}, "revoked": sorted(self.revoked), "nogoods": self.nogoods.as_dict(), "log": list(self.log)}


def mutant_majority_truth(registry: EvidenceRegistry, claims: Mapping[str, Iterable[str]]) -> str:
    """Planted M2 §3.3 defect: the claim cited by the most records wins, regardless of warrant."""
    return max(claims, key=lambda c: len(list(claims[c])))
