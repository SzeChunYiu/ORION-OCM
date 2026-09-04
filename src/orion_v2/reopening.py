from __future__ import annotations
from dataclasses import dataclass
from enum import Enum

@dataclass(frozen=True, slots=True)
class SupportFamily:
    family_id: str; evidence_ids: frozenset[str]; commitment_ids: frozenset[str] = frozenset()
    def __post_init__(self) -> None:
        if not self.family_id.strip(): raise ValueError("family_id must be non-blank")
        if not self.evidence_ids and not self.commitment_ids: raise ValueError("support family must bind evidence or commitments")
        if any(not item.strip() for item in (*self.evidence_ids, *self.commitment_ids)): raise ValueError("support identities may not be blank")

@dataclass(frozen=True, slots=True)
class Commitment:
    commitment_id: str; support_families: tuple[SupportFamily, ...]
    def __post_init__(self) -> None:
        if not self.commitment_id.strip(): raise ValueError("commitment_id must be non-blank")
        if not self.support_families: raise ValueError("commitments require support")
        ids = [f.family_id for f in self.support_families]
        if len(ids) != len(set(ids)): raise ValueError("support family identities must be unique")

class CommitmentDisposition(str, Enum):
    PRESERVED = "PRESERVED"; REOPENED = "REOPENED"; CANNOT_CHECK_CYCLE = "CANNOT_CHECK_CYCLE"

@dataclass(frozen=True, slots=True)
class ReopenRecord:
    commitment_id: str; disposition: CommitmentDisposition; surviving_family_ids: tuple[str, ...]; defeated_family_ids: tuple[str, ...]

@dataclass(frozen=True, slots=True)
class SelectiveReopenReceipt:
    invalidated_evidence_ids: tuple[str, ...]; records: tuple[ReopenRecord, ...]; reopened_commitment_ids: tuple[str, ...]; preserved_commitment_ids: tuple[str, ...]; authority_granted: bool = False
    def __post_init__(self) -> None:
        if self.authority_granted: raise ValueError("reopen receipt cannot grant authority")

def selective_reopen(commitments: tuple[Commitment, ...], invalidated_evidence_ids: tuple[str, ...]) -> SelectiveReopenReceipt:
    ids = [c.commitment_id for c in commitments]
    if len(ids) != len(set(ids)): raise ValueError("commitment identities must be unique")
    known = set(ids)
    for c in commitments:
        deps = {d for f in c.support_families for d in f.commitment_ids}
        if not deps <= known: raise ValueError("support references unknown commitment")
    invalidated = set(invalidated_evidence_ids)
    if any(not item.strip() for item in invalidated): raise ValueError("invalid evidence identity")
    reopened: set[str] = set(); records: dict[str, ReopenRecord] = {}; unresolved = set(ids); progress = True
    while unresolved and progress:
        progress = False
        for c in commitments:
            if c.commitment_id not in unresolved: continue
            deps = {d for f in c.support_families for d in f.commitment_ids}
            if deps & unresolved: continue
            surviving=[]; defeated=[]
            for f in c.support_families:
                ok = not (f.evidence_ids & invalidated) and not (f.commitment_ids & reopened)
                (surviving if ok else defeated).append(f.family_id)
            disposition = CommitmentDisposition.PRESERVED if surviving else CommitmentDisposition.REOPENED
            if disposition is CommitmentDisposition.REOPENED: reopened.add(c.commitment_id)
            records[c.commitment_id] = ReopenRecord(c.commitment_id, disposition, tuple(sorted(surviving)), tuple(sorted(defeated)))
            unresolved.remove(c.commitment_id); progress = True
    for commitment_id in unresolved: records[commitment_id] = ReopenRecord(commitment_id, CommitmentDisposition.CANNOT_CHECK_CYCLE, (), ())
    ordered = tuple(records[i] for i in sorted(records))
    return SelectiveReopenReceipt(tuple(sorted(invalidated)), ordered, tuple(sorted(reopened)), tuple(r.commitment_id for r in ordered if r.disposition is CommitmentDisposition.PRESERVED))
